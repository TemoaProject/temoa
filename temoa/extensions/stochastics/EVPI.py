# This version is compatible with Pyomo 5.2

import os
import sys

from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.pysp.ef import create_ef_instance
from pyomo.pysp.scenariotree.manager import ScenarioTreeManagerClientSerial


# To see detailed information about options
# for name in options.keys():
#    print(options.about(name))

# To see a more compact display of options
# options.display()

# options.model_location = \
#     os.path.join(farmer_example_dir, 'models')
# options.scenario_tree_location = \
#     os.path.join(farmer_example_dir, 'scenariodata')


class DummyTemoaConfig:
    pass


def compute_evpi(ef_result, pf_result):
    pf = 0
    for i in range(0, len(pf_result['cost'])):
        pf += pf_result['cd'][i] * pf_result['cost'][i]
    return ef_result - pf


def solve_pf(p_model, p_data):
    """
    solve_pf(p_model, p_data) -> dict()
    Solves the model in perfect sight mode.
    p_model -> string, the path to the model file.
    p_data -> string, the path to the directory of data for the stochastic
    model, where ScenarioStructure.dat should resides.
    Returns a dictionary including the value of objective function for each
    scenario and its conditional probability.
    """

    def return_obj(instance):
        from pyomo.core import Objective

        obj = instance.component_objects(Objective, active=True)
        obj_values = list()
        for o in obj:
            # See section 18.6.3 in Pyomo online doc
            # https://taizilongxu.gitbooks.io/stackoverflow-about-python/content/59/README.html
            method_obj = getattr(instance, str(o))
            obj_values.append(method_obj())
        # Assuming there is only one objective function
        return obj_values[0]

        # Out-of-date for Pyomo 4.1
        # obj = instance.active_components(Objective)
        # objs = obj.items()[0]
        # obj_name, obj_value = objs[0], value(objs[1]())
        # return obj_value

    import sys
    import os
    from collections import deque, defaultdict
    from pyomo.pysp.util.scenariomodels import scenario_tree_model

    (head, tail) = os.path.split(p_model)
    sys.path.insert(0, head)
    pwd = os.getcwd()
    os.chdir(p_data)

    s2fp_dict = defaultdict(deque)  # Scenario to 'file path' dictionary, .dat not included
    s2cd_dict = defaultdict(float)  # Scenario to conditonal density mapping
    sStructure = scenario_tree_model.create_instance(filename='ScenarioStructure.dat')

    # The following code is borrowed from Kevin's temoa_lib.py
    ###########################################################################
    # Step 1: find the root node.  PySP doesn't make this very easy ...

    # a child -> parent mapping, because every child has only one parent, but
    # not vice-versa
    ctpTree = dict()  # Child to parent dict, one to one mapping

    to_process = deque()
    to_process.extend(sStructure.children.keys())
    while to_process:
        node = to_process.pop()
        if node in sStructure.children:
            # it's a parent!
            new_nodes = set(sStructure.children[node])
            to_process.extend(new_nodes)
            ctpTree.update({n: node for n in new_nodes})

            # parents           -     children
    root_node = (set(ctpTree.values()) - set(ctpTree.keys())).pop()

    # ptcTree = defaultdict( list ) # Parent to child node, one to multiple mapping
    # for c, p in ctpTree.iteritems():
    #         ptcTree[ p ].append( c )
    # ptcTree = dict( ptcTree )   # be slightly defensive; catch any additions

    # leaf_nodes = set(ctpTree.keys()) - set(ctpTree.values())
    leaf_nodes = set(sStructure.scenario_leaf_node.values())  # Try to hack Kevin's code

    scenario_nodes = dict()  # Map from leafnode to 'node path'
    for node in leaf_nodes:  # e.g.: {Rs0s0: [R, Rs0, Rs0s0]}
        s = deque()
        scenario_nodes[node] = s
        while node in ctpTree:
            s.append(node)
            node = ctpTree[node]
        s.append(node)
        s.reverse()
    ###########################################################################

    for s in sStructure.scenarios:
        cp = 1.0  # Starting probability
        for n in scenario_nodes[sStructure.scenario_leaf_node[s]]:
            cp = cp * sStructure.conditional_probability[n]
            if not sStructure.scenario_based_data.value:
                s2fp_dict[s].append(n + '.dat')
        s2cd_dict[s] = cp

    if sStructure.scenario_based_data.value:
        for s in sStructure.scenarios:
            s2fp_dict[s].append(s + '.dat')
    # IP()
    model_module = __import__(tail[:-3], globals(), locals())
    model = model_module.model
    pf_result = {'cost': list(), 'cd': list()}
    for s in sStructure.scenarios:
        pf_result['cd'].append(s2cd_dict[s])
        data = DataPortal(model=model)
        for dat in s2fp_dict[s]:
            data.load(filename=dat)
        instance = model.create_instance(data)
        optimizer = SolverFactory('cplex')
        results = optimizer.solve(instance)

        instance.solutions.load_from(results)
        # instance.load(results)
        obj_val = return_obj(instance)
        pf_result['cost'].append(obj_val)
        sys.stdout.write(f'\nSolved .dat(s) {s2fp_dict[s]}\n')
        sys.stdout.write(f'    Total cost: {obj_val}\n')
    os.chdir(pwd)
    return pf_result


