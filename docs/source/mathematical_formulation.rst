
To understand this section, the reader will need at least a cursory
understanding of mathematical optimization.  We omit here that introduction,
and instead refer the reader to `various`_ `available`_ `online`_ `sources`_.
Temoa is formulated as an algebraic model that requires information organized
into sets, parameters, variables, and equation
definitions.

The heart of Temoa is a technology explicit energy system optimization model.
It is an algebraic network of linked processes -- where each process is defined
by a set of engineering characteristics (e.g. capital cost, efficiency, capacity
factor, emission rates) -- that transform raw energy sources into end-use
demands.  The model objective function minimizes the present-value cost of
energy supply by optimizing installed capacity and its utilization over time.

.. _simple_system:

.. figure:: images/simple_system2.*
   :align: center
   :width: 100%
   :alt: A simple energy system, with energy sources on the left and energy
         sinks (end-use demands) on the right.
   :figclass: align-center
   :figwidth: 70%

   A common visualization of energy system models is a directed network graph,
   with energy sources on the left and end-use demands on the right.  The
   modeler must specify the end-use demands to be met, the technologies defined
   within the system (rectangles), and the inputs and outputs of each (red and green
   arrows).  The circles represent distinct energy carriers that connect
   technologies within the energy system network.

The most fundamental tenet of the model is the understanding of energy flow,
treating all processes as black boxes that take inputs and produce outputs.
Specifically, Temoa does not care about the inner workings of a process, only
its global input and output characteristics.  In this vein, the above graphic
can be broken down into process-specific elements.  For example, the coal power
plant takes as input coal and produces electricity, and is subject to various
costs (e.g. variable costs) and constraints (e.g. efficiency) along the way.

.. figure:: images/coal_process.png
   :align: center
   :figclass: center
   :figwidth: 60%


The modeler defines the processes and engineering characteristics through a
combination of sets and parameters, described in the next few sections.  Temoa then
utilizes these parameters, along with the associated technology-specific decision
variables for capacity and activity, to create the objective function and
constraints that are used during the optimization process.

.. _Sets:


