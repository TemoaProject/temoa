
Commodity Network
=================

This documentation segment highlights some of the techniques to maintain the integrity of
the commodity flow network within Temoa.  The modeler is advised to be aware of how
Temoa processes flow of energy within an energy system and how escapes in network
integrity can lead to erroneous results.

Network Flow
------------

In a standard, static, and lossless ``s-t`` network, flow balance constraints fall into
place naturally.  The input flow at the source, ``s`` is set to equal the output flow
at termination point ``t`` and for all intermediary nodes, flow in is constrained to
equal flow out.  Temoa's energy network, however, is not static and has losses in the form
of efficiency losses within the ``tech`` processes that serve as the links between
``commodity`` nodes.  When a model is solved over several time periods with "perfect foresight"
the network may look quite different in each region and time period based on endogenous selections
of new technologies, lifetime expirations, etc.  This diversification of networks is compounded when running the
model myopically where previous non-selections remove options from the decision space in future
periods, outside of the modeler's control.

When developing data for a model to run with perfect foresight, or any of the more advanced modes,
it is incumbent upon the modeler to provide the vintages, technologies, lifespans, etc. in order
to allow Temoa to build a proper network.  Some explanation of how Temoa balances flow is in order
to help avoid pitfalls....

The energy network in each region and period is built dynamically from the `techs` that are
identified as existing capacity and whatever the model has ability to build from elements in
the optimization window identified in the ``efficiency`` table.  In order enforce conservation of
flow constraints, the model identifies output flows (commodities), including the demand
commodities and inventories all possible `techs` (existing or available) that *could* produce that commodity from
any input commodity and enforces flow balance by requiring capacity in one of the available technologies,
so that *some tech* must provide the flow to support that output.
This is the basis for satisfying demands at the termination of the network.

If at any point along the chain there are no `techs`
available to produce the commodity in question, the model *assumes this is a base or source commodity* for
flow balance purposes, which can lead to some intermediate physical commodities erroneously being
provided to the model freely without a preceding processing chain if there is not one avaialbe.
This can inadvertently come about from a variety of causes including:

* Failure to provide a linking technology in any region-period
* A technology that expires in a particular period with no replacement/alternate pathway provided
* Non-selection in a prior myopic period

These failures can be difficult to diagnose in large models with many periods/regions/technologies and serve
as the motivation to provide source-tracing (described in the next section) to help enforce network integrity.

Source Tracing
--------------

Source tracing from Demand back to a labeled "source" capacity is now available in Version 3.0+ of Temoa.
During pre-processing, before the model is built, Temoa can identify breaks in the network and can filter out problematic
data before the model is loaded/built.  Temoa can also check network integrity on a built model before solve is initiated.  Currently,
discrepancies are noted in the log file for the model.  The user can also request network plots, which are browser-capable
html files that can be used in diagnosis of problem areas.  The general intent is to ensure that all flows to Demand
commodities can be cleanly traced back to original sources.

#### An example

Consider the simple network below with one source, one
demand, and intermediate physical commodities ``{P1, P2, P3, P4}`` and the connective technologies ``T1``
through ``T6``.  This well-connected network works as intended and the singular demand is traceable via either path
back to source.

![Good Network](source/images/commodity_network.png)

A defective network (shown below) may occur for a several reasons, as cited in the previous section.  Suppose that
for some reason `T3` is no longer available in this or a subsequent period (never made available, lifetime
expiration earlier than other links, not selected by myopic process--which would normally remove the other links
as well, unless they had replacement vintages and ``T3`` did not, etc.)  Several problems now exist:

1. Supply side orphans.  Technology ``T1`` is now a "supply side" orphan, which shouldn't cause model problems, but represents bloat
in the model.  Legacy (pre version 3.0) Temoa does screen for unused outputs (like ``P1`` in this case) that are not used by other
processes and are not end demands, but it is currently only done 'globally' in all periods/regions.  Resultantly,
this orphan may not trigger a model error if it were used in another region/period.
These will now generate **WARNING** level log entries with source tracing.  It *could* be a source of unbounded behavior in the case where the
modeler attempts to use negative values for costs.

2. Technology ``T5`` and perhaps a now-available new vintage ``T5'`` are now "demand-side" orphans.  These are
problematic and will generate **WARNING** level log entries by source tracing because they would allow a
false/unlimited supply of ``P3`` as their inputs.

3. New technology ``T7`` (and any other linkages that are not reachable from either source or demand)
are complete orphans.
They will generate a **WARNING** level log entry during source tracing.

![Bad Network](source/images/broken_commodity_network.png)

Tech Suppression
---------------

When source tracing is used, Temoa will attempt to remedy network escapes as described above by suppressing
problematic `techs` or chains of technologies.  During runs where source tracing is enabled, Temoa's internal
`Network Data Magager` will preload essential data in order to analyze all networks (each region/period) within the
current optimization window.  Network tracing from demands down and sources up reveals `techs` that are "orphaned"
These `techs` and any unused commodities, etc. are removed with log entries and the remaining "good" data is
used to filter the ingestion of the full model data to support the build.

### Basic rules for `tech` Suppression

- All demand side orphans (and chains of orphans) are suppressed
* All supply-side orphans (and chains of orpahns) are suppressed
* For technologies that have multiple inputs or outputs, EACH commodity is treated separately (as it is
represented in the `efficiency` table.)  The modeler is advised to screen the log file for these entries if a
particular commodity is essential (a catalyst for example?) to a particular operation.
* For linked technologies, an "all or nothing" logic is implemented such that both the driver and driven
technologies must prove independently viable (without regard for the emission linkage) or the pair will be suppressed.
* Currently, exchange technologies are not checked during source tracing.  Any `tech` with a region link
(denoted with a dash `R1-R2`) provided for the region name is assumed good.  It behooves the modeler to
ensure that both ends of each link are well-connected in the model and to review their performance in output.

### Views across modeling periods

The approach descibed above is applied individually to each region-period pair within the optimization window.
Recall, that for perfect foresight runs, this will be all future periods.  For myopic or other limited-visibility runs,
this will be applied to each period within view.  The orphans are identified on a by period-region basis, but *the
suppression is applied for all periods within the view.*  For example, if technology `power_plant` has a vintage of
2020 and a lifetime of 40 years covering model periods {2020, 2030, 2040, 2050} and it is not viable in 2030, it will
be suppressed and not available in any of the periods.

Currently, for myopic applications, this decision is made on a per-iteration basis, so the technology may be
suppressed within the current iteration only.  For example, if the myopic view was 1 period, and if the `power_plant`
was selected for build in its vintage year, 2020, the modeler may see that it is used in 2020, "suppressed" in 2030
because it may run freely or cause problems in that period, but available again in 2040-2050.  This may/may not be
desired behavior and the modeler should be aware of these behaviors logged in the log file.

This screening prevents model errors and helps to reduce the size of the model in most cases.  These processes
with non-utilized outputs may be the result of erroneous data (perhaps a technology to produce liquid hydrogen
before there is a user of same) or via myopic actions were a technology in a chain is not selected for build,
rendering other processes in the chain irrelevant in a later period.  The main goal of using tracing and suppression
is to prevent "free" midstream commodities from erroneously feeding processes and prevent free-running techs that
might have a negative cost from making the model unbounded or infeasible.
