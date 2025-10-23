"""
Class to hold members of "validation sets" used by loader to validate elements as they are
read in to the DataPortal or other structure.  Motivation is to contain the values AND
any extra validation information in one instance.

"""

import re
from collections.abc import Iterable, Sequence
from operator import itemgetter
from typing import ClassVar, Self

type ValidationPrimitive = str | int | float | None
type ValidationElement = tuple[ValidationPrimitive, ...]
type InputElement = ValidationPrimitive | ValidationElement


class ViableSet:
    """
    Manages a set of valid elements and rules for "exception-based" matches.

    This class is designed for filtering data where an element is considered
    valid if it either:
    1.  Exactly matches a pre-defined tuple of values.
    2.  Matches a pre-defined tuple in all positions *except* for one, where
        the value at that "exception position" matches a given regex pattern.

    Example:
      - Core elements: {('a', 1), ('a', 2)}
      - Exception: location 0, regexes {r'dog', r'cat'}

    This will match:
      - ('a', 1), ('a', 2)  (exact matches)
      - ('dog', 1), ('cat', 1) (exception matches, since the non-exception part, (1,), is valid)
      - ('dog', 2), ('cat', 2) (exception matches, since the non-exception part, (2,), is valid)

    This will NOT match:
      - ('a', 4) (non-exception part (4,) is not in the valid set)
      - ('cat', 3) (non-exception part (3,) is not in the valid set)
    """

    # Stored for reference; these are examples of common automatic approvals.
    REGION_REGEXES: ClassVar[list[str]] = [
        r'\+',  # any grouping with a plus sign
        r'^global\Z',  # the exact word 'global' with no leader/trailer
    ]

    def __init__(
        self,
        elements: Iterable[InputElement],
        exception_loc: int | None = None,
        exception_vals: Iterable[str] | None = None,
    ) -> None:
        """
        Constructs a ViableSet instance.

        Args:
            elements: The core elements to match against.
            exception_loc: The index within an element to apply exception regexes.
            exception_vals: An iterable of regex patterns to match against.
        """
        self._elements: set[ValidationElement] = {self._tupleize(el) for el in elements}
        self.dim: int = self._calculate_dim()
        self._exception_loc: int | None = None
        self._exceptions: frozenset[str] = frozenset()
        self.non_excepted_items: set[ValidationElement] | None = set()
        # Cache for compiled regex patterns
        self._compiled_val_exceptions: list[re.Pattern[str]] = []

        if exception_loc is not None and exception_vals is not None:
            self.set_val_exceptions(exception_loc, exception_vals)

    @staticmethod
    def _tupleize(element: InputElement) -> ValidationElement:
        """Ensures an element is a tuple."""
        return element if isinstance(element, tuple) else (element,)

    def _calculate_dim(self) -> int:
        """Calculates the dimension of the elements."""
        if not self._elements:
            return 0
        # Get an arbitrary element to determine the dimension
        return len(next(iter(self._elements)))

    def _update_internals(self) -> None:
        """
        Updates internal lookup sets based on current elements and exceptions.
        This pre-calculates values for efficient filtering.
        """
        self.dim = self._calculate_dim()
        if self._exception_loc is None or not self._exceptions:
            self.non_excepted_items = set()
            return

        # Locations of items *not* at the exception index
        non_excepted_locs = [i for i in range(self.dim) if i != self._exception_loc]

        if not non_excepted_locs:
            # This occurs if dim is 1 and exception_loc is 0.
            # There are no other items to validate against.
            self.non_excepted_items = None
        else:
            getter = itemgetter(*non_excepted_locs)
            self.non_excepted_items = {self._tupleize(getter(t)) for t in self._elements}

    @property
    def exception_loc(self) -> int | None:
        return self._exception_loc

    @property
    def val_exceptions(self) -> frozenset[str]:
        return self._exceptions

    def set_val_exceptions(self, exception_loc: int, exception_vals: Iterable[str]) -> Self:
        """
        Sets or updates the validation exceptions.

        Args:
            exception_loc: The index for the exception.
            exception_vals: An iterable of regex patterns.

        Returns:
            The instance (self) to allow for method chaining.
        """
        if not (isinstance(exception_loc, int) and exception_loc >= 0):
            raise ValueError('exception_loc must be a non-negative integer')

        self._exception_loc = exception_loc
        # Use a frozenset for immutability and performance
        self._exceptions = frozenset(exception_vals)
        self._compiled_val_exceptions = [re.compile(p) for p in self._exceptions]
        self._update_internals()
        return self

    @property
    def member_tuples(self) -> set[ValidationElement]:
        """The elements of the membership set as tuples."""
        return self._elements

    @member_tuples.setter
    def member_tuples(self, elements: Iterable[InputElement]) -> None:
        """Sets the core elements, ensuring they are stored as tuples."""
        self._elements = {self._tupleize(el) for el in elements}
        self._update_internals()

    @property
    def members(self) -> set[ValidationElement] | set[ValidationPrimitive]:
        """
        The members of the validation set.
        Unwraps single-element tuples for convenience.
        """
        if self.dim > 1:
            # This branch returns set[ValidationElement]
            return self.member_tuples

        # This branch returns set[ValidationPrimitive]
        return {t[0] for t in self.member_tuples}


