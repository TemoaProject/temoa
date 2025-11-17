from typing import Any

import pytest

from temoa.extensions.myopic.myopic_sequencer import MyopicSequencer

params = [
    {
        'name': 'single_step',
        'conf_data': {'step_size': 1, 'view_depth': 3},
        'expected_steps': 4,
    },  # 4 single steps
    {
        'name': 'triple_step',
        'conf_data': {'step_size': 3, 'view_depth': 4},
        'expected_steps': 2,  # 1 step of 3, followed by 1 step of 1
    },
]

"""
assuming the periods are [0, 1, 2, 3, 4]
for single step, the myopic indices should be...
(base, last demand year, last year)
(0, 2, 3)
(1, 3, 4)
(2, 3, 4)
(3, 3, 4)

for triple step, the myopic indices should be...
(0, 3, 4)
(3, 3, 4)
"""


@pytest.mark.parametrize('param', params, ids=lambda p: p['name'])
def test_characterize_run(param: dict[str, Any]) -> None:
    """
    Test the slicing up of the future periods into myopic indices
    """

    ms = MyopicSequencer(config=None)
    ms.view_depth = param['conf_data']['view_depth']
    ms.step_size = param['conf_data']['step_size']

    ms.characterize_run(future_periods=list(range(5)))
    assert len(ms.instance_queue) == param['expected_steps'], (
        'number of myopic iterations does not match expected number of iterations'
    )

    # pop the last myopic index from the queue and inspect it.  Should be same for both cases
    last_mi = ms.instance_queue.popleft()
    assert last_mi.last_year == 4
    assert last_mi.last_demand_year == 3
    assert last_mi.base_year == 3
