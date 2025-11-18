# Overview

This folder contains files used to manage Temoa output data processing and visualization.

> **⚠️ Note:** These tools have not been fully tested with Temoa v4.0. They may require updates or fixes. Please report any issues on [GitHub Issues](https://github.com/TemoaProject/temoa/issues).

## Available Tools

### 1. `db_to_excel.py`

**Status:** ⚠️ Untested in v4.0

Python script that queries database output tables to create an Excel file containing scenario-specific results.

**Usage:**
```bash
uv run python temoa/data_processing/db_to_excel.py -i path/to/database.sqlite -s scenario_name
```

### 2. `make_graphviz.py`

**Status:** ⚠️ Untested in v4.0

Python script that creates Graphviz diagrams for visualizing the energy system network.

**Basic usage** - View the full energy system map:
```bash
uv run python temoa/data_processing/make_graphviz.py -i data_files/temoa_utopia.sqlite
```

**Advanced usage** - Capacitated flow graph for a specific period:
```bash
uv run python temoa/data_processing/make_graphviz.py \
  -i data_files/temoa_utopia.sqlite \
  -r utopia \
  -s scenario_name \
  -c \
  -y 2010
```

**Options:**
- `-i` : Input database file path
- `-r` : Region name
- `-s` : Scenario name
- `-c` : Include capacity information
- `-y` : Specific year to visualize

For all available options:
```bash
uv run python temoa/data_processing/make_graphviz.py --help
```

## Output Files

The scripts generate output files in the current directory or a specified output location. Graphviz creates both:
- **SVG/PNG files** - Viewable images of the network
- **DOT files** - Source files for Graphviz (useful for debugging and archiving)

## Environment Setup

These tools are included in the main Temoa installation. If you're working from the repository:

```bash
uv sync --all-extras
```

This ensures all required dependencies (pandas, graphviz, xlsxwriter, etc.) are installed.
