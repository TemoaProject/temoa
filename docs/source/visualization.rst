Network Diagrams
----------------

.. warning::
   The graphviz visualization tools have not been fully tested with Temoa v4.0.
   They may require updates. Please report any issues on
   `GitHub Issues <https://github.com/TemoaProject/temoa/issues>`_.

Since Temoa model consists of an energy network in which technologies are connected
by the flow of energy commodities, a directed network graph represents an excellent way
to visualize a given energy system representation in a Temoa-compatible input database.
Temoa utilizes an open source graphics package called `Graphviz`_ to create a series of
data-specific and interactive energy-system maps. Currently, the output graphs consist of
a full energy system map as well as capacity and activity results per model time period.
In addition, users can create subgraphs focused on a particular commodity or technology.


To use graphviz from the command line, navigate to the :code:`data_processing` folder,
where the graphviz script resides. To review all of the graphviz options, use the
:code:`--help` flag:

.. parsed-literal::
  $ python make_graphviz.py --help

The most basic way to use graphviz is to view the full energy system map:

.. parsed-literal::
  $ python make_graphviz.py -i ../data_files/temoa_utopia.sqlite

In the command above, note that we have to point the Graphviz module to the
:code:`temoa_utopia` database file, which resides in the :code:`data_files`
directory. The resultant system map will look like this:

.. figure:: images/simple_model.*
   :align: center
   :figclass: center
   :figwidth: 60%

   This is a map of the simple 'Utopia' system, which we often use for testing
   purposes. The map shows the possible commodity flows through the system,
   providing a comprehensive overview of the system. Creating the simple system
   map is useful for debugging purposes in order to make sure that technologies
   are linked together properly via commodity flows.

It is also possible to create a system map showing the optimal installed capacity
and technology flows in a particular model time period. These results are associated
with a specific model run stored in the model database. To view the results, include
the scenario flag (:code:`-s`) and a specific model year (:code:`-y`).

Note that when Graphiz runs, it creates a folder within the :code:`data_processing`
folder. The folder itself is assigned the name of the database file, with
:code:`input_graphviz` appended to the end. This descriptor changes if using Graphviz
to visualize output graphics. Within this Graphviz-generated folder are two files. The
graphics file (default: svg) is a viewable image of the network. The dot file is the
input file to Graphviz that is created programmatically. Note that the dot files provide
another means to debug the model and create an archive of visualizations for auditing
purposes. In addition, we have taken care to make these intermediate files well-formatted.

.. parsed-literal::
  $ python make_graphviz.py -i ../data_files/temoa_utopia.sqlite -s test_run -y 1990

.. figure:: images/global_results.*
   :align: center
   :figclass: center
   :figwidth: 60%

   This graph shows the optimal installed capacity and commodity flows from the
   'utopia' test system in 2010.

The output can also be fine-tuned to show results associated with a specific
commodity or technology. For example:

.. parsed-literal::
  $ python make_graphviz.py -i ../data_files/temoa_utopia.sqlite -s test_run -y 2010 -b E31

.. figure:: images/techvintage_results.*
   :align: center
   :figclass: center
   :figwidth: 60%

   In this case, the graph shows the commodity flow in and out of
   technology 'E31' in 2010, which is from the 'test_run' scenario drawn from the
   'temoa_utopia' database.

Output Graphs
-------------

Temoa can also be used to generate output graphs using `matplotlib <https://matplotlib.org/>`_.
From the command line, navigate to the :code:`data_processing` folder and execute the following command:

.. parsed-literal::
  $ python make_output_plots.py --help

The command above will specify all of the flags required to created a stacked bar
or line plot. For example, consider the following command:

.. parsed-literal::
  $ python make_output_plots.py -i ../data_files/temoa_utopia.sqlite -s test_run -p capacity -c electric --super

Here is the result:

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

.. _Graphviz: http://www.graphviz.org/
