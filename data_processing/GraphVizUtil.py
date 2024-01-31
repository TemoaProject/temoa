import sys
import getopt
import re
import os
import argparse


def processInput(args):
	parser = argparse.ArgumentParser(description="Generate Output Plot")
	parser.add_argument('-i', '--input', action="store", dest="ifile", help="Input Database Filename <path>", required=True)
	parser.add_argument('-f', '--format', action="store", dest="image_format", help="Graphviz output format (Default: svg)", default='svg')
	parser.add_argument('-c', '--show_capacity', action="store_true", dest="show_capacity",
							help="Whether capacity shows up in subgraphs (Default: not shown)", default=False)
	parser.add_argument('-v', '--splinevar', action="store_true", dest="splinevar", help="Whether subgraph edges to be straight or curved (Default: Straight)", default=False)
	parser.add_argument('-t', '--graph_type', action="store", dest="graph_type", help="Type of subgraph (Default: separate_vintages)",
							choices = ['separate_vintages', 'explicit_vintages'], default='separate_vintages')
	parser.add_argument('-g', '--gray', action="store_true", dest="grey_flag", help="If specified, generates graph in graycale", default=False)
	parser.add_argument('-n', '--name', action="store", dest="quick_name", help="Specify the extension you wish to give your quick run")
	parser.add_argument('-o', '--output', action="store", dest="res_dir", help='Optional output file path (to dump the images folder)', default='./')

	group1 = parser.add_mutually_exclusive_group()
	group1.add_argument('-b', '--technology', action="store", dest="inp_technology", help="Technology for which graph to be generated")
	group1.add_argument('-a', '--commodity', action="store", dest="inp_commodity", help="Commodity for which graph to be generated")

	parser.add_argument('-s', '--scenario', action="store", dest="scenario_name", help="Model run scenario name", default=None)
	parser.add_argument('-y', '--year', action="store", dest="period", type=int, help="The period for which the graph is to be generated (Used only for output plots)")
	parser.add_argument('-r', '--region', action="store", dest="region", help="The region for which the graph is to be generated", default=None)

	options = parser.parse_args(args)

	if (bool(options.scenario_name) ^ bool(options.period)):
		parser.print_help()
		raise ValueError("Scenario and input year must both be present or not present together")

	return vars(options)

def getColorConfig(grey_flag):
	grey_flag = not (grey_flag)
	kwargs = dict(
	  tech_color         = 'darkseagreen' if grey_flag else 'black',
	  commodity_color    = 'lightsteelblue' if grey_flag else 'black',
	  unused_color       = 'powderblue' if grey_flag else 'gray75',
	  arrowheadout_color = 'forestgreen' if grey_flag else 'black',
	  arrowheadin_color  = 'firebrick' if grey_flag else 'black',
	  usedfont_color     = 'black',
	  unusedfont_color   = 'chocolate' if grey_flag else 'gray75',
	  menu_color         = 'hotpink',
	  home_color         = 'gray75',
	  font_color	     = 'black' if grey_flag else 'white',
	  fill_color	     = 'lightsteelblue' if grey_flag else 'white',

	  #MODELDETAILED,
	  md_tech_color      = 'hotpink',

	  sb_incom_color     = 'lightsteelblue' if grey_flag else 'black',
	  sb_outcom_color    = 'lawngreen' if grey_flag else 'black',
	  sb_vpbackg_color   = 'lightgrey',
	  sb_vp_color        = 'white',
	  sb_arrow_color     = 'forestgreen' if grey_flag else 'black',

	  #SUBGRAPH 1 ARROW COLORS
	  color_list = ('red', 'orange', 'gold', 'green', 'blue', 'purple',
	                'hotpink', 'cyan', 'burlywood', 'coral', 'limegreen',
	                'black', 'brown') if grey_flag else ('black', 'black'),
	)
	return kwargs

def _getLen ( key ):
	def wrapped ( obj ):
		return len(obj[ key ])
	return wrapped


def create_text_nodes ( nodes, indent=1 ):
	"""\
Return a set of text nodes in Graphviz DOT format, optimally padded for easier
reading and debugging.

nodes: iterable of (id, attribute) node tuples
       e.g. [(node1, attr1), (node2, attr2), ...]

indent: integer, number of tabs with which to indent all Dot node lines
"""
	if not nodes: return '// no nodes in this section'

	# guarantee basic structure of nodes arg
	assert( len(nodes) == sum( 1 for a, b in nodes ) )

	# Step 1: for alignment, get max item length in node list
	maxl = max(map(_getLen(0), nodes)) + 2 # account for two extra quotes

	# Step 2: prepare a text format based on max node size that pads all
	#         lines with attributes
	nfmt_attr = '{0:<%d} [ {1} ] ;' % maxl      # node text format
	nfmt_noa  = '{0} ;'

	# Step 3: create each node, and place string representation in a set to
	#         guarantee uniqueness
	q = '"%s"' # enforce quoting for all nodes
	gviz = set( nfmt_attr.format( q % n, a ) for n, a in nodes if a )
	gviz.update( nfmt_noa.format( q % n ) for n, a in nodes if not a )

	# Step 4: return a sorted version of nodes, as a single string
	indent = '\n' + '\t' *indent
	return indent.join(sorted( gviz ))


def create_text_edges ( edges, indent=1 ):
	"""\
Return a set of text edge definitions in Graphviz DOT format, optimally padded
for easier reading and debugging.

edges: iterable of (from, to, attribute) edge tuples
       e.g. [(inp1, tech1, attr1), (inp2, tech2, attr2), ...]

indent: integer, number of tabs with which to indent all Dot edge lines
"""
	if not edges: return '// no edges in this section'

	# guarantee basic structure of edges arg
	assert( len(edges) == sum( 1 for a, b, c in edges ) )

	# Step 1: for alignment, get max length of items on left and right side of
	# graph operator token ('->')
	maxl, maxr = max(map(_getLen(0), edges)), max(map(_getLen(1), edges))
	maxl += 2  # account for additional two quotes
	maxr += 2  # account for additional two quotes

	# Step 2: prepare format to be "\n\tinp+PADDING -> out+PADDING [..."
	efmt_attr = '{0:<%d} -> {1:<%d} [ {2} ] ;' % (maxl, maxr) # with attributes
	efmt_noa  = '{0:<%d} -> {1} ;' % maxl                     # no attributes

	# Step 3: add each edge to a set (to guarantee unique entries only)
	q = '"%s"' # enforce quoting for all tokens
	gviz = set( efmt_attr.format( q % i, q % t, a ) for i, t, a in edges if a )
	gviz.update( efmt_noa.format( q % i, q % t ) for i, t, a in edges if not a )

	# Step 4: return a sorted version of the edges, as a single string
	indent = '\n' + '\t' *indent
	return indent.join(sorted( gviz ))