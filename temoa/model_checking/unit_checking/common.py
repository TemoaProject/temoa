"""
common elements used within Unit Checking
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

input_tables_with_units = [
    'capacity_to_activity',
    'commodity',
    'construction_input',
    'cost_emission',
    'cost_fixed',
    'cost_invest',
    'cost_variable',
    'demand',
    'efficiency',
    'emission_activity',
    'emission_embodied',
    'emission_end_of_life',
    'end_of_life_output',
    'existing_capacity',
    'lifetime_process',
    'lifetime_tech',
    'loan_lifetime_process',
    'limit_activity',
    'limit_capacity',
    #  Growth/degrowth tables use 'seed_units' column, not 'units' - handle separately
    # 'limit_degrowth_capacity',
    # 'limit_degrowth_new_capacity',
    # 'limit_degrowth_new_capacity_delta',
    'limit_emission',
    # 'limit_growth_capacity',
    # 'limit_growth_new_capacity',
    # 'limit_growth_new_capacity_delta',
    'limit_new_capacity',
    'limit_resource',
]

output_tables_with_units = [
    'output_built_capacity',
    'output_cost',
    'output_curtailment',
    'output_emission',
    'output_flow_in',
    'output_flow_out',
    'output_net_capacity',
    'output_retired_capacity',
    'output_storage_level',
]

# Combined list for backward compatibility
tables_with_units = input_tables_with_units + output_tables_with_units

ratio_capture_tables = {
    'efficiency',
    # 'emission_activity',  # Not using ratio format in v4
    'cost_emission',
    'cost_fixed',
    'cost_invest',
    'cost_variable',
}
"""Tables that require ratio capture in form "units / (other units)" """

commodity_based_tables = [
    'demand',
]

# Group tables Not Yet Implemented...  would need to gather by group name and tech, etc.
activity_based_tables = [
    'limit_activity',
    # 'limit_activity' with groups - NYI
]
"""Tables that should have units equivalent to the commodity's native units"""

# dev note:  The "grouped" functions below are not yet implemented / future work.
# They are (to date) seldom used.  Implementing would require grouping by group name,
# ensuring all techs in group are same...
capacity_based_tables = [
    'existing_capacity',
    'limit_capacity',
    'limit_new_capacity',
    # Group-based capacity limits - NYI
]
"""Tables that require conversion via capacity_to_activity to reach the native units"""

period_based_tables = [
    'lifetime_process',
    'lifetime_tech',
    'loan_lifetime_process',
]
"""Tables that align to the time period, presumably 'years'"""


# we need to delineate whether the units are commodity-referenced or tech-referenced
# and if they are "capacity based" so...
# format:  (table_name, commodity field name (None if 'tech' based),
#           capacity-based, period-based )
class CostTableData(NamedTuple):
    """A named tuple for the cost tables + important properties"""

    table_name: str
    commodity_reference: str | None
    capacity_based: bool
    period_based: bool


cost_based_tables = [
    CostTableData(
        table_name='cost_invest', commodity_reference=None, capacity_based=True, period_based=False
    ),
    CostTableData(
        table_name='cost_emission',
        commodity_reference='emis_comm',
        capacity_based=False,
        period_based=False,
    ),
    CostTableData(
        table_name='cost_fixed', commodity_reference=None, capacity_based=True, period_based=True
    ),
    CostTableData(
        table_name='cost_variable',
        commodity_reference=None,
        capacity_based=False,
        period_based=False,
    ),
]
"""Tables that have cost units and their properties"""


class RelationType(Enum):
    ACTIVITY = 1
    CAPACITY = 2
    COMMODITY = 3


@dataclass(frozen=True)
class UnitsFormat:
    format: str
    groups: int


# any gathering of letters and allowed symbols which are "*" and "_"
# with end lead/trail spaces trimmed
# We include numbers here for cases where there is an exponent in the units like "meter^2"
# the units *may* be parenthesized arbitrarily.  See the unit tests for examples.
SINGLE_ELEMENT = UnitsFormat(format=r'^\s*([A-Za-z0-9\*\^\_\s\/\(\)]+?)\s*$', groups=1)

# any fractional expression using the same pattern above with the denominator
# IN PARENTHESES this modification of above REQUIRES a parenthetical expression
# after the slash to isolate the denominator. see the unit tests for examples.
RATIO_ELEMENT = UnitsFormat(
    format=r'^\s*([A-Za-z0-9\*\/\^\_\s]+?)\s*\/\s*\(\s*([A-Za-z0-9\*\^\/\(\)\_\s]+?)\s*\)\s*$',
    groups=2,
)
"""Format for a units ratio.  re will return the first group as the numerator
and the second as the denominator"""

ACCEPTABLE_CHARACTERS = r'^\s*([A-Za-z0-9\*\^\_\s\/\(\)]+?)\s*$'


def consolidate_lines(line_nums: Sequence[int]) -> str:
    """A little sand wedge function to prevent lists of many line numbers
    and maxing at 5 or 5 + 'more'"""
    listed_lines = (
        ', '.join(str(t) for t in line_nums)
        if len(line_nums) < 5
        else f'{", ".join(str(t) for t in line_nums[:5])}, ... +{len(line_nums) - 5} more'
    )
    return listed_lines
