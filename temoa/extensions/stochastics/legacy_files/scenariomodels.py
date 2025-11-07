# grab the pyomo modeling components.
from pyomo.environ import *

scenario_tree_model = AbstractModel()

# all set/parameter values are strings, representing the names of various entities/variables.

scenario_tree_model.Stages = Set(ordered=True)
scenario_tree_model.Nodes = Set()

scenario_tree_model.NodeStage = Param(scenario_tree_model.Nodes, within=scenario_tree_model.Stages)
scenario_tree_model.Children = Set(
    scenario_tree_model.Nodes, within=scenario_tree_model.Nodes, ordered=True
)
scenario_tree_model.ConditionalProbability = Param(scenario_tree_model.Nodes)

scenario_tree_model.Scenarios = Set(ordered=True)
scenario_tree_model.ScenarioLeafNode = Param(
    scenario_tree_model.Scenarios, within=scenario_tree_model.Nodes
)

scenario_tree_model.StageVariables = Set(scenario_tree_model.Stages)
scenario_tree_model.Stagecost_variable = Param(scenario_tree_model.Stages)

# scenario data can be populated in one of two ways. the first is "scenario-based",
# in which a single .dat file contains all of the data for each scenario. the .dat
# file prefix must correspond to the scenario name. the second is "node-based",
# in which a single .dat file contains only the data for each node in the scenario
# tree. the node-based method is more compact, but the scenario-based method is
# often more natural when parameter data is generated via simulation. the default
# is scenario-based.
scenario_tree_model.ScenarioBasedData = Param(within=Boolean, default=True, mutable=True)

# do we bundle, and if so, how?
scenario_tree_model.Bundling = Param(within=Boolean, default=False, mutable=True)
scenario_tree_model.Bundles = Set()  # bundle names
scenario_tree_model.BundleScenarios = Set(scenario_tree_model.Bundles)


# scenario_tree_model = AbstractModel()

## all set/parameter values are strings, representing the names of various entities/variables.

# scenario_tree_model.Stages = Set(ordered=True)
# scenario_tree_model.Nodes = Set()

# scenario_tree_model.NodeStage = Param(scenario_tree_model.Nodes, within=scenario_tree_model.Stages)
# scenario_tree_model.Children = Set(scenario_tree_model.Nodes, within=scenario_tree_model.Nodes, ordered=True)
# scenario_tree_model.ConditionalProbability = Param(scenario_tree_model.Nodes)

# scenario_tree_model.Scenarios = Set(ordered=True)
# scenario_tree_model.ScenarioLeafNode = Param(scenario_tree_model.Scenarios, within=scenario_tree_model.Nodes)

# scenario_tree_model.StageVariables = Set(scenario_tree_model.Stages)
# scenario_tree_model.Stagecost_variable = Param(scenario_tree_model.Stages)

## scenario data can be populated in one of two ways. the first is "scenario-based",
## in which a single .dat file contains all of the data for each scenario. the .dat
## file prefix must correspond to the scenario name. the second is "node-based",
## in which a single .dat file contains only the data for each node in the scenario
## tree. the node-based method is more compact, but the scenario-based method is
## often more natural when parameter data is generated via simulation. the default
## is scenario-based.
# scenario_tree_model.ScenarioBasedData = Param(within=Boolean, default=True)
