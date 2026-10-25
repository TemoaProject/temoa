from pyomo.contrib.mpc.interfaces.copy_values import copy_values_at_time as copy_values_at_time

class DynamicVarLinker:
    def __init__(
        self, source_variables, target_variables, source_time=None, target_time=None
    ) -> None: ...
    def transfer(self, t_source=None, t_target=None) -> None: ...
