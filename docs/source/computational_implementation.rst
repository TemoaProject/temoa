The Temoa Computational Implementation
======================================

We have implemented Temoa within an algebraic modeling environment (AME).  AMEs
provide both a convenient way to describe mathematical optimization models
for a computational context, and allow for abstract model\ [#abstract_model]_
formulations :cite:`Kallrath_2004`.  In contrast to describing a model in a
formal computer programming language like C or Java, AMEs generally have syntax
that directly translates to standard mathematical notation.  Consequently,
models written in AMEs are more easily understood by a wider variety of researchers.
Further, by allowing abstract formulations, a model written with an AME may be
used with many different input data sets.

Three well-known and popular algebraic modeling environments are the General
Algebraic Modeling System (GAMS) :cite:`Brooke_Rosenthal_2003`, AMPL
:cite:`Fourer_etal_1987`, and GNU MathProg :cite:`Makhorin_2000`.  All three
environments provide concise syntax that closely resembles standard (paper)
notation.  We decided to implement Temoa within an AME called
Python Optimization Modeling Objects (Pyomo).

Pyomo provides similar functionality to GAMS, AMPL, and MathProg, but is open
source and written in the Python scripting language.  This has two general
consequences of which to be aware:

 * Python is a scripting language; in general, scripts are an order of
   magnitude slower than an equivalent compiled program.
 * Pyomo provides similar functionality, but because of its Python heritage, is
   **much** more verbose than GAMS, AMPL, or MathProg.

It is our view that the speed penalty of Python as compared to compiled
languages is inconsequential in the face of other large resource bottle necks,
so we omit any discussion of it as an issue.  However, the "boiler-plate" code
(verbosity) overhead requires some discussion.  We discuss this in the
:ref:`Anatomy of a Constraint <constraint-anatomy>`.


.. _constraint-anatomy:

Anatomy of a Constraint
-----------------------

To help explain the Pyomo implementation, we discuss a single constraint in
detail. Consider the :code:`Demand` :eq:`Demand` constraint:

.. math::
   \sum_{I, T, V} \textbf{FO}_{r, p, s, d, i, t, v, dem} +
   SEG_{s,d} \cdot  \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, i, t, v, dem}
   \ge
   {DEM}_{r, p, dem} \cdot {DSD}_{r, s, d, dem}

   \\
   \forall \{r, p, s, d, dem\} \in \Theta_{\text{Demand}}

Implementing this with Pyomo requires two pieces, and optionally a third:

 #. a constraint definition (in ``temoa/core/model.py``),
 #. the constraint implementation (in ``temoa/components/``), and
 #. (optional) sparse constraint index creation (in ``temoa/components/technology.py``).

We discuss first a straightforward implementation of this constraint, that
specifies the sets over which the constraint is defined.  We will follow it with
the actual implementation which utilizes a more computationally efficient but
less transparent constraint index definition (the optional step 3).

A simple definition of this constraint is:

.. topic:: in ``temoa/core/model.py``

   .. code-block:: python
      :linenos:

      M.demand_constraint = Constraint(
        M.regions, M.time_optimize, M.time_season, M.time_of_day, M.commodity_demand,
        rule=demand_constraint
      )

In line 1, '``M.demand_constraint =``' creates a place holder in the model object
``M``, called 'demand_constraint'.  Like a variable, this is the name through
which Pyomo will reference this class of constraints.  ``Constraint(...)`` is a
Pyomo-specific function that creates each individual constraint in the class.
The first arguments (line 2) are the index sets of the constraint class.  Line 2
is the Pyomo method of saying "for all" (:math:`\forall`).  Line 3 contains the
final, mandatory argument (``rule=...``) that specifies the name of the
implementation rule for the constraint, in this case ``demand_constraint``.
Pyomo will call this rule with each tuple in the Cartesian product of the index
sets.

An associated implementation of this constraint based on the definition above
is:

