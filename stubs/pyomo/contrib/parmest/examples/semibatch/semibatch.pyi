from _typeshed import Incomplete
from pyomo.contrib.parmest.experiment import Experiment as Experiment
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.dae import DerivativeVar as DerivativeVar
from pyomo.environ import ComponentUID as ComponentUID
from pyomo.environ import ConcreteModel as ConcreteModel
from pyomo.environ import Constraint as Constraint
from pyomo.environ import ConstraintList as ConstraintList
from pyomo.environ import Expression as Expression
from pyomo.environ import Objective as Objective
from pyomo.environ import Param as Param
from pyomo.environ import Set as Set
from pyomo.environ import SolverFactory as SolverFactory
from pyomo.environ import Suffix as Suffix
from pyomo.environ import TransformationFactory as TransformationFactory
from pyomo.environ import Var as Var
from pyomo.environ import exp as exp
from pyomo.environ import minimize as minimize

def generate_model(data): ...

class SemiBatchExperiment(Experiment):
    data: Incomplete
    model: Incomplete
    def __init__(self, data) -> None: ...
    def create_model(self) -> None: ...
    def label_model(self) -> None: ...
    def finalize_model(self) -> None: ...
    def get_labeled_model(self): ...

def main() -> None: ...
