"""
Type definitions for TemoaModel and related core classes.

This module provides comprehensive type annotations for the core Temoa model,
including the main TemoaModel class and its associated data structures.
"""

from collections import namedtuple
from enum import Enum, unique
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Protocol,
    Set,
    Tuple,
    runtime_checkable,
)

from . import (
    Commodity,
    CommoditySet,
    Period,
    Region,
    RegionPeriodSeasonTimeInputTechVintageOutput,
    RegionPeriodTechVintage,
    RegionSet,
    Season,
    SparseIndex,
    Technology,
    TechSet,
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
    PyomoSet = Any  # AbstractModel.Set
    PyomoParam = Any  # AbstractModel.Param
    PyomoVar = Any  # AbstractModel.Var
    PyomoConstraint = Any  # AbstractModel.Constraint
    PyomoBuildAction = Any  # AbstractModel.BuildAction
    PyomoObjective = Any  # AbstractModel.Objective

# Type aliases for model data structures
ProcessInputs = Dict[Tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
ProcessOutputs = Dict[Tuple[Region, Period, Commodity, Technology, Vintage, Commodity], float]
TechClassification = Dict[Technology, str]
SparseDict = Dict[SparseIndex, Set[SparseIndex]]

# Model sets type definitions (avoiding naming conflicts with Set import)
TimeSetTyped = Set[Period]
RegionSetTyped = Set[Region]
TechSetTyped = Set[Technology]
CommoditySetTyped = Set[Commodity]
VintageSetTyped = Set[Vintage]

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
    time_exist: TimeSetTyped
    time_future: TimeSetTyped
    time_optimize: TimeSetTyped
    vintage_exist: VintageSetTyped
    vintage_optimize: VintageSetTyped
    time_season: Set[Season]
    time_of_day: Set[TimeOfDay]

    # Geography sets
    regions: RegionSetTyped
    regionalIndices: Set[Region]

    # Technology sets
    tech_all: TechSetTyped
    tech_production: TechSetTyped
    tech_storage: TechSetTyped
    tech_reserve: TechSetTyped
    tech_exchange: TechSetTyped

    # Commodity sets
    commodity_all: CommoditySetTyped
    commodity_demand: CommoditySetTyped
    commodity_physical: CommoditySetTyped
    commodity_emissions: CommoditySetTyped

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
    activeFlow_rpsditvo: Set[RegionPeriodSeasonTimeInputTechVintageOutput]
    activeActivity_rptv: Set[RegionPeriodTechVintage]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


if TYPE_CHECKING:

    class TemoaModel(AbstractModel):  # type: ignore
        """
        Type stub for the main TemoaModel class.

        This provides type information for the core Temoa energy model.
        """

        # Class attributes
        default_lifetime_tech: int

        # Time-related sets
        time_exist: TimeSetTyped
        time_future: TimeSetTyped
        time_optimize: TimeSetTyped
        vintage_exist: VintageSetTyped
        vintage_optimize: VintageSetTyped
        vintage_all: VintageSetTyped
        time_season: Set[Season]
        time_of_day: Set[TimeOfDay]

        # Geography sets
        regions: RegionSetTyped
        regionalIndices: Set[Region]
        regionalGlobalIndices: Set[Region]

        # Technology sets
        tech_all: TechSetTyped
        tech_production: TechSetTyped
        tech_baseload: TechSetTyped
        tech_annual: TechSetTyped
        tech_storage: TechSetTyped
        tech_reserve: TechSetTyped
        tech_exchange: TechSetTyped
        tech_uncap: TechSetTyped
        tech_with_capacity: TechSetTyped
        tech_retirement: TechSetTyped

        # Commodity sets
        commodity_all: CommoditySetTyped
        commodity_demand: CommoditySetTyped
        commodity_physical: CommoditySetTyped
        commodity_emissions: CommoditySetTyped
        commodity_carrier: CommoditySetTyped

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
        used_techs: TechSet
        activeFlow_rpsditvo: Set[RegionPeriodSeasonTimeInputTechVintageOutput]
        activeActivity_rptv: Set[RegionPeriodTechVintage]

        def __init__(self, *args: Any, **kwargs: Any) -> None: ...


# Data structure types for model processing
class ModelData:
    """Container for model data and metadata."""

    def __init__(
        self,
        regions: RegionSet,
        periods: Set[Period],
        technologies: TechSet,
        commodities: CommoditySet,
        **kwargs: Any,
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
    'SparseDict',
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


EI = namedtuple('EI', ['r', 'p', 't', 'v', 'e'])
"""Emission Index"""


@unique
class FlowType(Enum):
    """Types of flow tracked"""

    IN = 1
    OUT = 2
    CURTAIL = 3
    FLEX = 4
    LOST = 5


FI = namedtuple('FI', ['r', 'p', 's', 'd', 'i', 't', 'v', 'o'])
"""Flow Index"""

SLI = namedtuple('SLI', ['r', 'p', 's', 'd', 't', 'v'])
"""Storage Level Index"""

CapData = namedtuple('CapData', ['built', 'net', 'retired'])
"""Small container to hold named dictionaries of capacity data for processing"""
