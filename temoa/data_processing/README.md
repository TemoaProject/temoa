# Overview

This folder contains files used to manage Temoa output data processing
> **⚠️ Note:** These tools have not been fully tested with Temoa v4.0. They may require updates or fixes. Please report any issues on [GitHub Issues](https://github.com/TemoaProject/temoa/issues).

## Available Tools

### 1. `db_to_excel.py`

**Status:** ⚠️ Untested in v4.0

Python script that queries database output tables to create an Excel file containing scenario-specific results.

**Usage:**

```bash
uv run python temoa/data_processing/db_to_excel.py -i path/to/database.sqlite -s scenario_name
```

