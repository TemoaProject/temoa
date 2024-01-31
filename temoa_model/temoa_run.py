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

from os import path, close as os_close
from sys import argv, stderr as SE, stdout as SO
from signal import signal, SIGINT, default_int_handler
from shutil import copyfile, move

from pyomo.opt import SolverFactory as SF
from pyomo.opt import SolverManagerFactory
from pyomo.environ import *

from temoa_config import TemoaConfig

import errno, warnings
import re as reg_exp

from argparse import Namespace
from os import sep

from pyutilib.services import TempfileManager
from pyutilib.services import TempfileManager
from pyutilib.common import ApplicationError

from sys import version_info, exit

from time import time
import sys, os, gc

from pyomo.environ import DataPortal

from pformat_results import pformat_results

from collections import defaultdict
from temoa_rules import TotalCost_rule, ActivityByTech_Constraint
from temoa_mga   import ActivityObj_rule, SlackedObjective_rule, PreviousAct_rule
import traceback


signal(SIGINT, default_int_handler)


'''
This is the main solver class.
This takes in input an Abstract Model after parameters initialization,
and a config_filename (which contains the input parameters)
If config_filename is empty, it assumes parameters from command line.

The yield statements in this file are used for sending output of this file to UI as it happens,
instead of waiting for it to finish and then sending it finally. yield statements are used by
StreamingHttpResponse of Django to render output as it happens.
any function that uses yield statements can't have return clause.
If it is needed, instead use a class global variable to store the return value.
If any new function is added and its output is also needed to be printed to UI,
then use yield statements along with yield and then at the time of calling that function
yield the output of the function. like:
for statement in function_call():
	yield statement
This will yield each statement being yielded by function_call().
This is followed all the way through to the first function_call of the UI where it is returned
as a StreamingHttpResponse().
'''
class TemoaSolver(object):
	def __init__(self, model, config_filename):
		self.model = model
		self.config_filename = config_filename
		self.temoa_setup()
		self.temoa_checks()

	def temoa_setup (self):
		"""This function prepares the model to be solved.

		Inputs:
		model -- the model object
		config_filename -- config filename, non-blank if called from the UI
		There are three possible ways to call the model:
		1. python temoa_model/ /path/to/data_files
		2. python temoa_model/ --config=/path/to/config/file
		3. function call from the UI
		This function discerns which way the model was called and process the
		inputs accordingly.
		"""
		if self.config_filename == '':  # Called from the command line
			self.options, config_flag = parse_args()
			if config_flag == 1:   # Option 2 (using config file)
				self.options.path_to_lp_files = self.options.path_to_logs + sep + "lp_files"
				TempfileManager.tempdir = self.options.path_to_lp_files
			else:  # Must be Option 1 (no config file)
				pass

		else:   # Config file already specified, so must be an interface call
			available_solvers, default_solver = get_solvers()
			temoa_config = TemoaConfig(d_solver=default_solver)
			temoa_config.build(config=self.config_filename)
			self.options = temoa_config

			self.temp_lp_dest = '/srv/thirdparty/temoa/data_files/'

			self.options.path_to_lp_files = self.options.path_to_logs + sep + "lp_files"
			TempfileManager.tempdir = self.options.path_to_lp_files


	def temoa_checks(self):
		"""Make sure Python 2.7 is used and that a suitable solver is available."""

		if version_info < (2, 7):
			msg = ("Temoa requires Python v2.7 to run.\n\n The model may not solve"
				"properly with another version.")
			raise SystemExit( msg )

		if self.options.neos is True:
		    # Invoke NEOS solver manager if flag is specified in config file
			self.optimizer = pyomo.opt.SolverManagerFactory('neos')
		else:
			self.optimizer = SolverFactory( self.options.solver )

		if self.optimizer:
			pass
		elif self.options.solver != 'NONE':
			SE.write( "\nWarning: Unable to initialize solver interface for '{}'\n\n"
				.format( self.options.solver ))
			if SE.isatty():
				SE.write( "Please press enter to continue or Ctrl+C to quit." )
				if os.path.join('temoa_model','config_sample_myopic') not in options.file_location:
					raw_input()


	'''
	This function is called when MGA option is specified.
	It uses the self.model, self.optimzer, and self.options parameters of the class object
	'''
	def solveWithMGA(self):
		scenario_names = []
		scenario_names.append( self.options.scenario )

		# The MGA algorithm uses different objectives per iteration, so the first
		# step is to remove the original objective function
		self.model.del_component( 'TotalCost' )
		# Create concrete model
		temoaInstance1 = TemoaSolverInstance(self.model, self.optimizer, self.options, self.txt_file)
		for k in temoaInstance1.create_temoa_instance():
			# yield "<div>" + k + "</div>"
			yield k
			#yield " " * 1024
		# Now add back the objective function that we earlier removed; note that name
		# we choose here (FirstObj) will be copied to the output file.
		temoaInstance1.instance.FirstObj = Objective( rule=TotalCost_rule, sense=minimize )
		temoaInstance1.instance.preprocess()
		temoaInstance1.instance.V_ActivityByTech = Var(temoaInstance1.instance.tech_all, domain=NonNegativeReals)
		temoaInstance1.instance.ActivityByTechConstraint = Constraint(temoaInstance1.instance.tech_all, rule=ActivityByTech_Constraint)

		for k in temoaInstance1.solve_temoa_instance():
			# yield "<div>" + k + "</div>"
			yield k
			#yield " " * 1024

		temoaInstance1.handle_files(log_name='Complete_OutputLog.log' )
		# using value() converts the now-loaded results into a single number,
		# which we'll use with our slightly unusual SlackedObjective_rule below
		# (but defined above).
		Perfect_Foresight_Obj = value( temoaInstance1.instance.FirstObj )

		# Create a new dictionary that stores the MGA objective function weights
		prev_activity_t = defaultdict( int )
		# Store first set of MGA objective weights drawn from base solution
		prev_activity_t = PreviousAct_rule( temoaInstance1.instance, self.options.mga_weight, prev_activity_t )

		# Perform MGA iterations
		while self.options.next_mga():
			temoaMGAInstance = TemoaSolverInstance(self.model, self.optimizer, self.options, self.txt_file)
			for k in temoaMGAInstance.create_temoa_instance():
				# yield "<div>" + k + "</div>"
				yield k
				#yield " " * 1024

			try:
				txt_file_mga = open(self.options.path_to_logs+os.sep+"Complete_OutputLog.log", "w")
			except BaseException as io_exc:
				yield "MGA Log file cannot be opened. Please check path. Trying to find:\n"+self.options.path_to_logs+" folder\n"
				SE.write("MGA Log file cannot be opened. Please check path. Trying to find:\n"+self.options.path_to_logs+" folder\n")
				txt_file_mga = open("OutputLog_MGA_last.log", "w")

			# Set up the Activity By Tech constraint, which is required for the
			# updated objective function.
			temoaMGAInstance.instance.V_ActivityByTech = Var(temoaMGAInstance.instance.tech_all, domain=NonNegativeReals)
			temoaMGAInstance.instance.ActivityByTechConstraint = Constraint(temoaMGAInstance.instance.tech_all, rule=ActivityByTech_Constraint)

			# Update second instance with the new MGA-specific objective function
			# and constraint.
			temoaMGAInstance.instance.SecondObj = Objective(
			expr=ActivityObj_rule( temoaMGAInstance.instance, prev_activity_t ),
			noruleinit=True,
			sense=minimize
			)
			temoaMGAInstance.instance.PreviousSlackedObjective = Constraint(
			rule=None,
			expr=SlackedObjective_rule( temoaMGAInstance.instance, Perfect_Foresight_Obj, self.options.mga ),
			noruleinit=True
			)
			temoaMGAInstance.instance.preprocess()
			for k in temoaMGAInstance.solve_temoa_instance():
				# yield "<div>" + k + "</div>"
				yield k
				#yield " " * 1024
			temoaMGAInstance.handle_files(log_name='Complete_OutputLog.log' )
			#Update MGA objective function weights for use in the next iteration
			prev_activity_t = PreviousAct_rule( temoaMGAInstance.instance, self.options.mga_weight, prev_activity_t )


	'''
	This function is called when MGA option is not specified.
	'''
	def solveWithoutMGA(self):

		temoaInstance1 = TemoaSolverInstance(self.model, self.optimizer, self.options, self.txt_file)

		if hasattr(self.options, 'myopic') and self.options.myopic:

			print ('This run is myopic ...')
			from temoa_myopic import myopic_db_generator_solver
			myopic_db_generator_solver ( self )

		else:

			for k in temoaInstance1.create_temoa_instance():
				# yield "<div>" + k + "</div>"
				yield k
				#yield " " * 1024
			for k in temoaInstance1.solve_temoa_instance():
				# yield "<div>" + k + "</div>"
				yield k
				#yield " " * 1024
			temoaInstance1.handle_files(log_name='Complete_OutputLog.log')

	'''
	This funciton creates and solves TemoaSolverInstance.
	This is the function that should be called from outside this class after __init__
	'''
	def createAndSolve(self):
		try:
			self.txt_file = open(self.options.path_to_logs+os.sep+"Complete_OutputLog.log", "w")

		except BaseException as io_exc:
			yield "Log file cannot be opened. Please check path. Trying to find:\n"+self.options.path_to_logs+" folder\n"
			SE.write("Log file cannot be opened. Please check path. Trying to find:\n"+self.options.path_to_logs+" folder\n")
			self.txt_file = open("Complete_OutputLog.log", "w")
			self.txt_file.write("Log file cannot be opened. Please check path. Trying to find:\n"+self.options.path_to_logs+" folder\n")

		# Check and see if mga attribute exists and if mga is specified
		try:
			if hasattr(self.options, 'mga') and self.options.mga:
				for k in self.solveWithMGA():
					#yield "<div>" + k + "</div>"
					yield k
					#yield " " * 1024
			else:  #  User requested a single run
				for k in self.solveWithoutMGA():
					#yield "<div>" + k + "</div>"
					yield k
					#yield " " * 1024

		except KeyboardInterrupt as e:
			self.txt_file.close()
			yield str(e) + '\n'
			yield 'User requested quit.  Exiting Temoa ...\n'
			SE.write(str(e)+'\n')
			SE.write( 'User requested quit.  Exiting Temoa ...\n' )
			traceback.print_exc()
			SE.flush()
		except SystemExit as e:
			self.txt_file.close()
			yield str(e) + '\n'
			yield 'Temoa exit requested.  Exiting ...\n'
			SE.write(str(e)+'\n')
			SE.write( 'Temoa exit requested.  Exiting ...\n' )
			traceback.print_exc()
			SE.flush()
		except Exception as e:
			self.txt_file.close()
			yield str(e) + '\n'
			yield 'Exiting Temoa ...\n'
			SE.write(str(e)+'\n')
			SE.write( 'Exiting Temoa ...\n' )
			traceback.print_exc()
			SE.flush()



