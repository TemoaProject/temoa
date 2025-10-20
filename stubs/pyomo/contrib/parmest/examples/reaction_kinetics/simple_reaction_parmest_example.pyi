from _typeshed import Incomplete
from pyomo.contrib.parmest.experiment import Experiment as Experiment
from pyomo.environ import ConcreteModel as ConcreteModel
from pyomo.environ import Constraint as Constraint
from pyomo.environ import Expression as Expression
from pyomo.environ import Objective as Objective
from pyomo.environ import Param as Param
from pyomo.environ import PositiveReals as PositiveReals
from pyomo.environ import RangeSet as RangeSet
from pyomo.environ import Var as Var
from pyomo.environ import exp as exp
from pyomo.environ import minimize as minimize
from pyomo.environ import value as value

def simple_reaction_model(data): ...

class SimpleReactionExperiment(Experiment):
    data: Incomplete
    model: Incomplete
    def __init__(self, data) -> None: ...
    def create_model(self) -> None: ...
    def label_model(self): ...
    def get_labeled_model(self): ...

class SimpleReactionExperimentK2Fixed(SimpleReactionExperiment):
    def label_model(self): ...

class SimpleReactionExperimentK2Variable(SimpleReactionExperiment):
    def label_model(self): ...

def main() -> None: ...
