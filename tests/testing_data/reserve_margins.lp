\* Source Pyomo model name=unknown *\

min
total_cost:
+0.0 ONE_VAR_CONSTANT

s.t.

c_u_capacity_constraint(C_A_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_2020_winter_night_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2020_HEAT_ANN_2020)
<= -0.25

c_u_capacity_constraint(B_C_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_night_HEAT_SYS_2020)_:
+1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(A_C_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2020_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2020_winter_night_SOLPV_2020)_:
-1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC)
-1 v_curtailment(A_2020_winter_night_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(B_2020_winter_night_NGCC_2020)_:
+1 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(A_2025_summer_day_HEAT_SYS_2025)_:
+1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(B_A_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(B_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_B_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2020_summer_day_SOLPV_2020)_:
-1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC)
+1.3139999999999998 v_capacity(A_2020_SOLPV_2020)
-1 v_curtailment(A_2020_summer_day_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(A_2025_summer_night_NGCC_2025)_:
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_e_capacity_constraint(A_2025_summer_day_SOLPV_2015)_:
-1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC)
+1.3139999999999998 v_capacity(A_2025_SOLPV_2015)
-1 v_curtailment(A_2025_summer_day_ethos_SOLPV_2015_ELC)
= 0

c_e_capacity_constraint(A_2025_winter_night_SOLPV_2015)_:
-1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC)
-1 v_curtailment(A_2025_winter_night_ethos_SOLPV_2015_ELC)
= 0

