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
    Commodityset,
    Period,
    Region,
    RegionPeriodSeasonTimeInputTechVintageOutput,
    RegionPeriodTechVintage,
    Regionset,
    Season,
    SparseIndex,
    Technology,
    Techset,
    TimeOfDay,
    Vintage,
)

if TYPE_CHECKING:
    from pyomo.core.base.constraint import Constraint as PyomoConstraint
    from pyomo.core.base.objective import Objective as PyomoObjective
    from pyomo.core.base.var import Var as PyomoVar
    from pyomo.environ import AbstractModel

# Import Pyomo stub types
if TYPE_CHECKING:
    from .pyomo_stubs import (
        PyomoBuildAction,
        PyomoConstraint,
        PyomoObjective,
        PyomoParam,
        PyomoSet,
        PyomoVar,
    )
else:
    # Runtime fallback for non-TYPE_CHECKING contexts
    PyomoSet = Any  # AbstractModel.set
    PyomoParam = Any  # AbstractModel.Param
    PyomoVar = Any  # AbstractModel.Var
    PyomoConstraint = Any  # AbstractModel.Constraint
    PyomoBuildAction = Any  # AbstractModel.BuildAction
    PyomoObjective = Any  # AbstractModel.Objective

# Type aliases for model data structures
ProcessInputs = dict[tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
ProcessOutputs = dict[tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
TechClassification = dict[Technology, str]
Sparsedict = dict[SparseIndex, set[SparseIndex]]

# Model sets type definitions (avoiding naming conflicts with set import)
TimesetTyped = set[Period]
RegionsetTyped = set[Region]
TechsetTyped = set[Technology]
CommoditysetTyped = set[Commodity]
VintagesetTyped = set[Vintage]

# Model parameters type definitions
EfficiencyParam = PyomoParam  # Multi-dimensional efficiency parameter
CostParam = PyomoParam  # Cost parameters (investment, fixed, variable)
CapacityParam = PyomoParam  # Capacity-related parameters
EmissionParam = PyomoParam  # Emission parameters

# Model variables type definitions
if TYPE_CHECKING:
    FlowVar = PyomoVar  # Flow variables
    CapacityVar = PyomoVar  # Capacity variables
    CostVar = PyomoVar  # Cost variables

    # Model constraints type definitions
    FlowConstraint = PyomoConstraint  # Flow balance constraints
    CapacityConstraint = PyomoConstraint  # Capacity constraints
    CostConstraint = PyomoConstraint  # Cost accounting constraints
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
    time_exist: TimesetTyped
    time_future: TimesetTyped
    time_optimize: TimesetTyped
    vintage_exist: VintagesetTyped
    vintage_optimize: VintagesetTyped
    time_season: set[Season]
    time_of_day: set[TimeOfDay]

    # Geography sets
    regions: RegionsetTyped
    regionalIndices: set[Region]

    # Technology sets
    tech_all: TechsetTyped
    tech_production: TechsetTyped
    tech_storage: TechsetTyped
    tech_reserve: TechsetTyped
    tech_exchange: TechsetTyped

    # Commodity sets
    commodity_all: CommoditysetTyped
    commodity_demand: CommoditysetTyped
    commodity_physical: CommoditysetTyped
    commodity_emissions: CommoditysetTyped

    # Model parameters
    GlobalDiscountRate: PyomoParam
    Demand: PyomoParam
    Efficiency: PyomoParam
    ExistingCapacity: PyomoParam
    CapacityToActivity: PyomoParam

    # Model variables
    V_FlowOut: Any
    V_Capacity: Any
    V_NewCapacity: Any

    # Model constraints
    DemandConstraint: Any
    CommodityBalanceConstraint: Any
    CapacityConstraint: Any

    # Internal data structures
    processInputs: ProcessInputs
    processOutputs: ProcessOutputs
    activeFlow_rpsditvo: set[RegionPeriodSeasonTimeInputTechVintageOutput]
    activeActivity_rptv: set[RegionPeriodTechVintage]

    def __init__(self, *args: object, **kwargs: object) -> None: ...


if TYPE_CHECKING:

    class TemoaModel(AbstractModel):  # type: ignore
        """
        Type stub for the main TemoaModel class.

        This provides type information for the core Temoa energy model.
        """

        # Class attributes
        default_lifetime_tech: int

        # Time-related sets
        time_exist: TimesetTyped
        time_future: TimesetTyped
        time_optimize: TimesetTyped
        vintage_exist: VintagesetTyped
        vintage_optimize: VintagesetTyped
        vintage_all: VintagesetTyped
        time_season: set[Season]
        time_of_day: set[TimeOfDay]

        # Geography sets
        regions: RegionsetTyped
        regionalIndices: set[Region]
        regionalGlobalIndices: set[Region]

        # Technology sets
        tech_all: TechsetTyped
        tech_production: TechsetTyped
        tech_baseload: TechsetTyped
        tech_annual: TechsetTyped
        tech_storage: TechsetTyped
        tech_reserve: TechsetTyped
        tech_exchange: TechsetTyped
        tech_uncap: TechsetTyped
        tech_with_capacity: TechsetTyped
        tech_retirement: TechsetTyped

        # Commodity sets
        commodity_all: CommoditysetTyped
        commodity_demand: CommoditysetTyped
        commodity_physical: CommoditysetTyped
        commodity_emissions: CommoditysetTyped
        commodity_carrier: CommoditysetTyped

        # Model parameters
        GlobalDiscountRate: PyomoParam
        PeriodLength: PyomoParam
        SegFrac: PyomoParam
        Demand: PyomoParam
        Efficiency: PyomoParam
        ExistingCapacity: PyomoParam
        CapacityToActivity: PyomoParam
        CostInvest: PyomoParam
        CostFixed: PyomoParam
        CostVariable: PyomoParam

        # Model variables
        V_FlowOut: Any
        V_Capacity: Any
        V_NewCapacity: Any
        V_RetiredCapacity: Any

        # Model constraints
        DemandConstraint: Any
        CommodityBalanceConstraint: Any
        CapacityConstraint: Any

        # Internal tracking dictionaries
        processInputs: ProcessInputs
        processOutputs: ProcessOutputs
        used_techs: Techset
        activeFlow_rpsditvo: set[RegionPeriodSeasonTimeInputTechVintageOutput]
        activeActivity_rptv: set[RegionPeriodTechVintage]

        def __init__(self, *args: object, **kwargs: object) -> None: ...


# Data structure types for model processing
class ModelData:
    """Container for model data and metadata."""

    def __init__(
        self,
        regions: Regionset,
        periods: set[Period],
        technologies: Techset,
        commodities: Commodityset,
        **kwargs: object,
    ) -> None: ...


# Export types for easy importing
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
    'Sparsedict',
    # Pyomo type aliases
    'PyomoSet',
    'PyomoParam',
    'PyomoVar',
    'PyomoConstraint',
    'PyomoBuildAction',
    'PyomoObjective',
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
