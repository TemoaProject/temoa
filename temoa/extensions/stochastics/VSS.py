# Script to determine the value of the stochastic solution using Temoa
from pyomo.core import DataPortal
from pyomo.opt import SolverFactory
from pyomo.pysp.ef_vss import *
from pyomo.pysp.ef_writer_script_old import *


def organize_csv():
    # This function was imported from the EVPI script
    from collections import OrderedDict
    from csv import reader, writer

    rows = list()
    tech = list()
    node = list()
    empty_row = [''] * 7
    with open('V_ActivityByPeriodAndTech.csv', 'rb') as f:
        csv_reader = reader(f, dialect='excel')
        for row in csv_reader:
            rows.append(row + [''])

    organized_rows = OrderedDict()
    for row in rows:
        this_tech = row[4]
        if row[1] not in node:
            node.append(row[1])
        if this_tech not in tech:
            tech.append(this_tech)
            organized_rows[this_tech] = [row]
        else:
            organized_rows[this_tech].append(row)

    for this_tech in tech:
        for i in range(0, len(organized_rows[this_tech])):
            if organized_rows[this_tech][i][1] != node[i]:
                organized_rows[this_tech].insert(i, empty_row)

                # tech.sort()
    with open('V_ActivityByPeriodAndTech_org.csv', 'wb') as f:
        csv_writer = writer(f, dialect='excel')
        for this_tech in organized_rows:
            row = list()
            for i in organized_rows[this_tech]:
                row += i
            csv_writer.writerow(row)


def my_ef_writer(scenario_tree):
    # This function was imported from the EVPI script
    from collections import OrderedDict
    from csv import writer

    rows = dict()  # Key is the variable's name
    for stage in scenario_tree._stages:
        stage_name = stage._name
        for tree_node in stage._tree_nodes:
            tree_node_name = tree_node._name
            for var_id in sorted(tree_node._variable_ids):
                var_name, index = tree_node._variable_ids[var_id]
                row = [str(stage_name), str(tree_node_name), str(var_name)]
                if isinstance(index, str):
                    row += [index]
                else:
                    for i in index:
                        row += [str(i)]
                row += [str(tree_node._solution[var_id])]
                if var_name not in rows:
                    rows[var_name] = [row]
                else:
                    rows[var_name].append(row)

            stage_cost_vardata = tree_node._cost_variable_datas[0][0]
            obj = str(stage_cost_vardata.parent_component().name)
            row = [
                str(stage_name),
                str(tree_node_name),
                str(obj),
                str(stage_cost_vardata.index()),
                str(stage_cost_vardata()),
            ]
            if obj not in rows:
                rows[obj] = [row]
            else:
                rows[obj].append(row)

    for ofile in rows.keys():
        with open(ofile + '.csv', 'wb') as f:
            csv_writer = writer(f, dialect='excel')
            csv_writer.writerows(rows[ofile])

            # To calculate V_Activity[p,t]
    if 'V_ActivityByPeriodAndProcess' in rows:
        V_Activity_ptv = rows['V_ActivityByPeriodAndProcess']
        V_Activity_pt = OrderedDict()
        for row in V_Activity_ptv:
            key = (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
            )  # (Stage, Node, var_name, p, t)
            if key not in V_Activity_pt:
                V_Activity_pt[key] = float(row[6])
            else:
                V_Activity_pt[key] += float(row[6])

        with open('V_ActivityByPeriodAndTech.csv', 'wb') as f:
            csv_writer = writer(f, dialect='excel')
            for key in V_Activity_pt.keys():
                row = list(key) + [V_Activity_pt[key]]
                csv_writer.writerow(row)


def solve_ef(ef_options):
    # This function solves a stochastic optimization problem via extensive form
    # This function was imported from the EVPI script
    import os
    import sys

    sif = ScenarioTreeInstanceFactory(
        ef_options.model_directory, ef_options.instance_directory, ef_options.verbose
    )
    scenario_tree = GenerateScenarioTreeForEF(ef_options, sif)
    ef = EFAlgorithmBuilder(ef_options, scenario_tree)
    f = open(os.devnull, 'w')
    sys.stdout = f
    ef.solve()
    # ef.save_solution() # This line saves the results into two csv files
    sys.stdout = sys.__stdout__
    f.close()
    sys.stderr.write('\nrunef output suppressed\n')
    my_ef_writer(ef._scenario_tree)
    root_node = ef._scenario_tree._stages[0]._tree_nodes[0]
    # II()
    return root_node.computeExpectedNodeCost()


def solve_ef_fix(ef_options, avg_instance):
    # This function solves a stochastic optimization problem via extensive form
    # where first stage decision variables are fixed at the optimal values from
    # the deterministic model called here avg_instance

    import os
    import sys

    sif = ScenarioTreeInstanceFactory(
        ef_options.model_directory, ef_options.instance_directory, ef_options.verbose
    )
    scenario_tree = GenerateScenarioTreeForEF(ef_options, sif)
    ef = EFAlgorithmBuilder(ef_options, scenario_tree)

    time_fut = avg_instance.time_future.data()
    techs = avg_instance.tech_all.data()
    dv_capacity = (
        avg_instance.v_capacity.get_values()
    )  # Getting dec vars that matters to be fixed
    # dV_HydroStorage = avg_instance.V_HydroStorage.get_values()

    # Storing techs and future time periods in vector for easy access
    vtime_fut = [0] * len(time_fut)
    k = 0
    for iaux in time_fut:
        vtime_fut[k] = iaux
        k = k + 1

    # Fixing Capacity values for first stage at the ef instance with values from
    # the deterministic instance
    for iaux1, iaux2 in dv_capacity:
        if iaux2 == vtime_fut[0]:
            ef._binding_instance.S0s0s0.v_capacity[iaux1, iaux2].fix(dv_capacity[iaux1, iaux2])
            # ef._binding_instance.S0.v_capacity[iaux1, iaux2].fix(3)
            # just for checking if fixing at one scen also fix in the other - ok for now

    # Fixing Hydro Storage values for first stage
    # for iaux1 , iaux2 in dV_HydroStorage:
    # if iaux2 == vtime_fut[0]:
    # ef._binding_instance.S0s0.V_HydroStorage[iaux1, iaux2].fix(dV_HydroStorage[iaux1,iaux2])

    f = open(os.devnull, 'w')
    sys.stdout = f
    ef.solve()
    # ef.save_solution() # This line saves the results into two csv files
    sys.stdout = sys.__stdout__
    f.close()
    sys.stderr.write('\nrunef output suppressed\n')
    my_ef_writer(ef._scenario_tree)
    root_node = ef._scenario_tree._stages[0]._tree_nodes[0]
    return root_node.computeExpectedNodeCost()


