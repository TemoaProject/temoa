=============
Visualization
=============

Network Diagrams
----------------

Since the Temoa model consists of an energy network in which technologies are connected
by the flow of energy commodities, a directed network graph represents an excellent way
to visualize a given energy system representation in a Temoa-compatible input database.

Temoa provides two types of network visualizations:

1. **Interactive HTML Network Graphs** - Dynamic, explorable visualizations showing commodity flows and technology connections
2. **Graphviz Diagrams** - Static SVG/DOT format diagrams showing the energy system structure

Generating Network Visualizations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to generate these diagrams is to enable visualization options in your
configuration TOML file. Add the following to your config file:

.. parsed-literal::
  # Enable interactive HTML network graphs (requires source_trace = true)
  source_trace = true
  plot_commodity_network = true

  # Enable Graphviz static diagrams
  graphviz_output = true

When these options are enabled, Temoa will automatically generate visualization files
in the output directory during model execution.

**Interactive Network Graphs** will be created as HTML files (one per time period) that
you can open in a web browser. These provide an interactive view where you can:

- Pan and zoom the network
- Click on nodes to see details
- Toggle between commodity-centric and technology-centric views
- Filter by sector using color-coded legends

**Graphviz Diagrams** will be created as both ``.dot`` (source) and ``.svg`` (rendered)
files in a subdirectory within your output folder. These provide static visualizations
showing:

- Full energy system maps
- Capacity and activity results per model time period
- Technology interconnections via commodity flows

Example Visualizations
~~~~~~~~~~~~~~~~~~~~~~

**Interactive Network Graph**

The interactive HTML network graphs provide dynamic exploration with pan, zoom, and filtering capabilities:

.. raw:: html

   <iframe src="_static/Network_Graph_utopia_1990.html" width="100%" height="600px" style="border:1px solid #ccc;"></iframe>

*Interactive network graph for the 'utopia' test system in 1990. You can pan, zoom, click nodes for details, and toggle between commodity-centric and technology-centric views. These files are automatically generated when* ``source_trace = true`` *and* ``plot_commodity_network = true`` *are set in the configuration file.*

**Static Graphviz Diagram**

Graphviz also generates static SVG diagrams showing the energy system structure:

.. figure:: images/results1990.*
   :align: center
   :figclass: center
   :width: 100%

   Static Graphviz diagram showing the optimal installed capacity and commodity flows
   for the 'utopia' test system in 1990. Technologies are shown as boxes,
   commodities as circles, with arrows indicating energy flows. These diagrams
   are automatically generated when ``graphviz_output = true`` is set in the
   configuration file.