c_e_capacity_constraint(A_2025_summer_night_SOLPV_2015)_:
-1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC)
-1 v_curtailment(A_2025_summer_night_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(A_2025_summer_day_NGCC_2015)_:
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_night_NGCC_2020)_:
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(A_B_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(A_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2025_winter_night_NGCC_2015)_:
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(C_2020_summer_night_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2020_HEAT_ANN_2020)
<= -0.25

c_u_capacity_constraint(C_2025_winter_day_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2025_HEAT_ANN_2020)
<= -0.275

c_u_capacity_constraint(C_A_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_day_NGCC_2025)_:
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
-2.19 v_capacity(B_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(A_2025_winter_day_NGCC_2025)_:
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(B_A_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(B_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_B_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2025_winter_day_SOLPV_2015)_:
-1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC)
+0.6569999999999999 v_capacity(A_2025_SOLPV_2015)
-1 v_curtailment(A_2025_winter_day_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(B_C_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2020_winter_night_NGCC_2015)_:
+1 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(A_2025_summer_day_HEAT_SYS_2020)_:
+1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
<= 0

c_e_capacity_constraint(A_2020_summer_day_SOLPV_2015)_:
-1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC)
+1.3139999999999998 v_capacity(A_2020_SOLPV_2015)
-1 v_curtailment(A_2020_summer_day_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(A_B_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(A_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2025_summer_night_NGCC_2020)_:
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(C_2020_winter_day_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2020_HEAT_ANN_2020)
<= -0.25

c_u_capacity_constraint(C_2020_summer_day_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2020_HEAT_ANN_2020)
<= -0.25

c_u_capacity_constraint(A_B_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(A_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_night_NGCC_2015)_:
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(A_2025_winter_night_HEAT_SYS_2025)_:
+1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(C_B_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_day_NGCC_2020)_:
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2025_NGCC_2020)
<= 0

c_e_capacity_constraint(A_2020_summer_night_SOLPV_2020)_:
-1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC)
-1 v_curtailment(A_2020_summer_night_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(A_2025_winter_day_NGCC_2020)_:
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(A_B_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(A_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2020_winter_day_NGCC_2020)_:
+1 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(A_2025_winter_day_HEAT_SYS_2025)_:
+1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(A_2020_summer_day_NGCC_2020)_:
+1 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(A_2025_summer_night_NGCC_2015)_:
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_night_NGCC_2025)_:
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
-2.19 v_capacity(B_2025_NGCC_2025)
<= 0

c_e_capacity_constraint(A_2020_winter_day_SOLPV_2020)_:
-1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC)
+0.6569999999999999 v_capacity(A_2020_SOLPV_2020)
-1 v_curtailment(A_2020_winter_day_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(B_2020_summer_night_NGCC_2020)_:
+1 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(A_2025_winter_night_HEAT_SYS_2020)_:
+1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(A_C_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_B_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2020_winter_night_SOLPV_2015)_:
-1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC)
-1 v_curtailment(A_2020_winter_night_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(B_2025_summer_day_NGCC_2015)_:
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(A_C_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2025_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2020_summer_night_SOLPV_2015)_:
-1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC)
-1 v_curtailment(A_2020_summer_night_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(A_2025_winter_day_NGCC_2015)_:
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(A_B_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(A_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2020_winter_night_HEAT_SYS_2020)_:
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
<= -0.75

c_u_capacity_constraint(C_B_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2020_winter_day_NGCC_2015)_:
+1 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(C_A_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2020_summer_day_NGCC_2020)_:
+1 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(B_A_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(B_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_summer_day_NGCC_2015)_:
+1 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(A_C_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2025_summer_night_HEAT_SYS_2025)_:
+1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
<= 0

c_e_capacity_constraint(A_2020_winter_day_SOLPV_2015)_:
-1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC)
+0.6569999999999999 v_capacity(A_2020_SOLPV_2015)
-1 v_curtailment(A_2020_winter_day_ethos_SOLPV_2015_ELC)
= 0

c_u_capacity_constraint(B_2025_summer_night_NGCC_2020)_:
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(B_2020_summer_night_NGCC_2015)_:
+1 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(C_2025_winter_night_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2025_HEAT_ANN_2020)
<= -0.275

c_u_capacity_constraint(B_A_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(B_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_winter_night_NGCC_2020)_:
+1 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
<= 0

c_e_capacity_constraint(A_2025_winter_day_SOLPV_2025)_:
-1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC)
+0.6569999999999999 v_capacity(A_2025_SOLPV_2025)
-1 v_curtailment(A_2025_winter_day_ethos_SOLPV_2025_ELC)
= 0

c_u_capacity_constraint(B_2020_winter_day_HEAT_SYS_2020)_:
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
<= -0.75

c_u_capacity_constraint(B_2025_winter_day_HEAT_SYS_2025)_:
+1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(A_2020_summer_night_NGCC_2020)_:
+1 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(C_A_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_day_HEAT_SYS_2025)_:
+1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(B_C_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_day_NGCC_2025)_:
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
-2.19 v_capacity(B_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(B_2025_summer_night_HEAT_SYS_2025)_:
+1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(B_2020_summer_day_NGCC_2015)_:
+1 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(C_B_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_A_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(B_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_winter_day_NGCC_2020)_:
+1 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
<= 0

c_u_capacity_constraint(A_B_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(A_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2025_summer_night_HEAT_SYS_2020)_:
+1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(B_A_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(B_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_C_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_C_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_A_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(B_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_winter_night_NGCC_2015)_:
+1 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_e_capacity_constraint(A_2025_winter_day_SOLPV_2020)_:
-1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC)
+0.6569999999999999 v_capacity(A_2025_SOLPV_2020)
-1 v_curtailment(A_2025_winter_day_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(B_2025_winter_day_HEAT_SYS_2020)_:
+1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
<= 0

c_e_capacity_constraint(A_2025_summer_day_SOLPV_2025)_:
-1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC)
+1.3139999999999998 v_capacity(A_2025_SOLPV_2025)
-1 v_curtailment(A_2025_summer_day_ethos_SOLPV_2025_ELC)
= 0

c_u_capacity_constraint(A_2020_summer_night_NGCC_2015)_:
+1 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_day_HEAT_SYS_2020)_:
+1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(C_B_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2025_winter_night_SOLPV_2025)_:
-1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC)
-1 v_curtailment(A_2025_winter_night_ethos_SOLPV_2025_ELC)
= 0

c_u_capacity_constraint(C_2025_summer_night_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2025_HEAT_ANN_2020)
<= -0.275

c_e_capacity_constraint(A_2025_summer_night_SOLPV_2025)_:
-1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC)
-1 v_curtailment(A_2025_summer_night_ethos_SOLPV_2025_ELC)
= 0

c_u_capacity_constraint(A_2025_winter_day_HEAT_SYS_2020)_:
+1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(A_2025_summer_day_NGCC_2025)_:
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(C_A_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2025_winter_night_NGCC_2025)_:
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(A_2020_summer_night_HEAT_SYS_2020)_:
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
<= -1.25

c_u_capacity_constraint(B_A_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(B_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_day_NGCC_2020)_:
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(B_2025_summer_night_HEAT_SYS_2020)_:
+1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
<= 0

c_u_capacity_constraint(A_C_2025_winter_day_E_TRANS_2015)_:
+1 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_A_2020_summer_day_E_TRANS_2015)_:
+1 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_C_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_summer_day_HEAT_SYS_2020)_:
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
<= -1.25

c_u_capacity_constraint(A_2020_winter_night_HEAT_SYS_2020)_:
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
<= -1.25

c_u_capacity_constraint(A_2020_winter_day_NGCC_2015)_:
+1 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_capacity_constraint(B_C_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_2025_winter_night_HEAT_SYS_2025)_:
+1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
<= 0

c_u_capacity_constraint(C_2025_summer_day_HEAT_ANN_2020)_:
-0.25 v_capacity(C_2025_HEAT_ANN_2020)
<= -0.275

c_u_capacity_constraint(A_B_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(A_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_B_2025_summer_night_E_TRANS_2015)_:
+1 v_flow_out(A_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_B_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_2020_winter_day_HEAT_SYS_2020)_:
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
<= -1.25

c_u_capacity_constraint(B_2020_summer_night_HEAT_SYS_2020)_:
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
<= -0.75

c_u_capacity_constraint(C_B_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_C_2025_winter_night_E_TRANS_2015)_:
+1 v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2025_E_TRANS_2015)
<= 0

c_u_capacity_constraint(C_A_2020_winter_day_E_TRANS_2015)_:
+1 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_C_2020_winter_night_E_TRANS_2015)_:
+1 v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(A_C_2020_summer_night_E_TRANS_2015)_:
+1 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(A_C_2020_E_TRANS_2015)
<= 0

c_u_capacity_constraint(B_C_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(B_C_2025_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2025_summer_day_SOLPV_2020)_:
-1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC)
+1.3139999999999998 v_capacity(A_2025_SOLPV_2020)
-1 v_curtailment(A_2025_summer_day_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(C_A_2025_summer_day_E_TRANS_2015)_:
+1 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
<= 0

c_e_capacity_constraint(A_2025_winter_night_SOLPV_2020)_:
-1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC)
-1 v_curtailment(A_2025_winter_night_ethos_SOLPV_2020_ELC)
= 0

c_e_capacity_constraint(A_2025_summer_night_SOLPV_2020)_:
-1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC)
-1 v_curtailment(A_2025_summer_night_ethos_SOLPV_2020_ELC)
= 0

c_u_capacity_constraint(B_2025_winter_night_NGCC_2025)_:
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
-2.19 v_capacity(B_2025_NGCC_2025)
<= 0

c_u_capacity_constraint(A_2025_summer_day_NGCC_2020)_:
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(A_2025_winter_night_NGCC_2020)_:
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2025_NGCC_2020)
<= 0

c_u_capacity_constraint(B_2025_winter_day_NGCC_2015)_:
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(B_2025_summer_night_NGCC_2015)_:
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(B_2025_NGCC_2015)
<= 0

c_u_capacity_constraint(B_2020_summer_day_HEAT_SYS_2020)_:
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
<= -0.75

c_u_capacity_annual_constraint(C_2025_ANN_IMP_2020)_:
-1 v_capacity(C_2025_ANN_IMP_2020)
+1 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
<= 0

c_u_capacity_annual_constraint(C_2020_ANN_IMP_2020)_:
-1 v_capacity(C_2020_ANN_IMP_2020)
+1 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
<= 0

c_e_capacity_available_by_period_and_tech_constraint(B_2025_NGCC)_:
-1 v_capacity(B_2025_NGCC_2025)
-1 v_capacity(B_2025_NGCC_2015)
-1 v_capacity(B_2025_NGCC_2020)
+1 v_capacity_available_by_period_and_tech(B_2025_NGCC)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2020_E_BATT)_:
-1 v_capacity(A_2020_E_BATT_2020)
+1 v_capacity_available_by_period_and_tech(A_2020_E_BATT)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_2025_HEAT_SYS)_:
-1 v_capacity(B_2025_HEAT_SYS_2020)
-1 v_capacity(B_2025_HEAT_SYS_2025)
+1 v_capacity_available_by_period_and_tech(B_2025_HEAT_SYS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_2025_HEAT_ANN)_:
-1 v_capacity(C_2025_HEAT_ANN_2020)
+1 v_capacity_available_by_period_and_tech(C_2025_HEAT_ANN)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_B_2025_E_TRANS)_:
-1 v_capacity(A_B_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(A_B_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_C_2025_E_TRANS)_:
-1 v_capacity(B_C_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(B_C_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_C_2020_E_TRANS)_:
-1 v_capacity(A_C_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(A_C_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_2020_HEAT_ANN)_:
-1 v_capacity(C_2020_HEAT_ANN_2020)
+1 v_capacity_available_by_period_and_tech(C_2020_HEAT_ANN)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_B_2025_E_TRANS)_:
-1 v_capacity(C_B_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(C_B_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2025_SOLPV)_:
-1 v_capacity(A_2025_SOLPV_2015)
-1 v_capacity(A_2025_SOLPV_2020)
-1 v_capacity(A_2025_SOLPV_2025)
+1 v_capacity_available_by_period_and_tech(A_2025_SOLPV)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_2020_NGCC)_:
-1 v_capacity(B_2020_NGCC_2015)
-1 v_capacity(B_2020_NGCC_2020)
+1 v_capacity_available_by_period_and_tech(B_2020_NGCC)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_B_2020_E_TRANS)_:
-1 v_capacity(A_B_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(A_B_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_A_2025_E_TRANS)_:
-1 v_capacity(B_A_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(B_A_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_C_2020_E_TRANS)_:
-1 v_capacity(B_C_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(B_C_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_2020_HEAT_SYS)_:
-1 v_capacity(B_2020_HEAT_SYS_2020)
+1 v_capacity_available_by_period_and_tech(B_2020_HEAT_SYS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2025_NGCC)_:
-1 v_capacity(A_2025_NGCC_2015)
-1 v_capacity(A_2025_NGCC_2020)
-1 v_capacity(A_2025_NGCC_2025)
+1 v_capacity_available_by_period_and_tech(A_2025_NGCC)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_2025_ANN_IMP)_:
-1 v_capacity(C_2025_ANN_IMP_2020)
+1 v_capacity_available_by_period_and_tech(C_2025_ANN_IMP)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_B_2020_E_TRANS)_:
-1 v_capacity(C_B_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(C_B_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2025_HEAT_SYS)_:
-1 v_capacity(A_2025_HEAT_SYS_2020)
-1 v_capacity(A_2025_HEAT_SYS_2025)
+1 v_capacity_available_by_period_and_tech(A_2025_HEAT_SYS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_A_2025_E_TRANS)_:
-1 v_capacity(C_A_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(C_A_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2020_SOLPV)_:
-1 v_capacity(A_2020_SOLPV_2015)
-1 v_capacity(A_2020_SOLPV_2020)
+1 v_capacity_available_by_period_and_tech(A_2020_SOLPV)
= 0

c_e_capacity_available_by_period_and_tech_constraint(B_A_2020_E_TRANS)_:
-1 v_capacity(B_A_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(B_A_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2025_E_BATT)_:
-1 v_capacity(A_2025_E_BATT_2020)
-1 v_capacity(A_2025_E_BATT_2025)
+1 v_capacity_available_by_period_and_tech(A_2025_E_BATT)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_C_2025_E_TRANS)_:
-1 v_capacity(A_C_2025_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(A_C_2025_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2020_NGCC)_:
-1 v_capacity(A_2020_NGCC_2020)
-1 v_capacity(A_2020_NGCC_2015)
+1 v_capacity_available_by_period_and_tech(A_2020_NGCC)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_2020_ANN_IMP)_:
-1 v_capacity(C_2020_ANN_IMP_2020)
+1 v_capacity_available_by_period_and_tech(C_2020_ANN_IMP)
= 0

c_e_capacity_available_by_period_and_tech_constraint(C_A_2020_E_TRANS)_:
-1 v_capacity(C_A_2020_E_TRANS_2015)
+1 v_capacity_available_by_period_and_tech(C_A_2020_E_TRANS)
= 0

c_e_capacity_available_by_period_and_tech_constraint(A_2020_HEAT_SYS)_:
-1 v_capacity(A_2020_HEAT_SYS_2020)
+1 v_capacity_available_by_period_and_tech(A_2020_HEAT_SYS)
= 0

c_e_adjusted_capacity_constraint(C_2025_HEAT_ANN_2020)_:
+1 v_capacity(C_2025_HEAT_ANN_2020)
-1 v_new_capacity(C_HEAT_ANN_2020)
= 0

c_e_adjusted_capacity_constraint(A_2020_HEAT_SYS_2020)_:
+1 v_capacity(A_2020_HEAT_SYS_2020)
-1 v_new_capacity(A_HEAT_SYS_2020)
= 0

c_e_adjusted_capacity_constraint(A_2025_SOLPV_2015)_:
+1 v_capacity(A_2025_SOLPV_2015)
= 0.2

c_e_adjusted_capacity_constraint(A_2025_E_BATT_2020)_:
+1 v_capacity(A_2025_E_BATT_2020)
-1 v_new_capacity(A_E_BATT_2020)
= 0

c_e_adjusted_capacity_constraint(A_2025_NGCC_2015)_:
+1 v_capacity(A_2025_NGCC_2015)
= 0.5

c_e_adjusted_capacity_constraint(A_B_2025_E_TRANS_2015)_:
+1 v_capacity(A_B_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_2020_NGCC_2020)_:
+1 v_capacity(A_2020_NGCC_2020)
-1 v_new_capacity(A_NGCC_2020)
= 0

c_e_adjusted_capacity_constraint(B_2025_NGCC_2025)_:
+1 v_capacity(B_2025_NGCC_2025)
-1 v_new_capacity(B_NGCC_2025)
= 0

c_e_adjusted_capacity_constraint(B_C_2020_E_TRANS_2015)_:
+1 v_capacity(B_C_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(C_B_2025_E_TRANS_2015)_:
+1 v_capacity(C_B_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_2025_SOLPV_2020)_:
+1 v_capacity(A_2025_SOLPV_2020)
-1 v_new_capacity(A_SOLPV_2020)
= 0

c_e_adjusted_capacity_constraint(C_A_2025_E_TRANS_2015)_:
+1 v_capacity(C_A_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_2025_NGCC_2020)_:
+1 v_capacity(A_2025_NGCC_2020)
-1 v_new_capacity(A_NGCC_2020)
= 0

c_e_adjusted_capacity_constraint(A_2025_E_BATT_2025)_:
+1 v_capacity(A_2025_E_BATT_2025)
-1 v_new_capacity(A_E_BATT_2025)
= 0

c_e_adjusted_capacity_constraint(A_2020_SOLPV_2015)_:
+1 v_capacity(A_2020_SOLPV_2015)
= 0.2

c_e_adjusted_capacity_constraint(B_2020_NGCC_2015)_:
+1 v_capacity(B_2020_NGCC_2015)
= 0.3

c_e_adjusted_capacity_constraint(A_2025_HEAT_SYS_2020)_:
+1 v_capacity(A_2025_HEAT_SYS_2020)
-1 v_new_capacity(A_HEAT_SYS_2020)
= 0

c_e_adjusted_capacity_constraint(B_2025_NGCC_2015)_:
+1 v_capacity(B_2025_NGCC_2015)
= 0.3

c_e_adjusted_capacity_constraint(B_2025_HEAT_SYS_2020)_:
+1 v_capacity(B_2025_HEAT_SYS_2020)
-1 v_new_capacity(B_HEAT_SYS_2020)
= 0

c_e_adjusted_capacity_constraint(B_A_2025_E_TRANS_2015)_:
+1 v_capacity(B_A_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(C_2020_ANN_IMP_2020)_:
+1 v_capacity(C_2020_ANN_IMP_2020)
-1 v_new_capacity(C_ANN_IMP_2020)
= 0

c_e_adjusted_capacity_constraint(C_2020_HEAT_ANN_2020)_:
+1 v_capacity(C_2020_HEAT_ANN_2020)
-1 v_new_capacity(C_HEAT_ANN_2020)
= 0

c_e_adjusted_capacity_constraint(A_B_2020_E_TRANS_2015)_:
+1 v_capacity(A_B_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_C_2020_E_TRANS_2015)_:
+1 v_capacity(A_C_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_2020_E_BATT_2020)_:
+1 v_capacity(A_2020_E_BATT_2020)
-1 v_new_capacity(A_E_BATT_2020)
= 0

c_e_adjusted_capacity_constraint(A_C_2025_E_TRANS_2015)_:
+1 v_capacity(A_C_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(B_2020_HEAT_SYS_2020)_:
+1 v_capacity(B_2020_HEAT_SYS_2020)
-1 v_new_capacity(B_HEAT_SYS_2020)
= 0

c_e_adjusted_capacity_constraint(A_2025_SOLPV_2025)_:
+1 v_capacity(A_2025_SOLPV_2025)
-1 v_new_capacity(A_SOLPV_2025)
= 0

c_e_adjusted_capacity_constraint(B_C_2025_E_TRANS_2015)_:
+1 v_capacity(B_C_2025_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(A_2025_NGCC_2025)_:
+1 v_capacity(A_2025_NGCC_2025)
-1 v_new_capacity(A_NGCC_2025)
= 0

c_e_adjusted_capacity_constraint(A_2025_HEAT_SYS_2025)_:
+1 v_capacity(A_2025_HEAT_SYS_2025)
-1 v_new_capacity(A_HEAT_SYS_2025)
= 0

c_e_adjusted_capacity_constraint(A_2020_SOLPV_2020)_:
+1 v_capacity(A_2020_SOLPV_2020)
-1 v_new_capacity(A_SOLPV_2020)
= 0

c_e_adjusted_capacity_constraint(A_2020_NGCC_2015)_:
+1 v_capacity(A_2020_NGCC_2015)
= 0.5

c_e_adjusted_capacity_constraint(B_2020_NGCC_2020)_:
+1 v_capacity(B_2020_NGCC_2020)
-1 v_new_capacity(B_NGCC_2020)
= 0

c_e_adjusted_capacity_constraint(B_2025_NGCC_2020)_:
+1 v_capacity(B_2025_NGCC_2020)
-1 v_new_capacity(B_NGCC_2020)
= 0

c_e_adjusted_capacity_constraint(C_B_2020_E_TRANS_2015)_:
+1 v_capacity(C_B_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(B_2025_HEAT_SYS_2025)_:
+1 v_capacity(B_2025_HEAT_SYS_2025)
-1 v_new_capacity(B_HEAT_SYS_2025)
= 0

c_e_adjusted_capacity_constraint(B_A_2020_E_TRANS_2015)_:
+1 v_capacity(B_A_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(C_A_2020_E_TRANS_2015)_:
+1 v_capacity(C_A_2020_E_TRANS_2015)
= 1.0

c_e_adjusted_capacity_constraint(C_2025_ANN_IMP_2020)_:
+1 v_capacity(C_2025_ANN_IMP_2020)
-1 v_new_capacity(C_ANN_IMP_2020)
= 0

c_e_demand_constraint(A_2025_HEAT)_:
+1 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT)
= 5.5

c_e_demand_constraint(B_2025_HEAT)_:
+1 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT)
+1 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT)
= 3.3

c_e_demand_activity_constraint(A_2025_winter_day_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_summer_night_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_winter_night_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_summer_night_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_winter_night_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_summer_day_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_winter_night_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_winter_night_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_summer_day_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_winter_day_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_winter_day_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(B_2025_winter_day_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_summer_night_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_summer_night_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_summer_day_HEAT_SYS_2025_HEAT)_:
-1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT)
= 0

c_e_demand_activity_constraint(A_2025_summer_day_HEAT_SYS_2020_HEAT)_:
-1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
+0.25 v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT)
= 0

c_e_commodity_balance_constraint(B_2020_winter_day_NG)_:
-1.8181818181818181 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2020_winter_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_summer_night_ELC)_:
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
-1.0526315789473684 v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(B_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
-1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
= 0

c_e_commodity_balance_constraint(C_2020_winter_night_ELC)_:
-1.0526315789473684 v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2025_winter_night_NG)_:
-1.8181818181818181 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
-1.8181818181818181 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_winter_night_ethos_IMP_NG_2020_NG)
= 0

c_e_commodity_balance_constraint(A_2025_summer_night_ELC)_:
+1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC)
+1 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC)
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
-1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
-1.0526315789473684 v_flow_out(A_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC)
+1 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
-1 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-1 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
= 0

c_e_commodity_balance_constraint(A_2025_winter_day_ELC)_:
+1 v_flow_out(B_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(A_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC)
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
-1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC)
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC)
+1 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
-1 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-1 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_winter_day_NG)_:
-1.8181818181818181 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
+1 v_flow_out(B_2025_winter_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
= 0

c_e_commodity_balance_constraint(C_2020_summer_night_ELC)_:
-1.0526315789473684 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2020_summer_night_NG)_:
-1.8181818181818181 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_summer_night_ethos_IMP_NG_2020_NG)
= 0

