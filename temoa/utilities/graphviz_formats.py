# SVG Formats

results_dot_fmt = """\
strict digraph model {{
	label = "Results for {period}"

	rankdir = "LR" ;
	smoothtype = "power_dist" ;
	splines = "{splinevar}" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph unused_techs {{
		node [
            color     = "{unused_color}",
            fontcolor = "{unusedfont_color}",
            shape     = "box",
            fontcolor = "{font_color}"
		] ;

		{dtechs}
	}}

	subgraph unused_energy_carriers {{
		node [
            color     = "{unused_color}",
            fontcolor = "{unusedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		] ;

		{dcarriers}
	}}

	subgraph unused_emissions {{
		node [
            color     = "{unused_color}",
            fontcolor = "{unusedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		]

		{demissions}
	}}

	subgraph in_use_techs {{
		node [
            color     = "{tech_color}",
			fontcolor = "{usedfont_color}",
			shape     = "box",
			fontcolor = "{font_color}"
		] ;

		{etechs}
	}}

	subgraph in_use_energy_carriers {{
		node [
            color     = "{commodity_color}",
            fontcolor = "{usedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		] ;

		{ecarriers}
	}}

	subgraph in_use_emissions {{
		node [
            color     = "{commodity_color}",
            fontcolor = "{usedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		] ;

		{eemissions}
	}}

	subgraph unused_flows {{
		edge [ color="{unused_color}" ]

		{dflows}
	}}

	subgraph in_use_flows {{
		subgraph inputs {{
			edge [ color="{arrowheadin_color}" ] ;

			{eflowsi}
		}}

		subgraph outputs {{
			edge [ color="{arrowheadout_color}" ] ;

			{eflowso}
		}}
	}}

	{{rank = same; {xnodes}}}
}}
"""


tech_results_dot_fmt = """\
strict digraph model {{
	label = "Results for {inp_technology} in {period}" ;

	compound    = "True" ;
	concentrate = "True";
	rankdir     = "LR" ;
	splines     = "{splinevar}" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph cluster_vintages {{
		label = "Vintages\\nCapacity: {total_cap:.2f}" ;

		href  = "{cluster_vintage_url}" ;
		style = "filled"
		color = "{sb_vpbackg_color}"

		node [ color="{sb_vp_color}", shape="box", fontcolor="{usedfont_color}" ] ;

		{vnodes}
	}}

	subgraph energy_carriers {{
		node [
            color     = "{commodity_color}",
            fontcolor = "{usedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		] ;

		{enodes}
	}}

	subgraph inputs {{
		edge [ color="{arrowheadin_color}" ] ;

		{iedges}
	}}

	subgraph outputs {{
		edge [ color="{arrowheadout_color}" ] ;

		{oedges}
	}}
}}
"""

slice_dot_fmt = """\
strict digraph model {{
	label = "Activity split of process {inp_technology}, {vintage} in year {period}" ;

	compound    = "True" ;
	concentrate = "True";
	rankdir     = "LR" ;
	splines     = "{splinevar}" ;

	node [ style="filled" ] ;
	edge [ arrowhead="vee" ] ;

	subgraph cluster_slices {{
		label = "{vintage} Capacity: {total_cap:.2f}" ;

		color = "{vintage_cluster_color}" ;
		rank  = "same" ;
		style = "filled" ;

		node [ color="{vintage_color}", shape="box", fontcolor="{usedfont_color}" ] ;

		{snodes}
	}}

	subgraph energy_carriers {{
		node [
            color     = "{commodity_color}",
            fontcolor = "{usedfont_color}",
            shape     = "circle",
            fillcolor = "{fill_color}"
		] ;

		{enodes}
	}}

	subgraph inputs {{
		edge [ color="{input_color}" ] ;

		{iedges}
	}}

	subgraph outputs {{
		edge [ color="{output_color}" ] ;

		{oedges}
	}}
}}
"""

commodity_dot_fmt = """\
strict digraph result_commodity_{inp_commodity} {{
	label       = "{inp_commodity} - {period}" ;

	compound    = "True" ;
	concentrate = "True" ;
	rankdir     = "LR" ;
	splines     = "True" ;

	node [ shape="box", style="filled", fontcolor="{font_color}" ] ;
	edge [
        arrowhead  = "vee",
        fontsize   = "8",
        label      = "   ",
        labelfloat = "False",
        labelfontcolor = "lightgreen"
        len        = "2",
        weight     = "0.5",
	] ;

	{resource_node}

	subgraph used_techs {{
		node [ color="{tech_color}" ] ;

		{used_nodes}
	}}

	subgraph used_techs {{
		node [ color="{unused_color}" ] ;

		{unused_nodes}
	}}

	subgraph in_use_flows {{
		edge [ color="{sb_arrow_color}" ] ;

		{used_edges}
	}}

	subgraph unused_flows {{
		edge [ color="{unused_color}" ] ;

		{unused_edges}
	}}
}}
"""

quick_run_dot_fmt = """\
strict digraph model {{
	rankdir = "LR" ;

	// Default node and edge attributes
	node [ style="filled" ] ;
	edge [ arrowhead="vee", labelfontcolor="lightgreen" ] ;

	// Define individual nodes
	subgraph techs {{
		node [ color="{tech_color}", shape="box", fontcolor="{font_color}" ] ;

		{tnodes}
	}}

	subgraph energy_carriers {{
		node [ color="{commodity_color}", shape="circle", fillcolor="{fill_color}" ] ;

		{enodes}
	}}

	// Define edges and any specific edge attributes
	subgraph inputs {{
		edge [ color="{arrowheadin_color}" ] ;

		{iedges}
	}}

	subgraph outputs {{
		edge [ color="{arrowheadout_color}" ] ;

		{oedges}
	}}

	{{rank = same; {snodes}}}
}}
"""
