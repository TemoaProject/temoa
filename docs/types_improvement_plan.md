# Temoa Types Subdirectory Improvement Plan

**Document Version:** 1.0
**Date:** 2025-10-17
**Status:** Draft for Review

## Executive Summary

This document outlines a comprehensive improvement plan for the `temoa/types` subdirectory, which currently contains 960 lines of type definitions across four files. The plan addresses five major categories of issues: incomplete stub coverage, inconsistent runtime fallback patterns, documentation gaps, missing type definitions, and organizational concerns. Implementation is structured in three phases over an estimated 3-4 week timeline.

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Issues Identified](#issues-identified)
3. [Prioritized Recommendations](#prioritized-recommendations)
4. [Phased Implementation Approach](#phased-implementation-approach)
5. [Expected Benefits](#expected-benefits)
6. [Risks and Mitigation Strategies](#risks-and-mitigation-strategies)
7. [Success Metrics](#success-metrics)

---

## Current State Analysis

### Directory Structure

```
temoa/types/
├── __init__.py           (390 lines) - Core type definitions and aliases
├── model_types.py        (343 lines) - TemoaModel-specific types
├── pandas_stubs.pyi      (123 lines) - Pandas type stubs
└── pyomo_stubs.pyi       (104 lines) - Pyomo type stubs
```

### Current Strengths

1. **Comprehensive Basic Types**: Well-defined core types for dimensions (Region, Period, Technology, etc.)
2. **Extensive Index Types**: 11 core index tuple types covering major model dimensions
3. **Rich Dictionary Types**: 31 specialized dictionary types for process tracking, commodities, and technology classification
4. **Proper TYPE_CHECKING Usage**: Conditional imports in [`__init__.py`](temoa/types/__init__.py:236-257) and [`model_types.py`](temoa/types/model_types.py:34-52)
5. **Compatibility Aliases**: Both lowercase and capitalized versions for backward compatibility

### Current Weaknesses

1. **Incomplete External Library Coverage**: Stubs missing critical methods and types
2. **Inconsistent Patterns**: Components define their own runtime fallbacks instead of importing from types
3. **Limited Documentation**: Complex types lack explanatory comments and usage examples
4. **Missing Domain Types**: No types for solver results, validation, or configuration objects
5. **Organizational Issues**: Large [`__init__.py`](temoa/types/__init__.py:1-390) mixing multiple concerns

---

## Issues Identified

### 1. Incomplete Stub Coverage

**Priority:** HIGH
**Impact:** Type checking effectiveness, IDE support quality

#### 1.1 Pyomo Stubs ([`pyomo_stubs.pyi`](temoa/types/pyomo_stubs.pyi:1-104))

**Missing Critical Types:**

- `ConcreteModel` class (used extensively in testing and extensions)
- `SolverFactory` and solver-related types
- `SolverResults`, `SolverStatus`, `TerminationCondition` enums
- Expression types (`SumExpression`, `ProductExpression`, etc.)
- `value()` function edge cases (handling None, expressions)
- Domain types (`NonNegativeReals`, `Binary`, `Integers`, etc.)
- `RangeSet`, `Set` initialization patterns

**Evidence from Codebase:**

```python
# From capacity.py line 20
from pyomo.environ import value  # Used 15+ times but stub is minimal

# From model.py (implied usage)
# ConcreteModel instances created but no stub exists
```

**Impact:**

- Type checkers cannot validate Pyomo-specific code
- IDE autocomplete limited for Pyomo objects
- No validation of solver result handling

#### 1.2 Pandas Stubs ([`pandas_stubs.pyi`](temoa/types/pandas_stubs.pyi:1-123))

**Missing Common Operations:**

- `pivot()`, `pivot_table()` methods
- `groupby()` aggregation methods (currently returns `Any`)
- `join()`, `concat()` operations
- `apply()`, `map()`, `transform()` methods
- `loc`, `iloc` indexers
- `drop()`, `rename()`, `reset_index()` methods
- `isna()`, `fillna()`, `dropna()` methods

**Evidence from Codebase:**

```python
# Data processing modules use these extensively
# DB_to_Excel.py, MakeOutputPlots.py, etc.
```

**Impact:**

- Limited type safety in data processing modules
- Poor IDE support for DataFrame operations
- Cannot catch common pandas usage errors

### 2. Runtime Fallback Patterns

**Priority:** HIGH
**Impact:** Code consistency, maintainability

#### 2.1 Inconsistent TYPE_CHECKING Usage

**Current State:**

- [`__init__.py`](temoa/types/__init__.py:236-257): Uses TYPE_CHECKING for pandas/numpy
- [`model_types.py`](temoa/types/model_types.py:34-52): Uses TYPE_CHECKING for Pyomo types
- [`capacity.py`](temoa/components/capacity.py:23-43): Defines its own runtime fallbacks
- [`flows.py`](temoa/components/flows.py:13-20): Imports directly from types (good pattern)

**Problem Example from [`capacity.py`](temoa/components/capacity.py:35-43):**

```python
else:
    # Runtime fallback for non-TYPE_CHECKING contexts
    Region = Any
    Period = Any
    Season = Any
    TimeOfDay = Any
    Technology = Any
    Vintage = Any
    RegionPeriodTechVintage = Any
```

**Issues:**

- Duplicates type definitions across modules
- Increases maintenance burden
- Risk of inconsistency between modules
- Violates DRY principle

#### 2.2 Recommended Pattern

**Centralized Approach:**

```python
# In temoa/types/__init__.py - expand runtime fallbacks
if TYPE_CHECKING:
    from .pandas_stubs import DataFrame, Series
    from .pyomo_stubs import PyomoSet, PyomoParam
    # ... other imports
else:
    # Comprehensive runtime fallbacks
    DataFrame = Any
    Series = Any
    PyomoSet = Any
    PyomoParam = Any
    # ... all types that might be used at runtime
```

**Component Usage:**

```python
# In components/*.py - always import from types
from temoa.types import Region, Period, Technology  # Works in both contexts
```

### 3. Documentation Gaps

**Priority:** MEDIUM
**Impact:** Developer onboarding, code understanding

#### 3.1 Missing Explanatory Comments

**Complex Types Without Documentation:**

1. **Process Dictionary Types** (lines 81-99 in [`__init__.py`](temoa/types/__init__.py:81-99))
   - `ProcessInputsByOutputdict`: What does "by output" mean?
   - `ProcessReservePeriodsdict`: When is this used?
   - `RetirementProductionProcessesdict`: Why tuple value?

2. **Sparse Index Sets** (lines 187-213 in [`__init__.py`](temoa/types/__init__.py:187-213))
   - `ActiveFlowset` vs `ActiveFlowAnnualset`: When to use which?
   - `ActiveFlexset`: What makes a flow "flexible"?
   - `StorageLevelIndicesset`: Relationship to storage technologies?

3. **Technology Classification** (lines 125-135 in [`__init__.py`](temoa/types/__init__.py:125-135))
   - `BaseloadVintagesdict`: Baseload definition?
   - `InputSplitVintagesdict`: What is the `str` parameter?

#### 3.2 Missing Usage Examples

**Needed Examples:**

- How to properly construct index tuples
- When to use dict vs set types
- Proper TYPE_CHECKING import patterns
- Common type annotation patterns for functions

#### 3.3 Missing Design Rationale

**Questions Without Answers:**

- Why both lowercase and capitalized aliases?
- Why Optional for some set types but not others?
- When to use `SparseIndex` vs specific tuple types?
- Why `Any` for database types instead of Protocol?

### 4. Missing Type Definitions

**Priority:** MEDIUM to HIGH
**Impact:** Type coverage completeness

#### 4.1 Solver-Related Types (HIGH Priority)

**Missing:**

```python
# Solver results and status
SolverResults = Any  # Should be proper type
SolverStatus = Any   # Should be enum
TerminationCondition = Any  # Should be enum
SolverFactory = Any  # Should be callable type

# Solver options
SolverOptions = dict[str, Any]  # Could be TypedDict
```

**Usage Context:**

- Model solving in `temoa/core/model.py`
- Extension modules (MGA, Morris, Myopic)
- Test suites checking solver status

#### 4.2 Configuration Types (MEDIUM Priority)

**Current State:**

```python
Configdict = dict[str, Any]  # Too generic
```

**Needed:**

```python
# Structured configuration types
class TemoaConfig(TypedDict, total=False):
    scenario_name: str
    input_database: str
    output_database: str
    solver_name: str
    # ... other config fields

# Or Protocol-based approach
class ConfigProtocol(Protocol):
    scenario_name: str
    input_database: str
    # ... required fields
```

**Benefits:**

- Type-safe configuration access
- IDE autocomplete for config keys
- Validation of required fields

#### 4.3 Database Schema Types (MEDIUM Priority)

**Current State:**

```python
DatabaseConnection = Any  # sqlite3.Connection or similar
DatabaseCursor = Any      # sqlite3.Cursor or similar
QueryResult = list[tuple[Any, ...]]  # Too generic
```

**Needed:**

```python
# Specific table row types
class TechnologyRow(TypedDict):
    region: str
    tech: str
    flag: str
    sector: str
    # ... other fields

# Query result types
TechnologyQueryResult = list[TechnologyRow]
```

**Benefits:**

- Type-safe database operations
- Clear schema documentation
- Easier refactoring

#### 4.4 Validation Result Types (LOW Priority)

**Missing:**

```python
# Validation results
class ValidationError(NamedTuple):
    severity: str  # 'error' | 'warning'
    message: str
    location: Optional[str]

ValidationResult = list[ValidationError]
```

**Usage Context:**

- `temoa/model_checking/validators.py`
- `temoa/model_checking/element_checker.py`

### 5. Organizational Issues

**Priority:** LOW to MEDIUM
**Impact:** Code maintainability, navigation

#### 5.1 Large [`__init__.py`](temoa/types/__init__.py:1-390) File

**Current Structure (390 lines):**

- Lines 1-43: Core types and basic indices
- Lines 44-59: Database and parameter types
- Lines 61-78: Core index types (11 types)
- Lines 80-114: Process dictionaries (13 types + aliases)
- Lines 116-122: Commodity dictionaries (2 types + aliases)
- Lines 124-146: Technology classification (9 types + aliases)
- Lines 148-156: Time sequencing (3 types + aliases)
- Lines 159-170: Geography/exchange (3 types + aliases)
- Lines 172-184: Boolean flags (4 types + aliases)
- Lines 186-228: Sparse index sets (13 types + aliases)
- Lines 230-257: Pyomo/Pandas/Numpy types with TYPE_CHECKING
- Lines 259-266: Configuration and constraint types
- Lines 268-390: **all** export list

**Issues:**

- Multiple concerns mixed together
- Difficult to locate specific type categories
- Large **all** list (122 exports)
- Scrolling required to find types

#### 5.2 Proposed Reorganization

**Option A: Logical Grouping (Recommended)**

```
temoa/types/
├── __init__.py           # Re-exports, core types only
├── model_types.py        # TemoaModel-specific (existing)
├── indices.py            # All index tuple types
├── dictionaries.py       # All dictionary types
├── sets.py               # All set types
├── external_stubs/
│   ├── pandas_stubs.pyi
│   └── pyomo_stubs.pyi
└── protocols.py          # Protocol definitions
```

**Option B: Domain-Based (Alternative)**

```
temoa/types/
├── __init__.py           # Re-exports
├── model_types.py        # TemoaModel (existing)
├── core.py               # Basic types (Region, Period, etc.)
├── process.py            # Process-related types
├── commodity.py          # Commodity-related types
├── technology.py         # Technology-related types
├── time.py               # Time-related types
└── external_stubs/       # External library stubs
```

**Recommendation:** Option A

- Clearer organization by type category
- Easier to find specific types
- Better separation of concerns
- Maintains backward compatibility through **init**.py

---

## Prioritized Recommendations

### High Priority (Phase 1)

#### H1: Complete Pyomo Stubs

**Effort:** 2-3 days
**Impact:** High

**Tasks:**

1. Add `ConcreteModel` class definition
2. Add solver-related types (`SolverFactory`, `SolverResults`, status enums)
3. Expand `value()` function signature with edge cases
4. Add domain types (`NonNegativeReals`, `Binary`, etc.)
5. Add expression types for common operations
6. Add comprehensive docstrings

**Deliverable:** Enhanced [`pyomo_stubs.pyi`](temoa/types/pyomo_stubs.pyi:1-104) with 200+ lines

#### H2: Standardize Runtime Fallbacks

**Effort:** 1-2 days
**Impact:** High

**Tasks:**

1. Audit all component files for local TYPE_CHECKING blocks
2. Move all runtime fallbacks to [`types/__init__.py`](temoa/types/__init__.py:236-257)
3. Update component imports to use centralized types
4. Add comprehensive runtime fallback section
5. Document the pattern in types module docstring

**Deliverable:** Consistent import pattern across all 15+ component files

#### H3: Add Solver Result Types

**Effort:** 1 day
**Impact:** High

**Tasks:**

1. Create solver result type definitions
2. Add status and termination condition enums
3. Update model solving code to use typed results
4. Add type hints to solver-related functions

**Deliverable:** New section in [`model_types.py`](temoa/types/model_types.py:1-343) or separate `solver_types.py`

### Medium Priority (Phase 2)

#### M1: Expand Pandas Stubs

**Effort:** 2-3 days
**Impact:** Medium

**Tasks:**

1. Add missing DataFrame methods (pivot, groupby aggregations, etc.)
2. Add indexer types (loc, iloc)
3. Add data manipulation methods (drop, rename, etc.)
4. Add missing Series methods
5. Improve return type specificity

**Deliverable:** Enhanced [`pandas_stubs.pyi`](temoa/types/pandas_stubs.pyi:1-123) with 250+ lines

#### M2: Add Type Documentation

**Effort:** 3-4 days
**Impact:** Medium

**Tasks:**

1. Add docstrings to all complex dictionary types
2. Create usage examples for common patterns
3. Document design rationale in module docstring
4. Add inline comments for non-obvious types
5. Create types usage guide in docs/

**Deliverable:** Comprehensive documentation in types module + new guide document

#### M3: Create Configuration Types

**Effort:** 2 days
**Impact:** Medium

**Tasks:**

1. Define `TemoaConfig` TypedDict or Protocol
2. Update config loading code to use typed config
3. Add validation for required fields
4. Document configuration schema

**Deliverable:** New `config_types.py` module

#### M4: Add Database Schema Types

**Effort:** 2-3 days
**Impact:** Medium

**Tasks:**

1. Define TypedDict for each major table
2. Create query result types
3. Update database utility functions with types
4. Document schema in types

**Deliverable:** New `database_types.py` module

### Low Priority (Phase 3)

#### L1: Reorganize Types Module

**Effort:** 2-3 days
**Impact:** Low (but improves maintainability)

**Tasks:**

1. Create new module structure (Option A recommended)
2. Move types to appropriate modules
3. Update [`__init__.py`](temoa/types/__init__.py:1-390) to re-export all types
4. Update imports across codebase
5. Verify no breaking changes

**Deliverable:** Reorganized types/ directory with backward compatibility

#### L2: Add Validation Result Types

**Effort:** 1 day
**Impact:** Low

**Tasks:**

1. Define validation error types
2. Update validator functions to use typed results
3. Add type hints to validation code

**Deliverable:** New `validation_types.py` module

#### L3: Create Type Usage Examples

**Effort:** 2 days
**Impact:** Low (but improves developer experience)

**Tasks:**

1. Create example scripts showing type usage
2. Add examples to documentation
3. Create type annotation cookbook

**Deliverable:** New `docs/type_usage_guide.md` with examples

---

## Phased Implementation Approach

### Phase 1: Critical Improvements (Week 1-2)

**Focus:** High-priority items that immediately improve type safety

**Week 1:**

- Days 1-3: Complete Pyomo stubs (H1)
- Days 4-5: Standardize runtime fallbacks (H2)

**Week 2:**

- Days 1-2: Add solver result types (H3)
- Days 3-5: Testing and validation of Phase 1 changes

**Deliverables:**

- Enhanced Pyomo stubs with 100+ new lines
- Consistent TYPE_CHECKING pattern across codebase
- Solver result types integrated
- All existing tests passing

**Success Criteria:**

- Type checker reports 30%+ fewer errors
- No runtime regressions
- All component files use centralized types

### Phase 2: Enhanced Coverage (Week 3)

**Focus:** Medium-priority items that improve developer experience

**Week 3:**

- Days 1-2: Expand Pandas stubs (M1)
- Day 3: Add type documentation (M2 - partial)
- Days 4-5: Create configuration types (M3) and database types (M4)

**Deliverables:**

- Enhanced Pandas stubs
- Initial documentation improvements
- Configuration and database type modules
- Updated usage examples

**Success Criteria:**

- Data processing code has better type coverage
- Configuration access is type-safe
- Documentation helps new developers

### Phase 3: Polish and Organization (Week 4)

**Focus:** Low-priority items that improve long-term maintainability

**Week 4:**

- Days 1-3: Reorganize types module (L1)
- Day 4: Add validation types (L2)
- Day 5: Create usage guide (L3)

**Deliverables:**

- Reorganized types directory
- Complete documentation
- Usage guide and examples
- Final testing and validation

**Success Criteria:**

- Types are easy to find and understand
- New developers can quickly learn type system
- All documentation is complete

### Implementation Guidelines

**For Each Phase:**

1. **Pre-Implementation:**
   - Create feature branch
   - Review current usage patterns
   - Identify affected files

2. **Implementation:**
   - Make changes incrementally
   - Run type checker after each change
   - Update tests as needed
   - Document changes

3. **Testing:**
   - Run full test suite
   - Verify type checker results
   - Check for runtime regressions
   - Test IDE autocomplete

4. **Review:**
   - Code review by team
   - Documentation review
   - Integration testing

5. **Deployment:**
   - Merge to main branch
   - Update changelog
   - Notify team of changes

---

## Expected Benefits

### Immediate Benefits (Phase 1)

1. **Improved Type Safety**
   - 30-40% reduction in type checker errors
   - Catch more bugs at development time
   - Better validation of Pyomo operations

2. **Consistent Patterns**
   - Single source of truth for type definitions
   - Easier to maintain and update types
   - Reduced code duplication

3. **Better IDE Support**
   - Improved autocomplete for Pyomo objects
   - Better error detection in IDE
   - Faster development workflow

### Medium-Term Benefits (Phase 2)

1. **Enhanced Developer Experience**
   - Clear documentation of type system
   - Easy-to-find type definitions
   - Usage examples for common patterns

2. **Safer Data Processing**
   - Type-safe DataFrame operations
   - Validation of configuration access
   - Better database query safety

3. **Reduced Onboarding Time**
   - New developers understand types faster
   - Clear examples to follow
   - Better code navigation

### Long-Term Benefits (Phase 3)

1. **Maintainability**
   - Well-organized type system
   - Easy to extend with new types
   - Clear separation of concerns

2. **Code Quality**
   - Fewer runtime type errors
   - Better refactoring support
   - Easier to catch breaking changes

3. **Documentation**
   - Types serve as documentation
   - Clear contracts between modules
   - Better understanding of data flow

### Quantifiable Metrics

**Type Coverage:**

- Current: ~60% of functions have type hints
- Phase 1 Target: ~75%
- Phase 2 Target: ~85%
- Phase 3 Target: ~95%

**Type Checker Errors:**

- Current: ~150 errors (estimated)
- Phase 1 Target: <100 errors
- Phase 2 Target: <50 errors
- Phase 3 Target: <20 errors

**Developer Productivity:**

- Reduced time to understand type system: 50%
- Faster code navigation: 30%
- Fewer type-related bugs: 40%

---

## Risks and Mitigation Strategies

### Risk 1: Breaking Changes

**Severity:** HIGH
**Probability:** MEDIUM

**Description:**
Reorganizing types or changing import patterns could break existing code.

**Mitigation:**

1. Maintain backward compatibility through re-exports in [`__init__.py`](temoa/types/__init__.py:1-390)
2. Use deprecation warnings for old patterns
3. Comprehensive testing before each merge
4. Gradual rollout with feature flags if needed
5. Keep old aliases during transition period

**Contingency:**

- Revert changes if critical issues found
- Extend transition period if needed
- Provide migration guide for affected code

### Risk 2: Incomplete Stub Coverage

**Severity:** MEDIUM
**Probability:** MEDIUM

**Description:**
External library stubs may not cover all edge cases or future API changes.

**Mitigation:**

1. Focus on commonly-used methods first
2. Add stubs incrementally based on actual usage
3. Use `Any` as fallback for complex types
4. Document known limitations
5. Regular updates as libraries evolve

**Contingency:**

- Maintain list of known gaps
- Provide workarounds for missing stubs
- Contribute stubs to typeshed if appropriate

### Risk 3: Performance Impact

**Severity:** LOW
**Probability:** LOW

**Description:**
Additional type checking might slow down development or runtime.

**Mitigation:**

1. Type checking is development-time only
2. No runtime overhead from type hints
3. Monitor CI/CD pipeline times
4. Optimize type checker configuration if needed

**Contingency:**

- Adjust type checker strictness if needed
- Use incremental type checking
- Cache type checking results

### Risk 4: Team Adoption

**Severity:** MEDIUM
**Probability:** LOW

**Description:**
Team may resist new type patterns or find them too complex.

**Mitigation:**

1. Provide clear documentation and examples
2. Gradual introduction of new patterns
3. Training sessions on type system
4. Make types optional initially
5. Demonstrate benefits with concrete examples

**Contingency:**

- Adjust complexity based on feedback
- Provide more examples and support
- Make certain types optional

### Risk 5: Maintenance Burden

**Severity:** MEDIUM
**Probability:** MEDIUM

**Description:**
Maintaining comprehensive type definitions requires ongoing effort.

**Mitigation:**

1. Automate type checking in CI/CD
2. Regular reviews of type coverage
3. Clear ownership of types module
4. Documentation of maintenance procedures
5. Use tools to detect type drift

**Contingency:**

- Reduce scope if maintenance becomes excessive
- Prioritize most-used types
- Community contributions for less-critical types

---

## Success Metrics

### Quantitative Metrics

1. **Type Coverage**
   - Measure: % of functions with complete type hints
   - Target: 95% by end of Phase 3
   - Tool: mypy coverage report

2. **Type Checker Errors**
   - Measure: Number of type errors reported
   - Target: <20 errors by end of Phase 3
   - Tool: mypy error count

3. **Test Coverage**
   - Measure: % of type-related code covered by tests
   - Target: >90% coverage maintained
   - Tool: pytest-cov

4. **Documentation Coverage**
   - Measure: % of complex types with docstrings
   - Target: 100% by end of Phase 2
   - Tool: Manual review

### Qualitative Metrics

1. **Developer Satisfaction**
   - Survey team on type system usability
   - Collect feedback on IDE experience
   - Track time to understand types

2. **Code Review Quality**
   - Fewer type-related review comments
   - Faster review process
   - Better understanding of changes

3. **Bug Reduction**
   - Track type-related bugs in issue tracker
   - Compare pre/post implementation
   - Monitor runtime type errors

### Monitoring and Reporting

**Weekly During Implementation:**

- Type checker error count
- Test pass rate
- Implementation progress

**Monthly After Implementation:**

- Type coverage trends
- Developer feedback summary
- Bug rate analysis

**Quarterly:**

- Comprehensive metrics review
- Adjustment of targets if needed
- Planning for next improvements

---

## Appendix A: File-by-File Analysis

### [`temoa/types/__init__.py`](temoa/types/__init__.py:1-390)

**Current State:** 390 lines, 122 exports
**Strengths:**

- Comprehensive core type definitions
- Good use of TYPE_CHECKING
- Backward compatibility aliases

**Weaknesses:**

- Too large, multiple concerns
- Limited documentation
- Some types could be more specific

**Recommendations:**

- Split into multiple modules (Phase 3)
- Add docstrings to complex types (Phase 2)
- Expand runtime fallbacks (Phase 1)

### [`temoa/types/model_types.py`](temoa/types/model_types.py:1-343)

**Current State:** 343 lines
**Strengths:**

- Good Protocol definition
- Proper TYPE_CHECKING usage
- Named tuples for indices

**Weaknesses:**

- Missing some TemoaModel attributes
- Could use more documentation
- Some types are too generic (Any)

**Recommendations:**

- Add solver result types (Phase 1)
- Expand TemoaModel stub (Phase 2)
- Add more specific types (Phase 2)

### [`temoa/types/pandas_stubs.pyi`](temoa/types/pandas_stubs.pyi:1-123)

**Current State:** 123 lines
**Strengths:**

- Basic DataFrame/Series coverage
- Protocol for DataFrame-like objects

**Weaknesses:**

- Missing many common methods
- groupby returns Any
- No indexer types

**Recommendations:**

- Add missing methods (Phase 2)
- Improve return type specificity (Phase 2)
- Add comprehensive docstrings (Phase 2)

### [`temoa/types/pyomo_stubs.pyi`](temoa/types/pyomo_stubs.pyi:1-104)

**Current State:** 104 lines
**Strengths:**

- Basic Pyomo component coverage
- Protocol for components

**Weaknesses:**

- Missing ConcreteModel
- No solver types
- Limited expression types
- Minimal value() function

**Recommendations:**

- Add ConcreteModel (Phase 1)
- Add solver types (Phase 1)
- Expand expression types (Phase 1)
- Improve value() signature (Phase 1)

---

## Appendix B: Example Improvements

### Example 1: Enhanced Pyomo Stubs

**Before:**

```python
def value(obj: Any) -> Any: ...
```

**After:**

```python
from typing import overload, Union

@overload
def value(obj: None) -> None: ...

@overload
def value(obj: int) -> int: ...

@overload
def value(obj: float) -> float: ...

@overload
def value(obj: PyomoVar) -> float: ...

@overload
def value(obj: PyomoParam) -> Union[int, float, str]: ...

@overload
def value(obj: PyomoExpression) -> float: ...

def value(obj: Any) -> Any:
    """
    Extract the numeric value from a Pyomo component.

    Args:
        obj: Pyomo variable, parameter, expression, or numeric value

    Returns:
        The numeric value, or None if undefined
    """
    ...
```

### Example 2: Configuration Types

**Before:**

```python
Configdict = dict[str, Any]
```

**After:**

```python
from typing import TypedDict, Literal

class TemoaConfig(TypedDict, total=False):
    """Configuration for Temoa model runs."""

    # Required fields
    scenario_name: str
    input_database: str

    # Optional fields
    output_database: str
    solver_name: Literal['gurobi', 'cplex', 'glpk', 'cbc']
    neos: bool
    save_excel: bool
    save_lp_file: bool
    save_duals: bool

    # Solver options
    solver_options: dict[str, Any]

    # Output options
    output_path: str
    plot_results: bool
```

### Example 3: Documented Dictionary Type

**Before:**

```python
ProcessInputsByOutputdict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
```

**After:**

```python
ProcessInputsByOutputdict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
"""
Maps a process and its output commodity to the set of valid input commodities.

Key: (region, period, technology, vintage, output_commodity)
Value: Set of input commodities that can produce this output

Example:
    For a coal power plant (COAL_PP) producing electricity (ELC):
    {
        ('R1', 2020, 'COAL_PP', 2020, 'ELC'): {'COAL', 'WATER'},
        ('R1', 2025, 'COAL_PP', 2020, 'ELC'): {'COAL', 'WATER'}
    }

Usage:
    Used in commodity balance constraints to determine valid input-output
    combinations for each process. Essential for multi-input technologies.
"""
```

---

## Appendix C: Migration Guide

### For Component Developers

**Old Pattern (Don't Use):**

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from temoa.types import Region, Period
else:
    Region = Any
    Period = Any
```

**New Pattern (Use This):**

```python
from temoa.types import Region, Period, Technology
# Works in both TYPE_CHECKING and runtime contexts
```

### For Type Stub Users

**Importing Stubs:**

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.types import DataFrame, PyomoVar
    # These are stubs, only for type checking
```

**Runtime Usage:**

```python
import pandas as pd
from pyomo.environ import Var

# Use actual libraries at runtime
df = pd.DataFrame()  # Real pandas
var = Var()  # Real Pyomo
```

### For Configuration Users

**Old Pattern:**

```python
config: dict[str, Any] = load_config()
solver = config['solver_name']  # No type checking
```

**New Pattern:**

```python
from temoa.types import TemoaConfig

config: TemoaConfig = load_config()
solver = config['solver_name']  # Type checked!
```

---

## Conclusion

This improvement plan provides a comprehensive roadmap for enhancing the `temoa/types` subdirectory over a 3-4 week period. By addressing incomplete stub coverage, standardizing patterns, improving documentation, adding missing types, and reorganizing the structure, we will significantly improve type safety, developer experience, and code maintainability.

The phased approach allows for incremental progress with regular validation, minimizing risk while maximizing benefit. Success metrics will track both quantitative improvements (type coverage, error reduction) and qualitative benefits (developer satisfaction, code quality).

Implementation should begin with Phase 1 high-priority items that provide immediate value, followed by Phase 2 enhancements, and concluding with Phase 3 organizational improvements for long-term maintainability.

---

**Next Steps:**

1. Review and approve this plan
2. Assign ownership for each phase
3. Create tracking issues for each task
4. Begin Phase 1 implementation
5. Schedule regular progress reviews
