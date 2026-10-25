"""
Quick utility to spit out the set members of a pyomo model
"""

import pyomo.environ as pyo

from temoa.core.model import TemoaModel


def spit_sets(model: TemoaModel, index_sets: bool = False) -> None:
    """
    print out the set data in pyomo pprint format
    :param model: a built model
    :param index_sets: True if the pyomo-built _index sets should be included
    :return:
    """
    model_sets = model.component_map(ctype=pyo.Set)
    for m_set in sorted(model_sets.keys()):
        if not index_sets and '_index' in m_set:
            continue
        else:
            model_sets[m_set].pprint()


def spit_params(model: TemoaModel) -> None:
    """
    Print out the parameters in pyomo-built pprint
    :param model: a built model
    :return:
    """
    model_params = model.component_map(ctype=pyo.Param)
    for m_param in sorted(model_params.keys()):
        model_params[m_param].pprint()
