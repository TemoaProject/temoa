Our discussion of sets is broken down into several logical categories to make it
easier to parse. The **first group of sets pertains to Temoa's treatment of time**,
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
   ":math:`{}^*\text{V}`", ":code:`time_period`", ":code:`vintage_exist`, :code:`vintage_optimize`, :code:`vintage_all`", "tech vintages, (:math:`\text{P}^e \cup \text{P}^o`), derived from time period set and used to track technology vintages across time periods"
   ":math:`\text{D}`", ":code:`time_of_day`", ":code:`time_of_day`", "intraday time divisions, either individual or blocks of hours"
   ":math:`\text{S}`", ":code:`season_label`", ":code:`time_season`", "intra-annual divisions, e.g., different seasons or different representative days"
   "", ":code:`time_season`", ":code:`time_season`", "ordered tuple of seasons by time period"
   "", ":code:`time_season_sequential`", ":code:`time_season_to_sequential, ordered_season_sequential`", "superimposed sequential seasons used for seasonal storage and inter-season ramping"

The sets in the table below define Temoa's representation of **regions**.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{R}`", ":code:`region`", ":code:`regions`", "distinct geographical regions"
   "", ":code:`region`", ":code:`regional_indices`", "set of all the possible combinations of interregional exchanges plus original region indices"
   "", ":code:`region_group_check`", ":code:`regional_global_indices`", "set used to validate regional group constraints; includes individual regions, exchange pairs, and groups"

The sets below define how technologies are represented within Temoa. Because technologies
can serve many different functions across an energy system, we need to define a large
number of **technology subsets**.

.. csv-table::
   :header: "Set", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`{}^*\text{T}`", ":code:`technology`", ":code:`tech_all`", "all technologies to be modeled (:math:`{T}^r \cup {T}^p`)"
   ":math:`\text{T}^p`", ":code:`technology, flag = p`", ":code:`tech_production`", "technologies producing intermediate commodities, like electricity"
   ":math:`\text{T}^b`", ":code:`technology, flag = pb`", ":code:`tech_baseload`", "baseload electric generators, which have constant output across intraday time segments (:math:`{T}^b \subset T`)"
   ":math:`\text{T}^s`", ":code:`technology, flag = ps`", ":code:`tech_storage`", "all storage technologies (:math:`{T}^s \subset T`)"
   ":math:`\text{T}^a`", ":code:`technology, annual = 1`", ":code:`tech_annual`", "technologies that produce constant annual output (:math:`{T}^a \subset T`)"
   ":math:`\text{T}^{res}`", ":code:`technology, reserve = 1`", ":code:`tech_reserve`", "electric generators contributing to the reserve margin requirement (:math:`{T}^{res} \subset T`)"
   ":math:`\text{T}^c`", ":code:`technology, curtail = 1`", ":code:`tech_curtailment`", "technologies with curtailable output and no upstream cost (:math:`{T}^c \subset (T - T^{res})`)"
   ":math:`\text{T}^f`", ":code:`technology, flex = 1`", ":code:`tech_flex`", "technologies producing excess commodity flows (:math:`{T}^f \subset T`)"
   ":math:`\text{T}^x`", ":code:`technology, exchange = 1`", ":code:`tech_exchange`", "technologies used for interregional commodity flows (:math:`{T}^x \subset T`)"
   ":math:`\text{T}^{ur}`", ":code:`technology, ramp_up = 1`", ":code:`tech_upramping`", "electric generators with a ramp up hourly rate limit (:math:`{T}^{ur} \subset T`)"
   ":math:`\text{T}^{dr}`", ":code:`technology, ramp_down = 1`", ":code:`tech_downramping`", "electric generators with a ramp down hourly rate limit (:math:`{T}^{dr} \subset T`)"
   ":math:`\text{T}^{ret}`", ":code:`technology, retire = 1`", ":code:`tech_retirement`", "technologies allowed to retire before end of life (:math:`{T}^{ret} \subset (T - T^{u})`)"
   ":math:`\text{T}^u`", ":code:`technology, unlim_cap = 1`", ":code:`tech_uncap`", "technologies that have no bound on capacity (:math:`{T}^u \subset (T - T^{res})`)"
   ":math:`\text{T}^{ss}`", ":code:`technology, seas_stor = 1`", ":code:`tech_seasonal_storage`", "seasonal storage technologies (:math:`{T}^{ss} \subset T^s`)"
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
   ":math:`\text{C}^p`", ":code:`commodity, flag = p`", ":code:`commodity_physical`", "physical energy commodities (e.g., electricity, coal, uranium, oil) produced and consumed across the energy system"
   ":math:`\text{C}^w`", ":code:`commodity, flag = w, wa , wp`", ":code:`commodity_waste`", "commodity whose production can be greater than its consumption; can be physical, annual, or neither (not balanced, all wasted)"
   ":math:`\text{C}^a`", ":code:`commodity, flag = a`", ":code:`commodity_annual`", "same as commodity physical but flows are only balanced over each period (:math:`\text{C}^a \subset \text{C}^p`)"
   ":math:`\text{C}^l`", ":code:`commodity, flag = l`", ":code:`commodity_flex`", "(disposable) commodities produced by a flex technology (:math:`\text{C}^l \subset \text{C}^p`)"
   ":math:`\text{C}^s`", ":code:`commodity, flag = s`", ":code:`commodity_source`", "primary source commodities, not balanced by :code:`CommodityBalance_constraint`"
   ":math:`{}^*\text{C}^k`", "", ":code:`commodity_sink`", "commodities that exit the process network (:math:`\text{C}_d \cup \text{C}_w`); union of demand and waste commodities"
   ":math:`{}^*\text{C}^c`", "", ":code:`commodity_carrier`", "physical energy carriers and end-use demands (:math:`\text{C}_p \cup \text{C}_d`); union of physical, demand, and waste commodities"
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
   ":math:`{}^*\text{C}^k`", ":code:`commodity_sink`", "commodities that exit the process network; union of demand and waste commodities"
   ":math:`{}^*\text{C}^c`", ":code:`commodity_carrier`", "physical energy carriers and end-use demands; union of physical, demand, and waste commodities"
   ":math:`{}^*\text{C}`", ":code:`commodity_all`", "union of all commodity sets; union of carrier and emissions commodities"
   ":math:`\text{T}^e`", ":code:`tech_exist`", "technologies with existing capacity; derived from existing_capacity table"

