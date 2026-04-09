from _typeshed import Incomplete
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.core.base.componentuid import ComponentUID as ComponentUID

class _CharMapper:
    table: Incomplete
    other: Incomplete
    def __init__(self, preserve, translate, other) -> None: ...
    def __getitem__(self, c): ...
    def make_table(self): ...

def cpxlp_label_from_name(name): ...
def alphanum_label_from_name(name): ...

class CuidLabeler:
    def __call__(self, obj=None): ...

class CounterLabeler:
    def __init__(self, start: int = 0) -> None: ...
    def __call__(self, obj=None): ...

class NumericLabeler:
    id: Incomplete
    prefix: Incomplete
    def __init__(self, prefix, start: int = 0) -> None: ...
    def __call__(self, obj=None): ...
    def remove_obj(self, obj) -> None: ...

class CNameLabeler:
    def __call__(self, obj): ...

class LPFileLabeler:
    def __call__(self, obj): ...
    def remove_obj(self, obj) -> None: ...

TextLabeler = LPFileLabeler

class AlphaNumericTextLabeler:
    def __call__(self, obj): ...

class NameLabeler:
    def __call__(self, obj): ...

class ShortNameLabeler:
    id: Incomplete
    prefix: Incomplete
    suffix: Incomplete
    limit: Incomplete
    labeler: Incomplete
    known_labels: Incomplete
    caseInsensitive: Incomplete
    legalRegex: Incomplete
    def __init__(
        self,
        limit,
        suffix,
        start: int = 0,
        labeler=None,
        prefix: str = '',
        caseInsensitive: bool = False,
        legalRegex=None,
    ) -> None: ...
    def __call__(self, obj=None): ...
