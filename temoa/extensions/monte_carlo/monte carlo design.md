## Overall Framework
### Objectives
- Provide a flexible framework in which user can execute an arbitrary number of structured runs
- Provide a clean interface which encapsulates the settings (or changes/deviations) for each run
- Each run may have a single or multitude of deviations from the base data
- Framework should do the "heavy lifting" to interpret the run settings within the DB context and
make adjustments as necessary
- Framework should record adjustments made to the DB for reporting/verification purposes
### Use Cases
- Primarily for Monte Carlo simulation where the settings for the individual runs represent a
probabilistic draw from a multivariate (or multiple independent) settings with the intent of
characterizing the related distribution of outcomes
- Alternatively, a space-filling design may be employed to do sensitivity analysis
### General Approach
1. Construct an inputs `csv` file that represents the deviations for each run.  The structure and
options for this file are described _______.
2. Make a `config.toml` file that employs the `monte_carlo` options and `MONTE_CARLO` mode to
point to this file and the related database
3. Run the model
4. Inspect the log file for warnings

### Design Decisions
- Allow individual lines in the settings `csv` to use either
  - explicit index matching
  - multiple explicit option combinations
  - wildcard characters
- Individual lines can then spawn an arbitrary number of elemental corrections
- Allow adjustments of 3 types for versatility:
  - relative change
  - absolute change
  - direct substitution of value
- Multiple lines can be used to describe an individual run
- Employ worker functionality similar to MGA.  Within the temoa extensions, there are 2 types of
parallel processing employed.  First, Method of Morris employs `joblib`'s parallel functionality.
MGA on the other hand, employs a fully-developed multiprocessing environment with custom workers.
- The advantages of `joblib` are:
  - relatively straightforward to implement and catch results
  - can pass in a thread-safe queue to capture log entries as is done in MM.
- The disadvantages of `joblib` (relative to some of the Temoa goals) are:
  - within the called function, we need to repeatedly re-spin-up a solver and db connection,
  if either are desired (no persistence in the process).
  - it is near impossible to catch "large results" like a solved model.  In MM, only small data
  is returned, in MC, we are probably going to return a full model and inspect/write to the DB
  from it.  We *might* be able to do that within the called function, but that would imply
  opening/closing a new DB connection for each run with `num_cores` possible simultaneous
  connections.