These are also python dictionaries and sets used to specific internal data
structures during model construction and are not considered formal model elements:

- :code:`process_inputs`, :code:`process_outputs`, :code:`process_loans`
- :code:`active_flow_rpsditvo`, :code:`active_flow_rpitvo`
- Various vintage and operational tracking dictionaries
- Time sequencing dictionaries (:code:`time_next`, :code:`time_next_sequential`)



Parameters
----------

Parameters are indexed by the sets defined above and used to specify input data.
In the leftmost column, the subscripts indicate the sets used to index the parameter.
As with sets, we categorize parameters thematically and present them below in
separate tables. 

Below are the **time-related** parameters.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{SEG}_{s,d}`", ":code:`time_segment_fraction`", ":code:`segment_fraction`", "fraction of year represented by each (s, d) tuple"
   "", ":code:`metadata`", ":code:`days_per_period`", "number of days per period, required to ensure proper representation of time"
   "", ":code:`time_season_sequential`", ":code:`time_season_sequential`", "sequential season ordering (mutable)"

Parameters in the table below relate to **capacity and its performance
characteristics**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{C2A}_{r,t,v}`", ":code:`capacity_to_activity`", ":code:`capacity_to_activity`", "converts from capacity to activity units"
   ":math:`\text{CC}_{r,p,t,v}`", ":code:`capacity_credit`", ":code:`capacity_credit`", "process-specific capacity credit used in the reserve margin constraint"
   ":math:`\text{CFT}_{r,s,d,t}`", ":code:`capacity_factor_tech`", ":code:`capacity_factor_tech`", "technology-specific capacity factor"
   ":math:`\text{CFP}_{r,s,d,t,v}`", ":code:`capacity_factor_process`", ":code:`capacity_factor_process`", "process-specific capacity factor; allows capacity factor to change with technology vintage"
   ":math:`\text{ECAP}_{r,t,v}`", ":code:`existing_capacity`", ":code:`existing_capacity`", "installed capacity that exists prior to first model time period"
   ":math:`\text{PRM}_{r}`", ":code:`planning_reserve_margin`", ":code:`planning_reserve_margin`", "planning reserve margin used to ensure sufficient generating capacity"
   "", ":code:`reserve_capacity_derate`", ":code:`reserve_capacity_derate`", "reserve capacity derate"
   ":math:`\text{RUH}_{r,t}`", ":code:`ramp_up_hourly`", ":code:`ramp_up_hourly`", "hourly rate at which generation techs can ramp output up"
   ":math:`\text{RDH}_{r,t}`", ":code:`ramp_down_hourly`", ":code:`ramp_down_hourly`", "hourly rate at which generation techs can ramp output down"