'''
This class is for creating one temoa solver instance. It is used by TemoaSolver.
(Multiple instances are created for MGA/non-MGA options).
'''
class TemoaSolverInstance(object):
	def __init__(self, model, optimizer, options, txt_file):
		self.model = model
		self.options = options
		self.optimizer = optimizer
		self.txt_file = txt_file

	def create_temoa_instance (self):
		"""Create a single instance of Temoa."""

		try:
			if self.options.keepPyomoLP:
				yield '\nSolver will write file: {}\n\n'.format( self.options.scenario + '.lp' )
				SE.write('\nSolver will write file: {}\n\n'.format( self.options.scenario + '.lp' ))
				self.txt_file.write('\nSolver will write file: {}\n\n'.format( self.options.scenario + '.lp' ))

			yield 'Reading data files.'
			SE.write( '[        ] Reading data files.'); SE.flush()
			self.txt_file.write( 'Reading data files.')
			begin = time()
			duration = lambda: time() - begin

			modeldata = DataPortal( model=self.model )
			# Recreate the pyomo command's ability to specify multiple "dot dat" files
			# on the command lin
			for fname in self.options.dot_dat:
				if fname[-4:] != '.dat':
					msg = "InputError: expecting a dot dat (e.g., data.dat) file, found '{}'\n"
					raise Exception( msg.format( fname ))
				modeldata.load( filename=fname )
			yield '\t\t\t\t\t[%8.2f]\n' % duration()
			SE.write( '\r[%8.2f]\n' % duration() )
			self.txt_file.write( '[%8.2f]\n' % duration() )

			yield 'Creating Temoa model instance.'
			SE.write( '[        ] Creating Temoa model instance.'); SE.flush()
			self.txt_file.write( 'Creating Temoa model instance.')

			self.model.dual = Suffix(direction=Suffix.IMPORT)
			#self.model.rc = Suffix(direction=Suffix.IMPORT)
			#self.model.slack = Suffix(direction=Suffix.IMPORT)

			self.instance = self.model.create_instance( modeldata )
			yield '\t\t\t\t[%8.2f]\n' % duration()
			SE.write( '\r[%8.2f]\n' % duration() )
			self.txt_file.write( '[%8.2f]\n' % duration() )

		except Exception as model_exc:
			yield "Exception found in create_temoa_instance\n"
			SE.write("Exeception found in create_temoa_instance\n")
			self.txt_file.write("Exception found in create_temoa_instance\n")
			yield str(model_exc)
			SE.write(str(model_exc))
			self.txt_file.write(str(model_exc))
			raise model_exc


	def solve_temoa_instance (self):
		'''Solve a Temoa instance.'''

		begin = time()
		duration = lambda: time() - begin
		try:
			yield 'Solving.'
			SE.write( '[        ] Solving.'); SE.flush()
			self.txt_file.write( 'Solving.')
			if self.optimizer:
				if self.options.neos:
				    self.result = self.optimizer.solve(self.instance, opt=self.options.solver)
				else:
				    self.result = self.optimizer.solve( self.instance, suffixes=['dual'],# 'rc', 'slack'],
								keepfiles=self.options.keepPyomoLP,
								symbolic_solver_labels=self.options.keepPyomoLP )
				yield '\t\t\t\t\t\t[%8.2f]\n' % duration()
				SE.write( '\r[%8.2f]\n' % duration() )
				self.txt_file.write( '[%8.2f]\n' % duration() )
				# return signal handlers to defaults, again
				signal(SIGINT, default_int_handler)

				# ... print the easier-to-read/parse format
				msg = '[        ] Calculating reporting variables and formatting results.'
				yield 'Calculating reporting variables and formatting results.'
				SE.write( msg ); SE.flush()
				self.txt_file.write( 'Calculating reporting variables and formatting results.')
				self.instance.solutions.store_to(self.result)
				formatted_results = pformat_results( self.instance, self.result, self.options )
				yield '\t[%8.2f]\n' % duration()
				SE.write( '\r[%8.2f\n' % duration() )
				self.txt_file.write( '[%8.2f]\n' % duration() )
				yield formatted_results.getvalue() + '\n'
				#SO.write( formatted_results.getvalue() )
				self.txt_file.write( formatted_results.getvalue() )
				if formatted_results.getvalue()=='No solution found.':
					SE.write( formatted_results.getvalue() + '\n')
			else:
				yield '\r---------- Not solving: no available solver\n'
				SE.write( '\r---------- Not solving: no available solver\n' )
				self.txt_file.write( '\r---------- Not solving: no available solver\n' )

		except BaseException as model_exc:
			yield "Exception found in solve_temoa_instance\n"
			SE.write("Exception found in solve_temoa_instance\n")
			self.txt_file.write("Exception found in solve_temoa_instance\n")
			yield str(model_exc)+'\n'
			SE.write(str(model_exc))
			self.txt_file.write(str(model_exc))
			raise model_exc

	def handle_files(self, log_name):
		"""Handle log and LP file assuming user called with config file or from interface."""
		if isinstance(self.options, TemoaConfig) and self.options.saveTEXTFILE:
			for inpu in self.options.dot_dat:
				file_ty = reg_exp.search(r"\b([\w-]+)\.(\w+)\b", inpu)
			new_dir = self.options.path_to_data+os.sep+file_ty.group(1)+'_'+self.options.scenario+'_model'
			if path.isfile(self.options.path_to_logs+os.sep+log_name) and path.exists(new_dir):
				copyfile(self.options.path_to_logs+os.sep+log_name, new_dir+os.sep+self.options.scenario+'_OutputLog.log')

		if isinstance(self.options, TemoaConfig) and self.options.keepPyomoLP:
			for inpu in self.options.dot_dat:
				file_ty = reg_exp.search(r"\b([\w-]+)\.(\w+)\b", inpu)

			new_dir = self.options.path_to_data+os.sep+file_ty.group(1)+'_'+self.options.scenario+'_model'

			for files in os.listdir(self.options.path_to_lp_files):
				if files.endswith(".lp"):
					lpfile = files
				else:
					if files == "README.txt":
						continue
					os.remove(self.options.path_to_lp_files+os.sep+files)

			if path.exists(new_dir):
				move(self.options.path_to_lp_files+os.sep+lpfile, new_dir+os.sep+self.options.scenario+'.lp')


