In a mathematical model like Temoa, sets are used to index parameters and
variables. To enable the modeler to translate between the algebraic formulation,
input database, and model code, we provide the mathematical notation used in the
model formulation, as well as the associated names in the
Python code and database schema in the tables below. The code representation is
more verbose than the algebraic version, using full words.

Our discussion of sets is broken down into several logical categories to make it
easier to parse. The **first group of sets pertains to Temoa's treatment of time**,
as shown below. **Note:** Some entries in the "Database Table" column are
comma-separated. In those cases, the first element refers to the name of the database
table, and the second refers to specific column within the database table used to
identify a specific subset. For example, in the first table below, :code:`time_period`
is the master set and :code:`time_exist` is a subset that defines the user-defined
model time periods to define historical technology vintages that exist prior to
the model's time horizon for optimization.


.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{P}^e`", ":code:`time_period, flag = e`", ":code:`time_exist`", "model periods prior to the beginning of the optimization time horizon"
   ":math:`\text{P}^f`", ":code:`time_period, flag = f`", ":code:`time_future`", "model periods within the optimization time horizon"
   ":math:`{}^*\text{P}^o`", ":code:`time_period`", ":code:`time_optimize`", "model time periods to optimize, (:math:`\text{P}^f - \text{max}(\text{P}^f)`); the last time period is removed as it represents the end of the final period"
   ":math:`{}^*\text{V}`", ":code:`time_period`", ":code:`vintage_exist`, :code:`vintage_optimize`, :code:`vintage_all`", "tech vintages, (:math:`\text{P}^e \cup \text{P}^o`), derived from time period set and used to track technology vintages across time periods"
   ":math:`\text{D}`", ":code:`time_of_day`", ":code:`time_of_day`", "intraday time divisions; each entry carries an :code:`hours` value (default 1) specifying how many hours it represents"
   ":math:`\text{S}`", ":code:`time_season`", ":code:`time_season`", "intra-annual divisions (e.g. seasons or representative days); each entry carries a :code:`segment_fraction` giving its share of the year; ordered by :code:`sequence` column"
   "", ":code:`time_season_sequential`", ":code:`time_season_sequential, ordered_season_sequential`", "superimposed sequential seasons used for seasonal storage and inter-season ramping; only required when :code:`time_sequencing = 'representative_periods'`"

The sets in the table below define Temoa's representation of **regions**.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{R}`", ":code:`region`", ":code:`regions`", "distinct geographical regions"
   "", ":code:`region`", ":code:`regional_indices`", "set of all the possible combinations of interregional exchanges plus original region indices"
   "", "", ":code:`regional_global_indices`", "set of all used combinations of interregional exchanges plus original region indices and groups"

The sets below define how technologies are represented within Temoa. Because technologies
can serve many different functions across an energy system, we need to define a large
number of **technology subsets**.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`{}^*\text{T}`", ":code:`technology`", ":code:`tech_all`", "all technologies to be modeled (in v4, all technologies are production-type: :math:`T = T^p`)"
   ":math:`\text{T}^p`", ":code:`technology, flag LIKE 'p%'`", ":code:`tech_production`", "all production technologies, including baseload and storage (:math:`{T}^b \cup {T}^s \subset {T}^p`)"
   ":math:`\text{T}^b`", ":code:`technology, flag = pb`", ":code:`tech_baseload`", "baseload electric generators, which have constant output across intraday time segments (:math:`{T}^b \subset T`)"
   ":math:`\text{T}^s`", ":code:`technology, flag = ps`", ":code:`tech_storage`", "all storage technologies (:math:`{T}^s \subset T`)"
   ":math:`\text{T}^a`", ":code:`technology, annual = 1`", ":code:`tech_annual`", "technologies that produce constant annual output (:math:`{T}^a \subset T`)"
   ":math:`\text{T}^{res}`", ":code:`technology, reserve = 1`", ":code:`tech_reserve`", "electric generators contributing to the reserve margin requirement (:math:`{T}^{res} \subset T`)"
   ":math:`\text{T}^c`", ":code:`technology, curtail = 1`", ":code:`tech_curtailment`", "technologies with curtailable output and no upstream cost (:math:`{T}^c \subset (T - T^{res})`)"
   ":math:`\text{T}^f`", ":code:`technology, flex = 1`", ":code:`tech_flex`", "technologies producing excess commodity flows (:math:`{T}^f \subset T`)"
   ":math:`\text{T}^x`", ":code:`technology, exchange = 1`", ":code:`tech_exchange`", "technologies used for interregional commodity flows (:math:`{T}^x \subset T`)"
   ":math:`\text{T}^{ur}`", ":code:`ramp_up_hourly`", ":code:`tech_upramping`", "electric generators with a ramp up hourly rate limit; derived from :code:`ramp_up_hourly` table (:math:`{T}^{ur} \subset T`)"
   ":math:`\text{T}^{dr}`", ":code:`ramp_down_hourly`", ":code:`tech_downramping`", "electric generators with a ramp down hourly rate limit; derived from :code:`ramp_down_hourly` table (:math:`{T}^{dr} \subset T`)"
   ":math:`\text{T}^{ret}`", ":code:`technology, retire = 1`", ":code:`tech_retirement`", "technologies allowed to retire before end of life (:math:`{T}^{ret} \subset (T - T^{u})`)"
   ":math:`\text{T}^u`", ":code:`technology, unlim_cap = 1`", ":code:`tech_uncap`", "technologies that have no bound on capacity (:math:`{T}^u \subset (T - T^{res})`)"
   ":math:`\text{T}^{ss}`", ":code:`technology, flag = 'ps' AND seas_stor = 1`", ":code:`tech_seasonal_storage`", "seasonal storage technologies; requires both storage flag and seas_stor column (:math:`{T}^{ss} \subset T^s`)"
   "", ":code:`tech_group`", ":code:`tech_group_names`", "named groups for use in group constraints"
   "", ":code:`tech_group_member`", ":code:`tech_group_members`", "each technology belonging to each group"
   ":math:`\text{T}^e`", ":code:`existing_capacity`", ":code:`tech_exist`", "existing technologies with a past vintage (:math:`{T}^e \subset T`)"

