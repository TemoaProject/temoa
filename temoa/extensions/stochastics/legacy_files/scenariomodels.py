# grab the pyomo modeling components.
from pyomo.environ import *

scenario_tree_model = AbstractModel()

# all set/parameter values are strings, representing the names of various entities/variables.

scenario_tree_model.stages = Set(ordered=True)
scenario_tree_model.nodes = Set()

scenario_tree_model.node_stage = Param(scenario_tree_model.nodes, within=scenario_tree_model.stages)
scenario_tree_model.children = Set(
    scenario_tree_model.nodes, within=scenario_tree_model.nodes, ordered=True
)
scenario_tree_model.conditional_probability = Param(scenario_tree_model.nodes)

scenario_tree_model.scenarios = Set(ordered=True)
scenario_tree_model.scenario_leaf_node = Param(
    scenario_tree_model.scenarios, within=scenario_tree_model.nodes
)

scenario_tree_model.stage_variables = Set(scenario_tree_model.stages)
scenario_tree_model.stage_cost_variable = Param(scenario_tree_model.stages)

# scenario data can be populated in one of two ways. the first is "scenario-based",
# in which a single .dat file contains all of the data for each scenario. the .dat
# file prefix must correspond to the scenario name. the second is "node-based",
# in which a single .dat file contains only the data for each node in the scenario
# tree. the node-based method is more compact, but the scenario-based method is
# often more natural when parameter data is generated via simulation. the default
# is scenario-based.
scenario_tree_model.scenario_based_data = Param(within=Boolean, default=True, mutable=True)

# do we bundle, and if so, how?
scenario_tree_model.bundling = Param(within=Boolean, default=False, mutable=True)
scenario_tree_model.bundles = Set()  # bundle names
scenario_tree_model.bundle_scenarios = Set(scenario_tree_model.bundles)


# scenario_tree_model = AbstractModel()

## all set/parameter values are strings, representing the names of various entities/variables.

# scenario_tree_model.stages = Set(ordered=True)
# scenario_tree_model.nodes = Set()

# scenario_tree_model.node_stage = Param(scenario_tree_model.nodes, within=scenario_tree_model.stages)
# scenario_tree_model.children = Set(scenario_tree_model.nodes, within=scenario_tree_model.nodes, ordered=True)
# scenario_tree_model.conditional_probability = Param(scenario_tree_model.nodes)

# scenario_tree_model.scenarios = Set(ordered=True)
# scenario_tree_model.scenario_leaf_node = Param(scenario_tree_model.scenarios, within=scenario_tree_model.nodes)

# scenario_tree_model.stage_variables = Set(scenario_tree_model.stages)
# scenario_tree_model.stage_cost_variable = Param(scenario_tree_model.stages)

## scenario data can be populated in one of two ways. the first is "scenario-based",
## in which a single .dat file contains all of the data for each scenario. the .dat
## file prefix must correspond to the scenario name. the second is "node-based",
## in which a single .dat file contains only the data for each node in the scenario
## tree. the node-based method is more compact, but the scenario-based method is
## often more natural when parameter data is generated via simulation. the default
## is scenario-based.
# scenario_tree_model.scenario_based_data = Param(within=Boolean, default=True)
