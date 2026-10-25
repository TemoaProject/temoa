import enum

from _typeshed import Incomplete

strictEnum: Incomplete

class TraversalStrategy(enum.Enum):
    BreadthFirstSearch = 1
    PrefixDepthFirstSearch = 2
    PostfixDepthFirstSearch = 3
    BFS = BreadthFirstSearch
    ParentLastDepthFirstSearch = PostfixDepthFirstSearch
    PostfixDFS = PostfixDepthFirstSearch
    ParentFirstDepthFirstSearch = PrefixDepthFirstSearch
    PrefixDFS = PrefixDepthFirstSearch
    DepthFirstSearch = PrefixDepthFirstSearch
    DFS = DepthFirstSearch

class SortComponents(enum.Flag):
    UNSORTED = 0
    ORDERED_INDICES = 2
    SORTED_INDICES = 4
    ALPHABETICAL = 8
    unsorted = UNSORTED
    indices = SORTED_INDICES
    declOrder = UNSORTED
    declarationOrder = declOrder
    alphaOrder = ALPHABETICAL
    alphabeticalOrder = alphaOrder
    alphabetical = alphaOrder
    deterministic = ORDERED_INDICES
    sortBoth = indices | alphabeticalOrder
    alphabetizeComponentAndIndex = sortBoth
    @staticmethod
    def default(): ...
    @staticmethod
    def sorter(sort_by_names: bool = False, sort_by_keys: bool = False): ...
    @staticmethod
    def sort_names(flag): ...
    @staticmethod
    def sort_indices(flag): ...
