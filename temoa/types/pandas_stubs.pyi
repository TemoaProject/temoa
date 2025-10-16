"""
Type stubs for pandas external dependency.

This module provides type annotations for pandas classes and functions
that are heavily used in Temoa but don't have proper type information.
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    runtime_checkable,
)

# Core pandas types
class DataFrame:
    """pandas DataFrame class."""

    def __init__(
        self,
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
        index: Optional[Any] = None,
        columns: Optional[Any] = None,
        dtype: Optional[Any] = None,
        copy: Optional[bool] = None,
    ) -> None: ...
    @property
    def index(self) -> Any: ...
    @property
    def columns(self) -> Any: ...
    @property
    def dtypes(self) -> Any: ...
    @property
    def shape(self) -> Tuple[int, int]: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def copy(self, deep: bool = True) -> 'DataFrame': ...
    def head(self, n: int = 5) -> 'DataFrame': ...
    def tail(self, n: int = 5) -> 'DataFrame': ...
    def to_excel(self, excel_writer: Any, **kwargs: Any) -> None: ...
    def to_csv(self, path_or_buf: Any, **kwargs: Any) -> None: ...
    def merge(
        self,
        right: 'DataFrame',
        how: str = 'inner',
        on: Optional[Any] = None,
        left_on: Optional[Any] = None,
        right_on: Optional[Any] = None,
        **kwargs: Any,
    ) -> 'DataFrame': ...
    def groupby(self, by: Any, **kwargs: Any) -> Any: ...
    def sum(self, **kwargs: Any) -> 'DataFrame': ...
    def mean(self, **kwargs: Any) -> 'DataFrame': ...
    def count(self, **kwargs: Any) -> 'DataFrame': ...

class Series:
    """pandas Series class."""

    def __init__(
        self,
        data: Optional[Any] = None,
        index: Optional[Any] = None,
        dtype: Optional[Any] = None,
        copy: Optional[bool] = None,
    ) -> None: ...
    @property
    def index(self) -> Any: ...
    @property
    def dtype(self) -> Any: ...
    @property
    def values(self) -> Any: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def to_frame(self, name: Optional[str] = None) -> DataFrame: ...

# Common pandas functions
def read_excel(
    io: Any,
    sheet_name: Optional[Union[str, int]] = None,
    **kwargs: Any,
) -> DataFrame: ...
def read_csv(
    filepath_or_buffer: Any,
    sep: str = ',',
    **kwargs: Any,
) -> DataFrame: ...
def ExcelWriter(path: Any, **kwargs: Any) -> Any: ...

# Type aliases for common pandas patterns in Temoa
PandasIndex = Any  # pandas Index objects
PandasDtype = Any  # pandas dtype objects

# Protocol for pandas-like data structures
@runtime_checkable
class DataFrameLike(Protocol):
    """Protocol for DataFrame-like objects."""

    @property
    def shape(self) -> Tuple[int, int]: ...
    @property
    def columns(self) -> Any: ...
    @property
    def index(self) -> Any: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def copy(self, deep: bool = True) -> 'DataFrameLike': ...
    def merge(self, right: 'DataFrameLike', **kwargs: Any) -> 'DataFrameLike': ...

# Export all stubs
__all__ = [
    'DataFrame',
    'Series',
    'PandasIndex',
    'PandasDtype',
    'DataFrameLike',
    'read_excel',
    'read_csv',
    'ExcelWriter',
]
