# Getting Started with TEMOA Version 4.0.0a1

## Overview

TEMOA (Tools for Energy Model Optimization and Analysis) is a sophisticated energy systems optimization framework that supports various modeling approaches including perfect foresight, myopic planning, uncertainty analysis, and alternative generation.

### Package Structure

The main subdirectories in the project are:

1. **`temoa/`** - Main package directory
   - **`temoa.core`** - Public API for end users (TemoaModel, TemoaConfig, TemoaMode)
   - **`temoa._internal`** - Private implementation modules (not for public use)
   - **`temoa.data_processing`** - Post-processing and output utilities
   - **`temoa.extensions`** - Optional extensions for different modeling approaches
   - **`temoa.utilities`** - Helper scripts and database utilities
   - **`temoa.model_checking`** - Model validation and integrity checking

2. **`data_files/`** - Input data files and configuration examples
3. **`tests/`** - Comprehensive test suite
4. **`docs/`** - Documentation source files
5. **`notebooks/`** - Jupyter notebooks for analysis and examples

### Installation

TEMOA can be installed as a pip package:

```bash
pip install -e .
```

Or using the provided requirements file:

```bash
pip install -r requirements.txt
```

## Guide to Setup

1. Obtain a current copy of Python from the python.org website.  The model has been tested with 3.11 and 3.12.  It will
fail (raise error) on earlier versions.
2. A `requirements.txt` file has been included to allow for use of `pip` to populate a virtual environment.  In order to use that the steps are:

