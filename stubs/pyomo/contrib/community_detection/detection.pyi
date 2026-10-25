from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.contrib.community_detection.community_graph import (
    generate_model_graph as generate_model_graph,
)
from pyomo.core import Block as Block
from pyomo.core import ComponentMap as ComponentMap
from pyomo.core import ConcreteModel as ConcreteModel
from pyomo.core import Constraint as Constraint
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.core.expr.visitor import replace_expressions as replace_expressions

logger: Incomplete
community_louvain: Incomplete
community_louvain_available: Incomplete

def detect_communities(
    model,
    type_of_community_map: str = 'constraint',
    with_objective: bool = True,
    weighted_graph: bool = True,
    random_seed=None,
    use_only_active_components: bool = True,
): ...

class CommunityMap:
    community_map: Incomplete
    type_of_community_map: Incomplete
    with_objective: Incomplete
    weighted_graph: Incomplete
    random_seed: Incomplete
    use_only_active_components: Incomplete
    model: Incomplete
    graph: Incomplete
    graph_node_mapping: Incomplete
    constraint_variable_map: Incomplete
    graph_partition: Incomplete
    def __init__(
        self,
        community_map,
        type_of_community_map,
        with_objective,
        weighted_graph,
        random_seed,
        use_only_active_components,
        model,
        graph,
        graph_node_mapping,
        constraint_variable_map,
        graph_partition,
    ) -> None: ...
    def __eq__(self, other): ...
    def __iter__(self): ...
    def __getitem__(self, item): ...
    def __len__(self) -> int: ...
    def keys(self): ...
    def values(self): ...
    def items(self): ...
    def visualize_model_graph(self, type_of_graph: str = 'constraint', filename=None, pos=None): ...
    def generate_structured_model(self): ...
