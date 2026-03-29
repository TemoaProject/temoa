

===========
Quick Start
===========

Installing Software Elements
----------------------------

Temoa is implemented in `Pyomo <https://www.pyomo.org/>`_, which is in turn
written in `Python <http://www.python.org/>`_. Consequently, Temoa will run on
Linux, Mac, Windows, or any operating system that Pyomo supports. There are
several open source software elements required to run Temoa.

**Using pip**:

The standard way to install Temoa:

First, it is highly recommended to use a Python virtual environment to manage dependencies:

.. parsed-literal::
  $ python -m venv temoa_env
  $ source temoa_env/bin/activate

Then, install Temoa:

.. parsed-literal::
  # Install from PyPI
  $ pip install temoa

  # Get started
  $ python -m temoa tutorial my_first_model
  $ python -m temoa run my_first_model.toml

**Using uv (Alternative)**:

For faster dependency resolution:

.. parsed-literal::
  # Install uv
  $ curl -LsSf https://astral.sh/uv/install.sh | sh

  # Create a uv initialized virtual environment
  $ uv init <dir_name>
  $ cd <dir_name>

  # add Temoa from PyPI to pyproject.toml
  $ uv add temoa

  # Get started
  $ uv run temoa tutorial my_first_model
  $ uv run temoa run my_first_model.toml

**For Contributors (Development Installation)**:

If you want to contribute to Temoa or modify the code:

.. parsed-literal::
  # Clone the repository
  $ git clone https://github.com/TemoaProject/temoa.git
  $ cd temoa

  # Install in development mode with uv (recommended)
  $ uv sync --all-extras --dev

  # Install pre-commit hooks
  $ uv run pre-commit install

For detailed contribution guidelines, see CONTRIBUTING.md in the repository.

Solvers
-------

A few notes for on the choice of solvers. Different solvers
have widely varying solution times. If you plan to run Temoa with large datasets
and/or conduct uncertainty analysis, you may want to consider installing
commercial linear solvers such as `CPLEX
<https://www.ibm.com/analytics/cplex-optimizer>`_ or `Gurobi
<https://www.gurobi.com/>`_. Both offer free academic licenses.

For smaller models, Temoa has been tested with the `HiGHS <https://pypi.org/project/highspy/>`_
solver. HiGHS is automatically available when you install Temoa and requires no additional setup.


Running Temoa
-------------

To run the model, a configuration (``config``) file is needed. An
example config file called :code:`config_sample.toml` resides within the
:code:`data_files/my_configs` folder. Running the model with a config file allows
the user to (1) use a sqlite database for storing input and output data, (2)
create a formatted Excel output file, (2) specify the solver to use, (3) return
the log file produced during model execution, (4) return the lp file utilized by
the solver, and (5) to execute several of the modeling extensions.

.. parsed-literal::
  $ temoa run config.toml

**For general help, use --help:**

.. parsed-literal::
  $ **temoa --help**
    usage: temoa [-h] [--version] [--how-to-cite] COMMAND ...

    Tools for Energy Model Optimization and Analysis (Temoa)

    options:
      -h, --help       show this help message and exit
      --version        Show version information
      --how-to-cite    Show citation information

    commands:
      COMMAND
        run            Run a Temoa model
        validate       Validate a configuration file
        check-units    Check unit consistency in a database
        migrate        Migrate a database to the latest schema
        tutorial       Create tutorial files

..
    dated references, preserved as comment here:

    To supplement this documentation, we have also created a
    `YouTube video tutorial <https://youtu.be/WtzCrroAXnQ>` that explains
    how to run Temoa from the command line. There is also an option to run
    `Temoa on the cloud <https://model.temoacloud.com>`, which
    is explained in `this video tutorial <https://youtu.be/fxYO_kIs364>`.
