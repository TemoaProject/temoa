
=======
Preface
=======

.. include:: preface.rst

===========
Quick Start
===========

.. include:: quick_start.rst

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

Output Graphs
-------------

.. warning::
   The ``make_output_plots.py`` script has not been fully tested with Temoa v4.0
   and is currently unsupported. Use at your own risk and please report any issues
   on `GitHub Issues`_.

Temoa can also be used to generate output graphs using `matplotlib <https://matplotlib.org/>`_.
From the command line, navigate to the :code:`data_processing` folder and execute the
following command:

.. parsed-literal::
  $ uv run python temoa/data_processing/make_output_plots.py --help

The command above will specify all of the flags required to create a stacked bar
or line plot. For example, consider the following command:

.. parsed-literal::
  $ uv run python temoa/data_processing/make_output_plots.py -i data_files/temoa_utopia.sqlite -s test_run -p capacity -c electric --super

.. figure:: images/output_flow_example.*
   :align: center
   :figclass: center
   :figwidth: 60%

   This stacked bar plot represents the activity (i.e., output commodity flow)
   associated with each technology in the electric sector from the 'test_run'
   scenario drawn from the 'temoa_utopia' database. Because the :code:`super`
   flag was specified, technologies are grouped together based on user-specified
   categories in the :code:`tech_category` column of the :code:`technologies`
   table of the database.

=====================
The Math Behind Temoa
=====================

.. include:: mathematical_formulation.rst

======================================
The Temoa Computational Implementation
======================================

.. include:: computational_implementation.rst

.. rubric:: Footnotes

.. [#open_source_realities] The two main goals behind Temoa are transparency and
   repeatability, hence the MIT license.  Unfortunately, there are some harsh
   realities in the current climate of energy modeling, so this license is not a
   guarantee of openness.  This documentation touches on the issues involved in
   the final section.

.. [#efficiency_table] The efficiency parameter is often referred to as the
   efficiency table, due to how it looks after even only a few entries in the
   Pyomo input "dot dat" file.

.. [#glpk_presolve] Circa 2013, GLPK uses more memory than commercial
   alternatives and has vastly weaker presolve capabilities.

.. [#esom_definition] For a more in-depth description of energy system
   optimization models (ESOMs) and guidance on how to use them, please see:
   DeCarolis et al. (2017) "Formalizing best practice for energy system
   optimization modelling", Applied Energy, 194: 184-198.

.. [#web_browser_svg] SVG support in web browsers is currently hit or miss.  The
   most recent versions of Chromium, Google Chrome, and Mozilla Firefox support
   SVG well enough for Temoa's current use of SVG.

.. [#return_expression] A word on `return` expressions in Pyomo: in most
   contexts a relational expression is evaluated instantly.  However, in Pyomo,
   a relational expression returns an `expression` object.  That is, `'M.aVar >=
   5'` does not evaluate to a boolean *true* or *false*, and Pyomo will
   manipulate it into the final LP formulation.

.. [#abstract_model] In contrast to a 'concrete' model, an abstract algebraic
   formulation describes the general equations of the model, but requires
   modeler-specified input data before it can compute any results.

.. |'''| replace:: ``'``\ ``'``\ ``'``

.. _GNU Linear Programming Kit: https://www.gnu.org/software/glpk/
.. _WinGLPK: http://winglpk.sf.net/
.. _Github repo: https://github.com/TemoaProject/temoa/
.. _Temoa model: http://temoaproject.org/download/temoa.py
.. _temoaproject.org: http://temoaproject.org/
.. _example data sets: http://temoaproject.org/download/example_data_sets.zip
.. _mailing list: https://groups.google.com/forum/\#\!forum/temoa-project
.. _Temoa Forum: https://groups.google.com/forum/\#\!forum/temoa-project
.. _various: http://xlinux.nist.gov/dads/HTML/optimization.html
.. _available: http://www.stanford.edu/\~boyd/cvxbook/
.. _online: https://en.wikipedia.org/wiki/Optimization_problem
.. _sources: https://en.wikipedia.org/wiki/Mathematical_optimization
.. _GAMS: http://www.gams.com/
.. _AMPL: http://www.ampl.com/
.. _PDF: https://temoacloud.com/wp-content/uploads/2020/02/toolsforenergymodeloptimizationandanalysistemoa.pdf
.. _HTML: http://temoaproject.org/docs/
.. _GitHub Issue tracker: https://github.com/TemoaProject/temoa/issues
.. _HTML version: http://temoaproject.org/docs/
.. _code smell: https://en.wikipedia.org/wiki/Code_smell
.. _PEP 8: http://www.python.org/dev/peps/pep-0008/
.. _PEP 3120: http://www.python.org/dev/peps/pep-3120/
.. _list comprehension: http://docs.python.org/tutorial/datastructures.html\#list-comprehensions
.. _lambda function: http://docs.python.org/tutorial/controlflow.html\#lambda-forms
.. _generally accepted relative rates: http://www.forecasts.org/inflation.htm
.. _Pull Request: https://help.github.com/articles/using-pull-requests
.. _quick start guide: http://rogerdudler.github.io/git-guide/
.. _sqlite: https://www.sqlite.org/
.. _Graphviz: http://www.graphviz.org/
.. _ruff: https://docs.astral.sh/ruff/

.. bibliography:: References.bib
.. _GitHub Issues: https://github.com/TemoaProject/temoa/issues
