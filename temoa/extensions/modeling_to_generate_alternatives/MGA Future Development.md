## Expanding MGA Capabilities

These notes are intended as a guide to follow-on developers who wish to employ other
MGA Axes for exploration.  This is a rough "how-to" guide to developing an additional `Vector Manager`
for MGA.

### Design Comments
An MGA process is orchestrated by the MGA Sequencer, but fundamentally employs 2 pieces of
functionality:  A `Vector Manager` and a `Weighting` plan.  It is up to the designer to decide
which pairings are supported.  Currently, only `Tech Activity` is employed as a manager and `Hull Expansion`
is employed as the weighting plan to support it.
- `Vector Manager`:  Responsible for producing new models to be solved and internally managing
the weighting of variable vectors for production of alternative objective functions.  New Vector
Managers should subclass `vector_manager.py` and implement all abstract methods.  The Sequencer is
designed to use those methods and should not need modification.
- `Weighting`:  An implement to be used by the `Vector Manager` to help develop weights for objective
vectors to follow an exploration plan.  It is up to the designer to choose what is eligible.  Design
choices should be reflected in the `manager_factory.py` module which is responsible for taking the
configuration inputs and providing the sequencer the correct manager-weighting combo.  It would also
be possible to just make a simple all-in-one manager and pass a `None` or such in the construction
process.

Additional named constants can be added to the `mga_constants.py` enumerations in order to support
decisions in the `Manager Factory`.

### Steps & Comments
1. Read the MGA Design document in the docs folder.  It describes the basic strategy and key
terminology used in the MGA extension.
2. Make a new manager module by sub-classing `VectorManager` as shown in the working
`tech_activity_vector_manager.py` class.  Add all inherited abstract methods (most IDE's will
offer to do this automatically).
3. Develop the functionality in the inherited methods.  The function dox should be fairly clear, but
the overall intent is to provide new models when called for by the sequencer.
   - The 2 core functions that the sequencer relies on are the model generator function and the result processor.
   The result processing function can be used to glean info from solved models (what is used/not used, etc.)
   in order to inform the weighter on generating new models.
   - Realize the manager probably needs to rely on variable NAMES internally (unless a more elaborate
   bookkeeping scheme is developed) because returned models will need to be interrogated by variable
   name as shown in the exemplar.  The order in which models are provided and returned is _not_
   synchronized because of multiprocessing.
4. Decide if `HULL_EXPANSION` is the right weighting scheme or if another is needed.  The interaction
between the manager & weighter is up to the designer.  If desired, and built smartly, a manager _could_
employ various weighting schemes.
5. Modify the code in the `Manager Factory` class to provide the correct manager when asked via config
values
