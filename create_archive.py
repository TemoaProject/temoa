#!/usr/bin/env python

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
"""

# This script creates the 'temoa.py' zip archive/executable using Python's
# PyZipFile interface.  It accepts no arguments.

import os, stat

from zipfile import PyZipFile, ZIP_DEFLATED

# Ensure compatibility with Python 2.7 and 3
try:
    from cStringIO import StringIO

    temoa_pkg = StringIO()
except ImportError:
    from io import BytesIO

    temoa_pkg = BytesIO()

with PyZipFile(temoa_pkg, mode="w", compression=ZIP_DEFLATED) as zf:
    zf.debug = 3
    zf.writepy("temoa_model/")

fname = "temoa.py"
with open(fname, "wb") as f:
    f.write(temoa_pkg.getvalue())

os.chmod(fname, stat.S_IRWXU)