- Ensure you have a copy of python 3.11/3.12 installed on your machine ([python.org](https://www.python.org))
- Make and activate a virtual environment using the `venv` package:

```
python3.11 -m venv venv
source venv/bin/activate   # for linux/osx, windows activation command may differ
```

- Verify that you have a prepended indicator on your cursor that you are in the virtual environment (see below)
- After activating the venv, use `pip` *within* the venv to install everything.  Most IDEs have automated tools to
help set up and associate this venv with the project.  It is also possible from the command line:

```
(venv) $ pip install -r requirements.txt
```

- For Conda users, an environment.yml file is provided that is not currently fully tested.  Additional installs may
be required.

3. **Usage as a Library**: Import and use TEMOA programmatically:

```python
import temoa
from temoa import TemoaModel, TemoaConfig, TemoaMode

# Create configuration
config = TemoaConfig(
    scenario="my_scenario",
    scenario_mode=TemoaMode.PERFECT_FORESIGHT,
    input_database="path/to/input.db",
    output_database="path/to/output.db",
    output_path="path/to/output",
    solver_name="gurobi"
)

# Build and solve model
model = TemoaModel()
# ... (additional usage)
```

4. **Command Line Usage**: Use the main entry point:

```bash
python -m temoa --config data_files/my_configs/config_sample.toml
```

## Database Setup

- Several sample database files in Version 3 format are provided in SQL format for learning/testing.  These are provided in the
`data_files/example_dbs` folder.  In order to use them, they must be converted into sqlite database files.  This can
be done from the command line using the sqlite3 engine to convert them.  sqlite3 is packaged with Python and should be
available.  If not, most configuration managers should be able to install it.  The command to make the `.sqlite` file
is (for Utopia as an example):

```
(venv) $ sqlite3 utopia.sqlite < utopia.sql
```

- Converting legacy db's to Version 3 can be done with the included database migration tool.  Users who use this
tool are advised to carefully review the console outputs during conversion to ensure accuracy and check the
converted database carefully.  The migration tool will build an empty new Version 3 database and move data from
the old database, preserving the legacy database in place.  The command can be run from the top level of the
project and needs pointers to the target database and the Version 3 schema file.  A typical execution from top level
should look like:

```bash
python -m temoa.utilities.db_migration_to_v3 --source data_files/<legacy db>.sqlite --schema data_files/temoa_schema_v3.sql
```

- Users may also create a blank full or minimal version of the database from the two schema files in the `data_files`
directory as described above using the `sqlite3` command.  The "minimal" version excludes some of the group
parameters and is recommended as a starting point for entry-level models.  It can be upgraded to the full set of
tables by executing the full schema SQL command on the resulting database later, which will add the missing tables.

## Config Files

- A configuration (config) file is required to run the model.  The `sample_config.toml` is provided as a reference
and has all parameters in it.  It can be copied/renamed, etc.
- Notes on Config Options:

| Field                  | Notes                                                                                                      |
|------------------------|------------------------------------------------------------------------------------------------------------|
| Scenario Name          | A name used in output tables for results (cannot contain dash '-' symbol)                                  |
| Temoa Mode             | The execution mode.  See note below on currently supported modes                                           |
| Input/Output DB        | The source (and optionally diffent) output database.  Note for myopic, MGA input must be same as output    |
| Price Checking         | Run the "price checker" on the built model to look for costing deficiencies and log them                   |
| Source Tracing         | Check the integrity of the commodity flow network in every region-period combination.  Required for Myopic |
| Plot Commodity Network | Produce HTML (viewable in any browser) displays of the networks built (see note at bottom)                 |
| Solver                 | The exact name of the solver executable to call                                                            |
| Save Excel             | Save core output data to excel files.  Needed if user intends to use the graphviz post-processing modules  |
| Save LP                | Save the created LP model files                                                                            |
| Save Duals             | Save the values of the Dual Variables in the Output Tables.  (Only supported by some solvers)              |
| Mode Specific Settings | See the README files within mode folders for up-to-date values                                             |

## Currently Supported Modes

### Check

Build the model and run the numerous checks on it.  Results will be in the log file.  No solve is attempted.
Note:  The LP file for the model can be saved with this option and solved later/independently by selecting
the ``save_lp_file`` option in the config.

### Perfect Foresight

All-in-one run that solves the entire model at once.  It is possible to run this without source tracing, which will
use raw data in the model without checking the integrity of the underlying network.  It is highly advised to use
source tracing for most accurate results.

### Myopic

Solve the model sequentially through iterative solves based on Myopic settings.  Source tracing is required to
accommodate build/no-build decisions made per iteration to ensure follow-on models are well built.

### MGA (Modeling to Generate Alternatives)

An iterative solving process to explore near cost-optimal solutions.  See the documentation on this mode.

### SVMGA (Single Vector MGA)

A sequence of 2 model solves that establishes a base optimal cost, then relaxes the cost then minimizes an
alternate unweighted objective function comprised of variables associated with labels selected in lists in the
config file.

### Method of Morris

A limited sensitivity analysis of user-selected variables using a Method of Morris approach.  See the documentation
on this mode.

### Build Only

Mostly for test/troubleshooting.  This builds/returns an un-solved model.

Several other options are possible to pass to the main execution command including changing the logging level to
`debug` or running silent (no console feedback) which may be best for server runs.  Also, redirecting the output
products is possible.  To see available options invoke the `main.py` file with the `-h` flag:

```bash
python -m temoa --help
```

## Typical Run

1. Prepare a database (or copy of one) as described above.  Runs will fill the output tables and overwrite any data with the
same scenario name.
2. Perepare a config file with paths to the database(s) relative to the top of the project, as in the example
3. Run the model using the module entry point:

```bash
python -m temoa --config data_files/my_configs/config_sample.toml
```

4. Review the config display and accept
5. Review the log file and output products which are automatically placed in a time-stamped folder in `output_files`,
unless user has redirected output
6. Review the data in the Output tables

## Testing

Users who wish to exercise the `pytest` based test in the test folder can do so from the command line or any IDE.
Note that many of the tests perform solves on small models using the freely available `cbc` solver, which is
required to run the testing suite.

The tests should all run and pass (several are currently skipped and reflect in-process work).  Tests should normally
be run from the top level of the `tests folder`.  If `pytest` is installed it will locate tests within the folder and
run/report them.  Note the dot '.' below indicating current folder:

```bash
python -m pytest tests/
```

Several of the packages used may currently generate warnings during this testing process, but the tests should all PASS
with the exception of skipped tests.

## Documentation and Additional Information

The full Temoa documentation can be built by following the build README file in the Documentation folder.

## Hot Fix for Network Plots on Windows Machines

Users wishing to utilize the feature to make the html network plots of the energy network using the
`plot_commodity_network` option in the config file who are working on Windows Operating System may need to make a
"hot fix" to the library code.  See note here:  <https://github.com/robert-haas/gravis/issues/10>

The `gravis` library which nicely makes these plots appears to currently be non-maintained and a 1-line fix is
likely needed to avoid error on Windows machines:

1. Within the `venv` that contains project dependencies, navigate to the `gravis` folder
2. Open the file `gravis/_internal/plotting/data_structures.py` and edit line 120 to include the encoding flag:

    `with open(filepath, 'w', encoding='utf-8') as file_handle:`

## Hot Fix for Graphviz

Users wishing to utilize the `graphviz` package to visualize results as described in the `README.md` file
in the `data_processing` package/folder may need to re-install `graphviz` using another delivery means
other than `pip`.  The current `requirements.txt` will attempt to install `graphviz`, but according to
their project page, this needs to be done with another configuration manager like `apt` or `homebrew`.

Mac users wishing to use `graphviz` should re-install using `homebrew` with the command:

`brew install graphviz`

(Any Windows users who have tips/info on this are asked to submit a PR to this file to update this section.)
