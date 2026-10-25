import pytest

from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)


def test__vector_engine() -> None:
    """
    Make sure the basis generation algorithm is accurate.  In this test case, there are unequal
    number of members per category and differing variables per member.  We should come up with
    4 orthogonal vectors
    :return:
    """
    cat_map = {
        'A': ['dog', 'pig'],
        'B': [
            'cat',
        ],
    }
    var_map = {'dog': ['red', 'blue'], 'pig': ['yellow', 'green'], 'cat': ['blue', 'gold']}
    tech_sizes = {k: len(v) for k, v in var_map.items()}
    # below is just to show the mapping back to variables.... test just want the coefficients from
    # res_values
    # res = [
    #     {'red': 0.25, 'blue': 0.25, 'yellow': 0.25, 'green': 0.25},
    #     {'red': -0.25, 'blue': -0.25, 'yellow': -0.25, 'green': -0.25},
    #     {'blue': 0.5, 'gold': 0.5},
    #     {'blue': -0.5, 'gold': -0.5},
    # ]
    res_values = [
        [0.25, 0.25, 0.25, 0.25, 0, 0],
        [-0.25, -0.25, -0.25, -0.25, 0, 0],
        [0.5, 0.5, 0, 0, 0, 0],
        [-0.5, -0.5, 0, 0, 0, 0],
    ]
    matrix = TechActivityVectorManager._generate_basis_coefficients(
        category_mapping=cat_map, technology_size=tech_sizes
    )
    rows = []
    if matrix.qsize() > 0:
        rows.append(matrix.get_nowait())
    for idx, row in enumerate(rows):
        assert row == pytest.approx(res_values[idx], abs=1e-2)