c_e_commodity_balance_constraint(A_2020_winter_day_NG)_:
-1.8181818181818181 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_winter_day_ethos_IMP_NG_2020_NG)
= 0

c_e_commodity_balance_constraint(C_2025_summer_day_ELC)_:
+1 v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_winter_night_NG)_:
+1 v_flow_out(B_2025_winter_night_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
-1.8181818181818181 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
= 0

c_e_commodity_balance_constraint(A_2020_summer_day_ELC)_:
-1.0526315789473684 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC)
+1 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
+1 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
+1 v_flow_out(B_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(A_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC)
-1 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
= 1.25

c_e_commodity_balance_constraint(B_2020_summer_day_ELC)_:
+1 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(B_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
-1.0526315789473684 v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
= 0.75

c_e_commodity_balance_constraint(B_2025_summer_day_NG)_:
-1.8181818181818181 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2025_summer_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
-1.8181818181818181 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2020_summer_night_NG)_:
-1.8181818181818181 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2020_summer_night_ethos_IMP_NG_2020_NG)
= 0

c_e_commodity_balance_constraint(B_2020_winter_day_ELC)_:
-1.0526315789473684 v_flow_out(B_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
-1.0526315789473684 v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
+1 v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
= 0.75

c_e_commodity_balance_constraint(B_2020_winter_night_NG)_:
-1.8181818181818181 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2020_winter_night_ethos_IMP_NG_2020_NG)
= 0

