from pyomo import dae as dae
from pyomo.common.timing import TicTocTimer as TicTocTimer
from pyomo.contrib.pynumero.interfaces.nlp import NLP as NLP
from pyomo.contrib.pynumero.interfaces.pyomo_nlp import PyomoNLP as PyomoNLP
from pyomo.contrib.pynumero.linalg.base import LinearSolverInterface as LinearSolverInterface
from pyomo.contrib.pynumero.linalg.base import LinearSolverStatus as LinearSolverStatus
from pyomo.contrib.pynumero.linalg.ma27_interface import MA27 as MA27
from pyomo.contrib.pynumero.sparse import BlockMatrix as BlockMatrix
from pyomo.contrib.pynumero.sparse import BlockVector as BlockVector
from scipy.sparse import tril as tril

def build_burgers_model(nfe_x: int = 100, nfe_t: int = 200, start_t: int = 0, end_t: int = 1): ...
def sqp(
    nlp: NLP,
    linear_solver: LinearSolverInterface,
    max_iter: int = 100,
    tol: float = 1e-08,
    output: bool = True,
): ...
def load_solution(m: None, nlp: PyomoNLP): ...
def main(linear_solver, nfe_x: int = 100, nfe_t: int = 200): ...
