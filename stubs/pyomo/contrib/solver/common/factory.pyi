from _typeshed import Incomplete
from pyomo.common.factory import Factory as Factory
from pyomo.contrib.solver.common.base import LegacySolverWrapper as LegacySolverWrapper
from pyomo.opt.base.solvers import LegacySolverFactory as LegacySolverFactory

class SolverFactoryClass(Factory):
    def register(self, name, legacy_name=None, doc=None): ...

SolverFactory: Incomplete
