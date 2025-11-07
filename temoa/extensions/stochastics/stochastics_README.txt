------------------------------
Stochastic Optimization README
------------------------------

(Solve a stochastic run and store results into a database using config file)
$ python temoa_model/temoa_stochastic.py --config=temoa_model/config_sample
# Note that to invoke the stochastic run, the "--input" flag must be the path
# to ScenarioStructure.dat, and "--output" flag is the path to the target
# database file, where the results will be stored.

(Extensive Formulation or Deterministic Equivalent)
runef -m ../../temoa_model/ -i ./ --solver=glpk --solve >> out.txt

(Progressive Hedging)
runph -m ../../temoa_model/ -i ./ --solver=ipopt --default-rho=1.0

(Solve a particular path in the tree as a linear program)
python ../../temoa_model/ R.dat Rs0.dat Rs0s2.dat

-----------------------------
Stochastic Optimization Tools
-----------------------------

(EVPI computation)
python test_EVPI.py

(VSS computation)
python VSS.py
	#(Information about how to setup a run of VSS):
	#Lines 246 - 249 specify the path to the folders and the solver to be used.
	#It is necessary to change these lines in order to properly point to the
	#instance that you want to solve. The first one just points to the path of the
	#temoa_stochastic.py file. The second one point to the folder of the instance
	#where the scenario tree structure and all the scenarios are represented.
	#p_model = '/home/arqueiroz/SSudan/S1_2_H/temoa_model/temoa_stochastic.py'
	#p_data  = '/home/arqueiroz/SSudan/S1_2_H/stochastic/S_Sudan_original_stoch_cap_cost_11'
	#optsolver = 'cplex'

	#(Deterministic file with average values):
	#Inside the stochastic folder where you want to run the VSS script it is necessary to
	#manually create an input file to represent the uncertainty with average values. This
	#file will be used to run the deterministic instance where we store information about the
	#decisions on the first stage.
	#The name of the input file is defined on line 195

	#(Get info about decisions on the first stage):
	#On line 147
	#ef._binding_instance.S0s0s0.v_capacity[iaux1, iaux2].fix(dv_capacity[iaux1,iaux2])
	#it is necessary to fix the first stage decisions from the deterministic model (with
	#average values) when solving the stochastic program (with fixed values) that will
	#be compared to the true stochastic program (without any fixed values)
	#Note that the left portion of the equation is the one that is fixed. As for now
	#it depends on the number of stages of the problem, for the one used here there is
	#a total of four stages and we need to fix .S0s0s0.v_capacity.fix if it was 3 stages we
	#would make S0s0.v_capacity.fix

	#Additional file for EVPI and VSS usage:
	#pyomo version 4.3.11388 requires the addition
	#of the file ef_writer_script_old.py within the installation
	#of pyomo under anaconda. The correct path to add the
	#file is: /anaconda/lib/python2.7/site-packages/pyomo/pysp

(Generate Scenario Tree)
python generate_scenario_tree.py options/uc_tl_unlim.py
	#Additional files needed for generate scenario tree script:
	#pyomo version 4.3.11388 requires the addition
	#of the file scenariomodels.py within the installation
	#of pyomo under anaconda. The correct path to add the
	#file is: /anaconda/lib/python2.7/site-packages/pyomo/pysp/util


(Script for Parallel runs of runph) (to be used on Neer super computer)
qsub jobTemoa.pbs
