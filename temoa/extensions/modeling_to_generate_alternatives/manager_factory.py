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
Created on:  4/16/24

"""

import sqlite3

from temoa.core.model import TemoaModel
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)
from temoa.extensions.modeling_to_generate_alternatives.vector_manager import VectorManager


def get_manager(
    axis: MgaAxis,
    weighting: MgaWeighting,
    model: TemoaModel,
    con: sqlite3.Connection | None,
    **kwargs,
) -> VectorManager:
    match axis:
        case MgaAxis.TECH_CATEGORY_ACTIVITY:
            if weighting != MgaWeighting.HULL_EXPANSION:
                raise NotImplementedError(
                    'TECH_CATEGORY_ACTIVITY is only implemented for HULL_EXPANSION'
                )
            return TechActivityVectorManager(
                base_model=model, conn=con, weighting=weighting, **kwargs
            )
        case _:
            raise NotImplementedError('This axis is not yet supported')
