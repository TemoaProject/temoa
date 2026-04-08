from __future__ import annotations

import csv
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

from joblib import Parallel, delayed  # type: ignore[import-untyped]
from numpy import array
from pyomo.dataportal import DataPortal
from SALib.analyze import morris  # type: ignore[import-untyped]
from SALib.sample.morris import sample  # type: ignore[import-untyped]
from SALib.util import compute_groups_matrix, read_param_file  # type: ignore[import-untyped]

from temoa._internal import run_actions
from temoa._internal.table_writer import TableWriter
from temoa.core.config import TemoaConfig
from temoa.data_io.hybrid_loader import HybridLoader

seed = 42


def evaluate(param_names: dict[int, list[Any]], param_values: Any,
            data: dict[str, Any], k: int) -> list[Any]:
    m = len(param_values)
    for j in range(0, m):
        names = param_names[j]

        match names[0]:
            case 'cost_invest':
                data[names[0]][tuple(names[1:4])] = param_values[j]
            case 'cost_variable':
                data[names[0]][tuple(names[1:5])] = param_values[j]
            case 'efficiency':
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
    table_writer.write_results(model=mdl)

    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('SELECT * FROM output_objective')
    output_query = cur.fetchall()
    for row in output_query:
        y_of = row[-1]
    cur.execute("SELECT emis_comm, SUM(emission) FROM output_emission WHERE emis_comm='co2'")
    output_query = cur.fetchall()
    for row in output_query:
        y_cumulative_co2 = row[-1]
    morris_objectives = []
    morris_objectives.append(y_of)
    morris_objectives.append(y_cumulative_co2)
    con.close()
    return morris_objectives


morris_root = Path(__file__).parent
perturbation_coefficient = 0.2  # minus plus 10% of the baseline values
param_file = morris_root / 'm_params.txt'

db_file = Path(__file__).parent / 'morris_utopia.sqlite'
config_path = Path(__file__).parent / 'morris_utopia.toml'

if not db_file.exists() or not config_path.exists():
    raise FileNotFoundError(
        "Example Morris data files not found in current directory. "
        "Please see MM_README.md for instructions on how to generate "
        "or provide the required 'morris_utopia.sqlite' and 'morris_utopia.toml'."
    )

with sqlite3.connect(str(db_file)) as con:
    with open(param_file, 'w') as file:
        param_names = {}
        cur = con.cursor()
        cur.execute(
            'SELECT region, period, tech, vintage, cost, MMAnalysis FROM cost_variable WHERE '
            'MMAnalysis is not NULL'
        )
        output_query = cur.fetchall()
        g1 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i] = [
                'cost_variable',
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
            'SELECT region, tech, vintage, cost, MMAnalysis FROM cost_invest WHERE MMAnalysis is '
            'not NULL'
        )
        output_query = cur.fetchall()
        g2 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i + g1] = ['cost_invest', *output_query[i][:3], 'cost_invest']

            file.write('x' + str(i + g1))
            file.write(' ')
            file.write(str(output_query[i][3] * 0.9))
            file.write(' ')
            file.write(str(output_query[i][3] * 1.1))
            file.write(' ')
            file.write(output_query[i][-1])
            file.write('\n')

        cur.execute(
            'SELECT DISTINCT region, input_comm, tech, vintage, output_comm, efficiency, '
            'MMAnalysis FROM efficiency WHERE MMAnalysis is not NULL'
        )
        output_query = cur.fetchall()
        g3 = len(output_query)
        for i in range(0, len(output_query)):
            param_names[i + g1 + g2] = [
                'efficiency',
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
        config = TemoaConfig.build_config(config_file=config_path, output_path=Path('.'))
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
        si_of = morris.analyze(
            problem,
            param_values,
            Morris_Objectives[:, 0],
            conf_level=0.95,
            print_to_console=False,
            num_levels=8,
            num_resamples=1000,
            seed=seed + 1,
        )

        si_cumulative_co2 = morris.analyze(
            problem,
            param_values,
            Morris_Objectives[:, 1],
            conf_level=0.95,
            print_to_console=False,
            num_levels=8,
            num_resamples=1000,
            seed=seed + 2,
        )
        groups, unique_group_names = compute_groups_matrix(problem['groups'])
        number_of_groups = len(unique_group_names)
        print(
            '{:<30} {:>10} {:>10} {:>15} {:>10}'.format(
                'Parameter', 'Mu_Star', 'Mu', 'Mu_Star_Conf', 'Sigma'
            )
        )
        for j in list(range(number_of_groups)):
            print(
                '{:30} {:10.3f} {:10.3f} {:15.3f} {:10.3f}'.format(
                    si_of['names'][j],
                    si_of['mu_star'][j],
                    si_of['mu'][j],
                    si_of['mu_star_conf'][j],
                    si_of['sigma'][j],
                )
            )

        line1 = si_of['mu_star']
        line2 = si_of['mu_star_conf']
        line3 = si_cumulative_co2['mu_star']
        line4 = si_cumulative_co2['mu_star_conf']
        with open('MMResults.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(unique_group_names)
            writer.writerow('Objective Function')
            writer.writerow(line1)
            writer.writerow(line2)
            writer.writerow('Cumulative CO2 Emissions')
            writer.writerow(line3)
            writer.writerow(line4)