c_e_commodity_balance_constraint(A_2025_summer_day_NG)_:
-1.8181818181818181 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_summer_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
-1.8181818181818181 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2025_winter_night_ELC)_:
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
+1 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(A_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC)
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
-1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC)
+1 v_flow_out(B_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC)
-1 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-1 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
= 0

c_e_commodity_balance_constraint(C_2025_winter_night_ELC)_:
+1 v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_winter_day_ELC)_:
-1.0526315789473684 v_flow_out(B_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
-1.0526315789473684 v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
-1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
= 0

c_e_commodity_balance_constraint(C_2020_winter_day_ELC)_:
+1 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2020_summer_night_ELC)_:
+1 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+1 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
+1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC)
+1 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
-1.0526315789473684 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(A_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC)
+1 v_flow_out(B_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
= 1.25

c_e_commodity_balance_constraint(A_2020_winter_day_ELC)_:
+1 v_flow_out(B_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
-1.0526315789473684 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
+1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC)
+1 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
-1.0526315789473684 v_flow_out(A_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC)
-1 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
= 1.25

c_e_commodity_balance_constraint(A_2020_winter_night_NG)_:
-1.8181818181818181 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_winter_night_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2025_summer_night_NG)_:
-1.8181818181818181 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_summer_night_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
-1.8181818181818181 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_summer_night_NG)_:
-1.8181818181818181 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
-1.8181818181818181 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2025_summer_night_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
= 0

