

Installing Software Elements
----------------------------

Temoa is implemented in `Pyomo <https://www.pyomo.org/>`_, which is in turn
written in `Python <http://www.python.org/>`_. Consequently, Temoa will run on
Linux, Mac, Windows, or any operating system that Pyomo supports. There are
several open source software elements required to run Temoa.

**Using pip (Recommended for most users)**:

The standard way to install Temoa:

.. parsed-literal::
  # Install from PyPI (when 4.0 is released)
  $ pip install temoa

  # Or install from nightlies (alpha/development versions)
  $ pip install --index-url https://temoaproject.github.io/temoa-nightlies/simple/ temoa --extra-index-url https://pypi.org/simple/

  # Get started
  $ temoa tutorial my_first_model
  $ temoa run my_first_model.toml

**Using uv (Alternative)**:

For faster dependency resolution:

.. parsed-literal::
  # Install uv
  $ curl -LsSf https://astral.sh/uv/install.sh | sh

  # Install Temoa from nightlies
  $ uv pip install --index-url https://temoaproject.github.io/temoa-nightlies/simple/ temoa --extra-index-url https://pypi.org/simple/

  # Get started
  $ temoa tutorial my_first_model
  $ temoa run my_first_model.toml

**For Contributors (Development Installation)**:

If you want to contribute to Temoa or modify the code:

.. parsed-literal::
  # Clone the repository
  $ git clone https://github.com/TemoaProject/temoa.git
  $ cd temoa

  # Install in development mode with uv (recommended)
  $ uv sync --all-extras --dev

  # Or with pip
  $ pip install -e ".[docs,plotting]"

For detailed contribution guidelines, see CONTRIBUTING.md in the repository.

Solvers
-------

A few notes for on the choice of solvers. Different solvers
have widely varying solution times. If you plan to run Temoa with large datasets
and/or conduct uncertainty analysis, you may want to consider installing
commercial linear solvers such as `CPLEX
<https://www.ibm.com/analytics/cplex-optimizer>`_ or `Gurobi
<https://www.gurobi.com/>`_. Both offer free academic licenses.

For smaller models, Temoa has been tested with both the `CBC <https://github.com/coin-or/Cbc>`_
solver and the more recently released `HiGHS <https://pypi.org/project/highspy/>`_ solver.
Each of the respective websites contains installation instructions for the individual
solvers.  For those wishing to run the internal tests on Temoa, the :code:`CBC` solver
is required.

There are three ways to run the model, each of which is detailed below. Note that
the example commands utilize 'temoa_utopia', a commonly used test case for ESOMs.

Obtaining Temoa
---------------

Now that you have functioning environment, you need to obtain the source code
for Temoa. There are a couple of options for obtaining and running Temoa from
GitHub. If you want to simply run the model, you can download Temoa from GitHub
as a zip file. Navigate to our `Github repo <https://github.com/TemoaProject/temoa>`__,
and click the green ‘clone or download’ button near the top-right corner. Select
‘Download ZIP,’ and you can download the entire Temoa :code:`main` (our main branch)
to your local machine. The second option creates a local copy of the model source
code in our GitHub repository. This is a two step process: first install git and
then ‘clone’ the repository. Under Linux, git can be installed through the default
package manager. Git for Windows and Mac can be downloaded from the `Git website
<https://git-scm.com/download/>`_. To clone the Temoa repository, navigate to
the directory where you want the model to reside and type the following from the
prompt:

.. parsed-literal::
  $ git clone https://github.com/TemoaProject/temoa/

Note that cloning the repository will supply the latest version of the code, and
allow you to archive changes to the code and data in your own local git
repository.

A few basic input data files are included in the :code:`temoa/data_files`` folder.
Additional Temoa-compatible datasets are available in `this separate GitHub
repo <https://github.com/TemoaProject/data>`_.

The installation procedures above are meant to be generic and should work across
different platforms. Nonetheless, system-specific ambiguities and unexpected
conditions inevitably arise. Please use
`GitHub Issues <https://github.com/TemoaProject/temoa/issues>`_ to ask for help.

Running Temoa
-------------

To run the model, a configuration (‘config’) file is needed. An
example config file called :code:`config_sample.toml` resides within the
:code:`data_files/my_configs` folder. Running the model with a config file allows
the user to (1) use a sqlite
database for storing input and output data, (2) create a formatted Excel output
file, (2) specify the solver to use, (3) return the log file produced during
model execution, (4) return the lp file utilized by the solver, and (5) to
execute several of the modeling extensions.

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
        migrate        Migrate a database to the latest schema
        tutorial       Create tutorial files

