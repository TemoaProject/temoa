# TEMOA Version 4.0.0a1

[![CI](https://github.com/TemoaProject/temoa/actions/workflows/ci.yml/badge.svg?branch=unstable)](https://github.com/TemoaProject/temoa/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/temoa/badge/?version=latest)](https://temoa.readthedocs.io/en/latest/?badge=latest)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://pyreadiness.org/3.12/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked with mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square&logo=python)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## Overview

TEMOA (Tools for Energy Model Optimization and Analysis) is a sophisticated energy systems optimization framework that supports various modeling approaches including perfect foresight, myopic planning, uncertainty analysis, and alternative generation.

## Quick Start

### Using uv (Recommended)

The fastest way to get started with Temoa:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

```

Bleeding-edge nightly development installation:

In a directory initialized with uv (e.g., `uv init .`) run:

```bash
uv add temoa --default-index https://pypi.temoaproject.org/simple/ --index https://pypi.org/simple/

# or

pip install --index-url https://temoaproject.github.io/temoa-nightlies/simple/ temoa --extra-index-url https://pypi.org/simple/

```

Or clone the repository and install in development mode:

```bash

# Clone and setup development environment
git clone https://github.com/TemoaProject/temoa.git
cd temoa
uv sync --all-extras --dev

# Run your first model
uv run temoa tutorial my_first_model
uv run temoa run my_first_model.toml
```

### Standard Installation

```bash
# Install from PyPI (not yet available)
pip install temoa

# Or install from source
pip install -e .
```

### Get Started in 30 Seconds

```bash
# Create tutorial files
temoa tutorial quick_start

# Run the model
temoa run quick_start.toml
```

## Package Structure

The Temoa package is organized into clear modules:

- **`temoa.core`** - Public API for end users (TemoaModel, TemoaConfig, TemoaMode)
- **`temoa.cli`** - Command-line interface and utilities
- **`temoa.components`** - Model components and constraints
- **`temoa.data_io`** - Data loading and validation
- **`temoa.extensions`** - Optional extensions for different modeling approaches
  - `modeling_to_generate_alternatives` - MGA analysis
  - `method_of_morris` - Sensitivity analysis
  - `monte_carlo` - Uncertainty quantification
  - `myopic` - Sequential decision making
- **`temoa.model_checking`** - Model validation and integrity checking
- **`temoa.data_processing`** - Output analysis and visualization
- **`temoa.utilities`** - Helper scripts and migration tools

## Installation & Setup

### Development Installation

For users who want to contribute or modify Temoa should install in development mode using `uv`:

```bash
# Clone repository
git clone https://github.com/TemoaProject/temoa.git
cd temoa

# Setup development environment with uv
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run type checking
uv run mypy
```

## Command Line Interface

Temoa provides a modern, user-friendly CLI built with Typer:

### Basic Commands

**Run a model:**

```bash
temoa run config.toml
temoa run config.toml --output results/
temoa run config.toml --build-only  # Build without solving
```

**Validate configuration:**

```bash
temoa validate config.toml
temoa validate config.toml --debug
```

**Database migration:**

```bash
temoa migrate old_database.sql --output new_database.sql
temoa migrate old_database.db --type db
temoa migrate old_database.sqlite --output migrated_v4.sqlite
```

**Generate tutorial files:**

```bash
temoa tutorial                    # Creates tutorial_config.toml and tutorial_database.sqlite
temoa tutorial my_model my_db     # Custom names
```

### Global Options

```bash
temoa --version                   # Show version information
temoa --how-to-cite              # Show citation information
temoa --help                     # Full help
```

### Using with uv

When working with the source code, use `uv run` to ensure you're using the correct dependencies:

```bash
uv run temoa run config.toml      # Run with project dependencies
uv run temoa validate config.toml # Validate configuration
uv run temoa tutorial my_first_model # Create tutorial files
```

## Programmatic Usage

You can use Temoa as a Python library:

```python
import temoa
from pathlib import Path
from temoa import TemoaModel, TemoaConfig, TemoaMode

# Create configuration
config = TemoaConfig(
    scenario="my_scenario",
    scenario_mode=TemoaMode.PERFECT_FORESIGHT,
    input_database=Path("path/to/input.db"),
    output_database=Path("path/to/output.db"),
    output_path=Path("path/to/output"),
    solver_name="appsi_highs"
)

# Build and solve model
model = TemoaModel(config)
result = model.run()  # Equivalent to: temoa run config.toml

# Check if run was successful
if result:
    print("Model solved successfully!")
else:
    print("Model failed to solve")
```

## Database Setup

### Quick Setup with Tutorial

The fastest way to get started:

```bash
temoa tutorial
```

This creates:

- `tutorial_config.toml` - Configuration file with example settings
- `tutorial_database.sqlite` - Sample database for learning

**Migration from older versions:**

```bash
# Migrate from v3.1 to v4
temoa migrate old_database_v3.1.sql --output new_database_v4.sql

# or for SQLite databases
temoa migrate old_database_v4.sqlite --output new_database_v4.sqlite
```

## Configuration Files

A configuration file is required to run the model. The tutorial command creates a complete example:

```toml
scenario = "tutorial"
scenario_mode = "perfect_foresight"
input_database = "tutorial_database.sqlite"
output_database = "tutorial_database.sqlite"
solver_name = "appsi_highs"
```

### Configuration Options

| Field | Notes |
|-------|-------|
| Scenario Name | Name used in output tables (cannot contain '-' symbol) |
| Temoa Mode | Execution mode (PERFECT_FORESIGHT, MYOPIC, MGA, etc.) |
| Input/Output DB | Source and output database paths |
| Price Checking | Run pricing analysis on built model |
| Source Tracing | Verify commodity flow network integrity |
| Plot Network | Generate HTML network visualizations |
| Solver | Solver executable name (appsi_highs, cbc, gurobi, cplex, etc.) |
| Save Excel | Export core output to Excel files |
| Save LP | Save LP model files for external solving |

## Supported Modes

### Perfect Foresight

Solves the entire model at once. Most common mode for optimization.

### Myopic

Sequential solving through iterative builds. Required for stepwise decision analysis.

### MGA (Modeling to Generate Alternatives)

Explores near cost-optimal solutions for robustness analysis.

### SVMGA (Single Vector MGA)

Two-solve process focusing on specific variables in the objective.

### Method of Morris

Limited sensitivity analysis of user-selected variables.

### Build Only

Builds model without solving. Useful for validation and troubleshooting.

## Typical Workflow

1. **Setup**: Create configuration and database files:

   ```bash
   temoa tutorial my_project
   ```

2. **Configure**: Edit the configuration file to match your scenario

3. **Validate**: Check configuration before running:

   ```bash
   temoa validate my_project_config.toml
   ```

4. **Run**: Execute the model:

   ```bash
   temoa run my_project_config.toml
   ```

5. **Review**: Check results in `output_files/YYYY-MM-DD_HHMMSS/`

6. **Iterate**: Modify configuration and run again

## Advanced Features

### Extensions

Temoa includes optional extensions for advanced analysis:

- **Monte Carlo**: Uncertainty quantification
- **Stochastic Programming**: Scenario-based optimization
- **Method of Morris**: Sensitivity analysis

### Data Processing

- Excel output generation
- Graphviz network visualization
- Interactive network diagrams

### Model Validation

- Built-in validation checks
- Commodity flow verification
- Price consistency analysis

### Solver Dependencies

TEMOA requires at least one optimization solver:

- **Free**: [HiGHS](https://ergo-code.github.io/HiGHS/)
  - Included via the `highspy` Python package (automatically installed with Temoa)
  - Default solver for tutorial and testing

- **Free**: [CBC](https://github.com/coin-or/Cbc)
  - Requires separate installation (see [CBC documentation](https://github.com/coin-or/Cbc))
  - Alternative free solver option

- **Commercial**: Gurobi, CPLEX, or Xpress
  - Requires separate license and installation
  - See individual solver documentation

## Troubleshooting

### Solver Issues

If you encounter solver errors:

```bash
# For commercial solvers (Gurobi, CPLEX)
pip install ".[solver]"  # Include specific solver packages

# For free solver
temoa run config.toml --debug  # Get detailed error information
```

## Documentation & Support

- **Full Documentation**: Built by following docs/README.md
- **API Reference**: See `temoa.core` module for public API
- **GitHub Issues**: Report bugs and request features
- **Tutorials**: Run `temoa tutorial` for guided examples

## Code Style & Quality

For contributors:

- **Ruff**: Code formatting and linting
- **mypy**: Type checking
- **pytest**: Testing framework
- **Pre-commit**: Automated quality checks

See CONTRIBUTING.md for detailed development guidelines.

## Citation

If you use Temoa in your research, please cite:

```bibtex
@article{hunter2013modeling,
  title={Modeling for insight using Tools for Energy Model Optimization and Analysis (Temoa)},
  journal={Energy Economics},
  volume={40},
  pages={339--349},
  year={2013},
  doi={10.1016/j.eneco.2013.07.014}
}
```

Or use: `temoa --how-to-cite`
