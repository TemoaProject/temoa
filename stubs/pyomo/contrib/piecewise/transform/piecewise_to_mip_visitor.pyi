from _typeshed import Incomplete
from pyomo.contrib.piecewise.piecewise_linear_expression import (
    PiecewiseLinearExpression as PiecewiseLinearExpression,
)
from pyomo.core import Expression as Expression
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor

class PiecewiseLinearToMIP(StreamBasedExpressionVisitor):
    transform_pw_linear_expression: Incomplete
    transBlock: Incomplete
    def __init__(self, transform_pw_linear_expression, transBlock) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data): ...
    finalizeResult: Incomplete
