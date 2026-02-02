Our discussion of sets is broken down into several logical categories to make it
easier to parse. The first group of sets pertains to Temoa's treatment of time,
as shown below. **Note:** Some entries in the "Database Table" column are
comma-separated. In those cases, the first element refers to the name of the database
table, and the second refers to specific column within the database column used to
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
   ":math:`{}^*\text{V}`", ":code:`time_period`", ":code:`vintage_exist`, :code:`vintage_optimize`, :code:`vintage_all`", "tech vintages, (:math:`\text{P}^e \cup \text{P}^o`), derived from time period set"
   ":math:`\text{D}`", ":code:`time_of_day`", ":code:`time_of_day`", "intraday time divisions"
   ":math:`\text{S}`", ":code:`season_label`", ":code:`time_season`", "intra-annual divisions, e.g., different seasons or different representative days"
   "", ":code:`time_season`", ":code:`time_season`", "ordered tuple of seasons by time period"
   "", ":code:`time_season_sequential`", ":code:`time_season_to_sequential, ordered_season_sequential`", "superimposed sequential seasons used for seasonal storage and inter-season ramping"

The sets in the table below define Temoa's representation of regions.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{R}`", ":code:`region`", ":code:`regions`", "distinct geographical regions; direct mapping"
   "", ":code:`region`", ":code:`regional_indices`", "set of all the possible combinations of interregional exchanges plus original region indices"
   "", ":code:`region_group_check`", ":code:`regional_global_indices`", "set used to validate regional group constraints; includes individual regions, exchange pairs, and groups"

The sets below define how technologies are represented within Temoa. Because technologies
can serve many different functions across an energy system, we need to define a large
number of technology subsets.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`{}^*\text{T}`", ":code:`technology`", ":code:`tech_all`", "all technologies to be modeled; (:math:`{T}^r \cup {T}^p`)"
   ":math:`\text{T}^p`", ":code:`technology, flag = p`", ":code:`tech_production`", "techs producing intermediate commodities, like electricity"
   ":math:`\text{T}^b`", ":code:`technology, flag = pb`", ":code:`tech_baseload`", "baseload electric generators, (:math:`{T}^b \subset T`)"
   ":math:`\text{T}^s`", ":code:`technology, flag = ps`", ":code:`tech_storage`", "all storage technologies, (:math:`{T}^s \subset T`)"
   ":math:`\text{T}^a`", ":code:`technology, annual = 1`", ":code:`tech_annual`", "technologies that produce constant annual output, (:math:`{T}^a \subset T`)"
   ":math:`\text{T}^{res}`", ":code:`technology, reserve = 1`", ":code:`tech_reserve`", "electric generators contributing to the reserve margin requirement, (:math:`{T}^{res} \subset T`)"
   ":math:`\text{T}^c`", ":code:`technology, curtail = 1`", ":code:`tech_curtailment`", "technologies with curtailable output and no upstream cost; (:math:`{T}^c \subset (T - T^{res})`)"
   ":math:`\text{T}^f`", ":code:`technology, flex = 1`", ":code:`tech_flex`", "technologies producing excess commodity flows, (:math:`{T}^f \subset T`)"
   ":math:`\text{T}^x`", ":code:`technology, exchange = 1`", ":code:`tech_exchange`", "technologies used for interregional commodity flows, (:math:`{T}^x \subset T`)"
   ":math:`\text{T}^{ur}`", ":code:`technology, ramp_up = 1`", ":code:`tech_upramping`", "electric generators with a ramp up hourly rate limit; (:math:`{T}^{ur} \subset T`)"
   ":math:`\text{T}^{dr}`", ":code:`technology, ramp_down = 1`", ":code:`tech_downramping`", "electric generators with a ramp down hourly rate limit; (:math:`{T}^{dr} \subset T`)"
   ":math:`\text{T}^{ret}`", ":code:`technology, retire = 1`", ":code:`tech_retirement`", "technologies allowed to retire before end of life, (:math:`{T}^{ret} \subset (T - T^{u})`)"
   ":math:`\text{T}^u`", ":code:`technology, unlim_cap = 1`", ":code:`tech_uncap`", "technologies that have no bound on capacity, (:math:`{T}^u \subset (T - T^{res})`)"
   ":math:`\text{T}^{ss}`", ":code:`technology, seas_stor = 1`", ":code:`tech_seasonal_storage`", "seasonal storage technologies, (:math:`{T}^{ss} \subset T^s`)"
   "", ":code:`tech_group`", ":code:`tech_group_names`", "named groups for use in group constraints"
   "", ":code:`tech_group_member`", ":code:`tech_group_members`", "each technology belonging to each group"
   ":math:`\text{T}^e`", ":code:`existing_capacity`", ":code:`tech_exist`", "technologies constructed in an existing (past) vintage; (:math:`{T}^e \subset T`)"