def solve_ef(p_model, p_data, dummy_temoa_options=None):
    """
    solve_ef(p_model, p_data) -> objective value of the extensive form
    Solves the model in stochastic mode.
    p_model -> string, the path to the model file (ReferenceModel.py).
    p_data -> string, the path to the directory of data for the stochastic
    mdoel, where ScenarioStructure.dat should resides.
    Returns a float point number of the value of objective function for the
    stochastic program model.
    """

    options = ScenarioTreeManagerClientSerial.register_options()

    if os.path.basename(p_model) == 'ReferenceModel.py':
        options.model_location = os.path.dirname(p_model)
    else:
        sys.stderr.write('\nModel file should be ReferenceModel.py. Exiting...\n')
        sys.exit(1)
    options.scenario_tree_location = p_data

    # using the 'with' block will automatically call
    # manager.close() and gracefully shutdown
    with ScenarioTreeManagerClientSerial(options) as manager:
        manager.initialize()

        ef_instance = create_ef_instance(manager.scenario_tree, verbose_output=options.verbose)

        ef_instance.dual = Suffix(direction=Suffix.IMPORT)

        with SolverFactory('cplex') as opt:
            ef_result = opt.solve(ef_instance)

        # Write to database
        if dummy_temoa_options:
            sys.path.append(options.model_location)
            from pformat_results import pformat_results
            from temoa_config import TemoaConfig

            temoa_options = TemoaConfig()
            temoa_options.config = dummy_temoa_options.config
            temoa_options.save_lp_file = dummy_temoa_options.save_lp_file
            temoa_options.saveTEXTFILE = dummy_temoa_options.saveTEXTFILE
            temoa_options.path_to_data = dummy_temoa_options.path_to_data
            temoa_options.save_excel = dummy_temoa_options.save_excel
            ef_result.solution.Status = 'feasible'  # Assume it is feasible
            for s in manager.scenario_tree.scenarios:
                ins = s._instance
                temoa_options.scenario = s.name
                temoa_options.dot_dat = [
                    os.path.join(options.scenario_tree_location, s.name + '.dat')
                ]
                temoa_options.output_file = os.path.join(
                    options.scenario_tree_location, dummy_temoa_options.output_file
                )
                msg = f'\nStoring results from scenario {s.name} to database.\n'
                sys.stderr.write(msg)
                formatted_results = pformat_results(ins, ef_result, temoa_options)

    ef_instance.solutions.store_to(ef_result)
    ef_obj = value(ef_instance.EF_EXPECTED_COST.values()[0])
    return ef_obj


def do_test(p_model, p_data, temoa_config=None):
    from time import time

    t0 = time()
    timeit = lambda: time() - t0

    if not isinstance(p_data, list):
        p_data = [p_data]
    for this_data in p_data:
        sys.stderr.write('\nSolving perfect sight mode\n')
        sys.stdout.write('-' * 25 + '\n')
        pf_result = solve_pf(p_model, this_data)
        msg = f'Time: {timeit()} s\n'
        sys.stderr.write(msg)

        sys.stderr.write('\nSolving extensive form\n')
        sys.stdout.write('-' * 25 + '\n')
        ef_result = solve_ef(p_model, this_data, temoa_config)

        msg = f'\nTime: {timeit()} s\n'
        msg += f'runef objective value: {ef_result}\n'
        msg += f'EVPI: {compute_evpi(ef_result, pf_result)}\n'
        sys.stderr.write(msg)


if __name__ == '__main__':
    # p_model = "/afs/unity.ncsu.edu/users/b/bli6/temoa/temoa_model"
    # p_data = [
    # "/afs/unity.ncsu.edu/users/b/bli6/TEMOA_stochastic/NC/noIGCC-CP",
    # "/afs/unity.ncsu.edu/users/b/bli6/TEMOA_stochastic/NC/noIGCC-noCP",
    # "/afs/unity.ncsu.edu/users/b/bli6/TEMOA_stochastic/NC/IGCC-CP",
    # "/afs/unity.ncsu.edu/users/b/bli6/TEMOA_stochastic/NC/IGCC-noCP",
    # ]
    # dummy_temoa_options = DummyTemoaConfig()
    # dummy_temoa_options.config = None
    # dummy_temoa_options.keepPyomoLP = False
    # dummy_temoa_options.saveTEXTFILE = False
    # dummy_temoa_options.path_to_data = None
    # dummy_temoa_options.saveEXCEL = False
    # dummy_temoa_options.output = "NCreference.db"
    # do_test(p_model, p_data, dummy_temoa_options)

    p_model = '/mnt/disk2/nspatank/SS_2_H/For_Jeff/temoa_ssudan/temoa_model/ReferenceModel.py'
    p_data = '/mnt/disk2/nspatank/SS_2_H/For_Jeff/temoa_ssudan/tools/S_Sudan'
    do_test(p_model, p_data)
