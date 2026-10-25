from pyomo.environ import ConcreteModel as ConcreteModel
from pyomo.environ import Constraint as Constraint
from pyomo.environ import ExternalFunction as ExternalFunction
from pyomo.environ import Objective as Objective
from pyomo.environ import Reals as Reals
from pyomo.environ import Var as Var
from pyomo.environ import cos as cos
from pyomo.environ import sin as sin
from pyomo.environ import sqrt as sqrt
from pyomo.opt import SolverFactory as SolverFactory

def ext_fcn(a, b): ...
def grad_ext_fcn(args, fixed): ...
def create_model(): ...
def main() -> None: ...