# dev note:  The reason for this filtering construct is to allow passage of items that either
#            match the basic 'valid' elements exactly OR match the exception regex in one
#            position and match all other elements.  The use case is for regions, where we
#            want to match explicit regions exactly, but also match 'global' and
#            region groups where we have a '+' sign in the name without having to
#            create all the possible permutations.  An alternate (rejected) approach
#            would be to re-create the region groups for something like 'global' to the
#            actually legal combinations on-the-fly from data, which would be more complex
#            and mask the intent of the original data.
def filter_elements(
    values: Sequence[tuple[ValidationPrimitive, ...]],
    validation: ViableSet,
    value_locations: tuple[int, ...],
) -> list[tuple[ValidationPrimitive, ...]]:
    """
    Filters a sequence of elements based on the rules in a ViableSet.

    Args:
        values: The sequence of data tuples to filter.
        validation: The ViableSet instance containing the validation rules.
        value_locations: A tuple of indices that maps a data tuple from `values`
                         to the format expected by `validation`.

    Returns:
        A list of the items from `values` that passed validation.

    Example:
      - A data item is `('USA', 'other', 'cars', 2020, 1.5)`
      - `validation` expects `(region, tech, vintage)`
      - `value_locations` would be `(0, 2, 3)` to extract ('USA', 'cars', 2020)
    """
    if not isinstance(validation, ViableSet):
        raise TypeError("'validation' must be an instance of ViableSet")

    if validation.dim > 0 and validation.dim != len(value_locations):
        raise ValueError(
            'The number of value_locations must match the dimensionality of the validation set.'
        )

    # Use the cached compiled regexes. Fall back to compiling for backward compatibility.
    exception_regexes = getattr(
        validation, '_compiled_val_exceptions', [re.compile(p) for p in validation.val_exceptions]
    )

    # Pre-build itemgetters for performance
    full_element_getter = itemgetter(*value_locations)

    # --- Simplified path for no exceptions ---
    if not exception_regexes:
        return [
            item
            for item in values
            if validation._tupleize(full_element_getter(item)) in validation.member_tuples
        ]

    assert validation.exception_loc is not None  # for mypy type checking

    # --- Main logic for filtering with exceptions ---
    non_exempt_item_locs: list[int] = [
        loc for i, loc in enumerate(value_locations) if i != validation.exception_loc
    ]
    non_exempt_getter = itemgetter(*non_exempt_item_locs) if non_exempt_item_locs else None

    filtered_list = []
    for item in values:
        element_to_check = validation._tupleize(full_element_getter(item))

        # 1. Check for a direct match
        if element_to_check in validation.member_tuples:
            filtered_list.append(item)
            continue

        # 2. Check for an exception-based match
        if validation.non_excepted_items is None:  # dim=1 case
            pass
        elif non_exempt_getter:
            non_exempt_part = validation._tupleize(non_exempt_getter(item))
            if non_exempt_part not in validation.non_excepted_items:
                continue

        # Check if the value at the exception location matches any regex
        exception_loc_in_item = value_locations[validation.exception_loc]
        value_at_exception_loc = str(item[exception_loc_in_item])

        for pattern in exception_regexes:
            if pattern.search(value_at_exception_loc):
                filtered_list.append(item)
                break

    return filtered_list