..
    dated references, preserved as comment here:

    To supplement this documentation, we have also created a
    `YouTube video tutorial <https://youtu.be/WtzCrroAXnQ>` that explains
    how to run Temoa from the command line. There is also an option to run
    `Temoa on the cloud <https://model.temoacloud.com>`, which
    is explained in `this video tutorial <https://youtu.be/fxYO_kIs364>`.

====================================
Database Construction
====================================

Input datasets in Temoa can be constructed either as text files or relational
databases. Input text files are referred to as 'DAT' files and follow a specific
format. Take a look at the example DAT files in the :code:`temoa/data_files`
directory.

While DAT files work fine for small datasets, relational databases are preferred
for larger datasets. To first order, you can think of a database as a collection
of tables, where a 'primary key' within each table defines a unique entry (i.e.,
row) within the table. In addition, a 'foreign key' defines a table element drawn
from another table. Foreign keys enforce the defined relationships between
different sets and parameters.

Temoa uses `sqlite`_, a widely used, self-contained database
system. Building a database first requires constructing a sql file, which is
simply a text file that defines the structure of different database tables and
includes the input data. The snippet below is from the technology table used to
define the 'temoa_utopia' dataset:

**NOTE**:  *As of Version 3, the below table format is dated, but still shows the general structure of
the SQL files used to create the database.*

.. parsed-literal::
  CREATE TABLE technologies (
  tech text primary key,
  flag text,
  sector text,
  tech_desc text,
  tech_category text,
  FOREIGN KEY(flag) REFERENCES technology_labels(tech_labels),
  FOREIGN KEY(sector) REFERENCES sector_labels(sector));
  INSERT INTO "technologies" VALUES('IMPDSL1','r','supply',' imported diesel','petroleum');
  INSERT INTO "technologies" VALUES('IMPGSL1','r','supply',' imported gasoline','petroleum');
  INSERT INTO "technologies" VALUES('IMPHCO1','r','supply',' imported coal','coal');

The first line creates the table. **Lines 2-6** define the columns within this table.
Note that the the technology ('tech') name defines the primary key. Therefore, the
same technology name cannot be entered twice; each technology name must be unique.
**Lines 7-8** define foreign keys within the table. For example, each technology
should be specified with a label (e.g., 'r' for 'resource'). Those labels must
come from the 'technology_labels' table. Likewise, the sector name must be defined
in the 'sector_labels' table. This enforcement of names across tables using
foreign keys helps immediately catch typos. (As you can imagine, typos happen in
plain text files and Excel when defining thousands of rows of data.) Another big
advantage of using databases is that the model run outputs are stored in
separate database output tables. The outputs by model run are indexed by a scenario name,
which makes it possible to perform thousands of runs, programatically store all
the results, and execute arbitrary queries that instantaneously return the requested
data.

Because some database table elements serve as foreign keys in other tables, we
recommend that you populate input tables in the following order:

**Group 1: labels used for internal database processing**
  * commodity_type: Need to identify which type of commodity. Do NOT change these abbreviations.
  * technology_type: Need to identify which type of technology. Do NOT change these abbreviations.  Categorizing
    and sub-categorizing can be done in the Technology table itself.
  * time_period_type: Used to distinguish which time periods are simply used to specify pre-existing
    vintages and which represent future optimization periods.
  * season_label: Unordered unique labels defining seasons in the model.


**Group 2: sets used within Temoa**
  * Commodity: list of commodities used within the database
  * Technology: list of technologies used within the database
  * time_period: list of both past and future time periods considered in the database
  * time_season: seasons modeled in the database
  * time_of_day: time of day segments modeled in the database


**Group 3: parameters used to define processes within Temoa**
  * metadata_real (global_discount_rate)
  * metadata (days_per_period)
  * Demand
  * demand_specific_distribution
  * efficiency
  * existing_capacity
  * capacity_factor
  * capacity_factor_process (only if CF varies by vintage; overwrites capacity_factor)
  * capacity_to_activity
  * cost_fixed
  * cost_invest
  * cost_variable
  * emission_activity
  * lifetime_tech
  * lifetime_process (only if LT varies by vintage; overwrites lifetime_tech)
  * time_segment_fraction: proportion of each period represented by each time slice

**Group 4: parameters used to define constraints within Temoa**
  * limit_activity
  * limit_capacity
  * limit_emission
  * limit_growth_capacity
  * limit_new_capacity
  * limit_resource
  * limit_tech_input_split
  * limit_tech_output_split

For help getting started, take a look at how :code:`data_files/temoa_utopia.sql` is
constructed. Use :code:`data_files/temoa_schema.sql` (a database file with the requisite
structure but no data added) to begin building your own database file. We recommend
leaving the database structure intact, and simply adding data to the schema file, or
constructing an empty database from the schema file and then using a database editor
to import data.
Once the sql file is complete, you can convert it into a binary sqlite file by
installing sqlite3 and executing the following command:

