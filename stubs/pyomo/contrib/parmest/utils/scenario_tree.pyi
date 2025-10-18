from _typeshed import Incomplete

def build_vardatalist(self, model, varlist=None): ...

class ScenarioNode:
    name: Incomplete
    cond_prob: Incomplete
    stage: Incomplete
    cost_expression: Incomplete
    nonant_list: Incomplete
    nonant_ef_suppl_list: Incomplete
    parent_name: Incomplete
    nonant_vardata_list: Incomplete
    nonant_ef_suppl_vardata_list: Incomplete
    def __init__(
        self,
        name,
        cond_prob,
        stage,
        cost_expression,
        scen_name_list,
        nonant_list,
        scen_model,
        nonant_ef_suppl_list=None,
        parent_name=None,
    ) -> None: ...
