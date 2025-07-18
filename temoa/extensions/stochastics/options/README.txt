Stochastic Temoa Tree Generation Options Files
==============================================

The options.py files in this directory describe stochastic trees as implemented
by the generate_scenario_tree.py script in the parent directory.  These files
serve as a command line input to that script, specifying various items necessary
to create a generic scenario tree stucture and input dot dat files.

The options.py files in this directory will generally be imported via the
generate_scenario_tree.py script in the parent directory.  The script then
expects to be able to access the below items via the imported file.

If any of the below is not clear, the other files in this directory can serve as
examples.  If you do not have the files, the Temoa repository contains them all
at http://svn.temoaproject.org/trac/.  Check "Browse Source".  At the time of
this writing, the files are located in

branches/stochastic/options/

Elements an options.py Should Specify
=====================================

(str) dirname (optional)
  This directory will be where all output files are placed.  If not specified,
  the name of the options file will be used as the default.

(bool) verbose
  Should the script give information about it's progress?

(bool) force
  If the dirname already exists, remove it before proceeding?

(path) modelpath
  Relative or absolute path of where to find the model

(path) dotdatpath
  Relative or absolute path of where to find the base LP dat file.

(str) stochasticset
  Within the model, the name of the stochastic set that indexes the parameters
  to be rate-modified.

(tuple) stochastic_points
  Within the model, specifically /which/ items in the stochastic set are the
  stochastic ones?  For the parameters specified in types and rates, the ones
  indexed by these points will be modified.  Note that for useful output, this
  item, if specified, needs at least two stochastic points, and the first one
  will have a conditional probability of 1.

(dict) stochastic_indices
  For each parameter to modify, the numerical order of its stochastic index.
  This is a 0-based, numerical specification.

(tuple of strings) types
  Each item in this tuple is the name of a decision branch from a node.  However
  many items specified here, are the number of branches each node in the event
  tree will have.

(dict) conditional_probability
  This dict specifies the conditional probability of each branch.

(dict of dicts of tuples) rates
  This is a two-level dict that specifies each parameter to modify, and for each
  branch in types, what to multiply against each index.  Indices can be
  explicitly spelled-out, or specified in a group via an asterisk.

-----