The sets below define **commodities** that are consumed and produced by different energy
technologies.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{C}^d`", ":code:`commodity, flag = d`", ":code:`commodity_demand`", "end-use demand commodities, representing the final consumer demands"
   ":math:`\text{C}^e`", ":code:`commodity, flag = e`", ":code:`commodity_emissions`", "emission commodities (e.g., :math:`\text{CO}_\text{2}` :math:`\text{NO}_\text{x}`); filtered by flag"
   ":math:`\text{C}^p`", ":code:`commodity, flag IN (p, wp, s, a, wa)`", ":code:`commodity_physical`", "superset of physical, source, annual, and their waste variants; includes all non-demand, non-emission commodities"
   ":math:`\text{C}^w`", ":code:`commodity, flag IN (w, wa , wp)`", ":code:`commodity_waste`", "commodity whose production can be greater than its consumption; can be physical, annual, or neither (not balanced, all wasted)"
   ":math:`\text{C}^a`", ":code:`commodity, flag IN (a, wa)`", ":code:`commodity_annual`", "commodities whose flows are only balanced over each period, not per-timeslice (:math:`\text{C}^a \subset \text{C}^p`)"
   ":math:`{}^*\text{C}^l`", "", ":code:`commodity_flex`", "derived set of commodities produced by a flex technology (:math:`\text{C}^l \subset \text{C}^p`); auto-populated from :code:`tech_flex` outputs"
   ":math:`\text{C}^s`", ":code:`commodity, flag = s`", ":code:`commodity_source`", "primary source commodities, not balanced by :code:`CommodityBalance_constraint`"
   ":math:`{}^*\text{C}^c`", "", ":code:`commodity_carrier`", "union of physical, demand, and waste commodities, (:math:`\text{C}_p \cup \text{C}_d \cup \text{C}^w`)"
   ":math:`{}^*\text{C}`", "", ":code:`commodity_all`", "union of all commodity sets; union of carrier and emissions commodities"

There is an additional set that defines **operators (=, <, >)**. While not strictly
necessary, defining these operators as a set allows modelers to express constraints
more efficiently.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   "", ":code:`operator`", ":code:`operator`", "constraint operators"

As indicated below, there are additional sets that are derived within the model
code and thus do not appear in the database schema.

.. csv-table::
   :header: "Set", "Model Element", "Notes"
   :widths: 15, 25, 60

   "", ":code:`tech_with_capacity`", "technologies eligible for capacitization; computed as tech_all - tech_uncap"
   "", ":code:`tech_or_group`", "technologies or groups combined; union of tech_group_names | tech_all"
   ":math:`{}^*\text{C}^c`", ":code:`commodity_carrier`", "physical energy carriers and end-use demands; union of physical, demand, and waste commodities"
   ":math:`{}^*\text{C}`", ":code:`commodity_all`", "union of all commodity sets; union of carrier and emissions commodities"
   ":math:`\text{T}^e`", ":code:`tech_exist`", "technologies with existing capacity; derived from existing_capacity table"

There are also python dictionaries and sets used to specify internal data
structures during model construction and are not considered formal model elements:

- :code:`process_inputs`, :code:`process_outputs`, :code:`process_loans`
- :code:`active_flow_rpsditvo`, :code:`active_flow_rpitvo`
- Various vintage and operational tracking dictionaries
- Time sequencing dictionaries (:code:`time_next`, :code:`time_next_sequential`)
