### Using MGA

It is likely helpful to read the `MGA Design.md` file in this directory that describes some of the terms/
analytic approach to MGA.  MGA uses multi-processing to iteratively explore near-optimal solutions.

#### Outputs

- The processing of results is left to the modeler and the results from runs are tagged iteratively in the Output
tables in the database.
- Running MGA analysis also adds an additional `output_flow_out_summary` table which
summarizes flows at the period level (summarizing time of day and season) to manage the size of the output for
larger models

#### Setup

- The Config file options
  - cost_epsilon:  The proportion to relax the minimal cost by to enable exploration
  - iteration_limit:  The max iterations to run.  Note:  Currently the process will run until either the
    iteration limit OR time limit is reached.  If using hull expansion as the weighting scheme (default), realize
    that "the magic" of that doesn't start until the hull is built which takes 2x |categories| solves to produce.
  - time_limit_hrs:  Self explanatory.  A backstop for long runs
  - axis:  The type of manager to use.  Only `tech_category_activity` is currently implemented
  - weighting:  The type of weighting to use by the manager
- The `MGA_solver_options.toml` file
  - Contains solver settings to optimize performance.  These settings are used *after* the first solve, which sets
  the optimized cost.  The "worker" solvers consume and use any options for the chosen solver from this file
  - Contains the number of workers setting.  Some balance must be considered between hardware resources and
  concurrency.  Six (the current setting) seems an OK balance...
    - Large models consume fairly large memory footprint.  It is possible to have `num_workers` + 2 models floating
    around either in solve, or waiting.
    - The number of workers should be balanced with number of cores per solve (if solver accepts that).  For example,
    with 6 workers and 20 threads/solve, this is a nice fit on 132 core servers, with a bit of slop.
