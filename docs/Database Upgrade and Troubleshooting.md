# Updating to Version 3 and Troubleshooting Legacy Databases

## Background

The upgrades in Version 3 of the Temoa codebase include much tighter scrutiny of the commodity network
via source tracing.  Source tracing is optional in some modes, but mandatory in Myopic mode.  The goal
of source tracing is to ensure the network of commodities is performing properly and not allowing
artificial sources of commodities to enter the network.  Additional details on this process are in
the `commodity network notes.md` file.

The complexity of some of the larger databases and networks and the actions of source tracing can
pose challenges in troubleshooting models that are infeasible or unbounded.  This set of notes
is intended to help modelers working with new large datasets or transitioned datasets in
working through infeasibilities and "getting the model breathing" so that refinements can be made.

## First steps

After using the version 3 updating python module (described in the top level `README.md` file) to transition a database to V3 compatibility, the
following **must** be done to get the model working.

1. Mark Source Commodities.  In the `Commodity` table, source commodities must be marked with
an "s" for the flag value.  This action identifies them as bedrock sources that serve as
sources for network analysis.  Things like "Ethos" are typically sources.  A source commodity
is interpreted as a freely available starting commodity that has no predecessors.  Multiple
sources are possible for bookkeeping or model clarity.
2. Identify Unlimited Capacity Technologies.  The `Technology` table has a new field labeled
`unlim_cap` to identify technologies that have no capacity limit.  This may represent things
like imports or use taxes or other notions that don't logically support a capacity
determination/assignment.  Assigning technologies to this category does several things.
First, it makes the model smaller and more flexible because capacity variables are
excluded for the technology, although activity is still an active variable.  It also
enables modes like Myopic to function more cleanly because the model does not make
capacity decisions on things that may need to be revised with higher demands in later
periods.  Unlimited capacity technologies may still have a lifetime and variable costs
but may not have the capacity-related investment and fixed costs.
3. Run the model in `Check` mode.  Doing this will run source tracing and price checking
on the model in its full form (everything in visibility).  Problems noted by `WARNING` in
the log file should be addressed.

## Troubleshooting

If the model does not solve after the steps above the following are possible actions to take.
Note that several of these involve altering the model code and should be done carefully.
A suggested approach for items that involve injecting or commenting out code is to try them,
make corrections as needed to the data, and then use Git's `rollback` feature on the
core model code to undo any "hacks" or patches that were used.  In no particular order:

- If the model is unbounded.  Look at negative cost items carefully.  A technique to
limit runaway activity is to limit all flows in the model.  The following code can
be slipped in to the `temoa_model.py` code anywhere in the constraint section.  It
will limit **all** flows to an upper bound.  If using this approach, the
modeler should also limit any arbitrarily large demands in the
demand table that may need to be revised downward in conjuction with this limit.
The `output_flow_out` table can then be inspected for unusually high activity.

```
@M.Constraint(M.flow_var_rpsditvo)
def flow_max(M, *rpsditvo):
    return M.v_flow_out[rpsditvo] <= 10_000_000
```

- Double check that items in the first period that should be marked as `unlim_capacity`
are correctly marked.  Older datasets tended to have imports and such only listed in
the first period.  The following query can be used, possibly with small modifications
to identify unique items in the first optimization period that should be reviewed.
Of note in this example, 2020 is the first optimization period:

```
-- technologies unique to first period
SELECT t.tech, unlim_cap
FROM Technology t
         LEFT OUTER JOIN (SELECT DISTINCT e.tech FROM efficiency e WHERE e.vintage != 2020) AS base
                         ON t.tech = base.tech
WHERE base.tech IS NULL;
```

- Selectively omit parameters that force or limit activity.  This can be done rather
easily by commenting out the read-in process for parameter data in `hybrid_loader.py`.
It should be possible to search for the table name and then just comment out the
entire block that reads in that table.  Much easier than manipulating the database.
Consideration for excluding min_activity, max_activity, EmissionLimit, etc. is
suggested.
