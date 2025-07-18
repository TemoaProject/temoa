# from __future__ import division
import time
from pathlib import Path

from pyomo.dataportal import DataPortal

from definitions import PROJECT_ROOT
from temoa.temoa_model import run_actions
from temoa.temoa_model.hybrid_loader import HybridLoader
from temoa.temoa_model.table_writer import TableWriter
from temoa.temoa_model.temoa_config import TemoaConfig

start_time = time.time()
import sqlite3

from joblib import Parallel, delayed
from numpy import array
from SALib.analyze import morris
from SALib.sample.morris import sample
from SALib.util import compute_groups_matrix, read_param_file

seed = 42


def evaluate(param_names, param_values, data: dict, k):
    m = len(param_values)
    for j in range(0, m):
        names = param_names[j]

        match names[0]:
            case 'CostInvest':
                data[names[0]][tuple(names[1:4])] = param_values[j]
            case 'CostVariable':
                data[names[0]][tuple(names[1:5])] = param_values[j]
            case 'Efficiency':
                data[names[0]][tuple(names[1:6])] = param_values[j]
            case _:
                raise ValueError(f'Unrecognized parameter: {names[0]}')

    dp = DataPortal(data_dict={None: data})
    instance = run_actions.build_instance(loaded_portal=dp)
    mdl, res = run_actions.solve_instance(instance=instance, solver_name=config.solver_name)
    status = run_actions.check_solve_status(res)
    if not status:
        raise RuntimeError('Bad solve during Method of Morris')
    table_writer = TableWriter(config)
    table_writer.write_results(M=mdl)

    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('SELECT * FROM OutputObjective')
    output_query = cur.fetchall()
    for row in output_query:
        Y_OF = row[-1]
    cur.execute("SELECT emis_comm, SUM(emission) FROM OutputEmission WHERE emis_comm='co2'")
    output_query = cur.fetchall()
    for row in output_query:
        Y_CumulativeCO2 = row[-1]
    Morris_Objectives = []
    Morris_Objectives.append(Y_OF)
    Morris_Objectives.append(Y_CumulativeCO2)
    con.close()
    return Morris_Objectives


morris_root = Path(PROJECT_ROOT, 'temoa/extensions/method_of_morris')
perturbation_coefficient = 0.2  # minus plus 10% of the baseline values
param_file = morris_root / 'm_params.txt'
db_file = Path(PROJECT_ROOT, 'data_files/untracked_data/morris/morris_utopia.sqlite')
config_path = Path(PROJECT_ROOT, 'data_files/untracked_data/morris/morris_utopia.toml')
with sqlite3.connect(db_file) as con:
    with open(param_file, 'w') as file:
        param_names = {}
        cur = con.cursor()
        cur.execute(
            'SELECT region, period, tech, vintage, cost, MMAnalysis FROM CostVariable WHERE MMAnalysis is not NULL'
        )
        output_query = cur.fetchall()
        g1 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i] = [
                'CostVariable',
                *output_query[i][:4],
                'cost_variable',
            ]

            file.write('x' + str(i))
            file.write(' ')
            file.write(str(output_query[i][4] * 0.9))
            file.write(' ')
            file.write(str(output_query[i][4] * 1.1))
            file.write(' ')
            file.write(output_query[i][-1])
            file.write('\n')

        cur.execute(
            'SELECT region, tech, vintage, cost, MMAnalysis FROM CostInvest WHERE MMAnalysis is not NULL'
        )
        output_query = cur.fetchall()
        g2 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i + g1] = ['CostInvest', *output_query[i][:3], 'cost_invest']

            file.write('x' + str(i + g1))
            file.write(' ')
            file.write(str(output_query[i][3] * 0.9))
            file.write(' ')
            file.write(str(output_query[i][3] * 1.1))
            file.write(' ')
            file.write(output_query[i][-1])
            file.write('\n')
        cur.execute(
            'SELECT DISTINCT region, input_comm, tech, vintage, output_comm, efficiency, MMAnalysis FROM Efficiency WHERE MMAnalysis is not NULL'
        )
        output_query = cur.fetchall()
        g3 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i + g1 + g2] = [
                'Efficiency',
                *output_query[i][:5],
                'efficiency',
            ]
            file.write('x' + str(i + g1 + g2))
            file.write(' ')
            file.write(str(output_query[i][5] * 0.9))
            file.write(' ')
            file.write(str(output_query[i][5] * 1.1))
            file.write(' ')
            file.write(output_query[i][-1])
            file.write('\n')

        # load a data portal, retrieve the data dict for the problem
        config = TemoaConfig.build_config(config_file=config_path, output_path='.')
        loader = HybridLoader(db_connection=con, config=config)
        loader.load_data_portal()
        data = loader.data

problem = read_param_file(str(param_file), delimiter=' ')
param_values = sample(
    problem, N=10, num_levels=8, optimal_trajectories=False, local_optimization=False, seed=seed
)
print(param_values)
print(param_names)
n = len(param_values)
# pull the data

num_cores = 1  # multiprocessing.cpu_count()
Morris_Objectives = Parallel(n_jobs=num_cores)(
    delayed(evaluate)(param_names, param_values[i, :], data, i) for i in range(0, n)
)
Morris_Objectives = array(Morris_Objectives)
print(Morris_Objectives)
Si_OF = morris.analyze(
    problem,
    param_values,
    Morris_Objectives[:, 0],
    conf_level=0.95,
    print_to_console=False,
    num_levels=8,
    num_resamples=1000,
    seed=seed + 1,
)

Si_CumulativeCO2 = morris.analyze(
    problem,
    param_values,
    Morris_Objectives[:, 1],
    conf_level=0.95,
    print_to_console=False,
    num_levels=8,
    num_resamples=1000,
    seed=seed + 2,
)
num_vars = problem['num_vars']
groups, unique_group_names = compute_groups_matrix(problem['groups'])
number_of_groups = len(unique_group_names)
print(
    '{0:<30} {1:>10} {2:>10} {3:>15} {4:>10}'.format(
        'Parameter', 'Mu_Star', 'Mu', 'Mu_Star_Conf', 'Sigma'
    )
)
for j in list(range(number_of_groups)):
    print(
        '{0:30} {1:10.3f} {2:10.3f} {3:15.3f} {4:10.3f}'.format(
            Si_OF['names'][j],
            Si_OF['mu_star'][j],
            Si_OF['mu'][j],
            Si_OF['mu_star_conf'][j],
            Si_OF['sigma'][j],
        )
    )
import csv

line1 = Si_OF['mu_star']
line2 = Si_OF['mu_star_conf']
line3 = Si_CumulativeCO2['mu_star']
line4 = Si_CumulativeCO2['mu_star_conf']
with open('MMResults.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(unique_group_names)
    writer.writerow('Objective Function')
    writer.writerow(line1)
    writer.writerow(line2)
    writer.writerow('Cumulative CO2 Emissions')
    writer.writerow(line3)
    writer.writerow(line4)

f.close
print('--- %s seconds ---' % (time.time() - start_time))