.. topic:: temoa/components/

   ...

   .. code-block:: python
      :linenos:

      def demand_constraint ( M, r, p, s, d, dem ):
         if (r,p,s,d,dem) not in M.demand_specific_distribution.sparse_keys():  # If user did not specify this Demand, tell
            return Constraint.Skip           # Pyomo to ignore this constraint index.

         supply = sum(
            M.v_flow_out[r, p, s, d, S_i, S_t, S_v, dem]
            for S_t, S_v in M.commodity_up_stream_process[r, p, dem] if S_t not in M.tech_annual
            for S_i in M.process_input_by_output[r, p, S_t, S_v, dem]
         )

         supply_annual = sum(
            M.v_flow_out_annual[r, p, S_i, S_t, S_v, dem]
            for S_t, S_v in M.commodity_up_stream_process[r, p, dem] if S_t in M.tech_annual
            for S_i in M.process_input_by_output[r, p, S_t, S_v, dem]
         ) * value( M.segment_fraction[ s, d])

         demand_constraintErrorCheck(supply + supply_annual, r, p, s, d, dem)

         expr = supply + supply_annual == M.Demand[r, p, dem] * M.demand_specific_distribution[r, s, d, dem]
         return expr

   ...

The Python boiler-plate code to create the rule is on line 1.  It begins with
:code:`def`, followed by the rule name (matching the :code:`rule=...` argument
in the constraint definition in ``temoa.core.model``), followed by the argument list.
The argument list will always start with the model (Temoa convention shortens
this to just :code:`M`) followed by local variable names in which to store the
index set elements passed by Pyomo.  Note that the ordering is the same as
specified in the constraint definition.  Thus the first item after :code:`M`
will be an item from :code:`region`, the second from :code:`time_optimize`,
the third from :code:`time_season`, fourth from :code:`time_of_day`, and the
fifth from :code:`commodity_demand`.  Though one could choose :code:`a`, :code:`b`,
:code:`c`, :code:`d`, and :code:`e` (or any naming scheme), we chose :code:`p`, :code:`s`,
:code:`d`, and :code:`dem` as part of a :ref:`naming scheme
<naming_conventions>` to aid in mnemonic understanding.  Consequently, the rule
signature (Line 1) is another place to look to discover what indices define a
constraint.

Lines 2 and 3 are an indication that this constraint is implemented in a
non-sparse manner.  That is, Pyomo does not inherently know the valid indices
for a given model parameter or equation.  In ``temoa.core.model``, the constraint definition
listed five index sets, so Pyomo will naively call this function for every
possible combination of tuple :math:`\{r, p, s, d, dem\}`.  However, as there
may be slices for which a demand does not exist (e.g., the winter season might
have no cooling demand), there is no need to create a constraint for any tuple
involving 'winter' and 'cooling'.  Indeed, an attempt to access a demand for
which the modeler has not specified a value results in a Pyomo error, so it is
necessary to ignore any tuple for which no Demand exists.

Lines 5 through 11 represent two *source-lines* that we split over several lines for
clarity.  These lines implement the summations of the demand commodity ``dem``
produced by demand technologies with both variable and constant output across the
year, summed over all relevant technologies, vintages, and the inputs. The
:code:`supply` and :code:`supply_annual` are local variables used in the expression
(:code:`expr`) shown below. Note that the sum is performed with sparse indices, which
are returned from dictionaries created in :code:`temoa/components/technology.py`.

Lines 5 through 11 also showcase a very common idiom in Python:
list-comprehension.  List comprehension is a concise and efficient syntax to
create lists.  As opposed to building a list element-by-element with for-loops,
list comprehension can convert many statements into a single operation.
Consider a naive approach to calculating the supply::

   to_sum = list()
   for S_t in M.tech_all:
      for S_v in M.vintage_all:
         for S_i in process_input_by_output( p, S_t, S_v, dem ):
            to_sum.append( M.v_flow_out[p, s, d, S_i, S_t, S_v, dem] )
   supply = sum( to_sum )

This implementation creates an extra list (:code:`to_sum`), then builds the list
element by element with :code:`.append()`, before finally calculating the summation.
This means that the Python interpreter must iterate through the elements of the
summation, not once, but twice.

A less naive approach would replace the :code:`.append()` call with the
:code:`+=` operator, reducing the number of iterations through the elements to
one::

   supply = 0
   for S_t in M.tech_all:
      for S_v in M.vintage_all:
         for S_i in process_input_by_output( p, S_t, S_v, dem ):
            supply += M.v_flow_out[p, s, d, S_i, S_t, S_v, dem]