def get_solvers():
	"""Return the solvers avaiable on the system."""
	from logging import getLogger

	logger = getLogger('pyomo.solvers')
	logger_status = logger.disabled
	logger.disabled = True  # no need for warnings: it's what we're testing!

	available_solvers = set()
	try:
		services = SF.services() # pyutilib version <= 5.6.3
	except RuntimeError as e:
		services = SF # pyutilib version >= 5.6.4

	for sname in services:
		# initial underscore ('_'): Pyomo's method to mark non-public plugins
		if '_' == sname[0]: continue

		solver = SF( sname )

		try:
			if not solver: continue
		except ApplicationError as e:
			continue

		if 'os' == sname: continue     # Workaround current bug in Coopr
		if not solver.available( exception_flag=False ): continue
		available_solvers.add( sname )

	logger.disabled = logger_status  # put back the way it was.

	if available_solvers:
		if 'cplex' in available_solvers:
			default_solver = 'cplex'
		elif 'gurobi' in available_solvers:
			default_solver = 'gurobi'
		elif 'cbc' in available_solvers:
			default_solver = 'cbc'
		elif 'glpk' in available_solvers:
			default_solver = 'glpk'
		else:
			default_solver = iter(available_solvers).next()
	else:
		default_solver = 'NONE'
		SE.write('\nNOTICE: Pyomo did not find any suitable solvers.  Temoa will '
		   'not be able to solve any models.  If you need help, ask on the '
		   'Temoa Project forum: http://temoaproject.org/\n\n' )

	return (available_solvers, default_solver)



