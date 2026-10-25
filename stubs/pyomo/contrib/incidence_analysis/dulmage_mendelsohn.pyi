from typing import NamedTuple

from _typeshed import Incomplete

class RowPartition(NamedTuple):
    unmatched: Incomplete
    overconstrained: Incomplete
    underconstrained: Incomplete
    square: Incomplete

class ColPartition(NamedTuple):
    unmatched: Incomplete
    underconstrained: Incomplete
    overconstrained: Incomplete
    square: Incomplete

def dulmage_mendelsohn(matrix_or_graph, top_nodes=None, matching=None): ...
