Notes on Myopic
===============

myopic_efficiency Table
----------------

- Largely similar to baseline efficiency table
- Built sequentially during myopic run from capacity built, not built, or retired in previous period.  This table
needs to be "actively maintained" during the run because it is the source of filtering for all other model elements.
  - Notable actions:
    - Items NOT built in previous myopic windows are removed in the subsequent iteration.  During normal model runs,
    the model will add entries from the normal efficiency tables for consideration, and then in the subsequent
    iteration, it will houseclean and remove any that were not selected for build.
    - Items that become fully retired *during their normal lifespan* are also deleted upon retirement.
- Uses base-year field (column) as reference to when added, and ``-1`` indicates original existing capacity
- Adds a computed Lifetime field, which is handy for future computations and used internally to screen active
technologies during data loading.
