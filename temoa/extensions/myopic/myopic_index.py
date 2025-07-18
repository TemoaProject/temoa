"""
A simple frozen data structure to hold instance info on myopic runs
"""

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
Created on:  1/18/24

"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MyopicIndex:
    """
    A frozen data structure to hold the years for a myopic iteration
    """

    base_year: int
    step_year: int
    last_demand_year: int
    last_year: int

    def __post_init__(self):
        if not self.base_year < self.step_year <= self.last_year:
            raise ValueError(
                f'Received a nonsense value for step_year: {self.step_year} with '
                f'base_year: {self.base_year} and last_year: {self.last_year}'
            )
        if not self.base_year <= self.last_demand_year < self.last_year:
            raise ValueError(
                f'Sequencing of years in MyopicIndex is wrong: {self.base_year}, '
                f'{self.last_demand_year}, {self.last_year}'
            )


"""
################### Myopic Index Description ###########################

Example for view depth=3, step size=1

periods:             *         *         *         *         *         *

                               |---------|---------|---------|
myopic_index                   BY        SY       LDY       LY
                               ^         ^         ^         ^
                       base year         |         |         |
                                         |         |         |
    step year, which is the next base year         |         |
                                                   |         |
              last "demand year" with 1 period after         |
                                                             |
        one period last LDY, to set length of last eval period

The model generally expects one extra period after the last period
to be optimized for the purpose of setting the last optimization
interval length.  So, when parsing out the "middle years" in myopic mode
we need to stop gathering demands in the 2nd year when we have a 3 year
view depth.

If the myopic view depth is 1 period, and therefore, the step can
only be 1 period, then:
FY = LDY                (we just need data that FY period)
SY = FY + 1 period      (we are going to step 1 period)
LY = FY + 1 period      (1 period after the LDY)
"""
