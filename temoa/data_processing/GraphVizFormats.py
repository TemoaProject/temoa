# SVG Formats

results_dot_fmt = """\
strict digraph model {
	label = "Results for %(period)s"

	rankdir = "LR" ;
	smoothtype = "power_dist" ;
	splines = "%(splinevar)s" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph unused_techs {
		node [
		  color     = "%(unused_color)s",
		  fontcolor = "%(unusedfont_color)s",
		  shape     = "box",
		  fontcolor = "%(font_color)s"
		] ;

		%(dtechs)s
	}

	subgraph unused_energy_carriers {
		node [
		  color     = "%(unused_color)s",
		  fontcolor = "%(unusedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		] ;

		%(dcarriers)s
	}

	subgraph unused_emissions {
		node [
		  color     = "%(unused_color)s",
		  fontcolor = "%(unusedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		]

		%(demissions)s
	}

	subgraph in_use_techs {
		node [
		  color     = "%(tech_color)s",
		  fontcolor = "%(usedfont_color)s",
		  shape     = "box"
		  fontcolor = "%(font_color)s"

		] ;

		%(etechs)s
	}

	subgraph in_use_energy_carriers {
		node [
		  color     = "%(commodity_color)s",
		  fontcolor = "%(usedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		] ;

		%(ecarriers)s
	}

	subgraph in_use_emissions {
		node [
		  color     = "%(commodity_color)s",
		  fontcolor = "%(usedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		] ;

		%(eemissions)s
	}

	subgraph unused_flows {
		edge [ color="%(unused_color)s" ]

		%(dflows)s
	}

	subgraph in_use_flows {
		subgraph inputs {
			edge [ color="%(arrowheadin_color)s" ] ;

			%(eflowsi)s
		}

		subgraph outputs {
			edge [ color="%(arrowheadout_color)s" ] ;

			%(eflowso)s
		}
	}

	{rank = same; %(xnodes)s}
}
"""


tech_results_dot_fmt = """\
strict digraph model {
	label = "Results for %(inp_technology)s in %(period)s" ;

	compound    = "True" ;
	concentrate = "True";
	rankdir     = "LR" ;
	splines     = "%(splinevar)s" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph cluster_vintages {
		label = "Vintages\\nCapacity: %(total_cap).2f" ;

		href  = "%(cluster_vintage_url)s" ;
		style = "filled"
		color = "%(sb_vpbackg_color)s"

		node [ color="%(sb_vp_color)s", shape="box", fontcolor="%(usedfont_color)s" ] ;

		%(vnodes)s
	}

	subgraph energy_carriers {
		node [
		  color     = "%(commodity_color)s",
		  fontcolor = "%(usedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		] ;

		%(enodes)s
	}

	subgraph inputs {
		edge [ color="%(arrowheadin_color)s" ] ;

		%(iedges)s
	}

	subgraph outputs {
		edge [ color="%(arrowheadout_color)s" ] ;

		%(oedges)s
	}
}
"""

slice_dot_fmt = """\
strict digraph model {
	label = "Activity split of process %(inp_technology)s, %(vintage)s in year %(period)s" ;

	compound    = "True" ;
	concentrate = "True";
	rankdir     = "LR" ;
	splines     = "%(splinevar)s" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph cluster_slices {
		label = "%(vintage)s Capacity: %(total_cap).2f" ;

		color = "%(vintage_cluster_color)s" ;
		rank  = "same" ;
		style = "filled" ;

		node [ color="%(vintage_color)s", shape="box", fontcolor="%(usedfont_color)s" ] ;

		%(snodes)s
	}

	subgraph energy_carriers {
		node [
		  color     = "%(commodity_color)s",
		  fontcolor = "%(usedfont_color)s",
		  shape     = "circle",
		  fillcolor = "%(fill_color)s"
		] ;

		%(enodes)s
	}

	subgraph inputs {
		edge [ color="%(input_color)s" ] ;

		%(iedges)s
	}

	subgraph outputs {
		edge [ color="%(output_color)s" ] ;

		%(oedges)s
	}
}
"""

commodity_dot_fmt = """\
strict digraph result_commodity_%(inp_commodity)s {
	label       = "%(inp_commodity)s - %(period)s" ;

	compound    = "True" ;
	concentrate = "True" ;
	rankdir     = "LR" ;
	splines     = "True" ;

	node [ shape="box", style="filled", fontcolor="%(font_color)s" ] ;
	edge [
	  arrowhead  = "vee",
	  fontsize   = "8",
	  label      = "   ",
	  labelfloat = "False",
	  labelfontcolor = "lightgreen"
	  len        = "2",
	  weight     = "0.5",
	] ;

	%(resource_node)s

	subgraph used_techs {
		node [ color="%(tech_color)s" ] ;

		%(used_nodes)s
	}

	subgraph used_techs {
		node [ color="%(unused_color)s" ] ;

		%(unused_nodes)s
	}

	subgraph in_use_flows {
		edge [ color="%(sb_arrow_color)s" ] ;

		%(used_edges)s
	}

	subgraph unused_flows {
		edge [ color="%(unused_color)s" ] ;

		%(unused_edges)s
	}
}
"""

quick_run_dot_fmt = """\
strict digraph model {
	rankdir = "LR" ;

	// Default node and edge attributes
	node [ style="filled" ] ;
	edge [ arrowhead="vee", labelfontcolor="lightgreen" ] ;

	// Define individual nodes
	subgraph techs {
		node [ color="%(tech_color)s", shape="box", fontcolor="%(font_color)s" ] ;

		%(tnodes)s
	}

	subgraph energy_carriers {
		node [ color="%(commodity_color)s", shape="circle", fillcolor="%(fill_color)s" ] ;

		%(enodes)s
	}

	// Define edges and any specific edge attributes
	subgraph inputs {
		edge [ color="%(arrowheadin_color)s" ] ;

		%(iedges)s
	}

	subgraph outputs {
		edge [ color="%(arrowheadout_color)s" ] ;

		%(oedges)s
	}

	{rank = same; %(snodes)s}
}
"""