def parse_args ( ):
	"""Parse arguments specfied from command line or in config file."""
	import argparse, sys
	import os, re
	from os.path import dirname, abspath

	available_solvers, default_solver = get_solvers()

	parser = argparse.ArgumentParser()
	parser.prog = path.basename( argv[0].strip('/') )

	parser.add_argument('dot_dat',
	  type=str,
	  nargs='*',
	  help='AMPL-format data file(s) with which to create a model instance. '
	       'e.g. "data.dat"'
	)

	parser.add_argument( '--path_to_logs',
	  help='Path to where debug logs will be generated by default. See folder debug_logs in data_files.',
	  action='store',
	  dest='path_to_logs',
	  default=re.sub('temoa_model$', 'data_files', dirname(abspath(__file__)))+os.sep+"debug_logs"
	)

	parser.add_argument( '--config',
	 help='Path to file containing configuration information.',
	 action='store',
	 dest='config',
	 default=None
	 )

	parser.add_argument('--solver',
	  help="Which backend solver to use.  See 'pyomo --help-solvers' for a list "
	       'of solvers with which Pyomo can interface.  The list shown here is '
	       'what Pyomo can currently find on this system.  [Default: {}]'
	       .format(default_solver),
	  action='store',
	  choices=sorted(available_solvers),
	  dest='solver',
	  default=default_solver)

	options = parser.parse_args()
	options.neos = False

	# Can't specify keeping the LP file without config file, so set this
	# attribute to false
	options.keepPyomoLP = False

	# If the user specifies the config flag, then call TemoaConfig and overwrite
	# the argument parser above.
	if options.config:
		config_flag = 1  #flag indicates config file was used.
		try:
			temoa_config = TemoaConfig(d_solver=default_solver)
			temoa_config.build(config=options.config)
			SE.write(repr(temoa_config))
			options = temoa_config
			SE.write('\nPlease press enter to continue or Ctrl+C to quit.\n')
			#raw_input() # Give the user a chance to confirm input
			if options.abort_temoa:
				return
		except KeyboardInterrupt:
			SE.write('\n\nUser requested quit.  Exiting Temoa ...\n')
			raise SystemExit()
	else:
		config_flag = 0	#flag indicates config file was not used.

	s_choice = str( options.solver ).upper()
	SE.write('Notice: Using the {} solver interface.\n'.format( s_choice ))
	SE.flush()

	SE.write("Continue Operation? [Press enter to continue or CTRL+C to abort]\n")
	SE.flush()
	try:  #make compatible with Python 2.7 or 3
		if os.path.join('temoa_model', 'config_sample_myopic') not in options.file_location:
			#
			raw_input() # Give the user a chance to confirm input
	except:
		input()

	return options, config_flag