c_e_commodity_balance_constraint(A_2025_winter_day_NG)_:
-1.8181818181818181 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
-1.8181818181818181 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_winter_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(C_2025_summer_night_ELC)_:
-1.0526315789473684 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_winter_night_ELC)_:
-1.0526315789473684 v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
+1 v_flow_out(A_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(B_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
-1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
= 0

c_e_commodity_balance_constraint(B_2020_summer_night_ELC)_:
+1 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
+1 v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
-1.0526315789473684 v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(B_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
= 0.75

c_e_commodity_balance_constraint(B_2020_winter_night_ELC)_:
+1 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
+1 v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(B_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
= 0.75

c_e_commodity_balance_constraint(A_2025_summer_day_ELC)_:
-1.0526315789473684 v_flow_out(A_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC)
+1 v_flow_out(B_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
+1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC)
+1 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
+1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC)
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
-1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-1.0526315789473684 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-1 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
= 0

c_e_commodity_balance_constraint(B_2025_summer_day_ELC)_:
+1 v_flow_out(A_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(B_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
-1.0526315789473684 v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
+1 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(C_2020_summer_day_ELC)_:
+1 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2020_summer_day_NG)_:
-1.8181818181818181 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_summer_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
= 0

c_e_commodity_balance_constraint(C_2025_winter_day_ELC)_:
+1 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
= 0

c_e_commodity_balance_constraint(A_2020_winter_night_ELC)_:
+1 v_flow_out(B_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
+1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC)
+1 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-1.0526315789473684 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
-1.0526315789473684 v_flow_out(A_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
+1 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC)
-1 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
= 1.25

c_e_commodity_balance_constraint(B_2020_summer_day_NG)_:
-1.8181818181818181 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
+1 v_flow_out(B_2020_summer_day_ethos_IMP_NG_2020_NG)
-1.8181818181818181 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
= 0

c_e_annual_commodity_balance_constraint(C_2020_ELC_C)_:
+1 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
= 1.0

c_e_annual_commodity_balance_constraint(C_2025_ELC_C)_:
+1 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
= 1.1

c_e_regional_exchange_capacity_constraint(A_C_2020_E_TRANS_2015)_:
+1 v_capacity(A_C_2020_E_TRANS_2015)
-1 v_capacity(C_A_2020_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(B_A_2020_E_TRANS_2015)_:
-1 v_capacity(A_B_2020_E_TRANS_2015)
+1 v_capacity(B_A_2020_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(C_B_2020_E_TRANS_2015)_:
-1 v_capacity(B_C_2020_E_TRANS_2015)
+1 v_capacity(C_B_2020_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(A_B_2025_E_TRANS_2015)_:
+1 v_capacity(A_B_2025_E_TRANS_2015)
-1 v_capacity(B_A_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(C_A_2025_E_TRANS_2015)_:
+1 v_capacity(C_A_2025_E_TRANS_2015)
-1 v_capacity(A_C_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(C_A_2020_E_TRANS_2015)_:
-1 v_capacity(A_C_2020_E_TRANS_2015)
+1 v_capacity(C_A_2020_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(A_B_2020_E_TRANS_2015)_:
+1 v_capacity(A_B_2020_E_TRANS_2015)
-1 v_capacity(B_A_2020_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(B_C_2025_E_TRANS_2015)_:
-1 v_capacity(C_B_2025_E_TRANS_2015)
+1 v_capacity(B_C_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(A_C_2025_E_TRANS_2015)_:
-1 v_capacity(C_A_2025_E_TRANS_2015)
+1 v_capacity(A_C_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(B_A_2025_E_TRANS_2015)_:
-1 v_capacity(A_B_2025_E_TRANS_2015)
+1 v_capacity(B_A_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(C_B_2025_E_TRANS_2015)_:
+1 v_capacity(C_B_2025_E_TRANS_2015)
-1 v_capacity(B_C_2025_E_TRANS_2015)
= 0

c_e_regional_exchange_capacity_constraint(B_C_2020_E_TRANS_2015)_:
+1 v_capacity(B_C_2020_E_TRANS_2015)
-1 v_capacity(C_B_2020_E_TRANS_2015)
= 0

c_e_storage_energy_constraint(A_2020_winter_night_E_BATT_2020)_:
-1 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
+1 v_storage_init(A_2020_winter_E_BATT_2020)
-1 v_storage_level(A_2020_winter_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2020_summer_night_E_BATT_2020)_:
-1 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+1 v_storage_init(A_2020_summer_E_BATT_2020)
-1 v_storage_level(A_2020_summer_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_winter_day_E_BATT_2020)_:
-1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
+1 v_storage_level(A_2025_winter_day_E_BATT_2020)
-1 v_storage_level(A_2025_winter_night_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_summer_night_E_BATT_2025)_:
-1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
+1 v_storage_init(A_2025_summer_E_BATT_2025)
-1 v_storage_level(A_2025_summer_day_E_BATT_2025)
= 0

c_e_storage_energy_constraint(A_2025_summer_day_E_BATT_2025)_:
-1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-1 v_storage_level(A_2025_summer_night_E_BATT_2025)
+1 v_storage_level(A_2025_summer_day_E_BATT_2025)
= 0

c_e_storage_energy_constraint(A_2025_winter_night_E_BATT_2020)_:
-1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
+1 v_storage_init(A_2025_winter_E_BATT_2020)
-1 v_storage_level(A_2025_winter_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_winter_day_E_BATT_2025)_:
-1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
+1 v_storage_level(A_2025_winter_day_E_BATT_2025)
-1 v_storage_level(A_2025_winter_night_E_BATT_2025)
= 0

c_e_storage_energy_constraint(A_2020_winter_day_E_BATT_2020)_:
-1 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
-1 v_storage_level(A_2020_winter_night_E_BATT_2020)
+1 v_storage_level(A_2020_winter_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_summer_night_E_BATT_2020)_:
-1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+1 v_storage_init(A_2025_summer_E_BATT_2020)
-1 v_storage_level(A_2025_summer_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_summer_day_E_BATT_2020)_:
-1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
-1 v_storage_level(A_2025_summer_night_E_BATT_2020)
+1 v_storage_level(A_2025_summer_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2020_summer_day_E_BATT_2020)_:
-1 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
+0.85 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
-1 v_storage_level(A_2020_summer_night_E_BATT_2020)
+1 v_storage_level(A_2020_summer_day_E_BATT_2020)
= 0

c_e_storage_energy_constraint(A_2025_winter_night_E_BATT_2025)_:
-1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
+1 v_storage_init(A_2025_winter_E_BATT_2025)
-1 v_storage_level(A_2025_winter_day_E_BATT_2025)
= 0

c_e_storage_level_last_tod_constraint(A_2025_summer_E_BATT_2020)_:
-1 v_storage_init(A_2025_summer_E_BATT_2020)
+1 v_storage_level(A_2025_summer_night_E_BATT_2020)
= 0

c_e_storage_level_last_tod_constraint(A_2025_winter_E_BATT_2020)_:
-1 v_storage_init(A_2025_winter_E_BATT_2020)
+1 v_storage_level(A_2025_winter_night_E_BATT_2020)
= 0

c_e_storage_level_last_tod_constraint(A_2020_summer_E_BATT_2020)_:
-1 v_storage_init(A_2020_summer_E_BATT_2020)
+1 v_storage_level(A_2020_summer_night_E_BATT_2020)
= 0

c_e_storage_level_last_tod_constraint(A_2020_winter_E_BATT_2020)_:
-1 v_storage_init(A_2020_winter_E_BATT_2020)
+1 v_storage_level(A_2020_winter_night_E_BATT_2020)
= 0

c_e_storage_level_last_tod_constraint(A_2025_summer_E_BATT_2025)_:
-1 v_storage_init(A_2025_summer_E_BATT_2025)
+1 v_storage_level(A_2025_summer_night_E_BATT_2025)
= 0

c_e_storage_level_last_tod_constraint(A_2025_winter_E_BATT_2025)_:
-1 v_storage_init(A_2025_winter_E_BATT_2025)
+1 v_storage_level(A_2025_winter_night_E_BATT_2025)
= 0

c_u_storage_energy_upper_bound_constraint(A_2020_winter_night_E_BATT_2020)_:
-0.73 v_capacity(A_2020_E_BATT_2020)
+1 v_storage_level(A_2020_winter_night_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2020_summer_night_E_BATT_2020)_:
-0.73 v_capacity(A_2020_E_BATT_2020)
+1 v_storage_level(A_2020_summer_night_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_winter_day_E_BATT_2020)_:
-0.73 v_capacity(A_2025_E_BATT_2020)
+1 v_storage_level(A_2025_winter_day_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_summer_night_E_BATT_2025)_:
-0.73 v_capacity(A_2025_E_BATT_2025)
+1 v_storage_level(A_2025_summer_night_E_BATT_2025)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_summer_day_E_BATT_2025)_:
-0.73 v_capacity(A_2025_E_BATT_2025)
+1 v_storage_level(A_2025_summer_day_E_BATT_2025)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_winter_night_E_BATT_2020)_:
-0.73 v_capacity(A_2025_E_BATT_2020)
+1 v_storage_level(A_2025_winter_night_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_winter_day_E_BATT_2025)_:
-0.73 v_capacity(A_2025_E_BATT_2025)
+1 v_storage_level(A_2025_winter_day_E_BATT_2025)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2020_winter_day_E_BATT_2020)_:
-0.73 v_capacity(A_2020_E_BATT_2020)
+1 v_storage_level(A_2020_winter_day_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_summer_night_E_BATT_2020)_:
-0.73 v_capacity(A_2025_E_BATT_2020)
+1 v_storage_level(A_2025_summer_night_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_summer_day_E_BATT_2020)_:
-0.73 v_capacity(A_2025_E_BATT_2020)
+1 v_storage_level(A_2025_summer_day_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2020_summer_day_E_BATT_2020)_:
-0.73 v_capacity(A_2020_E_BATT_2020)
+1 v_storage_level(A_2020_summer_day_E_BATT_2020)
<= 0

c_u_storage_energy_upper_bound_constraint(A_2025_winter_night_E_BATT_2025)_:
-0.73 v_capacity(A_2025_E_BATT_2025)
+1 v_storage_level(A_2025_winter_night_E_BATT_2025)
<= 0

c_u_storage_charge_rate_constraint(A_2020_winter_night_E_BATT_2020)_:
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2020_summer_night_E_BATT_2020)_:
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_winter_day_E_BATT_2020)_:
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_summer_night_E_BATT_2025)_:
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_summer_day_E_BATT_2025)_:
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_winter_night_E_BATT_2020)_:
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_winter_day_E_BATT_2025)_:
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2020_winter_day_E_BATT_2020)_:
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_summer_night_E_BATT_2020)_:
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_summer_day_E_BATT_2020)_:
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2020_summer_day_E_BATT_2020)_:
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_charge_rate_constraint(A_2025_winter_night_E_BATT_2025)_:
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_discharge_rate_constraint(A_2020_winter_night_E_BATT_2020)_:
+1 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2020_summer_night_E_BATT_2020)_:
+1 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_winter_day_E_BATT_2020)_:
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_summer_night_E_BATT_2025)_:
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_summer_day_E_BATT_2025)_:
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_winter_night_E_BATT_2020)_:
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_winter_day_E_BATT_2025)_:
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
<= 0

c_u_storage_discharge_rate_constraint(A_2020_winter_day_E_BATT_2020)_:
+1 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_summer_night_E_BATT_2020)_:
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_summer_day_E_BATT_2020)_:
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2020_summer_day_E_BATT_2020)_:
+1 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
<= 0

c_u_storage_discharge_rate_constraint(A_2025_winter_night_E_BATT_2025)_:
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
<= 0