Why is list comprehension necessary?  Strictly speaking, it is not, especially
in light of this last example, which may read more familiar to those comfortable
with C, Fortran, or Java.  However, due to quirks of both Python and Pyomo,
list-comprehension is preferred both syntactically as "the Pythonic" way, and as
the more efficient route for many list manipulations.  (It also *may* seem
slightly more familiar to those used to a more mainstream algebraic modeling
language.)

With the correct model variables summed and stored in the ``supply`` and
``supply_annual`` variables, Line 17 calls a function defined in
:code:`temoa/components/technology.py` that checks to make sure there is technology
that can supply each demand commodity ``dem`` in each :math:`\{r, p, s, d\}`.

If no process supplies the demand, then it quits computation immediately rather
than completing a potentially lengthy model generation and waiting for the
solver to recognize the infeasibility of the model. Further, the function
lists potential ways for the modeler to correct the problem. This is one of the
benefits of Temoa: we've incorporated error handling in several places to
try and capture the most common user errors. This capability is subtle, but in
practice extremely useful while building and debugging a model.

Line 19 creates the actual inequality comparison.  This line is superfluous, but
we leave it in the code as a reminder that inequality operators (i.e. :code:`<=`
and :code:`>=`) with a Pyomo object (like supply) generate a Pyomo *expression
object*, not a boolean True or False as one might expect.\ [#return_expression]_
It is this expression object that must be returned to Pyomo, as on Line 20.

In the above implementation, the constraint is called for every tuple in the
Cartesian product of the indices, and the constraint must then decide whether
each tuple is valid.  The below implementation differs from the one above
because it only calls the constraint rule for the valid tuples within the
Cartesian product, which is computationally more efficient than the simpler
implementation above.

.. topic:: in ``temoa/core/model.py`` (actual implementation)

   .. code-block:: python
      :linenos:

      M.demand_constraint_rpsdc = Set( dimen=5, rule=demand_constraint_indices )
      # ...
      M.demand_constraint = Constraint( M.demand_constraint_rpsdc, rule=demand_constraint )


As discussed above, the demand_constraint is only valid for certain
:math:`\{r, p, s, d, dem\}` tuples.  Since the modeler can specify the demand
distribution per commodity (necessary to model demands like heating, that do not
apply in all time slices), Temoa must ascertain the valid tuples. We have
implemented this logic in the function :code:`demand_constraint_indices` in
``temoa/components/technology.py``.  Thus, Line 1 tells Pyomo to instantiate
:code:`demand_constraint_rpsdc` as a Set of 5-length tuples indices
(:code:`dimen=5`), and populate it with what Temoa's rule
:code:`demand_constraint_indices` returns.  We omit here an explanation of the
implementation of the :code:`demand_constraint_indices` function, stating merely
that it returns the exact indices over which the demand_constraint must to be
created.  With the sparse set :code:`demand_constraint_rpsdc` created, we can now
can use it in place of the five sets specified in the non-sparse
implementation.  Pyomo will now call the constraint implementation rule the
minimum number of times.

On the choice of the :code:`_rpsdc` suffix for the index set name, there is no
Pyomo-enforced restriction.  However, use of an index set in place of the
non-sparse specification obfuscates over what indexes a constraint is defined.
While it is not impossible to deduce, either from this documentation
or from looking at the :code:`demand_constraint_indices` or
:code:`demand_constraint` implementations, the Temoa convention includes
index set names that feature the one-character representation of each set dimension.
In this case, the name :code:`demand_constraint_rpsdc` implies that this set has a
dimensionality of 5, and (following the :ref:`naming scheme
<naming_conventions>`) the first index of each tuple will be an element of
:code:`region`, the second an element of :code:`time_optimize`, the third
an element of :code:`time_season`, fourth an element of :code:`time_of_day`,
and fifth a commodity.  From the contextual information that this is the
Demand constraint, one can assume that the ``c`` represents an element from
:code:`commodity_demand`.





A Word on Verbosity
-------------------

Implementing this same constraint in AMPL, GAMS, or MathProg would require only
a single source-line (in a single file).  Using MathProg as an example, it might
look like:

.. code-block:: ampl

   s.t. demand_constraint{(p, s, d, dem) in sDemand_psd_dem} :
       sum{(p, s, d, Si, St, Sv, dem) in sFlowVar_psditvo}
         v_flow_out[p, s, d, Si, St, Sv, dem]
    =
       pDemand[p, s, d, dem];

While the syntax is not a direct translation, the indices of the constraint
(``p``, ``s``, ``d``, and ``dem``) are clear, and by inference, so are the
indices of summation (``i``, ``t``, ``v``) and operand (``v_flow_out``).  This
one-line definition creates an inequality for each period, season, time of day,
and demand, ensuring that total output meets each demand in each time slice --
almost exactly as we have formulated the demand constraint :eq:`Demand`.  In
contrast, Temoa's implementation in Pyomo takes 47 source-lines (the code
discussed above does not include the function documentation).  While some of the
verbosity is inherent to working with a general purpose scripting language, and
most of it is our formatting for clarity, the absolute minimum number of lines a
Pyomo constraint can be is 2 lines, and that likely will be even less readable.

