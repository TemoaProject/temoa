from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


def FlowVariableIndices(M: 'TemoaModel'):
    return M.activeFlow_rpsditvo


def FlowVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlow_rpitvo


def FlexVariablelIndices(M: 'TemoaModel'):
    return M.activeFlex_rpsditvo


def FlexVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlex_rpitvo


def FlowInStorageVariableIndices(M: 'TemoaModel'):
    return M.activeFlowInStorage_rpsditvo


def CurtailmentVariableIndices(M: 'TemoaModel'):
    return M.activeCurtailment_rpsditvo