c_u_storage_throughput_constraint(A_2020_winter_night_E_BATT_2020)_:
+1 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2020_summer_night_E_BATT_2020)_:
+1 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_winter_day_E_BATT_2020)_:
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_summer_night_E_BATT_2025)_:
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_summer_day_E_BATT_2025)_:
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_winter_night_E_BATT_2020)_:
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_winter_day_E_BATT_2025)_:
+1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_storage_throughput_constraint(A_2020_winter_day_E_BATT_2020)_:
+1 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_summer_night_E_BATT_2020)_:
+1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_summer_day_E_BATT_2020)_:
+1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2025_E_BATT_2020)
+0.85 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2020_summer_day_E_BATT_2020)_:
+1 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
-2.19 v_capacity(A_2020_E_BATT_2020)
+0.85 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_storage_throughput_constraint(A_2025_winter_night_E_BATT_2025)_:
+1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-2.19 v_capacity(A_2025_E_BATT_2025)
+0.85 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_B_2025_summer_night_elec_AB)_:
+1.08 v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
+1.08 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-1.1368421052631579 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC)
+1.08 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
+0.18000000000000005 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+0.18000000000000005 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
+1.08 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
+1.08 v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC)
+1.08 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
-2.0805 v_capacity(A_2025_NGCC_2015)
-2.0805 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.0805 v_capacity(B_2025_NGCC_2015)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-2.0805 v_capacity(B_2025_NGCC_2020)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
-0.18000000000000005 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-0.18000000000000005 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_2025_summer_day_elec_A)_:
-1.1578947368421053 v_flow_out(A_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+0.20000000000000007 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC)
+0.20000000000000007 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
-1.0512 v_capacity(A_2025_SOLPV_2015)
-2.0805 v_capacity(A_2025_NGCC_2015)
+2.19 v_capacity(A_B_2025_E_TRANS_2015)
-1.0512 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-1.0512 v_capacity(A_2025_SOLPV_2025)
-2.0805 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-0.20000000000000007 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-0.20000000000000007 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_operating_reserve_margin_constraint(B_2020_summer_day_NGCC)_:
+1.1 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
-2.0805 v_capacity(B_2020_NGCC_2015)
-2.0805 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_2020_winter_night_elec_A)_:
+1.1 v_flow_out(B_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC)
+0.20000000000000007 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(A_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-1.971 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(A_B_2020_E_TRANS_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.971 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.20000000000000007 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
<= -1.375

c_u_operating_reserve_margin_constraint(B_2020_winter_day_NGCC)_:
+1.1 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
-1.971 v_capacity(B_2020_NGCC_2015)
-1.971 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_B_2025_winter_day_elec_AB)_:
+0.18000000000000005 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+1.08 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
-1.1368421052631579 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+0.18000000000000005 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
+1.08 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC)
+1.08 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1.08 v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC)
+1.08 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_NGCC_2015)
-1.971 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-1.971 v_capacity(B_2025_NGCC_2015)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-1.971 v_capacity(B_2025_NGCC_2020)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
-0.18000000000000005 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-0.18000000000000005 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_2025_summer_night_elec_A)_:
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC)
+0.20000000000000007 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+0.20000000000000007 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
-1.1578947368421053 v_flow_out(A_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
-2.0805 v_capacity(A_2025_NGCC_2015)
+2.19 v_capacity(A_B_2025_E_TRANS_2015)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-0.20000000000000007 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-0.20000000000000007 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_2025_winter_day_elec_A)_:
+1.1 v_flow_out(B_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
+0.20000000000000007 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(A_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC)
+0.20000000000000007 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_NGCC_2015)
+2.19 v_capacity(A_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
-1.971 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-0.20000000000000007 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-0.20000000000000007 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_operating_reserve_margin_constraint(B_2025_winter_day_NGCC)_:
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
-1.971 v_capacity(B_2025_NGCC_2025)
-1.971 v_capacity(B_2025_NGCC_2015)
-1.971 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_B_2020_winter_day_elec_AB)_:
+0.18000000000000005 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
-1.1368421052631579 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-1.971 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
-1.971 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-1.971 v_capacity(A_2020_NGCC_2015)
-1.971 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.18000000000000005 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
<= -2.16

c_u_operating_reserve_margin_constraint(A_B_2025_summer_day_elec_AB)_:
+1.08 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC)
+1.08 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
+0.18000000000000005 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
+1.08 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
-1.1368421052631579 v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
+1.08 v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC)
+1.08 v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
+0.18000000000000005 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-1.1368421052631579 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
-1.0512 v_capacity(A_2025_SOLPV_2015)
-2.0805 v_capacity(A_2025_NGCC_2015)
-2.0805 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-1.0512 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.0805 v_capacity(B_2025_NGCC_2015)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-1.0512 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.0805 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-2.0805 v_capacity(B_2025_NGCC_2020)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
-0.18000000000000005 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-0.18000000000000005 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_operating_reserve_margin_constraint(B_2025_winter_night_NGCC)_:
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
-1.971 v_capacity(B_2025_NGCC_2025)
-1.971 v_capacity(B_2025_NGCC_2015)
-1.971 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(B_2020_summer_night_NGCC)_:
+1.1 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
-2.0805 v_capacity(B_2020_NGCC_2015)
-2.0805 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(B_2020_winter_night_NGCC)_:
+1.1 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
-1.971 v_capacity(B_2020_NGCC_2015)
-1.971 v_capacity(B_2020_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_B_2020_summer_night_elec_AB)_:
+0.18000000000000005 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
+1.08 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
-1.1368421052631579 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-2.0805 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-2.0805 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
-2.0805 v_capacity(A_2020_NGCC_2015)
-2.0805 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.18000000000000005 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
<= -2.16

c_u_operating_reserve_margin_constraint(B_2025_summer_day_NGCC)_:
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
-2.0805 v_capacity(B_2025_NGCC_2025)
-2.0805 v_capacity(B_2025_NGCC_2015)
-2.0805 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_2020_summer_day_elec_A)_:
-1.1578947368421053 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC)
+0.20000000000000007 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(A_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-2.0805 v_capacity(A_2020_NGCC_2020)
-1.0512 v_capacity(A_2020_SOLPV_2015)
+2.19 v_capacity(A_B_2020_E_TRANS_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.0512 v_capacity(A_2020_SOLPV_2020)
-2.0805 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.20000000000000007 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
<= -1.375

c_u_operating_reserve_margin_constraint(A_B_2020_winter_night_elec_AB)_:
+1.08 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
-1.1368421052631579 v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC)
+0.18000000000000005 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-1.1368421052631579 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-1.971 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-1.971 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
-1.971 v_capacity(A_2020_NGCC_2015)
-1.971 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.18000000000000005 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
<= -2.16

c_u_operating_reserve_margin_constraint(A_B_2025_winter_night_elec_AB)_:
+1.08 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
+1.08 v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC)
+1.08 v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+0.18000000000000005 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-1.1368421052631579 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
+1.08 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC)
+1.08 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
+1.08 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
+1.08 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+0.18000000000000005 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
+1.08 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1.08 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
+1.08 v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC)
-1.971 v_capacity(A_2025_NGCC_2015)
-1.971 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-1.971 v_capacity(B_2025_NGCC_2015)
-0.25 v_capacity(B_2025_HEAT_SYS_2020)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-1.971 v_capacity(B_2025_NGCC_2020)
-0.25 v_capacity(B_2025_HEAT_SYS_2025)
-0.18000000000000005 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-0.18000000000000005 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_2025_winter_night_elec_A)_:
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(A_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC)
+0.20000000000000007 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
+0.20000000000000007 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC)
-1.971 v_capacity(A_2025_NGCC_2015)
+2.19 v_capacity(A_B_2025_E_TRANS_2015)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2020)
-0.25 v_capacity(A_2025_HEAT_SYS_2020)
-2.19 v_capacity(B_A_2025_E_TRANS_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-1.971 v_capacity(A_2025_NGCC_2025)
-0.25 v_capacity(A_2025_HEAT_SYS_2025)
-0.20000000000000007 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-0.20000000000000007 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_operating_reserve_margin_constraint(A_2020_winter_day_elec_A)_:
+1.1 v_flow_out(B_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+0.20000000000000007 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(A_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-1.971 v_capacity(A_2020_NGCC_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
+2.19 v_capacity(A_B_2020_E_TRANS_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-1.971 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.20000000000000007 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
<= -1.375

c_u_operating_reserve_margin_constraint(B_2025_summer_night_NGCC)_:
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
-2.0805 v_capacity(B_2025_NGCC_2025)
-2.0805 v_capacity(B_2025_NGCC_2015)
-2.0805 v_capacity(B_2025_NGCC_2020)
<= 0

c_u_operating_reserve_margin_constraint(A_2020_summer_night_elec_A)_:
+0.20000000000000007 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(A_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-2.0805 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(A_B_2020_E_TRANS_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-2.0805 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_A_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.20000000000000007 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
<= -1.375

c_u_operating_reserve_margin_constraint(A_B_2020_summer_day_elec_AB)_:
-1.1368421052631579 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1.08 v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC)
+1.08 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
+0.18000000000000005 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
+1.08 v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
+1.08 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
-1.1368421052631579 v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.08 v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC)
-0.25 v_capacity(A_2020_HEAT_SYS_2020)
-2.0805 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-1.0512 v_capacity(A_2020_SOLPV_2015)
-2.0805 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-0.25 v_capacity(B_2020_HEAT_SYS_2020)
-1.0512 v_capacity(A_2020_SOLPV_2020)
-2.0805 v_capacity(A_2020_NGCC_2015)
-2.0805 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-0.18000000000000005 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
<= -2.16

c_u_planning_reserve_margin_constraint(A_B_2025_summer_night_elec_AB)_:
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
+1.1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_E_BATT_2020)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-1.971 v_capacity(A_2025_E_BATT_2025)
-2.19 v_capacity(B_2025_NGCC_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2025)
-2.19 v_capacity(B_2025_NGCC_2020)
-1.1 v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC)
-1.1 v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC)
<= 0

c_u_planning_reserve_margin_constraint(A_2020_summer_day_NGCC)_:
+1.15 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_planning_reserve_margin_constraint(C_2020_summer_day_elec_C_ann)_:
-0.25 v_capacity(C_2020_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
<= -0.3

c_u_planning_reserve_margin_constraint(A_B_2025_winter_day_elec_AB)_:
+1.1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC)
-1.1578947368421053 v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT)
+1.1 v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_E_BATT_2020)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-1.971 v_capacity(A_2025_E_BATT_2025)
-2.19 v_capacity(B_2025_NGCC_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2025)
-2.19 v_capacity(B_2025_NGCC_2020)
-1.1 v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC)
-1.1 v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC)
<= 0

