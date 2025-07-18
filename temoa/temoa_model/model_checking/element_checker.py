"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  4/24/24

class to hold members of "validation sets" used by loader to validate elements as they are
read in to the DataPortal or other structure.  Motivation is to contain the values AND
any extra validation information in one instance.

"""

import re
from collections.abc import Iterable, Sequence
from operator import itemgetter


class ViableSet:
    # automatic approvals for regions.  Stored here for reference
    REGION_REGEXES = [
        r'\+',  # any grouping with a plus sign
        r'^global\Z',  # the exact word 'global' with no leader/trailer
    ]

    def __init__(
        self,
        elements: Iterable,
        exception_loc: int | None = None,
        exception_vals: Iterable[str] | None = None,
    ):
        """
        Construct a match object.  The direct matches and the location/item for exceptions
        :param elements: The core elements to match against
        :param exception_loc: The location to consider for the exception
        :param exception_vals: Iterable of exception regexes to match against

        Example:  core elements {('a', 1), ('a', 2)}
                  exceptions {0: {r'dog', r'cat'}}
        should "match" for ('a', 1), ('a', 2), ('dog', 1), ('cat', 1)
        fail for:  ('a', 4), ('cat', 3), etc.
        """

        self._elements: set[tuple] = {self.tupleize(element) for element in elements}

        if exception_vals and exception_loc is None:
            raise ValueError('cannot have exception_vals without a location')
        self._exception_loc = exception_loc
        self._exceptions = exception_vals
        self.non_excepted_items = set()

        self.calc_dim()

        if self._exceptions and self.dim > 0:
            self._update()

    def calc_dim(self):
        # calculate the dimension...
        if self._elements:
            an_element = self._elements.pop()
            self._elements.add(an_element)
            self.dim = len(an_element)
        else:
            self.dim = 0

    def _update(self):
        """construct the set of non-excepted items in tuple format"""
        # we need to remove the item at the "excepted" location
        locs = list(range(self.dim))
        locs.remove(self._exception_loc)
        if len(locs) == 0:
            self.non_excepted_items = None
            return
        self.non_excepted_items = {itemgetter(*locs)(t) for t in self._elements}

    @property
    def exception_loc(self):
        return self._exception_loc

    @property
    def val_exceptions(self) -> Iterable[str]:
        return self._exceptions

    def set_val_exceptions(self, exception_loc: int, exception_vals: Iterable):
        if exception_loc is None or exception_vals is None:
            raise ValueError('cannot have exception_vals without a location')
        self._exception_loc = exception_loc
        self._exceptions = exception_vals
        self._update()

    @property
    def member_tuples(self):
        """the elements of the membership set AS TUPLES, including singleton tuples"""
        return self._elements

    @staticmethod
    def tupleize(element):
        return element if isinstance(element, tuple) else (element,)

    @member_tuples.setter
    def member_tuples(self, elements):
        self._elements = {self.tupleize(element) for element in elements}
        self.calc_dim()
        self._update()

    @property
    def members(self):
        """the members of the validation set"""
        if self.dim > 1:
            return self.member_tuples
        else:
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
    values: Sequence[tuple], validation: ViableSet, value_locations: tuple = (0,)
) -> list:
    """
    Filter elements according to a set of criteria.
    :param values: the values to filter
    :param validation: the validation item to use for filtering
    :param value_locations: the locations in the value items corresponding to the values in the validation
    :return: a list of filtered elements

    Ex:  if filtering by (region, tech, vintage) and the data is (region, _, _, tech, vintage, value) we need to identify
    the location of r, t, v in the element under review by the tuple (0, 3, 4)
    """
    if not isinstance(validation, ViableSet):
        raise ValueError("'validation' must be an instance of ViableSet")
    if 0 < validation.dim != len(value_locations):
        # if validation.dim == 0, it is empty, but might still be used for exempted items
        raise ValueError('the value locations must have same dimensionality as the validation set')

    # determine the location of the non-exempted items for comparison by removing the exempted location
    non_exempt_item_locs = None
    if validation.val_exceptions:
        non_exempt_item_locs = list(value_locations)
        non_exempt_item_locs.remove(validation.exception_loc)

    res = []

    for item in values:
        # check the "base case" first:  it's in the fundamental elements
        element = itemgetter(*value_locations)(item)
        if not isinstance(element, tuple):
            element = (element,)
        if element in validation.member_tuples:
            res.append(item)
        elif validation.val_exceptions:  # check each of the exceptions
            if (
                validation.non_excepted_items
                and itemgetter(*non_exempt_item_locs)(item) not in validation.non_excepted_items
            ):
                continue
            for val_exception in validation.val_exceptions:
                if re.search(val_exception, str(item[validation.exception_loc])):
                    res.append(item)
                    break

    return res
