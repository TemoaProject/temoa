from typing import Any

import pytest

from temoa.model_checking.element_checker import ViableSet, filter_elements

ParamType = dict[str, Any]
ElementType = tuple[Any, ...] | str | int
params: list[ParamType] = [
    {
        'name': 'group 1',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('bob+tom', 3)], exception_loc=0, exception_vals=[r'dog', r'\+']
        ),
        'testers': [('a', 1), ('b', 2), ('x', 2), ('dog', 4), ('dog', 1), ('cat+dog', 1)],
        'locs': (0, 1),
        'expected': [('a', 1), ('b', 2), ('dog', 1), ('cat+dog', 1)],
    },
    {
        'name': 'singletons',
        'filt': ViableSet(
            elements=[(1,), (2,), ('dog',), ('pig',)],
            exception_loc=0,
            exception_vals=[r'rhino', r'\+'],
        ),
        'testers': [(1,), ('dog',), ('cat',), ('rhino',)],
        'expected': [(1,), ('dog',), ('rhino',)],
    },
    {
        'name': 'param-like',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('c+d', 3)], exception_loc=0, exception_vals=[r'^dog\Z', r'\+']
        ),
        'testers': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('x', 2, 8.22),
            ('dog', 4, 'Bob'),
            ('dog', 1, 55),
            ('cat+dog', 1, 23),
            ('a', 1, None),
            ('a', 2, 44),
            ('bigdog', 1, 99),
        ],
        'locs': (0, 1),
        'expected': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('dog', 1, 55),
            ('cat+dog', 1, 23),
            ('a', 1, None),
        ],
    },
    {
        'name': 'use of defaults',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('c+d', 3)],
            exception_loc=0,
            exception_vals=ViableSet.REGION_REGEXES,
        ),
        'testers': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('x', 2, 8.22),
            ('dog', 4, 'Bob'),  # fail not in REGION_REGEXES
            ('global', 1, 55),
            ('global', 33, 22),  # fail 33 invalid
            ('Global', 1, 23),  # fail cap
            ('a', 1, None),
            ('a', 2, 44),
            ('horse+coat', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
        'locs': (0, 1),
        'expected': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('global', 1, 55),
            ('a', 1, None),
            ('horse+coat', 1, 99),
        ],
    },
    {
        'name': 'use of defaults with multi-dim params',
        'filt': ViableSet(
            [('a', 1), ('b', 2)],
            exception_loc=0,
            exception_vals=ViableSet.REGION_REGEXES,
        ),
        'testers': [
            ('a', 'stuff', 1, 0.2),
            ('b', 'stuff', 2, 1.5),
            ('a', 'other', 3, 8.22),
            ('global', 33, 1, 22),
            ('global', 1, 77, 66),  # fail 77
            ('a', 'zz top', 1, None),
            ('horse+coat', 'ugly', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
        'locs': (0, 2),
        'expected': [
            ('a', 'stuff', 1, 0.2),
            ('b', 'stuff', 2, 1.5),
            ('global', 33, 1, 22),
            ('a', 'zz top', 1, None),
            ('horse+coat', 'ugly', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
    },
]


@pytest.mark.parametrize('data', params, ids=[param['name'] for param in params])
def test_filter_elements(data: ParamType) -> None:
    # use the 'tester' elements against the filter to ensure we get expected results
    assert (
        filter_elements(
            values=data['testers'], validation=data['filt'], value_locations=data.get('locs', (0,))
        )
        == data['expected']
    )


def test_dimension_measurement() -> None:
    """quick test to ensure we are getting the correct dimension esp. when elements are not tuple"""
    elements: list[ElementType] = [(1, 2), (3, 4)]
    assert ViableSet(elements).dim == 2

    elements = ['dog', 'pig', 'uncle bob']
    assert ViableSet(elements).dim == 1

    elements = [('dog',), ('pig',), ('uncle bob',)]
    assert ViableSet(elements).dim == 1

    elements = [(1991,), (1987,)]
    assert ViableSet(elements).dim == 1

    elements = [2000, 2001]
    vs = ViableSet(elements)
    assert vs.dim == 1
    assert vs.members == {2000, 2001}
    assert vs.member_tuples == {(2000,), (2001,)}

    elements = []
    assert ViableSet(elements).dim == 0