def solve_dm(p_model, p_data, opt_solver):
    # This function solves a deterministic model with the inputs for
    # uncertainty values represented by their average values at each stage
    # We assume the ReferenceModel.dat as the average problem properly represented
    # inside the stochastic folder

    def return_obj(instance):
        from pyomo.core import Objective

        obj = instance.component_objects(Objective, active=True)
        obj_values = list()
        for o in obj:
            # See section 18.6.3 in Pyomo online doc
            method_obj = getattr(instance, str(o))
            obj_values.append(method_obj())
        # Assuming there is only one objective function
        return obj_values[0]

    import os
    import sys

    (head, tail) = os.path.split(p_model)
    sys.path.insert(0, head)
    pwd = os.getcwd()
    os.chdir(p_data)

    model_module = __import__(tail[:-3], globals(), locals())
    model = model_module.model
    dm_result = {'cost': list(), 'flowin': list(), 'flowout': list(), 'capacity': list()}

    data = DataPortal(model=model)

    dat = 'AverageModel.dat'  # Loading the model from the data file
    data.load(filename=dat)

    instance = model.create_instance(
        data
    )  # Defining the model instance with the data from .dat file
    optimizer = SolverFactory(opt_solver)  # Defining the optimization solver
    results = optimizer.solve(instance)  # Solving the optimization model

    instance.solutions.load_from(results)  # Saving solutions in memory

    # Getting objective function values
    obj_val = return_obj(instance)
    dm_result['cost'].append(obj_val)

    # Writting to the Shell
    sys.stdout.write(
        '\nSolved deterministic model with uncertainty at average valures \n'
    )
    sys.stdout.write(f'    Total cost: {obj_val}\n')
    os.chdir(pwd)
    return instance  # Returning instance solved, values will be used later


def runEVPI():
    # EVPI_value = test_twotechs_vss_base()
    EVPI_value = test_sudan_VSS()
    return EVPI_value


def runECIU():
    import os

    # folder_string = "stochastic/twotechs_vss_base/"
    folder_string = 'stochastic/utopia_vss/'
    os.system('python temoa_model/ --eciu ' + folder_string)


def runVSS():
    # This is the main function. It calls 1) Extensive Form 2)Deterministic LP
    # 3)Fixed Extensive Form. After results of 1) and 3) are obtained it computes the VSS
    # As input, this function requires the path of the stochastic folder and
    # temoa_stochastic.py file
    # It assumes that an instance named ReferenceModel.dat is located inside the stochastic folder

    import sys
    from time import time

    sys.stderr.write('\nFinding the Value of the Stochastic Solution using Temoa\n')

    p_model = '/home/arqueiroz/SSudan/S1_2_H/temoa_model/temoa_stochastic.py'
    p_data = '/home/arqueiroz/SSudan/S1_2_H/stochastic/S_Sudan_original_stoch_cap_cost_11'
    optsolver = 'cplex'

    # ---------------------
    # Solving the deterministic model with average values
    # ---------------------
    sys.stderr.write('\nSolving perfect sight with uncertainty at average values\n')
    dm_instance = solve_dm(
        p_model, p_data, optsolver
    )  # Here we have all the information with respect to objfunc and decvars

    zdm_result = dm_instance.total_cost.value
    # ---------------------
    # Solving the extensive model for the recoursive problem
    # ---------------------
    ef_args = ['-m', p_model, '-i', p_data, '--solver', optsolver, '--solve']
    ef_option_parser = construct_ef_writer_options_parser('runef [options]')
    start_time = time()
    (ef_options, args) = ef_option_parser.parse_args(args=ef_args)

    # II()
    sys.stderr.write('\nSolving extensive form\n')
    ef_result = solve_ef(ef_options)

    msg = f'\nrunef time: {time() - start_time} s\n'
    msg += f'runef objective value: {ef_result}\n'
    sys.stderr.write(msg)

    # ---------------------
    # Solving the extensive model fixing variables for stage 1
    # ---------------------
    ef_result_fixed = solve_ef_fix(ef_options, dm_instance)

    # Compute the value of the stochastic solution (vss = z_eev - z_rp)
    return ef_result, ef_result_fixed, zdm_result


if __name__ == '__main__':
    vZrp, vZeev, vZdm = runVSS()
    print('---------------------------------------------------------')
    print('---------------------------------------------------------')
    vEVPI = runEVPI()
    print('---------------------------------------------------------')
    print('---------------------------------------------------------')
    # runECIU()
    print('---------------------------------------------------------')
    print('---------------------------------------------------------')
    print('Zrp   = ', vZrp)
    print('Zeev  = ', vZeev)
    print('Zdm   = ', vZdm)
    print('EVPI  = ', vEVPI)
    print('VSS   = ', vZeev - vZrp)
