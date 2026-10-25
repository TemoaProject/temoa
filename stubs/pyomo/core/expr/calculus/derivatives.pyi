import enum

from .diff_with_pyomo import reverse_ad as reverse_ad
from .diff_with_pyomo import reverse_sd as reverse_sd

class Modes(str, enum.Enum):
    sympy = 'sympy'
    reverse_symbolic = 'reverse_symbolic'
    reverse_numeric = 'reverse_numeric'

def differentiate(expr, wrt=None, wrt_list=None, mode=...): ...