So why use Python and Pyomo if they are so verbose?  In short, for four
reasons:

 * Temoa has the full power of Python, and has access to a rich ecosystem of
   tools (e.g. numpy, matplotlib) that are not as cleanly available to other
   AMLs.  For instance, there is minimal capability in MathProg to error check a
   model before a solve, and providing interactive feedback like what Temoa's
   demand_constraintErrorCheck function does is difficult, if not impossible.
   While a subtle addition, specific and directed error messages are an
   effective measure to reduce the learning curve for new modelers.

 * Python has a vibrant community.  Whereas mathematical optimization has a
   small community, its open-source segment even smaller, and the energy modeling segment
   significantly smaller than that, the Python community is huge, and
   encompasses many disciplines.  This means that where a developer may struggle
   to find an answer, implementation, or workaround to a problem with a more
   standard AML, Python will likely enable a community-suggested solution.

 * Powerful documentation tools.  One of the available toolsets in the Python
   world is documentation generators that *dynamically* introspect Python code.
   While it is possible to inline and block comment with more traditional AMLs,
   the integration with Python that many documentation generators have is much
   more powerful.  Temoa uses this capability to embed user-oriented
   documentation literally in the code, and almost every constraint has a block
   comment.  Having both the documentation and implementation in one place helps
   reduce the mental friction and discrepancies often involved in maintaining
   multiple sources of model authority.

 * AMLs are not as concise as thought.

This last point is somewhat esoteric, but consider the MathProg implementation
of the Demand constraint in contrast with the last line of the Pyomo version::

   expr = (supply = M.Demand[p, s, d, dem])

While the MathProg version indeed translates more directly to standard notation,
consider that standard notation itself needs extensive surrounding text to
explain the significance of an equation.  *Why* does the equation compare the
sum of a subset of FlowOut to Demand?  In Temoa's implementation, a high-level
understanding of what a constraint does requires only the last line of code:
"Supply must meet demand."


Project Structure
-----------------

The Temoa model code is organized into clear, purpose-driven packages:

**Core Packages:**

* ``temoa.core`` - Public API for end users

  * ``model.py`` - Contains the ``TemoaModel`` class, the main entry point for building
    and solving energy system models. This class coordinates all model components.

  * ``config.py`` - Contains ``TemoaConfig`` and ``TemoaMode`` for model configuration
    and execution mode selection (perfect foresight, myopic, MGA, etc.).

* ``temoa.cli`` - Command-line interface

  * Provides the ``temoa`` command with subcommands for running models, validating
    configurations, migrating databases, and generating tutorial files.

* ``temoa.components`` - Model components and constraints

  * ``costs.py`` - Objective function implementation (total system cost minimization)
  * ``flows.py`` - Commodity flow balance constraints
  * ``capacity.py`` - Capacity and activity constraints
  * ``emissions.py`` - Emission accounting and constraints
  * ``reserves.py`` - Reserve margin requirements
  * ``limits.py`` - Various limit constraints (capacity, activity, emissions, etc.)
  * ``storage.py`` - Energy storage constraints
  * ``ramping.py`` - Ramping constraints for generators
  * Additional constraint modules for specific features

* ``temoa.data_io`` - Data loading and validation

  * ``hybrid_loader.py`` - Main data loading engine using manifest-driven architecture
  * ``component_manifest.py`` - Declarative specification of all data components
  * ``loader_manifest.py`` - Data structure definitions for the loader
  * Database interface and validation logic

* ``temoa.model_checking`` - Model validation and integrity checking

  * Price checking for cost data consistency
  * Source tracing for commodity network validation
  * Network visualization tools

