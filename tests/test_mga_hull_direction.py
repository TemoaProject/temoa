"""
Test that the objective built from a hull normal pushes the solve outward along that normal.

The MGA objective is minimized, so the objective coefficient of each category must have the
opposite sign of the category's entry in the (outward) normal vector of the hull facet.
"""

from collections import defaultdict
from queue import Queue
from typing import Any

import numpy as np
import pyomo.environ as pyo
import pytest

from temoa.extensions.modeling_to_generate_alternatives import manager_factory
from temoa.extensions.modeling_to_generate_alternatives.worker import set_objective


def _manager_and_model(vectors: list[list[float]]) -> tuple[Any, pyo.ConcreteModel]:
    """
    Build a bare-bones manager with 2 categories of unequal size:
    category A has 3 variables (2 techs), category B has 1 variable
    """
    model = pyo.ConcreteModel()
    model.x = pyo.Var(range(4), initialize=0.0)

    manager_class = next(
        cls for name, cls in vars(manager_factory).items() if name.endswith('VectorManager')
    )
    manager = manager_class.__new__(manager_class)
    manager.category_mapping = {'A': ['t1', 't2'], 'B': ['t3']}
    manager.technology_size = {'t1': 2, 't2': 1, 't3': 1}
    manager.variable_index_mapping = {'t1': {'x': [0, 1]}, 't2': {'x': [2]}, 't3': {'x': [3]}}
    manager.variable_weight_mapping = {
        tech: {var: [1.0] * len(idxs) for var, idxs in by_var.items()}
        for tech, by_var in manager.variable_index_mapping.items()
    }
    manager.hull_points = None
    manager.hull = None
    manager.coefficient_vector_queue = Queue()
    for vector in vectors:
        manager.coefficient_vector_queue.put(np.array(vector))
    return manager, model


def _category_coefficients(manager: Any, model: pyo.ConcreteModel) -> dict[str, float]:
    """Pull the next objective from the manager and total its coefficients by category"""
    coeffs = manager._next_objective_vector()
    assert coeffs is not None
    x: Any = model.x
    set_objective(model, list(x.values()), coeffs)
    coefficients = []
    for i in x:
        for j in x:
            x[j].value = 1.0 if i == j else 0.0
        coefficients.append(pyo.value(model.obj))
    res: dict[str, float] = defaultdict(float)
    for cat, idxs in (('A', [0, 1, 2]), ('B', [3])):
        res[cat] = sum(coefficients[i] for i in idxs)
    assert coefficients[0] == pytest.approx(coefficients[1]) == pytest.approx(coefficients[2])
    assert sum(abs(c) for c in coefficients) == pytest.approx(1.0)
    return res


@pytest.mark.parametrize(
    'normal',
    [
        [0.6, 0.8],
        [-0.6, -0.8],
        [0.8, -0.6],
        [-0.8, 0.6],
        [0.2, -0.98],
        [0.3162, -0.9487],
    ],
)
def test_objective_pushes_outward_along_normal(normal: list[float]) -> None:
    manager, model = _manager_and_model([normal] + [[1.0, 0.0]] * 5)
    coeffs = _category_coefficients(manager, model)

    for cat, entry in zip(('A', 'B'), normal, strict=True):
        assert np.sign(coeffs[cat]) == -np.sign(entry), f'category {cat} is pushed the wrong way'

    per_variable = np.array([coeffs['A'] / 3, coeffs['B'] / 1])
    cosine = per_variable @ np.array(normal) / np.linalg.norm(per_variable)
    assert cosine == pytest.approx(-1.0, abs=1e-3)
