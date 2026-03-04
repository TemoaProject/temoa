Parameters are indexed by the sets defined above and used to specify input data.
In the leftmost column below, the subscripts indicate the sets used to index the
parameter. As with sets, we categorize parameters thematically and present them
below in separate tables. 

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
   ":math:`\text{LS}_{r,t}`", ":code:`limit_resource`", ":code:`limit_resource`", "cumulative activity limit across time periods (not supported in myopic)"

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
   ":math:`\text{LIT}_{r,t,e,t'}`", ":code:`linked_tech`", ":code:`linked_techs`", "dummy techs used to convert CO2 emissions to physical commodity"

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

Finally, the database tables below do not have a directed mapping to the model
code.

.. csv-table::
   :header: "Database Table", "Purpose", "Notes"
   :widths: 30, 30, 40

   ":code:`myopic_efficiency`", "Myopic mode efficiency", "alternative efficiency for myopic optimization"
   ":code:`time_manual`", "Manual time sequencing", "hidden feature, rarely used"
   ":code:`sector_label`", "Sectoral classification", "used in output tables only"