c_u_planning_reserve_margin_constraint(A_2025_winter_night_NGCC)_:
+1.15 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
+1.15 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_planning_reserve_margin_constraint(C_2025_winter_day_elec_C_ann)_:
-0.25 v_capacity(C_2025_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
<= -0.33

c_u_planning_reserve_margin_constraint(A_2020_summer_night_NGCC)_:
+1.15 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
+1.15 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_planning_reserve_margin_constraint(A_B_2020_winter_day_elec_AB)_:
+1.1 v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
-2.19 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.971 v_capacity(A_2020_E_BATT_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-1.1 v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC)
<= -2.2

c_u_planning_reserve_margin_constraint(A_2020_winter_day_NGCC)_:
+1.15 v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC)
+1.15 v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_planning_reserve_margin_constraint(C_2020_winter_night_elec_C_ann)_:
-0.25 v_capacity(C_2020_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
<= -0.3

c_u_planning_reserve_margin_constraint(A_B_2025_summer_day_elec_AB)_:
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
+1.1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC)
+1.1 v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_E_BATT_2020)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-1.971 v_capacity(A_2025_E_BATT_2025)
-2.19 v_capacity(B_2025_NGCC_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2025)
-2.19 v_capacity(B_2025_NGCC_2020)
-1.1 v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC)
-1.1 v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC)
<= 0

c_u_planning_reserve_margin_constraint(A_B_2020_summer_night_elec_AB)_:
+1.1 v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
-2.19 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.971 v_capacity(A_2020_E_BATT_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-1.1 v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC)
<= -2.2

c_u_planning_reserve_margin_constraint(C_2020_summer_night_elec_C_ann)_:
-0.25 v_capacity(C_2020_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
<= -0.3

c_u_planning_reserve_margin_constraint(A_B_2020_winter_night_elec_AB)_:
+1.1 v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
-1.1578947368421053 v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC)
-1.1578947368421053 v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
-2.19 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.971 v_capacity(A_2020_E_BATT_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-1.1 v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC)
<= -2.2

c_u_planning_reserve_margin_constraint(C_2025_summer_day_elec_C_ann)_:
-0.25 v_capacity(C_2025_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
<= -0.33

c_u_planning_reserve_margin_constraint(A_B_2025_winter_night_elec_AB)_:
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC)
+1.1 v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
-1.1578947368421053 v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT)
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC)
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC)
+1.1 v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC)
+1.1 v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT)
+1.1 v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC)
+1.1 v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2015)
-1.971 v_capacity(A_2025_E_BATT_2020)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(B_2025_NGCC_2025)
-2.19 v_capacity(C_B_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2020)
-2.19 v_capacity(C_A_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-1.971 v_capacity(A_2025_E_BATT_2025)
-2.19 v_capacity(B_2025_NGCC_2015)
+2.19 v_capacity(A_C_2025_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2025_SOLPV_2025)
+2.19 v_capacity(B_C_2025_E_TRANS_2015)
-2.19 v_capacity(A_2025_NGCC_2025)
-2.19 v_capacity(B_2025_NGCC_2020)
-1.1 v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC)
-1.1 v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC)
<= 0

c_u_planning_reserve_margin_constraint(A_2025_summer_day_NGCC)_:
+1.15 v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC)
+1.15 v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_planning_reserve_margin_constraint(A_2020_winter_night_NGCC)_:
+1.15 v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
<= 0

c_u_planning_reserve_margin_constraint(A_2025_summer_night_NGCC)_:
+1.15 v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC)
+1.15 v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_planning_reserve_margin_constraint(A_2025_winter_day_NGCC)_:
+1.15 v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC)
+1.15 v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC)
+1.15 v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC)
-2.19 v_capacity(A_2025_NGCC_2015)
-2.19 v_capacity(A_2025_NGCC_2020)
-2.19 v_capacity(A_2025_NGCC_2025)
<= 0

c_u_planning_reserve_margin_constraint(C_2025_winter_night_elec_C_ann)_:
-0.25 v_capacity(C_2025_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
<= -0.33

c_u_planning_reserve_margin_constraint(C_2020_winter_day_elec_C_ann)_:
-0.25 v_capacity(C_2020_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C)
<= -0.3

c_u_planning_reserve_margin_constraint(C_2025_summer_night_elec_C_ann)_:
-0.25 v_capacity(C_2025_ANN_IMP_2020)
+0.3 v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C)
<= -0.33

c_u_planning_reserve_margin_constraint(A_B_2020_summer_day_elec_AB)_:
-1.1578947368421053 v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC)
+1.1 v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC)
+1.1 v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC)
+1.1 v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC)
+1.1 v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC)
-1.1578947368421053 v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC)
+1.1 v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC)
-2.19 v_capacity(A_2020_NGCC_2020)
+2.19 v_capacity(B_C_2020_E_TRANS_2015)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2015)
-2.19 v_capacity(B_2020_NGCC_2015)
+2.19 v_capacity(A_C_2020_E_TRANS_2015)
-1.971 v_capacity(A_2020_E_BATT_2020)
-0.32849999999999996 v_capacity(A_2020_SOLPV_2020)
-2.19 v_capacity(A_2020_NGCC_2015)
-2.19 v_capacity(B_2020_NGCC_2020)
-2.19 v_capacity(C_B_2020_E_TRANS_2015)
-2.19 v_capacity(C_A_2020_E_TRANS_2015)
-1.1 v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC)
<= -2.2