* ``temoa.data_processing`` - Output analysis and visualization

  * ``db_to_excel.py`` - Excel output generation (⚠️ untested in v4.0)
  * ``make_graphviz.py`` - Network diagram generation (⚠️ untested in v4.0)
  * Result processing utilities

* ``temoa.extensions`` - Optional extensions for advanced analysis

  * ``modeling_to_generate_alternatives`` - MGA analysis for exploring near-optimal solutions (⚠️ untested in v4.0)
  * ``method_of_morris`` - Sensitivity analysis (⚠️ untested in v4.0)
  * ``monte_carlo`` - Uncertainty quantification (⚠️ untested in v4.0)
  * ``myopic`` - Sequential decision making with limited foresight
  * ``single_vector_mga`` - Focused MGA on specific variables (⚠️ untested in v4.0)
  * ``stochastics`` - Stochastic programming capabilities (⚠️ untested in v4.0)

* ``temoa._internal`` - Internal utilities (not part of public API)

  * ``table_writer.py`` - Database output formatting
  * ``table_data_puller.py`` - Result extraction utilities
  * Other internal helper modules

If you are working with a Temoa Git repository, these packages are in the
``temoa/`` subdirectory. For detailed architecture documentation, see the
README.md file in the repository root.


The Bleeding Edge
-----------------

The Temoa Project uses the Git source code management system, and the services
of Github.com.  If you are inclined to work with the bleeding edge of the Temoa
Project code base, then take a look at the Temoa repository.  To acquire a
copy, make sure you have Git installed on your local machine, then execute this
command to clone the repository:

.. code::

   $ git clone git://github.com/TemoaProject/temoa.git
   Cloning into 'temoa'...
   remote: Counting objects: 2386, done.
   remote: Compressing objects: 100% (910/910), done.
   remote: Total 2386 (delta 1552), reused 2280 (delta 1446)
   Receiving objects: 100% (2386/2386), 2.79 MiB | 1.82 MiB/s, done.
   Resolving deltas: 100% (1552/1552), done.

You will now have a new subdirectory called ``temoa``, that contains the entire
Temoa Project code and archive history.  Note that Git is a *distributed* source
code management tool.  This means that by cloning the Temoa repository, you have
your own copy to which you are welcome (and encouraged!) to alter and make
commits to.  It will not affect the source repository.

Though this is not a Git manual, we recognize that many readers of this manual
may not be software developers, so we offer a few quick pointers to using Git
effectively.

If you want to see the log of commits, use the command git log:

.. code::

   $ git log -1
   commit b5bddea7312c34c5c44fe5cce2830cbf5b9f0f3b
   Date:   Thu Jul 5 03:23:11 2012 -0400

       Update two APIs

        * I had updated the internal global variables to use the _psditvo
          naming scheme, and had forgotten to make the changes to _graphviz.py
        * Coopr also updated their API with the new .sparse_* methods.

You can also explore the various development branches in the repository:

.. code::

   $ ls
   data_files  stochastic  temoa_model  create_archive.sh  README.txt

   $ git branch -a
   * energysystem
     remotes/origin/HEAD -> origin/energysystem
     remotes/origin/energysystem
     remotes/origin/exp_electric_load_duration_reorg
     remotes/origin/exp_electricity_sector
     remotes/origin/exp_energysystem_flow_based
     remotes/origin/exp_energysystem_match_markal
     remotes/origin/exp_energysystem_test_framework
     remotes/origin/misc_scripts
     remotes/origin/old_energysystem_coopr2
     remotes/origin/temoaproject.org

   $ git checkout exp_energysystem_match_markal
   Branch exp_energysystem_match_markal set up to track remote branch
   exp_energysystem_match_markal from origin.
   Switched to a new branch 'exp_energysystem_match_markal'

   $ ls
   temoa_model                create_archive.sh     utopia-markal-20.dat
   compare_with_utopia-15.py  README.txt
   compare_with_utopia-20.py  utopia-markal-15.dat

To view exactly what changes you have made since the most recent commit to the
repository use the ``diff`` command to ``git``:

.. code::

   $ git diff
   diff --git a/temoa_model/temoa_lib.py b/temoa_model/temoa_lib.py
   index 4ff9b30..0ba15b0 100644
   --- a/temoa_model/temoa_lib.py
   +++ b/temoa_model/temoa_lib.py
   @@ -246,7 +246,7 @@ def InitializeProcessParameters ( M ):
                   if l_vin in M.vintage_exist:
                           if l_process not in l_exist_indices:
                                   msg = ('Warning: %s has a specified efficiency, but does not '
   -                                 'have any existing install base (existing_capacity)\n.')
   +                                 'have any existing install base (existing_capacity).\n')
                                   SE.write( msg % str(l_process) )
                                   continue
                           if 0 == M.existing_capacity[ l_process ]:
    [ ... ]

For a crash course on git, here is a handy `quick start guide`_.


======================
Temoa Code Style Guide
======================

It is an open question in programming circles whether code formatting actually
matters.  The Temoa Project developers believe that it does for these main
reasons:

 * Consistently-formatted code reduces the cognitive work required to understand
   the structure and intent of a code base.  Specifically, we believe that
   before code is to be executed, it is to be understood by other humans.  The
   fact that it makes the computer do something useful is a (happy) coincidence.
 * Consistently-formatted code helps identify `code smell`_\ .
 * Consistently-formatted code helps one to spot code bugs and typos more
   easily.

Note, however, that this is a style `guide`, not a strict ruleset.  There will
also be corner cases to which a style guide does not apply, and in these cases,
the judgment of what to do is left to the implementers and maintainers of the
code base.  To this end, the Python project has a well-written treatise in `PEP
8`_\ :

   **A Foolish Consistency is the Hobgoblin of Little Minds**

   One of Guido's key insights is that code is read much more often than it is
   written.  The guidelines provided here are intended to improve the
   readability of code and make it consistent across the wide spectrum of Python
   code.  As PEP 20 says, "Readability counts".

   A style guide is about consistency.  Consistency with this style guide is
   important.  Consistency within a project is more important.  Consistency
   within one module or function is most important.

   But most importantly: know when to be inconsistent -- sometimes the style
   guide just doesn't apply.  When in doubt, use your best judgment.  Look at
   other examples and decide what looks best.  And don't hesitate to ask!

   Two good reasons to break a particular rule:

     1. When applying the rule would make the code less readable, even for
        someone who is used to reading code that follows the rules.
     2. To be consistent with surrounding code that also breaks it (maybe for
        historic reasons) -- although this is also an opportunity to clean up
        someone else's mess (in true XP style).

Ruff Formatting
---------------

The project has shifted to using Ruff (`ruff`_) as a formatter / linter.  Commits to
the project should use Ruff to format any changed code.  Ruff relies on
settings in the :code:`pyproject.toml` file.  Contributors should be able
to apply ruff to any changed files with the command :code:`ruff format <file>`.
If there is *specific* need to disable Ruff for a particular table or equation,
contributors can sparingly turn off Ruff formatting for sections of code using
comments.  (See the Ruff documentation.)

Indentation: Tabs and Spaces
----------------------------

The project is standardized to using spaces for indentation in accordance with
PEP-8 standards.  Ruff will convert tabs to spaces.


End of Line Whitespace
----------------------

Remove it.  Many editors have plugins or builtin functionality that will take
care of this automatically when the file is saved.


Maximum Line Length
-------------------

(Similar to `PEP 8`_\ ) Limit all lines to a maximum of 100 characters.

Historically, 80 characters was the width (in monospace characters) that a
terminal had to display output.  With the advent of graphical user interfaces
with variable font-sizes, this technological limit no longer exists.  While
80 characters remains an excellent metric of what constitutes a "long line" most
modern wide-screen displays can comfortably show side-by-side difference files with
100 characters per side, and 100 characters better accommodates some long equations. A
long line in this sense is one that is not as transparent as to its intent as it
could be.  **Ruff will enforce 100 character line length**, in accordance with the settings
in the ``pyproject.toml`` file

Slightly adapted from `PEP 8`_\ :

   The preferred way of wrapping long lines is by using Python's implied line
   continuation inside parentheses, brackets and braces.  Long lines can be
   broken over multiple lines by wrapping expressions in parentheses.  These
   should be used in preference to using a backslash for line continuation.
   Make sure to indent the continued line appropriately.  The preferred place to
   break around a binary operator is after the operator, not before it.  Some
   examples:

   .. code-block:: python

      class Rectangle ( Blob ):

         def __init__ ( self, width, height,
                        color='black', emphasis=None, highlight=0 ):
            if ( width == 0 and height == 0 and
                color == 'red' and emphasis == 'strong' or
                highlight > 100 ):
                raise ValueError("sorry, you lose")
            if width == 0 and height == 0 and (color == 'red' or
                                               emphasis is None):
                raise ValueError("I don't think so -- values are {}, {}".format(
                                 (width, height) ))
            Blob.__init__( self, width, height,
                          color, emphasis, highlight )