Parameters in the table below relate to the specification of **costs**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{CF}_{r,p,t,v}`", ":code:`cost_fixed`", ":code:`cost_fixed`", "fixed operations & maintenance  cost"
   ":math:`\text{CI}_{r,t,v}`", ":code:`cost_invest`", ":code:`cost_invest`", "tech-specific investment cost"
   ":math:`\text{CV}_{r,p,t,v}`", ":code:`cost_variable`", ":code:`cost_variable`", "variable operations & maintenance (O&M) cost"
   "", ":code:`cost_emission`", ":code:`cost_emission`", "emission costs"
   ":math:`\text{GDR}`", ":code:`metadata_real`", ":code:`global_discount_rate`", "global rate used to convert future time period costs to the present cost"
   "", ":code:`metadata_real`", ":code:`default_loan_rate`", "default loan rate used to amortize investment costs"
   ":math:`\text{LLP}_{r,t,v}`", ":code:`loan_lifetime_process`", ":code:`loan_lifetime_process`", "process-specific loan term (default=lifetime_process)"
   ":math:`\text{LR}_{r,t,v}`", ":code:`loan_rate`", ":code:`loan_rate`", "process-specific interest rate on investment cost"

Parameters in the table below relate to the specification of **technology efficiency
and performance**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{EFF}_{r,i,t,v,o}`", ":code:`efficiency`", ":code:`efficiency`", "technology- and commodity-specific conversion efficiency"
   ":math:`\text{EFF}_{r,p,s,d,i,t,v,o}`", ":code:`efficiency_variable`", ":code:`efficiency_variable`", "optional specification that allows efficiency to be specified by time slice"
   ":math:`\text{LTT}_{r,t}`", ":code:`lifetime_tech`", ":code:`lifetime_tech`", "technology-specific lifetime (default=40 years)"
   ":math:`\text{LTP}_{r,t,v}`", ":code:`lifetime_process`", ":code:`lifetime_process`", "tech- and vintage-specific lifetime (default=lifetime_tech)"
   ":math:`\text{LSC}_{r,p,t,v}`", ":code:`lifetime_survival_curve`", ":code:`lifetime_survival_curve`", "surviving fraction of original capacity"
   ":math:`\text{SD}_{r,t}`", ":code:`storage_duration`", ":code:`storage_duration`", "storage duration per technology, specified in hours"

Parameters in the table below relate to the specification of **end-use demands**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{DEM}_{r,p,c}`", ":code:`demand`", ":code:`demand`", "end-use demand by region-period-commodity"
   ":math:`\text{DSD}_{r,p,s,d,c}`", ":code:`demand_specific_distribution`", ":code:`demand_specific_distribution`", "fractional annual demand by time slice (s,d)"

Parameters in the table below relate to the specification of **emissions**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{EAC}_{r,i,t,v,o,e}`", ":code:`emission_activity`", ":code:`emission_activity`", "activity-based emissions rate"
   ":math:`\text{EE}_{r,t,v,e}`", ":code:`emission_embodied`", ":code:`emission_embodied`", "emissions associated with the creation of capacity; embodied emissions"
   ":math:`\text{EEOL}_{r,t,v,e}`", ":code:`emission_end_of_life`", ":code:`emission_end_of_life`", "emissions associated with the retirement/end of life of capacity"

Parameters in the table below relate to the specification of **absolute limits on
capacity, activity and emissions**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LC}_{r,p,t}`", ":code:`limit_capacity`", ":code:`limit_capacity`", "limit on tech-specific capacity by period"
   ":math:`\text{LNC}_{r,p,t}`", ":code:`limit_new_capacity`", ":code:`limit_new_capacity`", "limit on new capacity deployment by period"
   ":math:`\text{LA}_{r,p,t}`", ":code:`limit_activity`", ":code:`limit_activity`", "limit on technology-specific activity by region and period"
   ":math:`\text{LE}_{r,p,e}`", ":code:`limit_emission`", ":code:`limit_emission`", "limit on emissions by region and period"
   ":math:`\text{LR}_{r,t}`", ":code:`limit_resource`", ":code:`limit_resource`", "cumulative activity limit across time periods (not supported in myopic)"

Parameters in the table below relate to the specification of **growth and degrowth
limits**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LGC}_{r,t}`", ":code:`limit_growth_capacity`", ":code:`limit_growth_capacity`", "capacity growth rate limits"
   ":math:`\text{LDGC}_{r,t}`", ":code:`limit_degrowth_capacity`", ":code:`limit_degrowth_capacity`", "capacity degrowth rate limits"
   ":math:`\text{LGNC}_{r,t}`", ":code:`limit_growth_new_capacity`", ":code:`limit_growth_new_capacity`", "new capacity growth rate limits"
   ":math:`\text{LDGNC}_{r,t}`", ":code:`limit_degrowth_new_capacity`", ":code:`limit_degrowth_new_capacity`", "new capacity degrowth rate limits"
   ":math:`\mathrm{LGNC}_{\Delta,r,t}`", ":code:`limit_growth_new_capacity_delta`", ":code:`limit_growth_new_capacity_delta`", "new capacity growth acceleration limits"
   ":math:`\mathrm{LDGNC}_{\Delta,r,t}`", ":code:`limit_degrowth_new_capacity_delta`", ":code:`limit_degrowth_new_capacity_delta`", "new capacity degrowth deceleration limits"

