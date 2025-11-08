"""
Type definitions for TemoaModel and related core classes.

This module provides comprehensive type annotations for the core Temoa model,
including the main TemoaModel class and its associated data structures.
"""

from enum import Enum, unique
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    Protocol,
    runtime_checkable,
)

from . import (
    Commodity,
    CommoditySet,
    Period,
    Region,
    RegionSet,
    Season,
    SparseIndex,
    Technology,
    TechSet,
    TimeOfDay,
    Vintage,
)

if TYPE_CHECKING:
    from pyomo.core import (
        AbstractModel,
        Constraint,
        Param,
        Set,
        Var,
    )
else:
    # Runtime fallback for non-TYPE_CHECKING contexts
    Set = Any  # AbstractModel.set
    Param = Any  # AbstractModel.Param
    Var = Any  # AbstractModel.Var
    Constraint = Any  # AbstractModel.Constraint

# Type aliases for model data structures
ProcessInputs = dict[tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
ProcessOutputs = dict[tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
TechClassification = dict[Technology, str]
SparseDict = dict[SparseIndex, set[SparseIndex]]
# Model sets type definitions (avoiding naming conflicts with set import)
TimesetTyped = set[Period]
RegionsetTyped = set[Region]
TechsetTyped = set[Technology]
CommoditysetTyped = set[Commodity]
VintagesetTyped = set[Vintage]

# Model parameters type definitions
EfficiencyParam = Param  # Multi-dimensional efficiency parameter
CostParam = Param  # Cost parameters (investment, fixed, variable)
CapacityParam = Param  # Capacity-related parameters
EmissionParam = Param  # Emission parameters

# Model variables type definitions
if TYPE_CHECKING:
    FlowVar = Var  # Flow variables
    CapacityVar = Var  # Capacity variables
    CostVar = Var  # Cost variables

    # Model constraints type definitions
    FlowConstraint = Constraint  # Flow balance constraints
    CapacityConstraint = Constraint  # Capacity constraints
    CostConstraint = Constraint  # Cost accounting constraints
else:
    # Runtime fallback
    FlowVar = Any  # Flow variables
    CapacityVar = Any  # Capacity variables
    CostVar = Any  # Cost variables
    FlowConstraint = Any  # Flow balance constraints
    CapacityConstraint = Any  # Capacity constraints
    CostConstraint = Any  # Cost accounting constraints


@runtime_checkable
class TemoaModelProtocol(Protocol):
    """Protocol defining the interface for TemoaModel instances."""

    # Core identification
    name: str

    # Time-related sets
    time_exist: Set
    time_future: Set
    time_optimize: Set
    vintage_exist: Set
    vintage_optimize: Set
    time_season: Set
    time_of_day: Set

    # Geography sets
    regions: Set
    regional_indices: Set

    # Technology sets
    tech_all: Set
    tech_production: Set
    tech_storage: Set
    tech_reserve: Set
    tech_exchange: Set

    # Commodity sets
    commodity_all: Set
    commodity_demand: Set
    commodity_physical: Set
    commodity_emissions: Set

    # Model parameters
    global_discount_rate: Param
    demand: Param
    efficiency: Param
    existing_capacity: Param
    capacity_to_activity: Param

    # Model variables
    v_flow_out: Var
    v_capacity: Var
    v_new_capacity: Var

    # Model constraints
    demand_constraint: Constraint
    commodity_balance_constraint: Constraint
    capacity_constraint: Constraint

    # Internal data structures
    process_inputs: ProcessInputs
    process_outputs: ProcessOutputs
    active_flow_rpsditvo: (
        set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
        | None
    )
    active_activity_rptv: set[tuple[Region, Period, Technology, Vintage]] | None

    def __init__(self, *args: object, **kwargs: object) -> None: ...


if TYPE_CHECKING:

    class TemoaModel(AbstractModel):
        """
        Type stub for the main TemoaModel class.

        This provides type information for the core Temoa energy model.
        """

        # Class attributes
        default_lifetime_tech: int

        # Time-related sets
        time_exist: Set
        time_future: Set
        time_optimize: Set
        vintage_exist: Set
        vintage_optimize: Set
        vintage_all: Set
        time_season: Set
        time_of_day: Set

        # Geography sets
        regions: Set
        regional_indices: Set
        regional_global_indices: Set

        # Technology sets
        tech_all: Set
        tech_production: Set
        tech_baseload: Set
        tech_annual: Set
        tech_storage: Set
        tech_reserve: Set
        tech_exchange: Set
        tech_uncap: Set
        tech_with_capacity: Set
        tech_retirement: Set

        # Commodity sets
        commodity_all: Set
        commodity_demand: Set
        commodity_physical: Set
        commodity_emissions: Set
        commodity_carrier: Set

        # Model parameters
        global_discount_rate: Param
        period_length: Param
        segment_fraction: Param
        demand: Param
        efficiency: Param
        existing_capacity: Param
        capacity_to_activity: Param
        cost_invest: Param
        cost_fixed: Param
        cost_variable: Param

        # Model variables
        v_flow_out: Var
        v_capacity: Var
        v_new_capacity: Var
        v_retired_capacity: Var

        # Model constraints
        demand_constraint: Constraint
        commodity_balance_constraint: Constraint
        capacity_constraint: Constraint

        # Internal tracking dictionaries
        process_inputs: ProcessInputs
        process_outputs: ProcessOutputs
        used_techs: TechSet
        active_flow_rpsditvo: set[
            tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
        ]
        active_activity_rptv: set[tuple[Region, Period, Technology, Vintage]]

        def __init__(self, *args: object, **kwargs: object) -> None: ...


else:
    # Runtime alias for TemoaModel when not TYPE_CHECKING
    TemoaModel = Any


class EI(NamedTuple):
    """Emission Index"""

    r: Region
    p: Period
    t: Technology
    v: Vintage
    e: Commodity


class FI(NamedTuple):
    """Flow Index"""

    r: Region
    p: Period
    s: Season
    d: TimeOfDay
    i: Commodity
    t: Technology
    v: Vintage
    o: Commodity


class SLI(NamedTuple):
    """Storage Level Index"""

    r: Region
    p: Period
    s: Season
    d: TimeOfDay
    t: Technology
    v: Vintage


class CapData(NamedTuple):
    """Capacity Data Container"""

    built: Any
    net: Any
    retired: Any


@unique
class FlowType(Enum):
    """Types of flow tracked"""

    IN = 1
    OUT = 2
    CURTAIL = 3
    FLEX = 4
    LOST = 5


# Data structure types for model processing
class ModelData:
    """Container for model data and metadata."""

    def __init__(
        self,
        regions: RegionSet,
        periods: set[Period],
        technologies: TechSet,
        commodities: CommoditySet,
        **kwargs: object,
    ) -> None: ...


# Export types for easy importing
# ruff: noqa: RUF022
__all__ = [
    # Protocols
    'TemoaModelProtocol',
    # Core classes
    'TemoaModel',
    # Data structures
    'ModelData',
    'ProcessInputs',
    'ProcessOutputs',
    'TechClassification',
    'SparseDict',
    # Named tuples for indexing
    'EI',
    'FI',
    'SLI',
    'CapData',
    # Enums
    'FlowType',
    # Typed set aliases
    'TimesetTyped',
    'RegionsetTyped',
    'TechsetTyped',
    'CommoditysetTyped',
    'VintagesetTyped',
    # Pyomo type aliases
    'Set',
    'Param',
    'Var',
    'Constraint',
    # Parameter types
    'EfficiencyParam',
    'CostParam',
    'CapacityParam',
    'EmissionParam',
    # Variable types
    'FlowVar',
    'CapacityVar',
    'CostVar',
    # Constraint types
    'FlowConstraint',
    'CapacityConstraint',
    'CostConstraint',
]
