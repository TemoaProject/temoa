# Method of Morris

### This document gives a _brief_ description of MM application and shows how to execute the provided example

## Background

- MM is a Sensitivity Analysis (SA) technique that uses a unique Design Of Experiments (DOE) application to
explore the input space.
- The MM techniques in Temoa utilize `SALib` which has fairly
thorough [documentation](https://salib.readthedocs.io/en/latest/api.html#method-of-morris) online,
which also refers to relevant studies.

## Use

- The current MM setup in Temoa is capable of exploring input parameters from 3 tables:
  - cost_variable
  - cost_invest
  - efficiency
- The MM application will analyze effects of marked parameters (or groups) on the cost function
(objective) and on co2 emissions specifically.
  - It should be noted that co2 is _not_ optimized in any way, it is just the co2 emission
  for the optimal cost solution
  - Further, the code is currently hard-coded to look for _exactly_ the string `co2` in the
  `output_emissions` table.  It is highly advisable to do a "regular" run on the data to ensure
  that `co2` is properly represented in the commodity and output tables.

- The basic sequence is:  marking of input parameters (by user) and domains (through the `perturbation`
value in the `config`) -> make a MM Sample set -> run Temoa on the samples -> conduct MM analysis.
- In order to use MM in Temoa, the subject database needs to be augmented slightly to allow
relevant parameters to be marked for analysis.
- After Parameters are marked with group labels, the `morris` options should be set in the
relevant `config.toml` file which can then be run.
- Outputs are stored in the standard time-stamped output folder.

### Example:  `morris_utopia`

1. Convert the `.sql` file in the `example_dbs` folder back to a database:

`data_files/example_dbs % sqlite3 morris_utopia.sqlite < morris_utopia.sql`

2. Observe the markings (3 groups) in the `MMAnalysis` columns in `cost_variable` and `efficiency`.
3. Observe the `morris` configuration comments in the corresponding `morris_utopia.toml` file in `my_configs`.
4. Run the config as normal.
5. MM analysis is reported on screen and in 2 csv files for the objective and `co2` in the Outputs folder
6. The DB will contain updated values (tagged by scenario name and "dash run") in `output_objective` and `output_emissions`
_only_ which might be of secondary value to the modeler.  Other output tables are _not_ updated.

### Preparing Other Databases (or modifying `morris_utopia`)

1. Augment all 3 of the tables (`cost_invest`, `cost_invest`, `efficiency`) with a column (field) `MMAnalysis`
that is `TEXT` data type, allowing NULL.
2. Add labels within that column for analysis.  Note:
   - Labels that are repeated (in any table) are treated as a "Group" for MM purposes.
   - Labels that are used singly are a "group of 1".
   - The number of runs will be:  `(GROUPS + 1) x N` where `N` is the number of trajectories in the `config`.
   - Note:  number runs is _independent_ of the total params marked (groups can be large and are varied together)
   - The modeler need to consider how to group multiple vintages/periods for specific techs and/or group
   related techs.
3. The modeler should consider the architecture used to run the model for cpu utilization.  The number of
cores to use is selectable in the `config` for parallel use.  A `0` can be used to utilize all available cores
in parallel, which may cause memory issues for large models, requiring a "reasonable" lesser selection of `cores` in
the `config`.  For "smaller" models, let 'er rip and use all cores.  ;)