Blank Lines
-----------

 * Separate logical sections within a single function with a single blank line.
 * Separate function and method definitions with two blank lines.
 * Separate class definitions with three blank lines.


Encodings
---------

Following `PEP 3120`, all code files should use UTF-8 encoding.

.. _naming_conventions:

Naming Conventions
------------------

All constraints attached to a model should end with ``constraint``.  Similarly,
the function they use to define the constraint for each index should use the
same prefix and ``constraint`` suffix, but separate them with an underscore
(e.g. ``M.somename_constraint = Constraint( ...,  rule=somename_constraint``):

.. code-block:: python

   M.capacity_constraint = Constraint( M.CapacityVar_tv, rule=Capacity_constraint )

When providing the implementation for a constraint rule, use a consistent naming
scheme between functions and constraint definitions.  For instance, we have
already chosen ``model`` to represent the Pyomo model instance, ``t`` to represent
*technology*, and ``v`` to represent *vintage*:

.. code-block:: python

   def capacity_constraint ( model: TemoaModel, t: Technology, v: Vintage ):
      ...

The complete list we have already chosen:

 * :math:`p` to represent a period item from :math:`time\_optimize`
 * :math:`s` to represent a season item from :math:`time\_season`
 * :math:`d` to represent a time of day item from :math:`time\_of\_day`
 * :math:`i` to represent an input to a process, an item from
   :math:`commodity\_physical`
 * :math:`t` to represent a technology from :math:`tech\_all`
 * :math:`v` to represent a vintage from :math:`vintage\_all`
 * :math:`o` to represent an output of a process, an item from
   :math:`commodity\_carrier`

Note also the order of presentation, even in this list.  In order to reduce the
number mental "question marks" one might have while discovering Temoa, we
attempt to rigidly reference a mental model of "left to right".  Just as the
entire energy system that Temoa optimizes may be thought of as a left-to-right
graph, so too are the individual processes.  As mentioned above in `A Word on Index
Ordering`_:

  For any indexed parameter or variable within Temoa, our intent is to enable a
  mental model of a left-to-right arrow-box-arrow as a simple mnemonic to
  describe the "input :math:`\rightarrow` process :math:`\rightarrow` output"
  flow of energy.  And while not all variables, parameters, or constraints have
  7 indices, the 7-index order mentioned here (p, s, d, i, t, v, o) is the
  canonical ordering.  If you note any case where, for example, d comes before
  s, that is an oversight.


In-line Implementation Conventions
----------------------------------

Wherever possible, implement the algorithm in a way that is *pedagogically*
sound or reads like an English sentence.  Consider this snippet:

.. code-block:: python

   if ( a > 5 and a < 10 ):
      doSomething()

In English, one might translate this snippet as "If a is greater than 5 and less
then 10, do something."  However, a semantically stronger implementation might
be:

.. code-block:: python

   if ( 5 < a and a < 10 ):
      doSomething()

This reads closer to the more familiar mathematical notation of ``5 < a < 10``
and translates to English as "If a is between 5 and 10, do something."  The
semantic meaning that ``a`` should be *between* 5 and 10 is more readily
apparent from just the visual placement between 5 and 10, and is easier for the
"next person" to understand (who may very well be you in six months!).

Consider the reverse case:

.. code-block:: python

   if ( a < 5 or a > 10 ):
      doSomething()

On the number line, this says that a must fall before 5 or beyond 10.  But the
intent might more easily be understood if altered as above:

.. code-block:: python

   if not ( 5 < a and a < 10 ):
      doSomething()

This last snippet now makes clear the core question that a should ``not`` fall
between 5 and 10.

Consider another snippet:

.. code-block:: python

   acounter = scounter + 1

This method of increasing or incrementing a variable is one that many
mathematicians-turned-programmers prefer, but is more prone to error.  For
example, is that an intentional use of ``acounter`` or ``scounter``?  Assuming
as written that it's incorrect, a better paradigm uses the += operator:

.. code-block:: python

   acounter += 1

This performs the same operation, but makes clear that the ``acounter`` variable
is to be incremented by one, rather than be set to one greater than ``scounter``.

The same argument can be made for the related operators:

.. code-block:: python

   >>> a, b, c = 10, 3, 2

   >>> a += 5;  a    # same as a = a + 5
   15
   >>> a -= b;  a    # same as a = a - b
   12
   >>> a /= b;  a    # same as a = a / b
   4
   >>> a *= c;  a    # same as a = a * c
   8
   >>> a **= c; a    # same as a = a ** c
   64


Miscellaneous Style Conventions
-------------------------------

 * (Same as `PEP 8`_\ ) Do not use spaces around the assignment operator (``=``)
   when used to indicate a default argument or keyword parameter:

   .. code-block:: python

      def complex ( real, imag = 0.0 ):         # bad
         return magic(r = real, i = imag)       # bad

      def complex ( real, imag=0.0 ):           # good
         return magic( r=real, i=imag )         # good

 * (Same as `PEP 8`_\ ) Do not use spaces immediately before the open
   parenthesis that starts the argument list of a function call:

   .. code-block:: python

      a = b.calc ()         # bad
      a = b.calc ( c )      # bad
      a = b.calc( c )       # good

 * (Same as `PEP 8`_\ ) Do not use spaces immediately before the open
   bracket that starts an indexing or slicing:

   .. code-block:: python

      a = b ['key']         # bad
      a = b [a, b]          # bad
      a = b['key']          # good
      a = b[a, b]           # good


Patches and Commits to the Repository
-------------------------------------

In terms of code quality and maintaining a legible "audit trail," every patch
should meet a basic standard of quality:

 * Every commit to the repository must include an appropriate summary message
   about the accompanying code changes.  Include enough context that one reading
   the patch need not also inspect the code to get a high-level understanding of
   the changes.  For example, "Fixed broken algorithm" does not convey much
   information.  A more appropriate and complete summary message might be::

      Fixed broken storage algorithm

      The previous implementation erroneously assumed that only the energy
      flow out of a storage device mattered.  However, Temoa needs to know the
      energy flow in to all devices so that it can appropriately calculate the
      inter-process commodity balance.

      License: MIT

   If there is any external information that would be helpful, such as a bug
   report, include a "clickable" link to it, such that one reading the patch as
   via an email or online, can immediately view the external information.

   Specifically, commit messages should follow the form::

      A subject line of 50 characters or less
       [ an empty line ]
      1. http://any.com/
      2. http://relevant.org/some/path/
      3. http://urls.edu/~some/other/path/
      4. https://github.com/blog/926-shiny-new-commit-styles
      5. https://help.github.com/articles/github-flavored-markdown
       [ another empty line ]
      Any amount and format of text, such that it conforms to a line-width of
      72 characters[4].  Bonus points for being aware of the Github Markdown
      syntax[5].

      License: MIT

 * Ensure that each commit contains no more than one *logical* change to the
   code base.  This is very important for later auditing.  If you have not
   developed in a logical manner (like many of us don't), :code:`git add -p` is
   a very helpful tool.

 * If you are not a core maintainer of the project, all commits must also
   include a specific reference to the license under which you are giving your
   code to the project.  Note that Temoa will not accept any patches that
   are not licensed under MIT.  A line like this at the end of your commit
   will suffice::

      ... the last line of the commit message.

      License: MIT

   This indicates that you retain all rights to any intellectual property your
   (set of) commit(s) creates, but that you license it to the Temoa Project
   under the terms of the MIT license.  If
   the Temoa Project incorporates your commit, then Temoa may not relicense
   your (set of) patch(es), other than to increase the version number of the
   MIT license.  In short, the intellectual property remains yours, and the
   Temoa Project would be but a licensee using your code similarly under the
   terms of MIT.

   Executing licensing in this manner -- rather than requesting IP assignment --
   ensures that no one group of code contributers may unilaterally change the
   license of Temoa, unless **all** contributers agree in writing in a
   publicly archived forum (such as the `Temoa Forum`_).

 * When you are ready to submit your (set of) patch(es) to the Temoa Project,
   we will utilize GitHub's `Pull Request`_ mechanism.
