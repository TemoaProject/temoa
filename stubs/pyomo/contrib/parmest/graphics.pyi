from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.dependencies import check_min_version as check_min_version
from pyomo.common.dependencies import matplotlib as matplotlib
from pyomo.common.dependencies import matplotlib_available as matplotlib_available
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.dependencies import pandas_available as pandas_available
from pyomo.common.dependencies import scipy as scipy
from pyomo.common.dependencies import scipy_available as scipy_available
from pyomo.common.dependencies.scipy import stats as stats

sns: Incomplete
seaborn_available: Incomplete
imports_available: Incomplete

def pairwise_plot(
    theta_values,
    theta_star=None,
    alpha=None,
    distributions=[],
    axis_limits=None,
    title=None,
    add_obj_contour: bool = True,
    add_legend: bool = True,
    filename=None,
) -> None: ...
def fit_rect_dist(theta_values, alpha): ...
def fit_mvn_dist(theta_values): ...
def fit_kde_dist(theta_values): ...
def grouped_boxplot(
    data1, data2, normalize: bool = False, group_names=['data1', 'data2'], filename=None
) -> None: ...
def grouped_violinplot(
    data1, data2, normalize: bool = False, group_names=['data1', 'data2'], filename=None
) -> None: ...