.. parsed-literal::
  $ sqlite3 my_database.sqlite < my_database.sql

Now you can specify this database as the source for both input and output data
in the config file.

============
Data Quality
============

In addition to numerous internal checks, Temoa (optionally) employs two quality checks on
data read in from the database.  The outputs (actions and warnings) generated by these processes
are reported in the log file for the run.

Both of the checks below can be run to QA data by running the model in `CHECK` mode and inspecting
the log file.  During `CHECK` mode runs, no solve is attempted on the model.

Price Checking
--------------
The "price checker" reviews cost data in the 3 cost tables and considers technology lifetime.  It
screens for possible inconsistencies that would corrupt output quality.  Larger models may have
well over 100K cost entries and an overlooked investment cost for a particular vintage tech in
a particular region could easily be overlooked.  Price checks performed/reported:

1. **Missing Costs (Check 0)**:  This check looks for technologies that have no fixed/invest/variable
   costs at all.  Other checks are more discriminating, so this check is only reported when Temoa is run
   in `debug` mode by using the `-d` flag on the run command.
2. **Missing Fixed/Investment Costs (Check 1a)**:  This check identifies technologies that are *not*
   flagged as `uncapacitated` with neither a fixed or investment cost associated.  These *might* be
   problematic for solve because the model minimizes cost, so capacity in these technologies would be
   free.  `uncapacitated` technologies have no capacity measure, so fixed/investment costs are prohibited
   for them and that is checked elsewhere.
3. **Inconsistent Fixed/Investment Cost (Check 1b)**:  This check looks for inconsistent application
   of fixed or base costs in the "base" or vintage year across all vintages and regions.  So, if a tech has
   a fixed cost in some particular region and vintage year, but not in all, it will be flagged as a likely
   omission.
4. **Inconsistent Fixed & Variable Costs (Check 2)**:  This check identifies techs that have
   inconsistencies in the application of fixed - variable costs.  Techs that have *any* fixed cost for
   a particular [region, tech, vintage] process, but do not have entries that match the variable cost
   entries for the same process are flagged, and vice-versa.  This would hopefully identify an
   accidental omission of some of the fixed/var costs for processes that have at least 1 entry for either.
5. **Lifetime Costing (Check 3)**:  This check identifies costs that fall short or are missing
   during the process's lifetime.  If a process has a variable cost in *any* year during the lifetime, but
   not all years, it is flagged.  Same for fixed cost.
6. **Uncapacitated Tech Costs**:  Any technology flagged as `uncapacitated` will trigger warnings here
   if it has any fixed/invest costs.

Source Tracing
--------------

Temoa works backwards from demands to identify chains of technologies required to meet the demand.
Source Tracing is designed to ensure that this backward tracing from demands describes a proper
commodity network without gaps that might allow intermediate commodities to be treated as a free
"source" commodity.  Further description of possible network problems is included in the
`commodity network notes.md` file in the `docs` folder.

Source Tracing pre-builds the entire commodity network in each region-period contained in the
data and analyzes it for "orphans" which likely represent gaps in the network that would lead
to erroneous output data.  The operation is enabled by tagging foundational commodities for which
there are no predecessors as "source" commodities in the `Commodity` database table with an `s` tag.
Orphans (or chains of orphans) on either the demand or supply side are reported and *suppressed* in
the data to prevent network corruption.

Note that the myopic mode *requires* the use of Source Tracing to ensure accuracy as some orphans
may be produced by endogenous decisions in myopic runs.

Commodity Network Visualization
-------------------------------
The output of the Source Tracing operation can be visualized by enabling the commodity network plots
in the config file.  This will add a set of region-period specific html files to the Outputs folder.
These files *should* be open-able in any web browser.  (See the note in the main `README.md` for trouble
with Windows OS systems).

.. Figure:: images/utopia_commodity_network.png
   :align: center
   :figclass: center
   :figwidth: 60%

   An example of the Commodity Network for Utopia (interactive view in web browser by opening
   the generated html file)

The color legend for Commodity Networks is as follows:

* Green dot:  Source Commodity
* Orange dot:  Demand Commodity
* Violet dot:  Intermediate Commodity
* Black arc:  Technology
* Blue arc:  Linked Technology (the driven tech, *not* the driver)
* Yellow arc:  Supply-Side Orphan (shown, but suppressed when model built)
* Red arc:  Demand-Side Orphan (shown, but suppressed when model built)
* Green arc:  Any Tech with a Negative Variable Cost

=============