Parameters in the table below relate to the specification of **operational and
split limits**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LACF}_{r,p,t,o}`", ":code:`limit_annual_capacity_factor`", ":code:`limit_annual_capacity_factor`", "annual capacity factor limits"
   ":math:`\text{LSCF}_{r,p,s,t}`", ":code:`limit_seasonal_capacity_factor`", ":code:`limit_seasonal_capacity_factor`", "seasonal capacity factor limits"
   ":math:`\text{LSF}_{r,p,s,d,t,v}`", ":code:`limit_storage_level_fraction`", ":code:`limit_storage_fraction`", "limit on storage level in any time slice"
   ":math:`\text{TIS}_{r,i,t}`", ":code:`limit_tech_input_split`", ":code:`limit_tech_input_split`", "technology input split constraints specifying input fuel ratio at time slice level"
   ":math:`\text{TISA}_{r,i,t}`", ":code:`limit_tech_input_split_annual`", ":code:`limit_tech_input_split_annual`", "technology input split constraints specifying input fuel ratio at average annual level"
   ":math:`\text{TOS}_{r,t,o}`", ":code:`limit_tech_output_split`", ":code:`limit_tech_output_split`", "technology split constraints specifying output fuel ratio at time slice level"
   ":math:`\text{TOSA}_{r,t,o}`", ":code:`limit_tech_output_split_annual`", ":code:`limit_tech_output_split_annual`", "technology split constraints specifying output fuel ratio at average annual level"

Parameters in the table below relate to the specification of **share limits**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LCS}_{r,p,g_1,g_2}`", ":code:`limit_capacity_share`", ":code:`limit_capacity_share`", "capacity share limits between technology groups"
   ":math:`\text{LAS}_{r,p,g_1,g_2}`", ":code:`limit_activity_share`", ":code:`limit_activity_share`", "activity share limits between technology groups"
   ":math:`\text{LNCS}_{r,p,g_1,g_2}`", ":code:`limit_new_capacity_share`", ":code:`limit_new_capacity_share`", "new capacity share limits"

Parameters in the table below relate to the specification of **policy**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   "", ":code:`rps_requirement`", ":code:`renewable_portfolio_standard`", "**[Deprecated]** RPS requirements; use :code:`limit_activity_share` instead"
   ":math:`\text{LIT}_{r,t,e,t}`", ":code:`linked_tech`", ":code:`linked_techs`", "dummy techs used to convert CO2 emissions to physical commodity"

Parameters in the table below relate to the specification of **construction and
end-of-life**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{CON}_{r,i,t,v}`", ":code:`construction_input`", ":code:`construction_input`", "construction input requirements that represent commodities consumed by creation of process capacity"
   ":math:`\text{EOLO}_{r,t,v,o}`", ":code:`end_of_life_output`", ":code:`end_of_life_output`", "end-of-life outputs that represent commodities produced by retirement/end of life of capacity"

Parameters in the table below are **computed in code (i.e., model-derived) and
therefore do not appear in the database**.

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`{}^*\text{LEN}_p`", "", ":code:`period_length`", "number of years in period :math:`p`; computed from time periods"
   "", "", ":code:`segment_fraction_per_season`", "computed from segment fractions"
   ":math:`{}^*\text{LA}_{t,v}`", "", ":code:`loan_annualize`", "loan amortization by tech and vintage; based on :math:`DR_t`; computed from loan rate and lifetime"
   ":math:`{}^*\text{PLF}_{r,p,t,v}`", "", ":code:`process_life_frac`", "fraction of available process capacity by region and period; computed from process life fraction"
   "", "", ":code:`segment_fraction_per_season`", "computed internally from segment fractions"

The tables below specify **model outputs.** When constructing a new database,
they are left blank. These tables are auto-populated by the model after
successful run completion.

- :code:`output_dual_variable`
- :code:`output_objective`
- :code:`output_curtailment`
- :code:`output_net_capacity`
- :code:`output_built_capacity`
- :code:`output_retired_capacity`
- :code:`output_flow_in`
- :code:`output_flow_out`
- :code:`output_flow_out_summary`
- :code:`output_storage_level`
- :code:`output_emission`
- :code:`output_cost`

Finally, the database tables below do not have a directed mapping to the the
model code.

.. csv-table::
   :header: "Database Table", "Purpose", "Notes"
   :widths: 30, 30, 40

   ":code:`myopic_efficiency`", "Myopic mode efficiency", "alternative efficiency for myopic optimization"
   ":code:`time_manual`", "Manual time sequencing", "hidden feature, rarely used"
   ":code:`sector_label`", "Sectoral classification", "used in output tables only"
