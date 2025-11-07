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
Created on:  11/11/24

This file is intended to be a simple EXAMPLE for testing mainly of how one might make a set of
runs for a Monte Carlo simulation.

This scenario is based on Utopia with the following random variables:

Cost of Imported Oil will have a normal distribution of *relative changes* applied in all periods
Residential Heating (RH) will have a similar distribution, with some negative correlation (seems logical that
there is some hidden price sensitivity, even though RH could be satisfied from electricity as well.)

Additionally, we will assume there is an independent 20% chance that the govt will subsidize new nuclear
power by:
  (a) subsidizing the cost of any Investment Cost by 40%, in the out-years of 2000, 2010 (but not 1990)
  (b) paying all fixed costs in the same years.

Let's make a set of 500 runs and explore output

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from definitions import PROJECT_ROOT

# distro for the related cost vars

# multivariate norm generator:
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.multivariate_normal.html

num_runs = 1000
cov = np.array([[0.4, -0.1], [-0.1, 0.1]])
price_devs = np.random.multivariate_normal([0, 0], cov, size=num_runs)
print(f'correlation check: {np.corrcoef(price_devs.T)[0, 1]}')

# verify with a peek...
plt.plot(price_devs[:, 0], price_devs[:, 1], '.', alpha=0.5)
plt.axis('equal')
plt.grid()
plt.show()

# generate nuke discounts
nuc_dev = np.random.binomial(n=1, p=0.20, size=num_runs) * -0.4

# put it together...
file_loc = Path(PROJECT_ROOT) / 'data_files/monte_carlo/run_settings_2.csv'
with open(file_loc, 'w') as f:
    f.write('run,param,index,mod,value,notes\n')
    for run_idx in range(num_runs):
        f.write(
            f'{run_idx + 1},cost_variable,*|*|IMPOIL1|*,r,{price_devs[run_idx, 0]},oil relative change\n'
        )
        f.write(
            f'{run_idx + 1},Demand,*|*|RH,r,{price_devs[run_idx, 1]},res heat relative change\n'
        )
        f.write(
            f'{run_idx + 1},cost_invest,*|E21|2000/2010,r,{nuc_dev[run_idx]},nuclear invest relative discount\n'
        )
        if nuc_dev[run_idx] < 0:
            f.write(f'{run_idx + 1},cost_fixed,*|*|E21|2000/2010,s,0.0,nuclear op cost covered\n')
