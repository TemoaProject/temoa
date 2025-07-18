## Notes for follow-on development

#### Original Intent
The original intent for orchestration of the repeated solve process with MGA
was to utilize Pyomo's persistent solver interface to:
1. Load/solve the first MGA iteration (after the 0th min-cost solve and swap of
objective function.)
2. Maintain the loaded model and re-solve after substituting in refreshed objective
functions for follow-on iterations.

This approach is (was) attractive to prevent reconstruction of the model and hopefully
take advantage of quicker solve times using a warm start of the LP solve using Gurobi's
LPWarmStart parameter, enabled by setting the basis of the model.  This turns out to be
difficult and fragile:
- Setting the VBasis and CBasis elements required to take advantage of the warm start
for the LP involved modifying the Pyomo code which interfaces with Gurobi.  It
currently does NOT set these parameters.  It only sets the current values, which is only
used for MIP models in Gurobi.  I produced a working version of this with a few lines
of code in Pyomo, but it is not maintainable right now, and it doesn't have necessary error
handling for cases where the model is not solved and the basis is unavailable, etc.
- Using the warm start and a Simplex only solve in Gurobi did not speed things up appreciably.
Performance observed was near that of the performing Barrier solve with some relaxed options.
This could use some additional focused research if/when the pyomo interface supports LP warm start.
Solve times vary widely and a larger sample is needed.  Additionally, some ill-conditioning in the
model likely is causing slow performance and if that is fixed, this may be a fruitful future endeavor.
Several warm-start solves (seen in Gurobi logs) were running 4+ hours and seemed to be making little
progress on the model.  This is likely due to degeneracy in the model, which slows the
simplex approach down on this model.

#### Alternate (Current) Approach
Focus on doing Barrier concurrently on multiple instances of the model.  Gurobi maxes
out at 32 threads, so most server-side apps could run several instances at once
depending on server capability and desired # of threads.  This has some
challenges:
- We'll need to handle multiple instances of the model at once in memory while they are
being solved / analyzed.  Should not be a problem on server side, even though some instances
on the largest datasets are ~40GB currently.
- Need to have some threadsafe mechanism to create new instances and process the solved
instances.  The logical approach it seems is to use a threadsafe queue to hold pending
instances and solved instances for the core program to produce / process respectively.
- Will likely need to use by-name reference to pull data out of the solved instances unless
we keep a reference to the built instance in a threadsafe manner.
- UPDATE:  Review of the logs from TRACE HPC shows that model construction time for US_9R_TS
is 1:55 (less than 2 mins).  Getting fancy with building instances in advance isn't worth it to
recoup this small timeslice, so we can keep the "work queue" small and just build new when needed.