The sets below define commodities that are consumed and produced by different energy
technologies.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{C}^d`", ":code:`commodity, flag = d`", ":code:`commodity_demand`", "end-use demand commodities, representing the final consumer demands"
   ":math:`\text{C}^e`", ":code:`commodity, flag = e`", ":code:`commodity_emissions`", "emission commodities (e.g. :math:`\text{CO}_\text{2}` :math:`\text{NO}_\text{x}`); filtered by flag"
   ":math:`\text{C}^p`", ":code:`commodity, flag = p`", ":code:`commodity_physical`", "physical energy commodities (e.g. electricity, coal, uranium, oil) produced and consumed across the energy system"
   ":math:`\text{C}^w`", ":code:`commodity, flag = w, wa , wp`", ":code:`commodity_waste`", "production can be greater than consumption; can be physical, annual, or neither (not balanced, all wasted)"
   ":math:`\text{C}^a`", ":code:`commodity, flag = a`", ":code:`commodity_annual`", "same as commodity physical but flows are only balanced over each period (:math:`\text{C}^a \subset \text{C}^p`)"
   ":math:`\text{C}^l`", ":code:`commodity, flag = l`", ":code:`commodity_flex`", "(disposable) commodities produced by a flex technology (:math:`\text{C}^l \subset \text{C}^p`)"
   ":math:`\text{C}^s`", ":code:`commodity, flag = s`", ":code:`commodity_source`", "primary source commodities, not balanced by :code:`CommodityBalance_constraint`"
   ":math:`{}^*\text{C}^k`", "", ":code:`commodity_sink`", "commodities that exit the process network (:math:`\text{C}_d \cup \text{C}_w`); union of demand and waste commodities"
   ":math:`{}^*\text{C}^c`", "", ":code:`commodity_carrier`", "physical energy carriers and end-use demands (:math:`\text{C}_p \cup \text{C}_d`); union of physical, demand, and waste commodities"
   ":math:`{}^*\text{C}`", "", ":code:`commodity_all`", "union of all commodity sets; union of carrier and emissions commodities"

There is one additional set that defines operators (=, <, >). While not strictly
necessary, defining these operators as a set allows modelers to express constraints
more efficiently.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   "", ":code:`operator`", ":code:`operator`", "constraint operators"


Direct Mappings: Parameters
----------------------------

Time-Related Parameters
^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   "", "metadata_real (global_discount_rate)", "global_discount_rate", "global rate used to calculate present cost; global discount rate"
   ":math:`\text{SEG}_{s,d}`", "time_segment_fraction", "segment_fraction", "fraction of year represented by each (s, d) tuple; time slice fractions"
   "", "metadata (days_per_period)", "days_per_period", "days per period"
   "", "", "segment_fraction_per_season", "computed from segment fractions"
   "", "time_season_sequential", "time_season_sequential", "sequential season ordering (mutable)"

Capacity & Existing Infrastructure Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{ECAP}_{r,t,v}`", "existing_capacity", "existing_capacity", "pre-existing capacity; direct mapping"
   ":math:`\text{C2A}_{r,t,v}`", "capacity_to_activity", "capacity_to_activity", "converts from capacity to activity units; direct mapping"
   ":math:`\text{CFT}_{r,s,d,t}`", "capacity_factor_tech", "capacity_factor_tech", "technology-specific capacity factor; tech-level capacity factors"
   ":math:`\text{CFP}_{r,s,d,t,v}`", "capacity_factor_process", "capacity_factor_process", "process-specific capacity factor; process-level capacity factors"
   ":math:`\text{CC}_{r,p,t,v}`", "capacity_credit", "capacity_credit", "process-specific capacity credit; reserve capacity credit"

Cost Parameters
^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{CF}_{r,p,t,v}`", "cost_fixed", "cost_fixed", "fixed operations & maintenance cost; fixed O&M costs"
   ":math:`\text{CI}_{r,t,v}`", "cost_invest", "cost_invest", "tech-specific investment cost; investment costs"
   ":math:`\text{CV}_{r,p,t,v}`", "cost_variable", "cost_variable", "variable operations & maintenance cost; variable O&M costs"
   "", "cost_emission", "cost_emission", "emission costs"
   ":math:`\text{LR}_{r,t,v}`", "loan_rate", "loan_rate", "process-specific interest rate on investment cost; technology-specific loan rates"
   "", "metadata_real (default_loan_rate)", "default_loan_rate", "default loan rate"
   ":math:`\text{GDR}`", "metadata_real (global_discount_rate)", "global_discount_rate", "global rate used to calculate present cost; global discount rate"

Efficiency & Performance Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{EFF}_{r,i,t,v,o}`", "efficiency", "efficiency", "tech- and commodity-specific efficiency; base efficiency"
   "", "efficiency_variable", "efficiency_variable", "time-varying efficiency"
   ":math:`\text{LTT}_{r,t}`", "lifetime_tech", "lifetime_tech", "tech-specific lifetime (default=40 years); technology lifetime"
   ":math:`\text{LTP}_{r,t,v}`", "lifetime_process", "lifetime_process", "tech- and vintage-specific lifetime (default=lifetime_tech); process-specific lifetime"
   ":math:`\text{LSC}_{r,p,t,v}`", "lifetime_survival_curve", "lifetime_survival_curve", "surviving fraction of original capacity; survival curve fractions"
   ":math:`\text{LLP}_{r,t,v}`", "loan_lifetime_process", "loan_lifetime_process", "process-specific loan term (default=lifetime_process); loan lifetime"