Conventions
-----------

 * In the mathematical notation, we use CAPITALIZATION to denote a container,
   like a set, indexed variable, or indexed parameter.  Sets use only a single
   letter, so we use the lower case to represent an item from the set.  For
   example, :math:`T` represents the set of all technologies and :math:`t`
   represents a single item from :math:`T`.

 * Variables are named V\_VarName within the code to aid readability.  However,
   in the documentation where there is benefit of italics and other font
   manipulations, we elide the 'V\_' prefix.

 * In all equations, we **bold** variables to distinguish them from parameters.
   Take, for example, this excerpt from the Temoa default objective function:

   .. math::
      C_{variable} = \sum_{r, p, s, d, i, t, v, o \in \Theta_{VC}} \left (
              {VC}_{r, p, t, v}
        \cdot R_p
        \cdot \textbf{FO}_{r, p, s, d, i, t, v, o}
        \right )

   Note that :math:`C_{variable}` is not bold, as it is a temporary variable
   used for clarity while constructing the objective function.  It is not a
   structural variable and the solver never sees it.

 * Where appropriate, we put the variable on the right side of the coefficient.
   In other words, this is not a preferred form of the previous equation:

   .. math::

      C_{variable} = \sum_{r, p, s, d, i, t, v, o \in \Theta_{VC}} \left (
              \textbf{FO}_{r, p, s, d, i, t, v, o}
        \cdot {VC}_{r, p, t, v}
        \cdot R_p
        \right )

 * We generally put the limiting or defining aspect of an equation on the right
   hand side of the relational operator, and the aspect being limited or defined
   on the left hand side.  For example, equation :eq:`Capacity` defines Temoa's
   mathematical understanding of a process capacity (:math:`\textbf{CAP}`) in
   terms of that process' activity (:math:`\textbf{ACT}`):

   .. math::

       \left (
               \text{CFP}_{r, t, v}
         \cdot \text{C2A}_{r, t}
         \cdot \text{SEG}_{s, d}
       \right )
       \cdot \textbf{CAP}_{r, t, v}
    =
       \sum_{I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
    +
       \sum_{I, O} \textbf{CUR}_{r, p, s, d, i, t, v, o}

       \\
       \forall \{r, p, s, d, t, v\} \in \Theta_{\text{FO}}

 * We use the word 'slice' to refer to the tuple of season and time of day
   :math:`\{s,d\}`. Note that these time slices are user-defined, and can
   represent time ranging large blocks of time (e.g., winter-night) to every
   hour in a given season.

 * We use the word 'process' to refer to the tuple of technology and vintage
   (:math:`\{t,v\}`). For example, solar PV (technology) installed in 2030
   (vintage).


 * Mathematical notation:

   * We use the symbol :math:`\mathbb{I}` to represent the unit interval ([0,
     1]).

   * We use the symbol :math:`\mathbb{Z}` to represent "the set of all
     integers."

   * We use the symbol :math:`\mathbb{N}` to represent natural numbers (i.e.,
     integers greater than zero: 1, 2, 3, :math:`\ldots`).

   * We use the symbol :math:`\mathbb{R}` to denote the set of real numbers, and
     :math:`\mathbb{R}^+_0` to denote non-negative real numbers.


Sets
----

.. include:: db_model_comparison.rst


.. _table_set:

.. csv-table:: List of all Temoa sets with which a modeler might interact.  The
             asterisked (\*) elements are automatically derived by the model and
             are not user-specifiable.
   :header: "Set","Temoa Name","Data Type","Short Description"
   :widths: 8, 28, 14, 50

   ":math:`{}^*\text{C}`",":code:`commodity_all`","string","union of all commodity sets"
   ":math:`\text{C}^s`",":code:`commodity_source`","string","input sources (not balanced by CommodityBalance_constraint)"
   ":math:`\text{C}^d`",":code:`commodity_demand`","string","end-use demand commodities"
   ":math:`\text{C}^e`",":code:`commodity_emissions`","string","emission commodities (e.g. :math:`\text{CO}_\text{2}` :math:`\text{NO}_\text{x}`)"
   ":math:`\text{C}^p`",":code:`commodity_physical`","string","general energy forms (e.g. electricity, coal, uranium, oil)"
   ":math:`\text{C}^a`",":code:`commodity_annual`","string","same as commodity physical but flows are only balanced over each period (:math:`\text{C}^a \subset \text{C}^p`)"
   ":math:`\text{C}^w`",":code:`commodity_waste`","string","production can be greater than consumption. can be physical, annual, or neither (not balanced)"
   ":math:`{}^*\text{C}^c`",":code:`commodity_carrier`","string","physical energy carriers and end-use demands (:math:`\text{C}_p \cup \text{C}_d`)"
   ":math:`\text{I}`",,"string","alias of :math:`\text{C}^p`; used in documentation only to mean ""input"""
   ":math:`\text{O}`",,"string","alias of :math:`\text{C}^c`; used in documentation only to mean ""output"""
   ":math:`\text{P}^e`",":code:`time_existing`",":math:`\mathbb{Z}`","model periods before optimization begins"
   ":math:`\text{P}^f`",":code:`time_future`",":math:`\mathbb{Z}`","model time scale of interest; the last year is not optimized"
   ":math:`{}^*\text{P}^o`",":code:`time_optimize`",":math:`\mathbb{Z}`","model time periods to optimize; (:math:`\text{P}^f - \text{max}(\text{P}^f)`)"
   ":math:`\text{R}`",":code:`regions`","string","distinct geographical regions"
   ":math:`{}^*\text{V}`",":code:`vintage_all`",":math:`\mathbb{Z}`","possible tech vintages; (:math:`\text{P}^e \cup \text{P}^o`)"
   ":math:`\text{S}`",":code:`time_season`","string","seasonal divisions (e.g. winter, summer)"
   ":math:`\text{D}`",":code:`time_of_day`","string","time-of-day divisions (e.g. morning)"
   ":math:`{}^*\text{T}`",":code:`tech_all`","string","all technologies to be modeled; (:math:`{T}^r \cup {T}^p`)"
   ":math:`\text{T}^u`",":code:`tech_unlim_cap`","string","technologies that have no bound on capacity, and can have variable costs only (imports, taxes, etc.); (:math:`{T}^u \subset (T - T^{res})`)"
   ":math:`\text{T}^a`",":code:`tech_annual`","string","technologies that produce constant annual output; (:math:`{T}^a \subset T`)"
   ":math:`\text{T}^b`",":code:`tech_baseload`","string","baseload electric generators; (:math:`{T}^b \subset T`)"
   ":math:`\text{T}^c`",":code:`tech_curtailment`","string","technologies with curtailable output and no upstream cost; (:math:`{T}^c \subset (T - T^{res})`)"
   ":math:`\text{T}^x`",":code:`tech_exchange`","string","technologies used for interregional commodity flow; (:math:`{T}^x \subset T`).  See Note 1 below on capacity and cost application for `tech_exchange`"
   ":math:`\text{T}^e`",":code:`tech_existing`","string","technologies constructed in an existing (past) vintage; (:math:`{T}^e \subset T`)."
   ":math:`\text{T}^f`",":code:`tech_flex`","string","technologies producing excess commodity flows; (:math:`{T}^f \subset T`)"
   "",":code:`tech_group_names`","string","named groups for use in group constraints"
   "",":code:`tech_group_members`","(tech_group_names, tech)","Each technology belonging to each group defined above"
   ":math:`\text{T}^p`",":code:`tech_production`","string","techs producing intermediate commodities"
   ":math:`\text{T}^{ur}`",":code:`tech_upramping`","string","electric generators with a ramp up hourly rate limit; (:math:`{T}^{ur} \subset T`)"
   ":math:`\text{T}^{dr}`",":code:`tech_downramping`","string","electric generators with a ramp down hourly rate limit; (:math:`{T}^{dr} \subset T`)"
   ":math:`\text{T}^{res}`",":code:`tech_reserve`","string","electric generators contributing to the reserve margin requirement; (:math:`{T}^res \subset T`)"
   ":math:`\text{T}^{ret}`",":code:`tech_retirement`","string","technologies allowed to retire before end of life; (:math:`{T}^{ret} \subset (T - T^{u})`)"
   ":math:`\text{T}^s`",":code:`tech_storage`","string","all storage technologies; (:math:`{T}^s \subset T`)"
   ":math:`\text{T}^{ss}`",":code:`tech_seasonal_storage`","string","seasonal storage technologies; (:math:`{T}^{ss} \subset T^s`)"

Note 1:  Temoa sets Capacity for Exchange Technologies to be equal in both directions on the link automatically.
Costs are apportioned as follows:  If both directions of the link have a cost parameter, costs are accrued to
each region region directly based on flow *to* that region.  If only 1 element of the link holds a populated cost value,
then that cost divided between the 2 regions automatically based on use, where each region is "billed" according
to use as a receiver.

Temoa uses two different set notation styles, one for code representation and
one that utilizes standard algebraic notation.  For brevity, the mathematical
representation uses capital letters to denote sets, and lower case letters to
represent items within sets.  For example, :math:`T` represents the set of all
technologies and :math:`t` represents an item within :math:`T`.

The code representation is more verbose than the algebraic version, using full
words.  This documentation presents them in an italicized font.  The same
example of all technologies is represented in the code as :code:`tech_all`.
:ref:`Table 1 <table_set>` lists all of the Temoa sets, with both sets of notation.

There are four basic set "groups" within Temoa: periods, sub-annual "time slices",
technologies, and energy commodities.  The technology-related sets contain all the
possible energy technologies that the model may build and the commodities sets
contain all the input and output forms of energy that technologies consume and
produce.  The period and time slice sets merit a slightly longer discussion.

Temoa's conceptual model of *time* is broken up into three levels, and energy supply
and demand is balanced at each of these levels:

 * **Periods** - consecutive blocks of years, marked by the first year in the
   period.  For example, a two-period model might consist of :math:`\text{P}^f =
   \{2010, 2015, 2025\}`, representing the two periods of years from beginning 2010
   through 2014 end, and from beginning 2015 through 2024 end. Note the that last period element
   \(2025\) does not represent a new time period, but rather defines the end of the second time
   period and therefore the planning horizon.

 * **Seasonal** - Each year may have multiple seasons. In a conventional time-sliced
   model, the seasons may typically represent the four seasons: winter, spring summer,
   and fall. However, the seasonal slices can represent any amount of time at the
   sub-period scale. For example, in a database with representative days, the seasonal
   slices can be used as generic containers to represent blocks of days. The type of
   seasonal representation in use should be defined in the config file.

 * **Daily** - Within a season, a given day can be further subdivided into different
   time segments. Less detailed databases may include larger blocks of time, such as morning,
   afternoon, and night. In a database with representative days, each daily segment can
   be used to represent every hour of the day.


There are two specifiable period sets: :code:`time_exist` (:math:`\text{P}^e`)
and :code:`time_future` (:math:`\text{P}^f`).  The :code:`time_exist` set
contains periods before :code:`time_future`.  Its primary purpose is to specify
the vintages for capacity that exist prior to the model optimization.
The :code:`time_future` set contains the future periods that the model will
optimize.  As this set must contain only integers, Temoa interprets the elements
to be the boundaries of each period of interest.  Thus, this is an ordered set
and Temoa uses its elements to automatically calculate the length of each
optimization period; modelers may exploit this to create variable period lengths
within a given input database. Temoa "names" each optimization period by the first
year, and makes them easily accessible via the :code:`time_optimize` set.  This final
"period" set is not user-specifiable, but is an exact duplicate of
:code:`time_future`, less the largest element.  In the above example, since
:math:`\text{P}^f = \{2010, 2015, 2025\}`, :code:`time_optimize` does not
contain 2025: :math:`\text{P}^o =\{2010, 2015\}`.

One final note on periods: rather than optimizing each year within a period
individually, Temoa makes the simplifying assumption that each time period contains
:math:`n` copies of a single, representative year.  Temoa optimizes capacity
and activity for just this characteristic year within each time period, assuming
the results for different years in the same time period are identical. The Temoa
objective function, however, accounts for the total cost across all years in all
model time periods. Figure 3.3 gives a graphical explanation of the annual
delineation.

.. _FigureObjectiveComparison:

.. figure:: images/ObjectiveUsageVsCostComparison.png
   :align: center
   :width: 100%
   :alt: Energy use same each year; time-value of annual costs reduced each year
   :figclass: align-center
   :figwidth: 60%

   The left graph is of energy, while the right graph is of the annual costs.
   The energy used in a period by a process is the same for all
   years (with exception for those processes that cease their useful life
   mid-period).  However, even though the costs incurred will be the same, the
   time-value of money changes due to the discount-rate.  As the fixed costs of
   a process are tied to the length of its useful life, those processes that do
   not fall on a period boundary require unique time-value multipliers in the
   objective function.

As noted above, Temoa allows the modeler to subdivide each year into a set of time
slices, comprised of a season and a time of day.  Unlike :code:`time_future`, there
is no restriction on what labels the modeler may assign to the :code:`time_season`
and :code:`time_of_day` set elements.


A Word on Index Ordering
^^^^^^^^^^^^^^^^^^^^^^^^

The ordering of the indices is consistent throughout the model to promote an
intuitive "left-to-right" description of each parameter, variable, and
constraint set.  For example, Temoa's output commodity flow variable
:math:`FO_{r,p,s,d,i,t,v,o}` may be described as "in region (:math:`r`),
in period (:math:`p`) during season (:math:`s`) at time of day (:math:`d`),
the flow of input commodity (:math:`i`) to technology (:math:`t`) of vintage
(:math:`v`) generates an output commodity flow (:math:`o`) of
:math:`FO_{r,p,s,d,i,t,v,o}`."  For any indexed parameter or variable within
Temoa, our intent is to enable a mental model of a simple left-to-right, arrow-box-arrow
mnemonic to describe the "input :math:`\rightarrow` process
:math:`\rightarrow` output" flow of energy.  And while not all variables, parameters,
or constraints have 8 indices, the 8-index order mentioned here (r, p, s, d, i, t, v, o)
is the canonical ordering.  If you note any case where, for example, d comes before s,
that is an oversight.  In general, if there is an index ordering that does not follow
this rubric, we view that as a bug.


Deviations from Standard Mathematical Notation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Temoa deviates from standard mathematical notation and set understanding in two
ways.  The first is that Temoa places a restriction on the *time* set elements.
Specifically, while most optimization programs treat set elements as arbitrary
labels, Temoa assumes that all elements of the :code:`time_existing` and
:code:`time_future` sets are integers.  Further, these sets are assumed to be
ordered, such that the minimum element is "naught".  For example, if
:math:`\text{P}^f = \{2015, 2020, 2030\}`, then :math:`P_0 = 2015`.  In
other words, the capital :math:`\text{P}` with the naught subscript indicates
the first element in the :code:`time_future` set.  We will explain the reason
for this notation shortly.

The second set of deviations revolves around the use of the Theta superset
(:math:`\Theta`).  The Temoa code makes heavy use of sparse sets, for both
correctness and efficient use of computational resources.  For brevity, and
to avoid discussion of implementation details, we do not enumerate their
logical creation here.  Instead, we rely on the readers general understanding of
the context.  For example, in the sparse creation of the constraints of the
Demand constraint class (explained in :ref:`NetworkConstraints` and
:ref:`constraint-anatomy`), we state simply that the constraint is instantiated
"for all the :math:`\{p, s, d, dem\}` tuples in
:math:`\Theta_{\text{demand}}`".  This means that the constraint is only defined
for the exact indices for which the modeler specified end-use demands via the
Demand parameter in the input data file.

Summations also occur in a sparse manner.  For example, let's take another look at
the :code:`Capacity` :eq:`Capacity` Constraint:

.. math::

       \left (
               \text{CFP}_{r, s, d, t, v}
         \cdot \text{C2A}_{r, t}
         \cdot \text{SEG}_{s, d}
       \right )
       \cdot \textbf{CAP}_{r, t, v}
    =
       \sum_{I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
    +
       \sum_{I, O} \textbf{CUR}_{r, p, s, d, i, t, v, o}

   \\
   \forall \{p, s, d, t, v\} \in \Theta_{\text{Capacity}}

It defines the Capacity variable for every valid combination of :math:`\{p, v\}`,
and includes the sum over all inputs and outputs of the FlowOut variable.  A
naive implementation of this equation might include nonsensical items in each
summation, such as an input of vehicle miles traveled to an oil refinery or an
output of sunlight from nuclear generating capacity.  However, in this context,
summing over the inputs and outputs (:math:`i` and :math:`o`) implicitly
includes only the valid combinations of :math:`\{p, s, d, i, t, v, o\}`.


Parameters
----------

.. _table_parameter:

.. csv-table:: List of Temoa parameters with which a modeler might interact.
           The asterisked (\*) parameters specified at the end of the table
           are automatically derived by the model and are not user-specifiable.
   :header: "Parameter","Temoa Name","Domain","Short Description"
   :widths: 14, 27, 10, 49

   ":math:`\text{CC}_{r,p,t,v}`","capacity_credit",":math:`\mathbb{I}`","Process-specific capacity credit"
   ":math:`\text{CFT}_{r,s,d,t}`","capacity_factor_tech",":math:`\mathbb{I}`","Technology-specific capacity factor"
   ":math:`\text{CFP}_{r,s,d,t,v}`","capacity_factor_process",":math:`\mathbb{I}`","Process-specific capacity factor"
   ":math:`\text{C2A}_{r,t,v}`","capacity_to_activity",":math:`\mathbb{R}^+_0`","Converts from capacity to activity units"
   ":math:`\text{CF}_{r,p,t,v}`","cost_fixed",":math:`\mathbb{R}`","Fixed operations \& maintenance cost"
   ":math:`\text{CI}_{r,t,v}`","cost_invest",":math:`\mathbb{R}`","Tech-specific investment cost"
   ":math:`\text{CV}_{r,p,t,v}`","cost_variable",":math:`\mathbb{R}`","Variable operations \& maintenance cost"
   ":math:`\text{CON}_{r,i,t,v}`","construction_input",":math:`\mathbb{R}`","Commodities consumed by creation of process capacity"
   ":math:`\text{DEM}_{r,p,c}`","demand",":math:`\mathbb{R}^+_0`","End-use demands, by period"
   ":math:`\text{DDD}_{p,s,d}`","demand_default_distribution",":math:`\mathbb{I}`","Default demand distribution (currently not supported)"
   ":math:`\text{DSD}_{r,p,s,d,c}`","demand_specific_distribution",":math:`\mathbb{I}`","Demand-specific distribution"
   ":math:`\text{EFF}_{r,i,t,v,o}`","efficiency",":math:`\mathbb{R}^+_0`","Tech- and commodity-specific efficiency"
   ":math:`\text{EAC}_{r,i,t,v,o,e}`","emission_activity",":math:`\mathbb{R}`","Tech-specific emissions rate"
   ":math:`\text{EE}_{r,t,v,e}`","emission_embodied",":math:`\mathbb{R}`","Emissions associated with the creation of capacity"
   ":math:`\text{EEOL}_{r,t,v,e}`","emission_end_of_life",":math:`\mathbb{R}`","Emissions associated with the retirement/end of life of capacity"
   ":math:`\text{EOLO}_{r,t,v,o}`","end_of_life_output",":math:`\mathbb{R}`","Commodities produced by retirement/end of life of capacity"
   ":math:`\text{ECAP}_{r,t,v}`","existing_capacity",":math:`\mathbb{R}^+_0`","Pre-existing capacity"
   ":math:`\text{GDR}`","global_discount_rate",":math:`\mathbb{R}`","Global rate used to calculate present cost"
   ":math:`\text{LTP}_{r,t,v}`","lifetime_process",":math:`\mathbb{N}`","Tech- and vintage-specific lifetime (default=lifetime_tech)"
   ":math:`\text{LTT}_{r,t}`","lifetime_tech",":math:`\mathbb{N}`","Tech-specific lifetime (default=40 years)"
   ":math:`\text{LSC}_{r,p,t,v}`","lifetime_survival_curve",":math:`\mathbb{R}^+_0`","Surviving fraction of original capacity"
   ":math:`\text{LIT}_{r,t,e,t}`","linked_techs","text","Dummy techs used to convert CO2 emissions to physical commodity"
   ":math:`\text{LLP}_{r,t,v}`","loan_lifetime_process",":math:`\mathbb{N}`","Process-specific loan term (default=lifetime_process)"
   ":math:`\text{LR}_{r,t,v}`","loan_rate",":math:`\mathbb{R}`","Process-specific interest rate on investment cost"
   ":math:`\text{LE}_{r,p,e}`","limit_emission",":math:`\mathbb{R}^+_0`","Limit emissions by region and period"
   ":math:`\text{LA}_{r,p,t}`","limit_activity",":math:`\mathbb{R}^+_0`","Limit tech-specific activity by region and period"
   ":math:`\text{LC}_{r,p,t}`","limit_capacity",":math:`\mathbb{R}^+_0`","Limit tech-specific capacity by period"
   ":math:`\text{LR}_{r,t}`","limit_resource",":math:`\mathbb{R}^+_0`","Limit resource production by tech across time periods"
   ":math:`\text{LSF}_{r,p,s,d,t,v}`","limit_storage_level_fraction",":math:`\mathbb{R}^+_0`","Limit storage level in any time slice"
   ":math:`\text{MDY}`","myopic_discounting_year",":math:`\mathbb{N}`","Objective function NPV year when running myopically"
   ":math:`\text{PRM}_{r}`","planning_reserve_margin",":math:`\mathbb{I}`","Margin used to ensure sufficient generating capacity"
   ":math:`\text{RDH}_{r,t}`","ramp_down_hourly",":math:`\mathbb{R}`","Hourly rate at which generation techs can ramp output down"
   ":math:`\text{RUH}_{r,t}`","ramp_up_hourly",":math:`\mathbb{R}`","Hourly rate at which generation techs can ramp output up"
   ":math:`\text{SD}_{r,t}`","storage_duration",":math:`\mathbb{N}`","Storage duration per technology, specified in hours"
   ":math:`\text{SEG}_{s,d}`","segment_fraction",":math:`\mathbb{I}`","Fraction of year represented by each (s, d) tuple"
   ":math:`\text{TIS}_{r,i,t}`","tech_input_split",":math:`\mathbb{I}`","Technology input fuel ratio at time slice level"
   ":math:`\text{TISA}_{r,i,t}`","tech_input_split_annual",":math:`\mathbb{I}`","Average annual technology input fuel ratio"
   ":math:`\text{TOS}_{r,t,o}`","tech_output_split",":math:`\mathbb{I}`","Technology output fuel ratio at time slice level"
   ":math:`\text{TISA}_{r,i,t}`","tech_output_split_annual",":math:`\mathbb{I}`","Average annual technology output fuel ratio"
   ":math:`{}^*\text{LA}_{t,v}`","loan_annualize",":math:`\mathbb{R}^+_0`","Loan amortization by tech and vintage; based on :math:`DR_t`"
   ":math:`{}^*\text{MPL}_{p,t,v}`","model_process_life",":math:`\mathbb{N}`","Smaller of remaining model horizon or process tech life"
   ":math:`{}^*\text{PLF}_{r,p,t,v}`","process_life_frac",":math:`\mathbb{I}`","Fraction of available process capacity by region and period "
   ":math:`{}^*\text{LEN}_p`","period_length",":math:`\mathbb{N}`","Number of years in period :math:`p`"


.. _influential_efficiency:

efficiency
^^^^^^^^^^

:math:`{EFF}_{r \in R, i \in C_p, t \in T, v \in V, o \in C_c}`

We present the efficiency (:math:`EFF`) parameter first as it is one of the most
critical model parameters.  Beyond defining the conversion efficiency of each
process, Temoa also utilizes the indices to understand the valid input
:math:`\rightarrow` process :math:`\rightarrow` output paths for energy. For
instance, if a modeler does not specify an efficiency for a 2020 vintage coal
power plant, then Temoa will recognize any mention of a 2020 vintage coal power
plant elsewhere as an error. Generally, if a process is not specified in the
efficiency table,\ [#efficiency_table]_ Temoa assumes it is not a valid process
and will provide the user a warning with pointed debugging information.


.. _capacity_factor_tech:

capacity_credit
^^^^^^^^^^^^^^^

:math:`{CC}_{r \in R, p \in P, t \in T, v \in V}`

The capacity credit represents the fraction of total installed capacity of
a process that can be relied upon during the time slice in which peak
electricity demand occurs. This parameter is used in the :math:`reserve_margin`
constraint.

capacity_factor_tech
^^^^^^^^^^^^^^^^^^^^

:math:`{CFT}_{r \in R, s \in S, d \in D, t \in T}`

Temoa indexes the :code:`capacity_factor_tech` parameter by season, time-of-day,
and technology.

capacity_factor_process
^^^^^^^^^^^^^^^^^^^^^^^

:math:`{CFP}_{r \in R, s \in S, d \in D, t \in T, v \in V}`

In addition to :ref:`capacity_factor_tech`, there may be cases where different
vintages of the same technology have different capacity factors. For example,
newer vintages of wind turbines may have higher capacity factors. So,
:code:`capacity_factor_process` allows users to specify the capacity factor by
season, time-of-day, technology, and vintage.


capacity_to_activity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:math:`{C2A}_{r \in R, t \in T}`

Capacity and Activity are inherently two different units of measure.  Capacity
represents the maximum flow of energy per time (:math:`\frac{energy}{time}`),
while Activity is a measure of total energy actually produced. However, there are
times when one needs to compare the two, and this parameter makes those
comparisons more natural.  For example, a capacity of 1 GW for one year works
out to an activity of

.. math::

   {1 GW} \cdot {8,760 \tfrac{hr}{yr}} \cdot {3,600 \tfrac{sec}{hr}} \cdot
      {10^{-6} \tfrac{P}{G}} = {31.536 \tfrac{PJ}{yr}}

.. centered::
   or

.. math::

   {1 GW} \cdot {8,760 \tfrac{hr}{yr}} \cdot {10^{-3} \tfrac{T}{G}} = {8.75 TWh}

When comparing one capacity to another, the comparison is easy, unit wise.
However, when one *needs* to compare capacity and activity, how does one
reconcile the units?  One way to think about the utility of this parameter is in
the context of the question: "How much activity would this capacity create, if
used 100% of the time?"


cost_fixed
^^^^^^^^^^

:math:`{CF}_{r \in R, p \in P, t \in T, v \in V}`

The :code:`cost_fixed` parameter specifies the fixed cost associated with any
process.  Fixed costs are those that must be paid, regardless of how much the
process is utilized.  For instance, if the model decides to build a nuclear
power plant, even if it decides not utilize the plant, the model must pay the
fixed costs. These costs are in addition to the capital cost, so once the
capital is paid off, these costs are still incurred every year the process
exists.

Temoa's default objective function assumes the modeler has specified this
parameter in units of currency per unit capacity (:math:`\tfrac{Dollars}{Unit
Cap}`).


cost_invest
^^^^^^^^^^^

:math:`{CI}_{r \in R, t \in T, v \in P}`

The :code:`cost_invest` parameter specifies the process-specific investment cost.
Unlike the :code:`cost_fixed` and :code:`cost_variable` parameters,
:code:`cost_invest` only applies to vintages of technologies within the model
optimization horizon (:math:`\text{P}^o`).  Like :code:`cost_fixed`,
:code:`cost_invest` is specified in units of cost per unit of capacity and is
only used in the default objective function (:math:`\tfrac{Dollars}{Unit Cap}`).


cost_variable
^^^^^^^^^^^^^

:math:`{CV}_{r \in R, p \in P,t \in T,v \in V}`

The :code:`cost_variable` parameter represents the cost of a process-specific unit
of activity. Thus the incurred variable costs are proportional to the activity
of the process.


construction_input
^^^^^^^^^^^^^^^^^^

:math:`{CON}_{r \in R, i \in C^p,t \in T \setminus T^u,v \in V}`

The :code:`construction_input` parameter allows the modeller to attach commodity
input flows to the production of new capacity, in units of activity per unit
capacity. Assumes that capacity is produced evenly over years in its vintage
period.


.. _demand:

demand
^^^^^^

:math:`{DEM}_{r \in R, p \in P, c \in C^d}`

The :code:`demand` parameter allows the modeler to define the total end-use
demand levels for all periods.  In combination with the :code:`efficiency`
parameter, this parameter is the most important because without it, the rest of
model has no incentive to build anything.  This parameter specifies the end-use
demands that appear at the far right edge of the system diagram.

To specify the distribution of demand, look to the
:code:`demand_default_distribution` (DDD) and :code:`demand_specific_distribution`
(DSD) parameters.

As a historical note, this parameter was at one time also indexed by season and
time of day, allowing modelers to specify exact demands for every time slice.
However, while extremely flexible, this proved too tedious to maintain for any
data set of appreciable size.  Thus, we implemented the DDD and DSD parameters.


.. _DDD:

demand_default_distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:math:`{DDD}_{s \in S, d \in D}`

**Note**:  The Demand Specific Distribution is currently not supported in
the project.  Modelers should use the DSD or rely on a "flat" distribution default
from the time_segment_fraction.

By default, Temoa assumes that end-use demands (:ref:`Demand`) are evenly
distributed throughout a year.  In other words, the Demand will be apportioned
by the :code:`segment_fraction` parameter via:

.. math::

   \text{EndUseDemand}_{s, d, c} = {segment_fraction}_{s, d} \cdot {Demand}_{p, c}

Temoa enables this default action by automatically setting DDD equivalent to
:code:`segment_fraction` for all seasons and times of day.  If a modeler would like a
different default demand distribution, the indices and values of the DDD
parameter must be specified.  Like the :ref:`segment_fraction` parameter, the sum of
DDD must be 1.


demand_specific_distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:math:`{DSD}_{r \in R, s \in S, d \in D, c \in C^d}`

If there is an end-use demand that varies over the course of a day or across
seasons -- for example, heating or cooling in the summer or winter -- the
modeler may specify the fraction of annual demand occurring in each time slice.
Like :ref:`segment_fraction` and :ref:`DDD`, the sum of DSD for each :math:`c` must be 1.
If the modeler does not define DSD for a season, time of day, and demand
commodity, Temoa automatically populates this parameter according to DDD.
It is this parameter that is actually multiplied by the :code:`Demand` parameter
in the Demand constraint.


emission_activity
^^^^^^^^^^^^^^^^^

:math:`{EAC}_{e \in C_e,\{r,i,t,v,o\} \in \Theta_{\text{efficiency}}}`

Temoa currently has two methods for enabling a process to produce an output: the
:code:`efficiency` parameter, and the :code:`emission_activity` parameter.  Where
the :code:`efficiency` parameter defines the amount of output energy a process
produces per unit of input, the :code:`emission_activity` parameter allows for
secondary outputs.  As the name suggests, this parameter was originally intended
to account for emissions per unit activity, but it more accurately describes
*parallel* activity.  It is restricted to emissions accounting (by the
:math:`e \in C^e` set restriction).


emission_embodied
^^^^^^^^^^^^^^^^^

:math:`{EE}_{r \in R,t \in T \setminus T^u, v \in V,e \in C_e}`

Like the emission_activity parameter, but attaches emission outputs to the creation
of capacity instead of activity flows. Assumes that capacity is produced evenly
over each year in the deployment vintage.


emission_end_of_life
^^^^^^^^^^^^^^^^^^^^

:math:`{EEOL}_{r \in R,t \in T \setminus T^u, v \in V,e \in C_e}`

Like emission_embodied, but attaches emissions to the retirement/end of life of
capacity rather than production of capacity. Assumes that retirement or end of
life occur evenly over years in that period.


end_of_life_output
^^^^^^^^^^^^^^^^^^

:math:`{EOLO}_{r \in R,t \in T \setminus T^u, v \in V,o \in C_p}`

Like construction_input, but attaches flows to the retirement/end of life of
capacity rather than production of capacity. Assumes that retirement or end of
life occur evenly over years in that period.


.. limit_emission
.. ^^^^^^^^^^^^^

.. :math:`{LE}_{r \in R, p \in P, e \in C^e}`

.. The :code:`emission_limit` parameter ensures that Temoa finds a solution that
.. fits within the modeler-specified limit of emission :math:`e` in time period
.. :math:`p`.


existing_capacity
^^^^^^^^^^^^^^^^^

:math:`{ECAP}_{r \in R, t \in T, v \in \text{P}^e}`

The :code:`existing_capacity` parameter defines the capacity installed prior to the
beginning of :code:`time_optimize`. Note that processes with existing capacity
require all of the engineering-economic characteristics of a standard process,
with the exception of an investment cost.

retired_capacity
^^^^^^^^^^^^^^^^

:math:`{ECAP}_{r \in R, t \in T, v \in \text{P}^e}`

The :code:`existing_capacity` parameter defines the capacity installed prior to the
beginning of :code:`time_optimize`. Note that processes with existing capacity
require all of the engineering-economic characteristics of a standard process,
with the exception of an investment cost.

.. _GDR:

global_discount_rate
^^^^^^^^^^^^^^^^^^^^

:math:`{GDR}`

The :code:`GDR` parameter represents the global discount rate used to convert
cash flows in future model time periods into a present value. The future value
(FV) of a sum of currency is related to the net present value (NPV) via the
formula:

.. math::

   \text{FV} = \text{NPV} \cdot {(1 + GDR)^n}

where :math:`n` is in years.  This parameter is used to calculate all discounted
costs, which are the basis of the objective function.  Costs are discounted to the
first future time period in the model by default.  If running a Myopic run, the
discount base year can be set in the metadata table.  This is the :code:`myopic_base_year`.

The output in the :code:`output_cost` table shows both discounted and non-discounted (raw)
values for all model costs.  Of note, all loan costs are displayed as an annuity cost in
the vintage year, not as a string of payments.

The Global Discount Rate is entered in the metadata_real table in the database.

growth_rate_max
^^^^^^^^^^^^^^^

:math:`{GRM}_{r \in R, t \in T}`

The :code:`GRM` parameter defines the maximum annual rate at which the capacity of
a given technology can grow. Note that the growth rate is not defined by vintage,
but rather across all vintages of a given technology.


growth_rate_seed
^^^^^^^^^^^^^^^^

:math:`{GRS}_{r \in R, t \in T}`

The :code:`GRS` parameter defines the maximum capacity of a given technology when
first installed in a given time period. The growth rate is applied to this initial
capacity seed in subsequent time periods.


loan_lifetime_process
^^^^^^^^^^^^^^^^^^^^^

:math:`{LLP}_{r \in R, t \in T, v \in P}`

**Note**:  :code:`LifetimeLoanProcess` is currently not supported in the database.
Modelers should use the :code:`loan_lifetime_tech` below.

Temoa gives the modeler the ability to separate the loan lifetime from the
useful life of a process.  This parameter specifies the loan term associated
with capital investment in a process, in years.  If not specified, the model
assigns the technology lifetime to the loan period in :code:`temoa/components/technology.py`.


loan_lifetime_tech
^^^^^^^^^^^^^^^^^^

:math:`{LLT}_{r \in R, t \in T}`

Same as the :code:`loan_lifetime_process` but without the vintage index. If all
vintages of a given technology are assumed to have the same loan term, then
:code:`loan_lifetime_tech` can be defined instead of :code:`loan_lifetime_process`.


lifetime_process
^^^^^^^^^^^^^^^^

:math:`{LTP}_{r \in R, t \in T, v \in P}`

This parameter specifies the total useful life of a given process in years.


lifetime_tech
^^^^^^^^^^^^^

:math:`{LTT}_{r \in R, t \in T}`

Similar to lifetime_process, this parameter specifies the total useful life of a
given technology in years. If all vintages of a given technology have the same
lifetime, then :code:`LifeTimeTech` can be used instead of :code:`LifeTimeProcess`.


linked_techs
^^^^^^^^^^^^

:math:`{LIT}_{r \in R, t \in T, e \in C^e, t \in T}`

In power-to-gas pathways, :math:`CO2` is an input to some processes, including
synthetic natural gas production and liquid fuel production via Fischer-Tropsch.
Within the model, :math:`CO2` must be converted from an emissions commodity to a
physical commodity that can be included in the :code:`efficiency` table. The
:code:`linked_techs` parameter specifies the dummy technology used to convert an
emissions commodity to a physical commodity. Note that the first :code:`t`
represents the primary upstream technology linked to the dummy linked technology,
which is represented by the second :code:`t` index.


loan_rate
^^^^^^^^^

:math:`{LR}_{r \in r, t \in T, v \in V}`

The interest rate used for loans supporting investment costs.  The default
loan rate is accessible in the metadata_real table in the database.


.. _ParamMaxCapacity:


max_activity
^^^^^^^^^^^^

:math:`{MAA}_{r \in R, p \in P, t \in T}`

The :code:`max_activity` parameter is used to constrain the total activity (i.e.,
energy production) from a given technology in each model time period. Note that the
total activity is constrained across all vintages of a technology. This parameter
is used in the :code:`max_activity_constraint`.


max_capacity
^^^^^^^^^^^^

:math:`{MAC}_{r \in R, p \in P, t \in T}`

The :code:`max_capacity` parameter represents an upper bound on the total installed
capacity of a given technology in each model time period. Note that the total
capacity is constrained across all vintages of a technology. This parameter is
used in the :code:`max_capacity_constraint`.


max_capacity_sum
^^^^^^^^^^^^^^^^

:math:`{MCS}_{t \in T}`

Similar to the :code:`max_capacity` parameter, but represents an upper bound on
the total installed capacity across all model time periods. In addition,
this parameter specifies the upper bound on a group of technologies specified
in the :code:`tech_capacity_max` subset. This parameter is used in the
:code:`MaxCapacitySet_constraint`.


max_resource
^^^^^^^^^^^^

:math:`{MAR}_{r \in R, t \in T}`

**Note**:  The max_resource parameter/constraint is currently not supported in the model.

The :code:`max_resource` parameter represents an upper bound on the cumulative
amount of commodity that can be produced by region and technology over the model time
horizon. This parameter is used in :code:`max_resource_constraint`. Note that
this parameter differs from :code:`resource_bound`, which is also indexed by
model time period.


min_activity
^^^^^^^^^^^^

:math:`{MIA}_{r \in R, p \in P, t \in T}`

The :code:`min_activity` parameter represents a lower bound on the total activity (i.e.,
energy production) of a given technology in each model time period. Note that the
total activity is constrained across all vintages of a technology. This parameter
is used in the :code:`min_activity_constraint`.


min_capacity
^^^^^^^^^^^^

:math:`{MIC}_{r \in R, p \in P,t \in T}`

The :code:`min_capacity` parameter represents a lower bound on the total installed
capacity of a given technology in each model time period. Note that the total
capacity is constrained across all vintages of a technology. This parameter is
used in the :code:`min_capacity_constraint`.


min_capacity_sum
^^^^^^^^^^^^^^^^

:math:`{MCS}_{t \in T}`

The :code:`min_capacity_sum` parameter represents the minimum cumulative
capacity associated with technologies belonging to :code:`tech_group`.
This parameter is used in the :code:`min_activityGroup_constraint`.


min_gen_group_target
^^^^^^^^^^^^^^^^^^^^

:math:`{MGT}_{r \in R}`

The :code:`min_gen_group_target` parameter is similar to :code:`min_activity`, but
represents a minimum activity limit for a user-defined technology group
(:code:`tech_groups`) rather than a single technology. This parameter is used
in the :code:`min_activityGroup_constraint`.


min_gen_group_weight
^^^^^^^^^^^^^^^^^^^^

:math:`{MGW}_{r \in R, t \in T}`

The :code:`min_gen_group_weight` parameter represents a weight that is applied
to each technology within each :code:`tech_group`, which determines the
technology-specific activity shares that can count towards meeting the
:code:`min_activityGroup_constraint`.


myopic_base_year
^^^^^^^^^^^^^^^^

:math:`MBY`

Temoa is typically run in "perfect foresight" mode, where all decision variables
in all time periods are solved simultaneously. However, it is also possible to
solve the model myopically, whereby the model solves a subset of time periods
in sequence. The :code:`myopic_base_year` parameter specifies the base year to which
all future costs are discounted.  This parameter is located in the :code:`metadata`
table in the database.


planning_reserve_margin
^^^^^^^^^^^^^^^^^^^^^^^

:math:`{PRM}_{r \in R}`

The :code:`planning_reserve_margin` parameter specifies that capacity reserve margin
in the electric sector by region. The capacity reserve margin represents the
installed generating capacity - expressed as a share of peak load - that must be
available to meet contingencies. Note that since electricity demand is often
endogeous in Temoa databases, we calculate electricity production by time slice
to estimate the peak electricity demand. This parameter is used in
:code:`ReserveMargin_constraint`.


ramp_down
^^^^^^^^^

:math:`{RMD}_{r \in R, t \in T}`

To account for the limited ramping capability of some thermal generators, a
ramp down rate can be specified via the :code:`ramp_down` parameter. The specified
value represents the fraction of installed capacity that can be ramped down when moving
from one time slice to the next. There is an equivalent :code:`ramp_up` parameter, to
specify ramping limits in the upward direction. This parameter is used in the
:code:`ramp_down_day_constraint` and `ramp_down_season_constraint`. The former constrains
the downward ramp rate between time-of-day slices, and the latter constrains the downward
ramp rate between the last time-of-day slice in a given season and the first time-of-day
slice in the next season.


ramp_up
^^^^^^^

:math:`{RMU}_{r \in R, t \in T}`

To account for the limited ramping capability of some thermal generators, a
ramp up rate can be specified via the :code:`ramp_up` parameter. The specified
value represents the fraction of installed capacity that can be ramped up when moving
from one time slice to the next. There is an equivalent :code:`ramp_down` parameter, to
specify ramping limits in the downward direction. This parameter is used in the
:code:`ramp_up_day_constraint` and `ramp_up_season_constraint`. The former constrains
the upward ramp rate between time-of-day slices, and the latter constrains the upward
ramp rate between the last time-of-day slice in a given season and the first time-of-day
slice in the next season.


resource_bound
^^^^^^^^^^^^^^

:math:`{RSC}_{r \in R, p \in P, c \in C_p}`

This parameter allows the modeler to specify commodity production limits per period.
Note that a constraint in one period does not relate to any other periods.  For
instance, if the modeler specifies a limit in period 1 and does not specify a
limit in period 2, then the model may use as much of that resource as it would
like in period 2. This parameter is used in :code:`ResourceExtraction_constraint`.
Note that the :code:`max_resource` parameter is similar, but constrains total
cumulative resource consumption across all model time periods.


.. _segment_fraction:

segment_fraction
^^^^^^^^^^^^^^^^

:math:`{SEG}_{s \in S,d \in D}`

The :code:`segment_fraction` parameter specifies the fraction of the year represented by
each combination of season and time of day.  The sum of all combinations within
:code:`segment_fraction` must be 1, representing 100% of a year.


storage_duration
^^^^^^^^^^^^^^^^

:math:`{SD}_{r \in R, t \in T^{S}}`

The :code:`storage_duration` parameter represents the number of hours over which
storage can discharge if it starts at full charge and produces maximum output
until empty. The parameter value defaults to 4 hours if not specified by the user.


storage_init
^^^^^^^^^^^^

:math:`{SI}_{r \in R, t \in T^{S}, v \in P}`

The :code:`storage_init` parameter determines the initial charge level associated
with each storage technology. The value should be expressed as a fraction between
0 and 1.

Note 1:  that this is an optional parameter and should only be used if the
user wishes to set the initial charge rather than allowing the model to optimize it.

Note 2:  This initialization is currently *not supported*.  Values in the storage_init
table will be ignored and a log warning will be generated.


tech_input_split
^^^^^^^^^^^^^^^^^^^^^^^

:math:`{TIS}_{r \in R, p \in P, i \in C_p, t \in T}`

Some technologies have a single output but have multiple input fuels. The
:code:`tech_input_split` parameter fixes the shares of commodity input to a
specific technology in a given period. Note that this fixed share is maintained
across all model time slices. This parameter is used in
:code:`TechInputSplit_constraint`.


tech_input_split_average
^^^^^^^^^^^^^^^^^^^^^^^^

:math:`{TISA}_{r \in R, p \in P, i \in C_p, t \in T}`

The :code:`tech_input_split_average` is similar to :code:`tech_input_split`, as
they both fix input commodity shares to technologies with multiple inputs.
However, :code:`tech_input_split_average` only fixes the average shares at the
annual level, allowing the shares at the time slice level to vary. This
parameter is used in :code:`TechInputSplitAverage_constraint`.


tech_output_split
^^^^^^^^^^^^^^^^^

:math:`{TOS}_{t \in T, o \in C_c}`

Some technologies have a single input fuel but have multiple outputs. The
:code:`tech_output_split` parameter fixes the shares of commodity input to a
specific technology in a given period. Note that this fixed share is maintained
across all model time slices. This parameter is used in
:code:`TechOutputSplit_constraint`.


\*loan_annualize
^^^^^^^^^^^^^^^^

:math:`{LA}_{r \in R, t \in T, v \in P}`

This is a model-calculated parameter based on the process-specific loan length
(its indices are the same as the :code:`LifetimeLoan` parameter), and
process-specific discount rate (the :code:`DiscountRate` parameter).  It is
calculated via the formula:

.. math::

   LA_{t,v} = \frac{DR_{r,t,v}}{1 - (1 + DR_{r,t,v})^{{}^- LLN_{r,t,v}}}

   \forall \{t, v\} \in \Theta_{\text{cost\_invest}}


model_process_life
^^^^^^^^^^^^^^^^^^

:math:`{MPL}_{r \in R, p \in P, t \in T, v \in P}`

The :code:`model_process_life` parameter is internally-derived by the model calculated in
:code:`ParamModelProcessLife_rule` and which makes use of the :code:`lifetime_process`
parameter. For a given technology vintage in a given model time period, it returns the
lesser of the period length and the remaining process lifetime. This parameter is used
to sum the annual :code:`fixed_costs` and :code:`variable_costs` across all years within
a given time period.


\*period_length
^^^^^^^^^^^^^^^

:math:`{LEN}_{p \in P}`

Given that the modeler may specify arbitrary time period boundaries, this
parameter specifies the number of years contained in each period. The final year
is the largest element in :code:`time_future` which is specifically not included
in the list of periods in :code:`time_optimize` (:math:`\text{P}^o`). The length
calculation for each period then exploits the fact that the ``time`` sets are
ordered:

.. math::

   \text{LET boundaries} & = \text{sorted}(\text{P}^f) \\
   \text{LET I(p)} & = \text{index of p in boundaries} \\
   & \therefore \\
   {LEN}_p & = \text{boundaries}[ I(p) + 1 ] - p

   \forall p \in P

The first line creates a sorted array of the period boundaries, called
*boundaries*.  The second line defines a function `I` that finds the index of
period :math:`p` in boundaries. The third line then defines the length of period
:math:`p` to be the number of years between period :math:`p` and the next
period.  For example, if :math:`\text{P}^f = \{2015, 2020, 2030, 2045\}`,
then *boundaries* would be :code:`[2015, 2020, 2030, 2045]`.  For 2020, I(2020)
would return 2.  Similarly, boundaries[ 3 ] = 2030.  Then,

.. math::
   {LEN}_{2020} & = \text{boundaries}[I(2020) + 1] - (2020) \\
   & = \text{boundaries} [2 + 1] - 2020                     \\
   & = \text{boundaries} [3] - 2020                         \\
   & = 2030 - 2020                                          \\
   & = 10

Note that LEN is only defined for elements in :math:`\text{P}^o`, and is
specifically not defined for the final element in :math:`\text{P}^f`.


\*process_life_frac
^^^^^^^^^^^^^^^^^^^

:math:`{PLF}_{r \in R, p \in P,t \in T,v \in P}`

The modeler may specify a useful lifetime of a process such that the process
will be decommissioned part way through a period.  Rather than attempt to
delineate each year within that final period, Temoa averages the total output
of the process over the entire period but limits the available capacity and
output of the decommissioning process by the ratio of how long through the
period the process is active.  This parameter is that ratio, formally defined
as:

.. math::

   PLF_{p,t,v} = \frac{v + LTP_{t,v} - p}{LEN_p}

   \\
   \forall \{p,t,v\} & \in \Theta_\text{Activity by PTV} | \\
   v + LTP_{t,v} & \notin P, \\
   v + LTP_{t,v} & \le max(F), \\
   p & = max(P | p < v + LTP_{t,v})

Note that this parameter is defined over the same indices as
:code:`cost_variable` -- the active periods for each process :math:`\{p, t,
v\}`.  As an example, if a model has :math:`P = \{2010, 2012,
2020, 2030\}`, and a process :math:`\{t, v\} = \{car, 2010\}` has a useful
lifetime of 5 years, then this parameter would include only the first two
activity indices for the process.  Namely, :math:`p \in \{2010, 2012\}` as
:math:`\{p, t, v\} \in \{\{2010, car, 2010\}, \{2012, car,
2010\}\}`.  The values would be :math:`{TLF}_{2010, car, 2010} = 1`, and
:math:`{TLF}_{2012, car, 2010} = \frac{3}{8}`.


Variables
---------

.. _table_variable:
.. csv-table:: Temoa's Main Variables
   :header: "Variable","Temoa Name","Domain","Short Description"
   :widths: 18, 22, 10, 50

   ":math:`FO_{r,p,s,d,i,t,v,o}`","v_flow_out",":math:`\mathbb{R}^+_0`","Commodity flow by time slice out of a tech based on a given input"
   ":math:`FOA_{r,p,s,d,i,t,v,o}`","v_flow_out_annual",":math:`\mathbb{R}^+_0`","Annual commodity flow out of a tech based on a given input"
   ":math:`FIS_{r,p,s,d,i,t,v,o}`","v_flow_in",":math:`\mathbb{R}^+_0`","Commodity flow into a storage tech to produce a given output"
   ":math:`FLX_{r,p,s,d,i,t,v,o}`","v_flex",":math:`\mathbb{R}^+_0`","The portion of commodity production exceeding demand"
   ":math:`FLXA_{r,p,i,t,v,o}`","v_flex_annual",":math:`\mathbb{R}^+_0`","The portion of commodity production from constant production techs exceeding demand"
   ":math:`CUR_{r,p,s,d,i,t,v,o}`","v_curtailment",":math:`\mathbb{R}^+_0`","Commodity flow out of a tech that is curtailed"
   ":math:`CAP_{r,t,v}`","v_capacity",":math:`\mathbb{R}^+_0`","Required tech capacity to support associated activity"
   ":math:`CAPAVL_{r,p,t}`","v_capacity_available_by_period_and_tech",":math:`\mathbb{R}^+_0`","Derived variable representing the capacity of technology :math:`t` available in period :math:`p`"
   ":math:`SI_{r,t,v}`","v_storage_init",":math:`\mathbb{R}^+_0`","Initial charge level associated with storage techs"
   ":math:`SL_{r,p,s,d,t,v}`","v_storage_level",":math:`\mathbb{R}^+_0`","Charge level each time slice associated with storage techs"
   ":math:`SSL_{r,p,s,t,v}`","v_seasonal_storage_level",":math:`\mathbb{R}^+_0`","Base charge level of sequential seasons for seasonal storage"
   ":math:`RCAP_{r,p,t,v}`","v_retired_capacity",":math:`\mathbb{R}^+_0`","Capacity retired before end of life"
   ":math:`ART_{r,p,t,v}`","v_annual_retirement",":math:`\mathbb{R}^+_0`","Annualised capacity retiring or reaching end of life"
   ":math:`NCAP_{r,t,v}`","v_new_capacity",":math:`\mathbb{R}^+_0`","New deployed capacity"

v_flow_out
^^^^^^^^^^

:math:`FO_{r,p,s,d,i,t,v,o}`

The most fundamental variable in the Temoa formulation is the
:code:`v_flow_out` variable. It describes the commodity flow out of a
process in a given time slice. To balance input and output flows in the
:code:`CommodityBalance_constraint`, the commodity flow into a given
process can be calculated as
:math:`\sum_{T, V, O} \textbf{FO}_{p, s, d, c, t, v, o}
/EFF_{c,t,v,o}`.

v_flow_out_annual
^^^^^^^^^^^^^^^^^

:math:`FOA_{r,p,i,t,v,o}`

Similar to :code:`v_flow_out`, but used for technologies that are members
of the :code:`tech_annual` set, whose output does not vary across seasons
and times-of-day. Eliminating the :code:`s,d` indices for these technologies
improves computational performance.


v_flex
^^^^^^

:math:`FLX_{r,p,s,d,i,t,v,o}`

In some cases, the overproduction of a commodity may be required, such
that supply exceeds the endogenous demand. Refineries represent a
common example, where the share of different refined products are governed
by tech_output_split, but total production is driven by a particular commodity.
For example, gasoline production may be artificially constrained in order to
ensure the appropriate balance for lower demand fuels such as propane or
kerosene. Instead, we allow overproduction, i.e., production exceeding
endogenous demand, for commodities produced by technologies belonging to
the :code:`tech_flex` set. In the example above, adding the refinery to
the :code:`tech_flex` set allows for the overproduction of propane and
kerosene, allowing the model to fulfill the endogenous demand
for gasoline. This flexible technology designation activates a slack
variable (:math:`\textbf{FLX}_{r, p, s, d, i, t, v, c}`)representing
the excess production in the :code:`CommodityBalanceAnnual_constraint`.


v_flex_annual
^^^^^^^^^^^^^

:math:`FLXA_{r,p,i,t,v,o}`

Similar to :code:`v_flex`, but used for technologies that are members
of the :code:`tech_flex` set, whose output does not vary across seasons
and times-of-day. Eliminating the :code:`s,d` indices for these technologies
improves computational performance.


v_curtailment
^^^^^^^^^^^^^

:math:`CUR_{r,p,s,d,i,t,v,o}`

The :code:`v_curtailment` variable is an accounting tool to help calculate
the unused production capacity of technologies annotated in the Technology
database table as curtailable technologies belonging to the
:code:`tech_curtailment` set.
Renewables such as wind and solar are often placed in this set. While we
used to simply formulate the :code:`Capacity` and :code:`CommodityBalance`
constraints as inequalities that implicitly allowed for curtailment, this
simpler approach does not work with renewable targets because the curtailed
portion of the electricity production counts towards the target, and there is
no way to distinguish it from the useful production. Including an explicit
curtailment term addresses the issue.  Curtailment in the model is simply
the production activity that is not used in the model and is reported as
such in the output_curtailment table.  Note:  Outputs presented in the
`output_curtailment` table for curtailment (the table separately includes
flex outputs) are limited by Capacity Factor.  Meaning:  if a tech has a
capacity of 10 units, and a CF of 0.8 and a usage of 5 units, then the reported
curtailment is 3 units (0.8 x 10 - 5).


v_flow_in_storage
^^^^^^^^^^^^^^^^^

:math:`FIS_{r,p,s,d,i,t,v,o}`

Because the production and consumption associated with storage techs occur
across different time slices, the comodity flow into a storage technologiy
cannot be discerned from :code:`v_flow_out`. Thus an explicit :math:`flow_in`
variable is required for storage.

v_capacity
^^^^^^^^^^

:math:`CAP_{r,t,v}`

The :code:`v_capacity` variable determines the required capacity of all processes
across the user-defined system.  It is indexed for each process (t,v), and Temoa
constrains the capacity variable to be able to meet the total commodity flow out
of that process in all time slices in which it is active :eq:`Capacity`.

v_capacity_available_by_period_and_tech
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:math:`CAPAVL_{r,p,t}`

:code:`CapacityAvailableByPeriodAndTech` is a convenience variable that is
not strictly necessary, but used where the individual vintages of a technology
are not warranted (e.g. in calculating the maximum or minimum total capacity
allowed in a given time period).

v_storage_init
^^^^^^^^^^^^^^

:math:`SI_{r,t,v}`

The :code:`v_storage_init` variable determines the initial storage charge level
at the beginning of the first time slice within a given time period. Each vintage
of each technology can have a different optimal initial value. Note that
this value also determines the ending storage charge level at the end of the
last time slice within each model time period.

v_storage_level
^^^^^^^^^^^^^^^

:math:`SL_{r,p,s,d,t,v}`

The :code:`v_storage_level` variable tracks the storage charge level across ordered
time slices and is critical to ensure that storage charge and dispatch is constrained
by the energy available in the storage units.



We explain the equations governing these variables the :ref:`Constraints`
section.


.. _constraints:

Equations
---------

There are four main equations that govern the flow of energy through the model
network.  The :code:`Demand_Constrant` :eq:`Demand` ensures that the supply meets
demand in every time slice.  For each process, the :code:`Capacity_constraint` :eq:`Capacity`
ensures that there is sufficient capacity to meet the optimal commodity flows across all
time slices. Between processes, the :code:`CommodityBalance_constraint` :eq:`CommodityBalance`
ensures that global commodity production across the energy system is sufficient to meet the
endogenous demands for that commodity. Finally, the objective function :eq:`obj_invest` drives
the model to minimize the system-wide cost of energy supply by optimizing the deployment and
utilization of energy technologies across the system.

One additional point regarding the model formulation. Technologies that
produce constant annual output can be placed in the :code:`tech_annual` set.
While not required, doing so improves computational performance by eliminating the
season and time of day :code:`(s,d)` indices associated with these technologies.
In order to ensure the model functions correctly with these simplified technologies,
slightly different formulations of the capacity and commodity balance constraints
are required. See the :code:`AnnualCommodityBalance_constraint` and
:code:`CapacityAnnual_constraint` :eq:`CapacityAnnual` below for details.

The rest of this section defines each model constraint, with a rationale for
existence.  We use the implementation-specific names for the constraints to
highlight the organization of the functions within the actual code. Note that
the definitions below are pulled directly from the docstrings embedded in
:code:`temoa/components/`.


.. _DecisionVariables:

Constraints Defining Derived Decision Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These first four constraints define derived variables that are used within
the model. The :code:`Capacity_constraint` and :code:`CapacityAnnual_constraint`
are particularly important because they define the relationship between installed
capacity and allowable commodity flow.

.. autofunction:: temoa.components.capacity.capacity_constraint

.. autofunction:: temoa.components.capacity.capacity_annual_constraint

.. autofunction:: temoa.components.capacity.adjusted_capacity_constraint

.. autofunction:: temoa.components.capacity.annual_retirement_constraint

.. autofunction:: temoa.components.capacity.capacity_available_by_period_and_tech_constraint


.. _NetworkConstraints:

Network Constraints
^^^^^^^^^^^^^^^^^^^

These three constraints define the core of the Temoa model; together, they
define the algebraic energy system network.

.. autofunction:: temoa.components.commodities.demand_constraint

.. autofunction:: temoa.components.commodities.commodity_balance_constraint

.. autofunction:: temoa.components.commodities.annual_commodity_balance_constraint


Physical and Operational Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These constraints fine-tune the model formulation to account for
various physical and operational real-world phenomena.

.. autofunction:: temoa.components.operations.baseload_diurnal_constraint

.. autofunction:: temoa.components.commodities.demand_activity_constraint

.. autofunction:: temoa.components.storage.storage_energy_constraint

.. autofunction:: temoa.components.storage.seasonal_storage_energy_constraint

.. autofunction:: temoa.components.storage.storage_energy_upper_bound_constraint

.. autofunction:: temoa.components.storage.seasonal_storage_energy_upper_bound_constraint

.. autofunction:: temoa.components.storage.storage_charge_rate_constraint

.. autofunction:: temoa.components.storage.storage_discharge_rate_constraint

.. autofunction:: temoa.components.storage.storage_throughput_constraint

.. autofunction:: temoa.components.operations.ramp_up_day_constraint

.. autofunction:: temoa.components.operations.ramp_down_day_constraint

.. autofunction:: temoa.components.operations.ramp_up_season_constraint

.. autofunction:: temoa.components.operations.ramp_down_season_constraint

.. autofunction:: temoa.components.reserves.reserve_margin_static

.. autofunction:: temoa.components.reserves.reserve_margin_dynamic


Objective Function
^^^^^^^^^^^^^^^^^^

.. autofunction:: temoa.components.costs.annuity_to_pv

.. autofunction:: temoa.components.costs.pv_to_annuity

.. autofunction:: temoa.components.costs.fv_to_pv

.. autofunction:: temoa.components.costs.total_cost_rule


User-Specific Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^

The constraints provided in this section are not required for proper system
operation, but allow the modeler some further degree of system specification.

..  commented out... not used?
    .. autofunction:: temoa.components.capacity.existing_capacity_constraint

.. autofunction:: temoa.components.limits.limit_emission_constraint

.. autofunction:: temoa.components.limits.limit_activity_constraint

.. autofunction:: temoa.components.limits.limit_activity_share_constraint

.. _max_capacity_constraint:

.. autofunction:: temoa.components.limits.limit_capacity_constraint

.. autofunction:: temoa.components.limits.limit_new_capacity_constraint

.. autofunction:: temoa.components.limits.limit_capacity_share_constraint

.. autofunction:: temoa.components.limits.limit_new_capacity_share_constraint

.. autofunction:: temoa.components.limits.limit_resource_constraint

.. _TechOutputSplit_constraint:

.. autofunction:: temoa.components.limits.limit_tech_input_split_constraint

.. autofunction:: temoa.components.limits.limit_tech_output_split_constraint

.. autofunction:: temoa.components.limits.limit_tech_input_split_annual_constraint

.. autofunction:: temoa.components.limits.limit_tech_output_split_annual_constraint

.. autofunction:: temoa.components.limits.limit_tech_input_split_average_constraint

.. autofunction:: temoa.components.limits.limit_tech_output_split_average_constraint

.. autofunction:: temoa.components.limits.limit_annual_capacity_factor_constraint

.. autofunction:: temoa.components.limits.limit_seasonal_capacity_factor_constraint

.. autofunction:: temoa.components.storage.limit_storage_fraction_constraint

.. autofunction:: temoa.components.limits.limit_growth_capacity

.. autofunction:: temoa.components.limits.limit_growth_new_capacity

.. autofunction:: temoa.components.limits.limit_growth_new_capacity_delta



General Caveats
---------------

Temoa does not currently provide an easy avenue to track multiple concurrent
energy flows through a process.  Consider a cogeneration plant.  Where a
conventional power plant might simply emit excess heat as exhaust, a
cogeneration plant harnesses some or all of that heat for heating purposes,
either very close to the plant, or generally as hot water for district heating.
Temoa's flow variables can track both flows through a process, but each flow
will have its own efficiency from the efficiency parameter.  This implies that
to produce 1 unit of electricity will require :math:`\frac{1}{elc eff}` units of
input.  At the same time, to produce 1 unit of heat will require units of input
energy, and to produce both output units of heat and energy, both flows must be
active, and the desired activity will be double-counted by Temoa.

To model a parallel output device (c.f., a cogeneration plant), the modeler must
currently set up the process with the :code:`tech_input_split` and
:code:`tech_output_split` parameters, appropriately adding each flow to the
efficiency parameter and accounting for the overall process efficiency through
all flows.