bounds
   1 <= ONE_VAR_CONSTANT <= 1
   0 <= v_flow_out(B_A_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(B_C_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(B_A_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_C_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(B_A_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_A_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_C_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(C_A_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(C_A_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_A_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(B_2020_summer_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(B_C_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(B_C_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2020_summer_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(C_A_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_C_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_C_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2025_winter_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_A_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2020_summer_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_C_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(B_C_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_2025_winter_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_C_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2025_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_C_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(C_B_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_A_2025_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(C_B_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2020_summer_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(C_A_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2020_winter_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2020_winter_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(C_A_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_2020_summer_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_B_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_night_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(B_2020_summer_night_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_C_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2020_summer_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_out(B_A_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_night_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2020_winter_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_out(B_C_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2020_summer_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2025_winter_day_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(B_2020_summer_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(B_2025_winter_night_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(B_C_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(B_C_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2025_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_flow_out(B_2020_winter_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_A_2020_winter_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2020_winter_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2020_summer_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_out(A_B_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_A_2020_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out(A_2025_summer_day_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out(A_2025_summer_night_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_summer_night_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_flow_out(A_C_2025_summer_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(C_B_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_day_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(B_2025_winter_day_NG_NGCC_2020_ELC) <= +inf
   0 <= v_flow_out(A_2025_winter_night_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(B_A_2020_summer_night_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_B_2020_winter_day_ELC_E_TRANS_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_day_ethos_IMP_NG_2020_NG) <= +inf
   0 <= v_flow_out(A_2025_summer_night_NG_NGCC_2015_ELC) <= +inf
   0 <= v_flow_out(B_2025_summer_night_NG_NGCC_2025_ELC) <= +inf
   0 <= v_flow_out(A_2020_summer_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_flow_out(A_2020_winter_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_capacity(C_2025_HEAT_ANN_2020) <= +inf
   0 <= v_capacity(A_2020_HEAT_SYS_2020) <= +inf
   0 <= v_capacity(A_2025_SOLPV_2015) <= +inf
   0 <= v_capacity(A_2025_E_BATT_2020) <= +inf
   0 <= v_capacity(A_2025_NGCC_2015) <= +inf
   0 <= v_capacity(A_B_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_2020_NGCC_2020) <= +inf
   0 <= v_capacity(B_2025_NGCC_2025) <= +inf
   0 <= v_capacity(B_C_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(C_B_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_2025_SOLPV_2020) <= +inf
   0 <= v_capacity(C_A_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_2025_NGCC_2020) <= +inf
   0 <= v_capacity(A_2025_E_BATT_2025) <= +inf
   0 <= v_capacity(A_2020_SOLPV_2015) <= +inf
   0 <= v_capacity(B_2020_NGCC_2015) <= +inf
   0 <= v_capacity(A_2025_HEAT_SYS_2020) <= +inf
   0 <= v_capacity(B_2025_NGCC_2015) <= +inf
   0 <= v_capacity(B_2025_HEAT_SYS_2020) <= +inf
   0 <= v_capacity(B_A_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(C_2020_ANN_IMP_2020) <= +inf
   0 <= v_capacity(C_2020_HEAT_ANN_2020) <= +inf
   0 <= v_capacity(A_B_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_C_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_2020_E_BATT_2020) <= +inf
   0 <= v_capacity(A_C_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(B_2020_HEAT_SYS_2020) <= +inf
   0 <= v_capacity(A_2025_SOLPV_2025) <= +inf
   0 <= v_capacity(B_C_2025_E_TRANS_2015) <= +inf
   0 <= v_capacity(A_2025_NGCC_2025) <= +inf
   0 <= v_capacity(A_2025_HEAT_SYS_2025) <= +inf
   0 <= v_capacity(A_2020_SOLPV_2020) <= +inf
   0 <= v_capacity(A_2020_NGCC_2015) <= +inf
   0 <= v_capacity(B_2020_NGCC_2020) <= +inf
   0 <= v_capacity(B_2025_NGCC_2020) <= +inf
   0 <= v_capacity(C_B_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(B_2025_HEAT_SYS_2025) <= +inf
   0 <= v_capacity(B_A_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(C_A_2020_E_TRANS_2015) <= +inf
   0 <= v_capacity(C_2025_ANN_IMP_2020) <= +inf
   0 <= v_curtailment(A_2025_summer_day_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2025_summer_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2020_winter_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2025_summer_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_day_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_curtailment(A_2020_winter_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2020_summer_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2025_summer_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2025_summer_night_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_curtailment(A_2020_winter_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2020_summer_night_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_night_ethos_SOLPV_2025_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2020_summer_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2025_summer_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2020_summer_day_ethos_SOLPV_2015_ELC) <= +inf
   0 <= v_curtailment(A_2020_winter_day_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_curtailment(A_2025_winter_night_ethos_SOLPV_2020_ELC) <= +inf
   0 <= v_flow_out_annual(A_2025_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out_annual(B_2025_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out_annual(A_2025_ELC_HEAT_SYS_2020_HEAT) <= +inf
   0 <= v_flow_out_annual(C_2025_ethos_ANN_IMP_2020_ELC_C) <= +inf
   0 <= v_flow_out_annual(B_2025_ELC_HEAT_SYS_2025_HEAT) <= +inf
   0 <= v_flow_out_annual(C_2020_ethos_ANN_IMP_2020_ELC_C) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_2025_NGCC) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2020_E_BATT) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_2025_HEAT_SYS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_2025_HEAT_ANN) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_B_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_C_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_C_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_2020_HEAT_ANN) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_B_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2025_SOLPV) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_2020_NGCC) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_B_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_A_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_C_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_2020_HEAT_SYS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2025_NGCC) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_2025_ANN_IMP) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_B_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2025_HEAT_SYS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_A_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2020_SOLPV) <= +inf
   0 <= v_capacity_available_by_period_and_tech(B_A_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2025_E_BATT) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_C_2025_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2020_NGCC) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_2020_ANN_IMP) <= +inf
   0 <= v_capacity_available_by_period_and_tech(C_A_2020_E_TRANS) <= +inf
   0 <= v_capacity_available_by_period_and_tech(A_2020_HEAT_SYS) <= +inf
   0 <= v_new_capacity(A_SOLPV_2020) <= +inf
   0 <= v_new_capacity(B_NGCC_2020) <= +inf
   0 <= v_new_capacity(A_HEAT_SYS_2025) <= +inf
   0 <= v_new_capacity(A_NGCC_2020) <= +inf
   0 <= v_new_capacity(A_E_BATT_2020) <= +inf
   0 <= v_new_capacity(B_HEAT_SYS_2020) <= +inf
   0 <= v_new_capacity(A_SOLPV_2025) <= +inf
   0 <= v_new_capacity(B_NGCC_2025) <= +inf
   0 <= v_new_capacity(C_ANN_IMP_2020) <= +inf
   0 <= v_new_capacity(A_HEAT_SYS_2020) <= +inf
   0 <= v_new_capacity(A_NGCC_2025) <= +inf
   0 <= v_new_capacity(A_E_BATT_2025) <= +inf
   0 <= v_new_capacity(C_HEAT_ANN_2020) <= +inf
   0 <= v_new_capacity(B_HEAT_SYS_2025) <= +inf
   0 <= v_flow_in(A_2020_winter_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2025_winter_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2020_summer_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2025_summer_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2025_winter_night_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_in(A_2025_winter_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2025_winter_day_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_in(A_2025_summer_day_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_in(A_2025_summer_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2020_winter_night_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_flow_in(A_2025_summer_night_ELC_E_BATT_2025_ELC) <= +inf
   0 <= v_flow_in(A_2020_summer_day_ELC_E_BATT_2020_ELC) <= +inf
   0 <= v_storage_init(A_2025_summer_E_BATT_2020) <= +inf
   0 <= v_storage_init(A_2025_winter_E_BATT_2020) <= +inf
   0 <= v_storage_init(A_2020_summer_E_BATT_2020) <= +inf
   0 <= v_storage_init(A_2020_winter_E_BATT_2020) <= +inf
   0 <= v_storage_init(A_2025_summer_E_BATT_2025) <= +inf
   0 <= v_storage_init(A_2025_winter_E_BATT_2025) <= +inf
   0 <= v_storage_level(A_2020_winter_night_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2020_summer_night_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_winter_day_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_summer_night_E_BATT_2025) <= +inf
   0 <= v_storage_level(A_2025_summer_day_E_BATT_2025) <= +inf
   0 <= v_storage_level(A_2025_winter_night_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_winter_day_E_BATT_2025) <= +inf
   0 <= v_storage_level(A_2020_winter_day_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_summer_night_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_summer_day_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2020_summer_day_E_BATT_2020) <= +inf
   0 <= v_storage_level(A_2025_winter_night_E_BATT_2025) <= +inf
end