Demand Parameters
^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{DEM}_{r,p,c}`", "demand", "demand", "end-use demands, by period; demand by region-period-commodity"
   ":math:`\text{DSD}_{r,p,s,d,c}`", "demand_specific_distribution", "demand_specific_distribution", "demand-specific distribution; demand time distribution"

Emission Parameters
^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{EAC}_{r,i,t,v,o,e}`", "emission_activity", "emission_activity", "tech-specific emissions rate; activity-based emissions"
   ":math:`\text{EE}_{r,t,v,e}`", "emission_embodied", "emission_embodied", "emissions associated with the creation of capacity; embodied emissions"
   ":math:`\text{EEOL}_{r,t,v,e}`", "emission_end_of_life", "emission_end_of_life", "emissions associated with the retirement/end of life of capacity; end-of-life emissions"


Absolute Limits (Capacity, Activity, Emission)
"""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LC}_{r,p,t}`", "limit_capacity", "limit_capacity", "limit tech-specific capacity by period; capacity limits"
   ":math:`\text{LNC}_{r,p,t}`", "limit_new_capacity", "limit_new_capacity", "Limit new capacity deployment by period"
   ":math:`\text{LA}_{r,p,t}`", "limit_activity", "limit_activity", "limit tech-specific activity by region and period; activity limits"
   ":math:`\text{LE}_{r,p,e}`", "limit_emission", "limit_emission", "limit emissions by region and period; emission limits"
   ":math:`\text{LR}_{r,t}`", "limit_resource", "limit_resource", "Cumulative activity limit across time periods (not supported in myopic)"

Growth & Degrowth Limits
""""""""""""""""""""""""

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LGC}_{r,t}`", "limit_growth_capacity", "limit_growth_capacity", "capacity growth rate limits"
   ":math:`\text{LDGC}_{r,t}`", "limit_degrowth_capacity", "limit_degrowth_capacity", "capacity degrowth rate limits"
   ":math:`\text{LGNC}_{r,t}`", "limit_growth_new_capacity", "limit_growth_new_capacity", "new capacity growth rate limits"
   ":math:`\text{LDGNC}_{r,t}`", "limit_degrowth_new_capacity", "limit_degrowth_new_capacity", "new capacity degrowth rate limits"
   ":math:`\mathrm{LGNC}_{\Delta,r,t}`", "limit_growth_new_capacity_delta", "limit_growth_new_capacity_delta", "new capacity growth acceleration limits"
   ":math:`\mathrm{LDGNC}_{\Delta,r,t}`", "limit_degrowth_new_capacity_delta", "limit_degrowth_new_capacity_delta", "new capacity degrowth deceleration limits"

Operational & Split Limits
""""""""""""""""""""""""""

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LACF}_{r,p,t,o}`", "limit_annual_capacity_factor", "limit_annual_capacity_factor", "annual capacity factor limits"
   ":math:`\text{LSCF}_{r,p,s,t}`", "limit_seasonal_capacity_factor", "limit_seasonal_capacity_factor", "seasonal capacity factor limits"
   ":math:`\text{TIS}_{r,i,t}`", "limit_tech_input_split", "limit_tech_input_split", "technology input fuel ratio at time slice level; tech input split constraints"
   ":math:`\text{TISA}_{r,i,t}`", "limit_tech_input_split_annual", "limit_tech_input_split_annual", "average annual technology input fuel ratio; annual tech input splits"
   ":math:`\text{TOS}_{r,t,o}`", "limit_tech_output_split", "limit_tech_output_split", "technology output fuel ratio at time slice level; tech output split constraints"
   ":math:`\text{TOSA}_{r,t,o}`", "limit_tech_output_split_annual", "limit_tech_output_split_annual", "average annual technology output fuel ratio; annual tech output splits"
   ":math:`\text{LSF}_{r,p,s,d,t,v}`", "limit_storage_level_fraction", "limit_storage_fraction", "limit storage level in any time slice; storage level fraction limits"

Share Limits
""""""""""""

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LCS}_{r,p,g_1,g_2}`", "limit_capacity_share", "limit_capacity_share", "capacity share limits between technology groups"
   ":math:`\text{LAS}_{r,p,g_1,g_2}`", "limit_activity_share", "limit_activity_share", "activity share limits between technology groups"
   ":math:`\text{LNCS}_{r,p,g_1,g_2}`", "limit_new_capacity_share", "limit_new_capacity_share", "new capacity share limits"

Storage Parameters
^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{SD}_{r,t}`", "storage_duration", "storage_duration", "storage duration per technology, specified in hours; storage duration in hours"

Operations Parameters
^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{RUH}_{r,t}`", "ramp_up_hourly", "ramp_up_hourly", "hourly rate at which generation techs can ramp output up; hourly ramp-up rates"
   ":math:`\text{RDH}_{r,t}`", "ramp_down_hourly", "ramp_down_hourly", "hourly rate at which generation techs can ramp output down; hourly ramp-down rates"

Reserve Margin Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{PRM}_{r}`", "planning_reserve_margin", "planning_reserve_margin", "margin used to ensure sufficient generating capacity; planning reserve margin"
   "", "reserve_capacity_derate", "reserve_capacity_derate", "reserve capacity derate"

Policy Parameters
^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   "", "rps_requirement", "renewable_portfolio_standard", "**[Deprecated]** RPS requirements; use limit_activity_share instead"
   ":math:`\text{LIT}_{r,t,e,t}`", "linked_tech", "linked_techs", "dummy techs used to convert CO2 emissions to physical commodity; linked technology specs"

Construction & End-of-Life Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{CON}_{r,i,t,v}`", "construction_input", "construction_input", "commodities consumed by creation of process capacity; construction input requirements"
   ":math:`\text{EOLO}_{r,t,v,o}`", "end_of_life_output", "end_of_life_output", "commodities produced by retirement/end of life of capacity; end-of-life outputs"

Computed Parameters (Model-Derived)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`{}^*\text{LEN}_p`", "", "period_length", "number of years in period :math:`p`; computed from time periods"
   "", "", "segment_fraction_per_season", "computed from segment fractions"
   ":math:`{}^*\text{LA}_{t,v}`", "", "loan_annualize", "loan amortization by tech and vintage; based on :math:`DR_t`; computed from loan rate and lifetime"
   ":math:`{}^*\text{PLF}_{r,p,t,v}`", "", "process_life_frac", "fraction of available process capacity by region and period; computed process life fraction"


Output Tables (Not in Model Input)
-----------------------------------

These tables store optimization results and are not part of model input:

- output_dual_variable
- output_objective
- output_curtailment
- output_net_capacity
- output_built_capacity
- output_retired_capacity
- output_flow_in
- output_flow_out
- output_flow_out_summary
- output_storage_level
- output_emission
- output_cost


Model-Only Elements (Not Directly from Database)
-------------------------------------------------

Derived Sets
^^^^^^^^^^^^

.. csv-table::
   :header: "Set", "Model Element", "Notes"
   :widths: 15, 25, 60

   "", "tech_with_capacity", "technologies eligible for capacitization; computed as tech_all - tech_uncap"
   "", "tech_or_group", "technologies or groups combined; union of tech_group_names | tech_all"
   ":math:`{}^*\text{C}^k`", "commodity_sink", "commodities that exit the process network; union of demand and waste commodities"
   ":math:`{}^*\text{C}^c`", "commodity_carrier", "physical energy carriers and sinks; union of physical and sink commodities"
   ":math:`{}^*\text{C}`", "commodity_all", "union of all commodity sets; union of carrier and emissions commodities"
   ":math:`\text{T}^e`", "tech_exist", "technologies with existing capacity; derived from existing_capacity table"

Internal Data Structures (Not Formal Model Elements)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are dictionaries and sets used internally during model construction:

- process_inputs, process_outputs, process_loans
- active_flow_rpsditvo, active_flow_rpitvo
- Various vintage and operational tracking dictionaries
- Time sequencing dictionaries (time_next, time_next_sequential)


Database Tables Without Direct Model Mapping
---------------------------------------------

.. csv-table::
   :header: "Database Table", "Purpose", "Notes"
   :widths: 30, 30, 40

   "myopic_efficiency", "Myopic mode efficiency", "alternative efficiency for myopic optimization"
   "time_manual", "Manual time sequencing", "hidden feature, rarely used"
   "sector_label", "Sectoral classification", "used in output tables only"


Summary Statistics
------------------

- **Database Tables**: 73 total (63 input, 10 output)
- **Model Sets**: 101 total (37 core sets, 64 constraint index sets)
- **Model Parameters**: 60 total
- **Direct Mappings**: ~55 database tables map to model elements
- **Output-Only Tables**: 10 tables
- **Model-Derived Elements**: ~20 sets/parameters computed from database data
