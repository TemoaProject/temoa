from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.core import Expression
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


logger = getLogger(__name__)


def operator_expression(lhs: Expression | None, operator: str | None, rhs: Expression | None):
    """Returns an expression, applying a configured operator"""
    if any((lhs is None, operator is None, rhs is None)):
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg)
    try:
        match operator:
            case 'e':
                expr = lhs == rhs
            case 'le':
                expr = lhs <= rhs
            case 'ge':
                expr = lhs >= rhs
            case _:
                msg = (
                    'Tried to build a constraint using a bad operator. Allowed operators are "e","le", or "ge". Got "{}": {} {} {}'
                ).format(operator, lhs, operator, rhs)
                logger.error(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg) from e

    return expr


# To avoid building big many-indexed parameters when they aren't needed - saves memory
# Much faster to build a dictionary and check that than check the parameter
# indices directly every time - saves build time
def get_variable_efficiency(M: 'TemoaModel', r, p, s, d, i, t, v, o):
    if M.isEfficiencyVariable[r, p, i, t, v, o]:
        return value(M.Efficiency[r, i, t, v, o]) * value(
            M.EfficiencyVariable[r, p, s, d, i, t, v, o]
        )
    else:
        return value(M.Efficiency[r, i, t, v, o])
