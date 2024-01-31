import sqlite3
import os
import sys
import re
import pandas as pd


class DatabaseUtil(object):
	def __init__(self, databasePath, scenario=None):
		self.database = os.path.abspath(databasePath)
		self.scenario = scenario
		if not os.path.exists(self.database):
			raise ValueError("The database file path doesn't exist")
		
		if self.isDataBaseFile(self.database):
			try:
				self.con = sqlite3.connect(self.database)
				self.cur = self.con.cursor()
				self.con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding
			except Exception as e:
				raise ValueError('Unable to connect to database')
		elif self.database.endswith('.dat'):
			self.con = None
			self.cur = None

	def close(self):
		if (self.cur):
			self.cur.close()
		if (self.con):
			self.con.close()

	@staticmethod
	def isDataBaseFile(file):
		if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
			return True
		else:
			return False

	def readFromDatFile(self, inp_comm, inp_tech):
		if (not self.cur is None):
			raise ValueError("Invalid Operation For Database file")
		if inp_comm is None and inp_tech is None :
			inp_comm = "\w+"
			inp_tech = "\w+"
		else :
			if inp_comm is None :
				inp_comm = "\W+"
			if inp_tech is None :
				inp_tech = "\W+"

		test2 = []
		eff_flag = False
		with open (self.database) as f:
			for line in f:
				if eff_flag is False and re.search("^\s*param\s+efficiency\s*[:][=]", line, flags = re.I) : 
					#Search for the line param Efficiency := (The script recognizes the commodities specified in this section)
					eff_flag = True
				elif eff_flag:
					line = re.sub("[#].*$", " ", line)
					if re.search("^\s*;\s*$", line)	:
						break #  Finish searching this section when encounter a ';'
					if re.search("^\s+$", line)	:
						continue
					line = re.sub("^\s+|\s+$", "", line)
					row = re.split("\s+", line)
					if not re.search(inp_comm, row[0]) and not re.search(inp_comm, row[3]) and not re.search(inp_tech, row[1]) :
						continue
					
					test2.append(tuple(row))

		result = pd.DataFrame(test2, columns = ['input_comm', 'tech', 'period', 'output_comm', 'flow'])
		return result[['input_comm', 'tech', 'output_comm']]


	def getTimePeridosForFlags(self, flags=[]):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		query = ''
		if (flags is None) or (not flags):
			query = "SELECT t_periods FROM time_periods"
		else:
			flag = flags[0]
			query = "SELECT t_periods FROM time_periods WHERE flag is '"+flag+"'"
			for i in range(1, len(flags)):
				query += " OR flag is '"+flags[i]+"'"

		self.cur.execute(query)
		result = set()
		for row in self.cur:
			result.add(int(row[0]))

		return result

	def getTechnologiesForFlags(self, flags=[]):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		query = ''
		if (flags is None) or (not flags):
			query = "SELECT tech FROM technologies"
		else:
			flag = flags[0]
			query = "SELECT tech FROM technologies WHERE flag='"+flag+"'"
			for i in range(1, len(flags)):
				query += " OR flag='"+flags[i]+"'"

		result = set()
		for row in self.cur.execute(query):
			result.add(row[0])

		return result

	# TODO: Merge this with next function (getExistingTechnologiesForCommodity)
	def getCommoditiesAndTech(self, inp_comm, inp_tech, region):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		if inp_comm is None and inp_tech is None :
			inp_comm = "NOT NULL"
			inp_tech = "NOT NULL"
		else :
			if inp_comm is None :
				inp_comm = "NULL"
			else :
				inp_comm = "'"+inp_comm+"'"
			if inp_tech is None :
				inp_tech = "NULL"
			else :
				inp_tech = "'"+inp_tech+"'"

		if region==None:
			self.cur.execute("SELECT input_comm, tech, output_comm FROM Efficiency WHERE input_comm is "+inp_comm+" or output_comm is "+inp_comm+" or tech is "+inp_tech)
		else:
			self.cur.execute("SELECT input_comm, tech, output_comm FROM Efficiency WHERE regions LIKE '%"+region+"%' and (input_comm is "+inp_comm+" or output_comm is "+inp_comm+" or tech is "+inp_tech+")")
		return pd.DataFrame(self.cur.fetchall(), columns = ['input_comm', 'tech', 'output_comm'])

	def getExistingTechnologiesForCommodity(self, comm, region, comm_type='input'):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		query = ''
		if (comm_type == 'input'):
			query = "SELECT DISTINCT tech FROM Efficiency WHERE input_comm is '"+comm+"'"
		else:
			query = "SELECT DISTINCT tech FROM Efficiency WHERE output_comm is '"+comm+"'"
		if region:
			query +=" AND regions LIKE '%" + region + "%'"

		self.cur.execute(query)
		result = pd.DataFrame(self.cur.fetchall(), columns = ['tech'])
		return result
		

	def getCommoditiesForFlags(self, flags=[]):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		query = ''
		if (flags is None) or (not flags):
			query = "SELECT comm_name FROM commodities"
		else:
			flag = flags[0]
			query = "SELECT comm_name FROM commodities WHERE flag is '"+flag+"'"
			for i in range(1, len(flags)):
				query += " OR flag is '"+flags[i]+"'"

		result = set()
		for row in self.cur.execute(query):
			result.add(row[0])

		return result

	# comm_type can be 'input' or 'output'
	def getCommoditiesByTechnology(self, region, comm_type='input'):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		query = ''
		if (comm_type == 'input'):
			query = 'SELECT DISTINCT input_comm, tech FROM Efficiency'
		elif (comm_type == 'output'):
			query = 'SELECT DISTINCT tech, output_comm FROM Efficiency'
		else:
			raise ValueError('Invalid commodity comm_type: can only be input or output')

		if region:
			query += " WHERE regions LIKE '%" + region + "%'"
		result = set()
		for row in self.cur.execute(query):
			result.add((row[0], row[1]))

		return result

	def getCapacityForTechAndPeriod(self, tech = None, period = None, region = None):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		if self.scenario is None or self.scenario == '':
			raise ValueError('For Output related queries, please set a scenario first')

		columns = []
		if tech is None:
			columns.append('tech')
		if period is None:
			columns.append('t_periods')
		columns.append('capacity')
		columns.append('regions')

		query = "SELECT "+columns[0]

		for col in columns[1:]:
			query += ", " + col

		query += " FROM Output_CapacityByPeriodAndTech WHERE scenario == '"+self.scenario+"'"

		if (region):
			query += " AND regions LIKE '" + region + "%'"
		if (tech):
			query += " AND tech is '"+tech+"'"
		if (period):
			query += " AND t_periods == '"+str(period)+"'"

		self.cur.execute(query)
		result = pd.DataFrame(self.cur.fetchall(), columns=columns)
		if region is None:
			mask = result['regions'].str.contains('-')
			result.loc[mask, 'capacity'] /=2

		result.drop(columns=['regions'], inplace=True)
		if (len(columns) == 2):
			return result.sum()
		else:
			return result.groupby(by='tech').sum().reset_index()

	def getOutputFlowForPeriod(self, period, region, comm_type='input', commodity=None):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		if self.scenario is None or self.scenario == '':
			raise ValueError('For Output related queries, please set a scenario first')
		columns = []
		table = ''
		col = ''
		if (comm_type =='input'):
			table = 'Output_VFlow_In'
			if (commodity is None):
				columns.append('input_comm')
			col = 'vflow_in'
		columns.append('tech')
		if (comm_type== 'output'):
			table = 'Output_VFlow_Out'
			if (commodity is None):
				columns.append('output_comm')
			col = 'vflow_out'

		query = "SELECT DISTINCT "
		for c in columns:
			query += c+", "
		query += 'SUM('+col+") AS flow FROM "+table+" WHERE scenario is '"+self.scenario+"'"
		if (region) and (comm_type=='input'):
			query += " AND regions LIKE '" + region + "%'"
		if (region) and (comm_type=='output'):
			query += " AND regions LIKE '%" + region + "'"
		query += " AND t_periods is '"+str(period)+"' "

		query2 = " GROUP BY tech"
		if (not commodity is None):
			query += ' AND '+comm_type+"_comm is '"+commodity+"'"
			if (comm_type == 'output'):
				query += " AND input_comm != 'ethos' "
		else:
			query2 += ", "+comm_type+'_comm'
		
		query += query2
		columns.append('flow')
		self.cur.execute(query)
		result = pd.DataFrame(self.cur.fetchall(), columns=columns)
		return result

	def getEmissionsActivityForPeriod(self, period, region):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		if self.scenario is None or self.scenario == '':
			raise ValueError('For Output related queries, please set a scenario first')
		query = "SELECT E.emis_comm, E.tech, SUM(E.emis_act*O.vflow_out) FROM EmissionActivity E, Output_VFlow_Out O " + \
		"WHERE E.input_comm == O.input_comm AND E.tech == O.tech AND E.vintage  == O.vintage AND E.output_comm == O.output_comm AND O.scenario == '"+ self.scenario +"' " + \
		"and O.t_periods == '"+str(period) + "'"
		if (region):
			query += " AND E.regions LIKE '%" + region + "%'"
		query +=" GROUP BY E.tech, E.emis_comm"
		self.cur.execute(query)
		result = pd.DataFrame(self.cur.fetchall(), columns=['emis_comm', 'tech', 'emis_activity'])
		return result

	def getCommodityWiseInputAndOutputFlow(self, tech, period, region):
		if (self.cur is None):
			raise ValueError("Invalid Operation For dat file")
		if self.scenario is None or self.scenario == '':
			raise ValueError('For Output related queries, please set a scenario first')

		query = "SELECT OF.input_comm, OF.output_comm, OF.vintage, OF.regions,\
	SUM(OF.vflow_in) vflow_in, SUM(OFO.vflow_out) vflow_out, OC.capacity \
FROM (SELECT regions, scenario, sector, t_periods, input_comm, tech, vintage, output_comm, sum(vflow_in) AS vflow_in \
 FROM Output_VFlow_In GROUP BY regions, scenario, sector, t_periods, input_comm, tech, vintage, output_comm) AS OF \
INNER JOIN (SELECT regions, scenario, sector, t_periods, input_comm, tech, vintage, output_comm, sum(vflow_out) AS vflow_out \
 FROM Output_VFlow_Out GROUP BY regions, scenario, sector, t_periods, input_comm, tech, vintage, output_comm) AS OFO \
ON  \
    OF.regions = OFO.regions AND \
	OF.scenario = OFO.scenario AND \
	OF.t_periods = OFO.t_periods AND \
	OF.tech = OFO.tech AND \
	OF.input_comm = OFO.input_comm AND \
	OF.vintage = OFO.vintage AND \
	OF.output_comm = OFO.output_comm \
INNER JOIN \
	Output_V_Capacity OC \
ON \
	OF.regions = OC.regions AND \
	OF.scenario = OC.scenario AND \
	OF.tech = OC.tech AND \
	OF.vintage = OC.vintage \
WHERE \
	OF.t_periods ='"+ str(period) + "' AND \
	OF.tech is '" + tech+ "' AND \
	OF.scenario is '" + self.scenario + "'"

		if (region):
			query += " AND OF.regions LIKE '%" + region + "%'"

		query +=" GROUP BY OF.regions, OF.vintage, OF.input_comm, OF.output_comm"

		self.cur.execute(query)
		result = pd.DataFrame(self.cur.fetchall(), columns=['input_comm', 'output_comm', 'vintage', 'regions','flow_in', 'flow_out', 'capacity'])
		result = pd.DataFrame(result.groupby(['input_comm', 'output_comm', 'vintage']).sum().reset_index())
		return result
		
