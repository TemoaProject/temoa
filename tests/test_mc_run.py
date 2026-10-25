import pytest

from temoa.extensions.monte_carlo.mc_run import RowData, TweakFactory


@pytest.fixture(scope='module')
def tweak_factory() -> TweakFactory:
    tweak_factory = TweakFactory(
        data_store={'dog': {(1, 2): 3.0, (5, 6): 4.0}, 'cat': {('a', 'b'): 7.0, ('c', 'd'): 8.0}}
    )
    return tweak_factory


good_params = [
    pytest.param(
        '1,dog,1|2,a,1.0,some good notes',
        RowData(1, 'dog', '1|2', 'a', 1.0, 'some good notes'),
        1,
        id='good_param_0',
    ),
    pytest.param(
        '1  , dog,  1|2  , a , 1.0,',
        RowData(1, 'dog', '1|2', 'a', 1.0, ''),
        1,
        id='good_param_1_strip_spaces',
    ),  # we should be able to strip lead/trail spaces
    pytest.param(
        '22,cat,c|d/e/f|9/10,r,2,',
        RowData(22, 'cat', 'c|d/e/f|9/10', 'r', 2.0, ''),
        6,
        id='good_param_2',
    ),
]

fail_examples = [
    pytest.param('z,dog,1|2,a,1.0,', id='non-int run label'),  # has 'z' for run, non integer
    pytest.param('1,dog,1||2,a,1.0,', id='empty index'),  # has empty index location
    pytest.param('2,dog,5|6,x,2.0,', id='non r/s/a'),  # has 'x' not in r/s/a
    pytest.param('3,pig,4|5|7,r,2.0,', id='no-match param'),  # no pig in data source
]


@pytest.mark.parametrize(('row', 'expected', '_'), good_params)
def test__row_parser(row: str, expected: RowData, _: object, tweak_factory: TweakFactory) -> None:
    assert tweak_factory.row_parser(0, row=row) == expected


@pytest.mark.parametrize('row', fail_examples)
def test__row_parser_fail(row: str, tweak_factory: TweakFactory) -> None:
    with pytest.raises(ValueError):
        tweak_factory.row_parser(0, row=row)


@pytest.mark.parametrize(('row', '_', 'num_tweaks'), good_params)
def test_make_tweaks(row: str, _: object, num_tweaks: int, tweak_factory: TweakFactory) -> None:
    _, tweaks = tweak_factory.make_tweaks(0, row=row)
    assert len(tweaks) == num_tweaks
