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
Created on:  11/28/23

The possible operating modes for a scenario

"""

from enum import Enum, unique


@unique
class TemoaMode(Enum):
    """The processing mode for the scenario"""

    PERFECT_FORESIGHT = 1  # Normal run, single execution for full time horizon
    MGA = 2  # Modeling for Generation of Alternatives, multiple runs w/ changing constrained obj
    MYOPIC = 3  # Step-wise execution through the future
    METHOD_OF_MORRIS = 4  # Method-of-Morris run
    BUILD_ONLY = 5  # Just build the model, no solve
    CHECK = 6  # build and run price check, source trace it
    SVMGA = 7  # single-vector MGA
    MONTE_CARLO = 8  # MC optimization
