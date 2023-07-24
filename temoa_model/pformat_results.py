"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.
"""

# ---------------------------------------------------------------------------
# This module processes model output data, which can be sent to three possible
# locations: the shell, a user-specified database, or an Excel file. Users can
# configure the available outputs.
# ---------------------------------------------------------------------------


__all__ = ('pformat_results', 'stringify_data')

from collections import defaultdict
from sys import stderr as SE, stdout as SO
from shutil import rmtree
import sqlite3
import os
import re
import subprocess
import sys
import pandas as pd

from temoa_config import TemoaConfig

# Need line below to import DB_to_Excel.py from data_processing
sys.path.append(os.path.join(os.getcwd(), 'data_processing'))
from DB_to_Excel import make_excel

# Ensure compatibility with Python 2.7 and 3
try:
	from cStringIO import StringIO
except ImportError:
	from io import StringIO

from pyomo.core import value


def stringify_data ( data, ostream=SO, format='plain' ):
	# data is a list of tuples of ('var_name[index]', value)
	#  data must be a list, as this function replaces each row,
	# format is currently unused, but will be utilized to implement things like
	# csv

	# This padding code is what makes the display of the output values
	# line up on the decimal point.
	for i, (v, val) in enumerate( data ):
		ipart, fpart = repr(f"{val:.6f}").split('.')
		data[i] = (ipart, fpart, v)
	cell_lengths = ( map(len, l[:-1] ) for l in data )
	max_lengths = map(max, zip(*cell_lengths))   # max length of each column
	fmt = u'  {{:>{:d}}}.{{:<{:d}}}  {{}}\n'.format( *max_lengths )

	for row in data:
		ostream.write( fmt.format(*row) )


def pformat_results ( pyomo_instance, pyomo_result, options ):
	from pyomo.core import Objective, Var, Constraint

	output = StringIO()

	m = pyomo_instance            # lazy typist
	result = pyomo_result

	soln = result['Solution']
	solv = result['Solver']      # currently unused, but may want it later
	prob = result['Problem']     # currently unused, but may want it later

	optimal_solutions = (
	  'feasible', 'globallyOptimal', 'locallyOptimal', 'optimal'
	)
	if str(soln.Status) not in optimal_solutions:
		output.write( 'No solution found.' )
		return output

	objs = list(m.component_data_objects( Objective ))
	if len( objs ) > 1:
		msg = '\nWarning: More than one objective.  Using first objective.\n'
		SE.write( msg )

	Cons = soln.Constraint


	def collect_result_data( cgroup, clist, epsilon):
		# cgroup = "Component group"; i.e., Vars or Cons
		# clist = "Component list"; i.e., where to store the data
		# epsilon = absolute value below which to ignore a result
		results = defaultdict(list)
		for name, data in cgroup.items():
			if 'Value' not in data.keys() or (abs( data['Value'] ) < epsilon ) : continue

			# name looks like "Something[some,index]"
			group, index = name[:-1].split('[')
			results[ group ].append( (name.replace("'", ''), data['Value']) )
		clist.extend( t for i in sorted( results ) for t in sorted(results[i]))

		supp_outputs_df = pd.DataFrame.from_dict(cgroup, orient='index')
		supp_outputs_df = supp_outputs_df.loc[(supp_outputs_df != 0).any(axis=1)]
		if 'Dual' in supp_outputs_df.columns:
			duals = supp_outputs_df['Dual'].copy()
			duals = duals[abs(duals)>1e-5]
			duals.index.name = 'constraint_name'
			duals = duals.to_frame()
			if (hasattr(options, 'scenario')) & (len(duals)>0):
				duals.loc[:,'scenario'] = options.scenario
				return duals
			else:
				return []

	#Create a dictionary in which to store "solved" variable values
	svars = defaultdict( lambda: defaultdict( float ))

	con_info = list()
	epsilon = 1e-5   # threshold for "so small it's zero"

	emission_keys = { (r, i, t, v, o) : set() for r, e, i, t, v, o in m.EmissionActivity }
	for r, e, i, t, v, o in m.EmissionActivity:
		emission_keys[(r, i, t, v, o)].add(e)
	P_0 = min( m.time_optimize )
	P_e = m.time_future.last()
	GDR = value( m.GlobalDiscountRate )
	MPL = m.ModelProcessLife
	LLN = m.LifetimeLoanProcess
	x   = 1 + GDR    # convenience variable, nothing more

	if hasattr(options, 'file_location') and os.path.join('temoa_model', 'config_sample_myopic') in options.file_location:
		original_dbpath = options.output
		con = sqlite3.connect(original_dbpath)
		cur = con.cursor()
		time_periods = cur.execute("SELECT t_periods FROM time_periods WHERE flag='f'").fetchall()
		P_0 = time_periods[0][0]
		P_e = time_periods[-1][0]
		# We need to know if a myopic run is the last run or not.
		P_e_time_optimize = time_periods[-2][0]
		P_e_current = int(options.file_location.split("_")[-1])
		con.commit()
		con.close()

	# Extract optimal decision variable values related to commodity flow:
	for r, p, s, d, t, v in m.V_StorageLevel:
		val = value( m.V_StorageLevel[r, p, s, d, t, v] )
		if abs(val) < epsilon: continue

		svars['V_StorageLevel'][r, p, s, d, t, v] = val

	# vflow_in is defined only for storage techs
	for r, p, s, d, i, t, v, o in m.V_FlowIn:
		val_in = value( m.V_FlowIn[r, p, s, d, i, t, v, o] )
		if abs(val_in) < epsilon: continue

		svars['V_FlowIn'][r, p, s, d, i, t, v, o] = val_in

	for r, p, s, d, i, t, v, o in m.V_FlowOut:
		val_out = value( m.V_FlowOut[r, p, s, d, i, t, v, o] )
		if abs(val_out) < epsilon: continue

		svars['V_FlowOut'][r, p, s, d, i, t, v, o] = val_out

		if t not in m.tech_storage:
			val_in = value( m.V_FlowOut[r, p, s, d, i, t, v, o] ) / value(m.Efficiency[r, i, t, v, o])
			svars['V_FlowIn'][r, p, s, d, i, t, v, o] = val_in

		if (r, i, t, v, o) not in emission_keys: continue

		emissions = emission_keys[r, i, t, v, o]
		for e in emissions:
			evalue = val_out * m.EmissionActivity[r, e, i, t, v, o]
			svars[ 'V_EmissionActivityByPeriodAndProcess' ][r, p, e, t, v] += evalue

	for r, p, i, t, v, o in m.V_FlowOutAnnual:
		for s in m.time_seasons_per_period_dict[p]:
			for d in m.time_of_day:
				val_out = value( m.V_FlowOutAnnual[r, p, i, t, v, o] ) * value( m.SegFrac[s , d ])
				if abs(val_out) < epsilon: continue
				svars['V_FlowOut'][r, p, s, d, i, t, v, o] = val_out
				svars['V_FlowIn'][r, p, s, d, i, t, v, o] = val_out / value(m.Efficiency[r, i, t, v, o])
				if (r, i, t, v, o) not in emission_keys: continue
				emissions = emission_keys[r, i, t, v, o]
				for e in emissions:
					evalue = val_out * m.EmissionActivity[r, e, i, t, v, o]
					svars[ 'V_EmissionActivityByPeriodAndProcess' ][r, p, e, t, v] += evalue

	for r, p, s, d, i, t, v, o in m.V_Curtailment:
		val = value( m.V_Curtailment[r, p, s, d, i, t, v, o] )
		if abs(val) < epsilon: continue
		svars['V_Curtailment'][r, p, s, d, i, t, v, o] = val
		svars['V_FlowIn'][r, p, s, d, i, t, v, o] = (val + value( m.V_FlowOut[r, p, s, d, i, t, v, o] )) / value(m.Efficiency[r, i, t, v, o])

		if (r, i, t, v, o) not in emission_keys: continue

		emissions = emission_keys[r, i, t, v, o]
		for e in emissions:
			evalue = val * m.EmissionActivity[r, e, i, t, v, o]
			svars[ 'V_EmissionActivityByPeriodAndProcess' ][r, p, e, t, v] += evalue

	for r, p, i, t, v, o in m.V_FlexAnnual:
		for s in m.time_seasons_per_period_dict[p]:
			for d in m.time_of_day:
				val_out = value( m.V_FlexAnnual[r, p, i, t, v, o] ) * value( m.SegFrac[s , d ])
				if abs(val_out) < epsilon: continue
				svars['V_Curtailment'][r, p, s, d, i, t, v, o] = val_out
				svars['V_FlowOut'][r, p, s, d, i, t, v, o] -= val_out


	for r, p, s, d, i, t, v, o in m.V_Flex:
		val_out = value( m.V_Flex[r, p, s, d, i, t, v, o] )
		if abs(val_out) < epsilon: continue
		svars['V_Curtailment'][r, p, s, d, i, t, v, o] = val_out
		svars['V_FlowOut'][r, p, s, d, i, t, v, o] -= val_out

	# Extract optimal decision variable values related to capacity:
	if hasattr(options, 'file_location') and os.path.join('temoa_model', 'config_sample_myopic') not in options.file_location:
		for r, t, v in m.V_Capacity:
			val = value( m.V_Capacity[r, t, v] )
			if abs(val) < epsilon: continue
			svars['V_Capacity'][r, t, v] = val
	else:
		for r, t, v in m.V_Capacity:
			if v in m.time_optimize:
				val = value( m.V_Capacity[r, t, v] )
				if abs(val) < epsilon: continue
				svars['V_Capacity'][r, t, v] = val

	for r, p, t in m.V_CapacityAvailableByPeriodAndTech:
		val = value( m.V_CapacityAvailableByPeriodAndTech[r, p, t] )
		if abs(val) < epsilon: continue
		svars['V_CapacityAvailableByPeriodAndTech'][r, p, t] = val

	# Calculate model costs:
	if hasattr(options, 'file_location') and os.path.join('temoa_model', 'config_sample_myopic') not in options.file_location:
		# This is a generic workaround.  Not sure how else to automatically discover
		# the objective name
		obj_name, obj_value = objs[0].getname(True), value( objs[0] )
		svars[ 'Objective' ]["('"+obj_name+"')"] = obj_value

		for r, t, v in m.CostInvest.sparse_iterkeys():   # Returns only non-zero values

			icost = value( m.V_Capacity[r, t, v] )
			if abs(icost) < epsilon: continue
			icost *= value( m.CostInvest[r, t, v] ) \
			* (
				min( value(m.LifetimeLoanProcess[r, t, v]), P_e - v ) /
				value( m.LifetimeLoanProcess[r, t, v] )
				if not GDR
				else (
						(
							1 -  x**( -min( value(m.LifetimeLoanProcess[r, t, v]), P_e - v ) )
						)/(
							1 -  x**( -value( m.LifetimeLoanProcess[r, t, v] ) )
						)
					)
			)
			svars[	'Costs'	][ 'V_UndiscountedInvestmentByProcess', r, t, v] += icost

			icost *= value( m.LoanAnnualize[r, t, v] )
			icost *= (
			  value( LLN[r, t, v] ) if not GDR else
				(x **(P_0 - v + 1) * (1 - x **(-value( LLN[r, t, v] ))) / GDR)
			)

			svars[	'Costs'	][ 'V_DiscountedInvestmentByProcess', r, t, v] += icost


		for r, p, t, v in m.CostFixed.sparse_iterkeys():
			fcost = value( m.V_Capacity[r, t, v] )
			if abs(fcost) < epsilon: continue

			fcost *= value( m.CostFixed[r, p, t, v] )
			svars[	'Costs'	][ 'V_UndiscountedFixedCostsByProcess', r, t, v] += fcost * value( MPL[r, p, t, v] )

			fcost *= (
			  value( MPL[r, p, t, v] ) if not GDR else
				(x **(P_0 - p + 1) * (1 - x **(-value( MPL[r, p, t, v] ))) / GDR)
			)

			svars[	'Costs'	][ 'V_DiscountedFixedCostsByProcess', r, t, v] += fcost

		for r, p, t, v in m.CostVariable.sparse_iterkeys():
			if t not in m.tech_annual:
				vcost = sum(
					value (m.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o])
					for S_i in m.processInputs[r, p, t, v]
					for S_o in m.ProcessOutputsByInput[r, p, t, v, S_i]
					for S_s in m.time_seasons_per_period_dict[p]
					for S_d in m.time_of_day
				)
			else:
				vcost = sum(
					value (m.V_FlowOutAnnual[r, p, S_i, t, v, S_o])
					for S_i in m.processInputs[r, p, t, v]
					for S_o in m.ProcessOutputsByInput[r, p, t, v, S_i]
				)
			if abs(vcost) < epsilon: continue

			vcost *= value( m.CostVariable[r, p, t, v] )
			svars[	'Costs'	][ 'V_UndiscountedVariableCostsByProcess', r, t, v] += vcost * value( MPL[r, p, t, v] )
			vcost *= (
			  value( MPL[r, p, t, v] ) if not GDR else
				(x **(P_0 - p + 1) * (1 - x **(-value( MPL[r, p, t, v] ))) / GDR)
			  )
			svars[	'Costs'	][ 'V_DiscountedVariableCostsByProcess', r, t, v] += vcost



		#update the costs of exchange technologies.
		#Assumption 1: If Ri-Rj appears in the cost tables but Rj-Ri does not,
		#then the total costs are distributed between the regions
		#Ri and Rj proportional to their use of the exchange technology connecting the
		#regions.
		#Assumption 2: If both the directional entries appear in the cost tables,
		#Assumption 1 is no longer applied and the costs are calculated as they
		#are entered in the cost tables.
		# assumption 3: Unlike other output tables in which Ri-Rj and Rj-Ri entries
		# are allowed in the region column, for the Output_Costs table the region
		#to the right of the hyphen sign gets the costs.
		for i in m.RegionalExchangeCapacityConstraint_rrtv.keys():
			if i == None:
				continue
			reg_dir1  = i[0]+"-"+i[1]
			reg_dir2 = i[1]+"-"+i[0]
			tech = i[2]
			vintage  = i[3]
			key = (reg_dir1, tech, vintage)
			try:
				act_dir1 = value (sum(m.V_FlowOut[reg_dir1, p, s, d, S_i, tech, vintage, S_o]
					for p in m.time_optimize if (p < vintage + value(m.LifetimeProcess[reg_dir1, tech, vintage])) and (p >= vintage)
					for s in m.time_seasons_per_period_dict[p]
					for d in m.time_of_day
					for S_i in m.processInputs[reg_dir1, p, tech, vintage]
					for S_o in m.ProcessOutputsByInput[reg_dir1, p, tech, vintage, S_i]
					))
				act_dir2 = value (sum(m.V_FlowOut[reg_dir2, p, s, d, S_i, tech, vintage, S_o]
					for p in m.time_optimize if (p < vintage + value(m.LifetimeProcess[reg_dir1, tech, vintage])) and (p >= vintage)
					for s in m.time_seasons_per_period_dict[p]
					for d in m.time_of_day
					for S_i in m.processInputs[reg_dir2, p, tech, vintage]
					for S_o in m.ProcessOutputsByInput[reg_dir2, p, tech, vintage, S_i]
					))
			except:
				act_dir1 = value (sum(m.V_FlowOutAnnual[reg_dir1, p, S_i, tech, vintage, S_o]
					for p in m.time_optimize if (p < vintage + value(m.LifetimeProcess[reg_dir1, tech, vintage])) and (p >= vintage)
					for S_i in m.processInputs[reg_dir1, p, tech, vintage]
					for S_o in m.ProcessOutputsByInput[reg_dir1, p, tech, vintage, S_i]
					))
				act_dir2 = value (sum(m.V_FlowOutAnnual[reg_dir2, p, S_i, tech, vintage, S_o]
					for p in m.time_optimize if (p < vintage + value(m.LifetimeProcess[reg_dir1, tech, vintage])) and (p >= vintage)
					for S_i in m.processInputs[reg_dir2, p, tech, vintage]
					for S_o in m.ProcessOutputsByInput[reg_dir2, p, tech, vintage, S_i]
					))

			for item in list(svars[	'Costs'	]):
				if item[2] == tech:
					opposite_dir = item[1][item[1].find("-")+1:]+"-"+item[1][:item[1].find("-")]
					if (item[0],opposite_dir,item[2],item[3]) in svars[	'Costs'	].keys():
						continue #if both directional entries are already in svars[	'Costs'	], they're left intact.
					if item[1] == reg_dir1:
						if (act_dir1+act_dir2)>0:
							svars[	'Costs'	][(item[0],reg_dir2,item[2],item[3])] = svars[	'Costs'	][item] * act_dir2 / (act_dir1 + act_dir2)
							svars[	'Costs'	][item] = svars[	'Costs'	][item] * act_dir1 / (act_dir1 + act_dir2)


		#Remove Ri-Rj entries from being populated in the Outputs_Costs. Ri-Rj means a cost
		#for region Rj
		for item in list(svars[	'Costs'	]):
			if item[2] in m.tech_exchange:
				svars[	'Costs'	][(item[0],item[1][item[1].find("-")+1:],item[2],item[3])] = svars[	'Costs'	][item]
				del svars[	'Costs'	][item]

	if options.saveDUALS:
		duals = collect_result_data( Cons, con_info, epsilon=1e-9 )

	msg = ( 'Model name: %s\n'
	   'Objective function value (%s): %s\n'
	   'Non-zero variable values:\n'
	)
	if hasattr(options, 'file_location') and os.path.join('temoa_model', 'config_sample_myopic') not in options.file_location:
		output.write( msg % (m.name, obj_name, obj_value) )

	def make_var_list ( variables ):
		var_list = []
		for vgroup, values in sorted( variables.items() ):
			for vindex, val in sorted( values.items() ):
				if isinstance( vindex, tuple ):
					vindex = ','.join( str(i) for i in vindex )
				var_list.append(( '{}[{}]'.format(vgroup, vindex), val ))
		return var_list

	if svars:
		stringify_data( make_var_list(svars), output )
	else:
		output.write( '\nAll variables have a zero (0) value.\n' )

	if len( con_info ) > 0:
		output.write( '\nBinding constraint values:\n' )
		stringify_data( con_info, output )
		del con_info
	else:
		# Since not all Coopr solvers give constraint results, must check
		msg = '\nSelected Coopr solver plugin does not give constraint data.\n'
		output.write( msg )

	output.write( '\n\nIf you use these results for a published article, '
	  "please run Temoa with the '--how_to_cite' command line argument for "
	  'citation information.\n')

	# -----------------------------------------------------------------
	# Write outputs stored in dictionary to the user-specified database
	# -----------------------------------------------------------------

	# Table dictionary below maps variable names to database table names
	tables = { "V_FlowIn"   : "Output_VFlow_In",  \
			   "V_FlowOut"  : "Output_VFlow_Out", \
			   "V_Curtailment"  : "Output_Curtailment", \
			   "V_Capacity" : "Output_V_Capacity",       \
			   "V_CapacityAvailableByPeriodAndTech"   : "Output_CapacityByPeriodAndTech",  \
			   "V_EmissionActivityByPeriodAndProcess" : "Output_Emissions", \
			   "Objective"  : "Output_Objective", \
			   "Costs"      : "Output_Costs"
			   }

	db_tables = ['time_periods', 'time_season', 'time_of_day', 'technologies', 'commodities',\
				'LifetimeTech', 'LifetimeProcess', 'Efficiency', 'EmissionActivity', 'ExistingCapacity']

	if isinstance(options, TemoaConfig):
		if not options.output:
			if options.saveTEXTFILE or options.keepPyomoLP:
				for inpu in options.dot_dat:
					print(inpu)
					file_ty = re.search(r"\b([\w-]+)\.(\w+)\b", inpu)
				new_dir = options.path_to_data+os.sep+file_ty.group(1)+'_'+options.scenario+'_model'
				if os.path.exists( new_dir ):
					rmtree( new_dir )
				os.mkdir(new_dir)
			print("No Output File specified.")
			return output

		if not os.path.exists(options.output) :
			print("Please put the "+options.output+" file in the right Directory")
			return output


		con = sqlite3.connect(options.output)
		cur = con.cursor()   # A database cursor enables traversal over DB records
		con.text_factory = str # This ensures data is explored with UTF-8 encoding

		### Copy tables from Input File to DB file.
		# IF output file is empty database.
		cur.execute("SELECT * FROM technologies")
		is_db_empty = False #False for empty db file
		for elem in cur:
			is_db_empty = True #True for non-empty db file
			break


		if is_db_empty: #This file could be schema with populated results from previous run. Or it could be a normal db file.
			cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_file';")
			does_input_file_table_exist = False
			for i in cur: # This means that the 'input_file' table exists in db.
				does_input_file_table_exist = True
			if does_input_file_table_exist: #This block distinguishes normal database from schema.
				#This is schema file.
				cur.execute("SELECT file FROM input_file WHERE id is '1';")
				for i in cur:
					tagged_file = i[0]
				tagged_file = re.sub('["]', "", tagged_file)

				if tagged_file == options.dot_dat[0]:
					#If Input_file name matches, add output and check tech/comm
					dat_to_db(options.dot_dat[0], con)
				else:
					#If not a match, delete output tables and update input_file. Call dat_to_db
					for i in db_tables:
						cur.execute("DELETE FROM "+i+";")
						cur.execute("VACUUM;")

					for i in tables.keys():
						cur.execute("DELETE FROM "+tables[i]+";")
						cur.execute("VACUUM;")

					for i in options.dot_dat:
						cur.execute("DELETE FROM input_file WHERE id=1;")
						cur.execute("INSERT INTO input_file VALUES(1, '"+i+"');")
						break
					dat_to_db(i, con)

		else: #empty schema db file
			cur.execute("CREATE TABLE IF NOT EXISTS input_file ( id integer PRIMARY KEY, file varchar(30));")

			for i in tables.keys():
				cur.execute("DELETE FROM "+tables[i]+";")
				cur.execute("VACUUM;")

			for i in options.dot_dat:
				cur.execute("DELETE FROM input_file WHERE id=1;")
				cur.execute("INSERT INTO input_file(id, file) VALUES(?, ?);", (1,  '"'+i+'"'))
				break
			dat_to_db(i, con)


		for table in svars.keys() :
			if table in tables :
				cur.execute("SELECT DISTINCT scenario FROM '"+tables[table]+"'")
				for val in cur :
					# If scenario exists, delete unless it's a myopic run (for myopic, the scenario results are deleted
					# before the run in temoa_config.py)
					if hasattr(options, 'file_location') and options.scenario == val[0] and os.path.join('temoa_model', 'config_sample_myopic') not in options.file_location:
						cur.execute("DELETE FROM "+tables[table]+" \
									WHERE scenario is '"+options.scenario+"'")
				if table == 'Objective' : # Only table without sector info
					for key in svars[table].keys():
						key_str = str(key) # only 1 row to write
						key_str = key_str[1:-1] # Remove parentheses
						cur.execute("INSERT INTO "+tables[table]+" \
									VALUES('"+options.scenario+"',"+key_str+", \
									"+str(svars[table][key])+");")
				else : # First add 'NULL' for sector then update
					for key in svars[table].keys() : # Need to loop over keys (rows)
						key_str = str(key)
						key_str = key_str[1:-1] # Remove parentheses
						if table != 'Costs':
							cur.execute("INSERT INTO "+tables[table]+ \
										" VALUES('"+str(key[0])+"', '"+options.scenario+"','NULL', \
											"+key_str[key_str.find(',')+1:]+","+str(svars[table][key])+");")
						else:
							key_str = str((key[0],key[2],key[3]))
							key_str = key_str[1:-1] # Remove parentheses
							cur.execute("INSERT INTO "+tables[table]+ \
										" VALUES('"+str(key[1])+"', '"+options.scenario+"','NULL', \
										"+key_str+","+str(svars[table][key])+");")
					cur.execute("UPDATE "+tables[table]+" SET sector = \
								(SELECT technologies.sector FROM technologies \
								WHERE "+tables[table]+".tech = technologies.tech);")

		#WRITE DUALS RESULTS
		if (options.saveDUALS):
			if (len(duals)!=0):
				overwrite_keys = [str(tuple(x)) for x in duals.reset_index()[['constraint_name','scenario']].to_records(index=False)]
				#delete records that will be overwritten by new duals dataframe
				cur.execute("DELETE FROM Output_Duals WHERE (constraint_name, scenario) IN (VALUES " + ','.join(overwrite_keys) + ")")
				#write new records from new duals dataframe
				duals.to_sql('Output_Duals',con, if_exists='append')

		con.commit()
		con.close()

		if options.saveEXCEL or options.saveTEXTFILE or options.keepPyomoLP:
			for inpu in options.dot_dat:
				file_ty = re.search(r"\b([\w-]+)\.(\w+)\b", inpu)
			new_dir = options.path_to_data+os.sep+file_ty.group(1)+'_'+options.scenario+'_model'
			if os.path.exists( new_dir ):
				rmtree( new_dir )
			os.mkdir(new_dir)

			if options.saveEXCEL:
				file_type = re.search(r"([\w-]+)\.(\w+)\b", options.output)
				file_n = file_type.group(1)
				temp_scenario = set()
				temp_scenario.add(options.scenario)
				#make_excel function imported near the top
				make_excel(options.output, new_dir+os.sep+options.scenario, temp_scenario)
				#os.system("python data_processing"+os.sep+"DB_to_Excel.py -i \
				#		  ""+options.output+" \
				#		  " -o data_files"+os.sep+options.scenario+" -s "+options.scenario)

	return output

def dat_to_db(input_file, output_schema, run_partial=False):

	def traverse_dat(dat_filename, search_tablename):

		result_string = ""
		table_found_flag = False

		with open(dat_filename) as f:
			for line in f:
				line = re.sub("[#].*$", " ", line)

				if table_found_flag:
					result_string += line
					if re.search(";\s*$", line):
						break

				if re.search(""+search_tablename+"\s*[:][=]", line):
					result_string += line
					table_found_flag = True
					if re.search(";\s*$", line):
						break

		return result_string

	#####Code Starts here
	tables_single_value = [	'time_exist', 'time_future', 'time_season', 'time_of_day', \
				'tech_baseload', 'tech_resource', 'tech_production', 'tech_storage', \
				'commodity_physical', 'commodity_demand', 'commodity_emissions']

	partial_run_tech = ['tech_baseload', 'tech_resource', 'tech_production', 'tech_storage']

	partial_run_comm = ['commodity_physical', 'commodity_demand', 'commodity_emissions']

	tables_multiple_value = ['ExistingCapacity', 'Efficiency', 'LifetimeTech', \
								'LifetimeProcess', 'EmissionActivity']

	parsed_data = {}

	#if db_or_dat_flag: #This is an input db file
	#	import pdb; pdb.set_trace()
	#	output_schema.execute("ATTACH DATABASE ? AS db2;", "'"+input_file+"'")
	#	for i in db_tables:
	#		output_schema.execute("INSERT INTO "+i+" SELECT * FROM db2."+i+";")

	if run_partial:
		comm_set = set()
		tech_set = set()
		for i in partial_run_comm:
			raw_string = traverse_dat(input_file, i)
			raw_string = re.sub("\s+", " ", raw_string)
			raw_string = re.sub("^.*[:][=]", "", raw_string)
			raw_string = re.sub(";\s*$", "", raw_string)
			raw_string = re.sub("^\s+|\s+$", "", raw_string)
			parsed_data[i] = re.split(" ", raw_string)
			for datas in parsed_data[i]:
				if datas == '':
					continue
				comm_set.add(datas)

		for i in partial_run_tech:
			raw_string = traverse_dat(input_file, i)
			raw_string = re.sub("\s+", " ", raw_string)
			raw_string = re.sub("^.*[:][=]", "", raw_string)
			raw_string = re.sub(";\s*$", "", raw_string)
			raw_string = re.sub("^\s+|\s+$", "", raw_string)
			parsed_data[i] = re.split(" ", raw_string)
			for datas in parsed_data[i]:
				if datas == '':
					continue
				tech_set.add(datas)

		return comm_set, tech_set

	#This is an input dat file
	for i in tables_single_value:
		raw_string = traverse_dat(input_file, i)
		raw_string = re.sub("\s+", " ", raw_string)
		raw_string = re.sub("^.*[:][=]", "", raw_string)
		raw_string = re.sub(";\s*$", "", raw_string)
		raw_string = re.sub("^\s+|\s+$", "", raw_string)
		parsed_data[i] = re.split(" ", raw_string)

	for i in tables_multiple_value:
		raw_string = traverse_dat(input_file, i)
		raw_string = re.sub("\n", ",", raw_string)
		raw_string = re.sub("\s+", " ", raw_string)
		raw_string = re.sub("^.*[:][=]\s*,", "", raw_string)
		raw_string = re.sub(",?;\s*,?$", "", raw_string)
		raw_string = re.sub("^\s+|\s+$", "", raw_string)
		raw_string = re.sub("\s?,\s?", ",", raw_string)
		raw_string = re.sub(",+", ",", raw_string)
		parsed_data[i] = re.split(",", raw_string)

	#Fill time_periods
	for i in parsed_data['time_exist']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO time_periods VALUES("+i+", 'e');")
	for i in parsed_data['time_future']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO time_periods VALUES("+i+", 'f');")

	#Fill time_season
	for i in parsed_data['time_season']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO time_season VALUES('"+i+"');")

	#Fill time_of_day
	for i in parsed_data['time_of_day']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO time_of_day VALUES('"+i+"');")

	#Fill technologies
	for i in parsed_data['tech_baseload']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO technologies VALUES('"+i+"', 'pb', '', '');")
	for i in parsed_data['tech_storage']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO technologies VALUES('"+i+"', 'ph', '', '');")
	for i in parsed_data['tech_production']:
		if i == '':
			continue
		if i in parsed_data['tech_storage']:
			continue
		if i in parsed_data['tech_baseload']:
			continue
		output_schema.execute("INSERT OR REPLACE INTO technologies VALUES('"+i+"', 'p', '', '');")
	for i in parsed_data['tech_resource']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO technologies VALUES('"+i+"', 'r', '', '');")

	#Fill commodities
	for i in parsed_data['commodity_demand']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO commodities VALUES('"+i+"', 'd', '');")
	for i in parsed_data['commodity_physical']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO commodities VALUES('"+i+"', 'p', '');")
	for i in parsed_data['commodity_emissions']:
		if i == '':
			continue
		output_schema.execute("INSERT OR REPLACE INTO commodities VALUES('"+i+"', 'e', '');")


	#Fill ExistingCapacity
	for i in parsed_data['ExistingCapacity']:
		if i == '':
			continue
		row_data = re.split(" ", i)
		row_data.append('')
		row_data.append('')
		output_schema.execute("INSERT OR REPLACE INTO ExistingCapacity VALUES(?, ?, ?, ?, ?);", row_data)

	#Fill Efficiency
	for i in parsed_data['Efficiency']:
		if i == '':
			continue
		row_data = re.split(" ", i)
		row_data.append('')
		output_schema.execute("INSERT OR REPLACE INTO Efficiency VALUES(?, ?, ?, ?, ?, ?);", row_data)

	#Fill LifetimeTech
	for i in parsed_data['LifetimeTech']:
		if i == '':
			continue
		row_data = re.split(" ", i)
		row_data.append('')
		output_schema.execute("INSERT OR REPLACE INTO LifetimeTech VALUES(?, ?, ?);", row_data)

	#Fill LifetimeProcess
	for i in parsed_data['LifetimeProcess']:
		if i == '':
			continue
		row_data = re.split(" ", i)
		row_data.append('')
		output_schema.execute("INSERT OR REPLACE INTO LifetimeProcess VALUES(?, ?, ?, ?);", row_data)

	#Fill EmissionActivity
	for i in parsed_data['EmissionActivity']:
		if i == '':
			continue
		row_data = re.split(" ", i)
		row_data.append('')
		if len(row_data) == 7:
			row_data.append('')
		output_schema.execute("INSERT OR REPLACE INTO EmissionActivity VALUES(?, ?, ?, ?, ?, ?, ?, ?);", row_data)
