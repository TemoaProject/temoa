from __future__ import annotations

from typing import TYPE_CHECKING

from deprecated import deprecated

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

from logging import getLogger

logger = getLogger(name=__name__)


def get_default_loan_rate(M: 'TemoaModel', *_):
    """get the default loan rate from the DefaultLoanRate param"""
    return M.DefaultLoanRate()


@deprecated(reason='vintage defaults are no longer available, so this should not be needed')
def CreateCosts(M: 'TemoaModel'):
    """
    Steps to creating fixed and variable costs:
    1. Collect all possible cost indices (CostFixed, CostVariable)
    2. Find the ones _not_ specified in CostFixed and CostVariable
    3. Set them, based on Cost*VintageDefault
    """
    logger.debug('Started Creating Fixed and Variable costs in CreateCosts()')
    # Shorter names, for us lazy programmer types
    CF = M.CostFixed
    CV = M.CostVariable

    # Step 1
    fixed_indices = set(M.CostFixed_rptv)
    var_indices = set(M.CostVariable_rptv)

    # Step 2
    unspecified_fixed_prices = fixed_indices.difference(CF.sparse_iterkeys())
    unspecified_var_prices = var_indices.difference(CV.sparse_iterkeys())

    # Step 3

    # Some hackery: We futz with _constructed because Pyomo thinks that this
    # Param is already constructed.  However, in our view, it is not yet,
    # because we're specifically targeting values that have not yet been
    # constructed, that we know are valid, and that we will need.

    if unspecified_fixed_prices:
        # CF._constructed = False
        for r, p, t, v in unspecified_fixed_prices:
            if (r, t, v) in M.CostFixedVintageDefault:
                CF[r, p, t, v] = M.CostFixedVintageDefault[r, t, v]  # CF._constructed = True

    if unspecified_var_prices:
        # CV._constructed = False
        for r, p, t, v in unspecified_var_prices:
            if (r, t, v) in M.CostVariableVintageDefault:
                CV[r, p, t, v] = M.CostVariableVintageDefault[r, t, v]
    # CV._constructed = True
    logger.debug('Created M.CostFixed with size: %d', len(M.CostFixed))
    logger.debug('Created M.CostVariable with size: %d', len(M.CostVariable))
    logger.debug('Finished creating Fixed and Variable costs')


def CostFixedIndices(M: 'TemoaModel'):
    # we pull the unlimited capacity techs from this index.  They cannot have fixed costs
    return {(r, p, t, v) for r, p, t, v in M.activeActivity_rptv if t not in M.tech_uncap}


def CostVariableIndices(M: 'TemoaModel'):
    return M.activeActivity_rptv


# dev note:  appears superfluous...
# def CostInvestIndices(M: 'TemoaModel'):
#     indices = set((r, t, v) for r, p, t, v in M.processLoans)
#
#     return indices


def get_loan_life(M: 'TemoaModel', r, t, v):
    return M.LifetimeProcess[r, t, v]


def LifetimeLoanProcessIndices(M: 'TemoaModel'):
    """\
Based on the Efficiency parameter's indices and time_future parameter, this
function returns the set of process indices that may be specified in the
CostInvest parameter.
"""
    min_period = min(M.vintage_optimize)

    indices = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys() if v >= min_period)

    return indices
