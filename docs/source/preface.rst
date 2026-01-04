

This manual, in both `PDF`_ and `HTML`_ form, is the official documentation of
Tools for Energy Model Optimization and Analysis (Temoa).  It describes all
functionality of the Temoa model, and provides a mathematical description of
the implemented equations.

Besides this documentation, there are a couple other sources for Temoa-oriented
information.  For questions, bug reports, or feature requests, please use our
`GitHub Issues`_.  Publications are good introductory resources, but are not
guaranteed to be the most up-to-date as information and implementations evolve
quickly.  As with many software-oriented projects, even before this manual,
`the code is the most definitive resource`.  That said, please let us know
(via `GitHub Issues`_) of any discrepancies you find, and we will fix it as
soon as possible.

What is Temoa?
--------------
Temoa is an energy system optimization model (ESOM) developed over many years
to support transparent, data-driven analysis of energy systems. ESOMs
serve as an important planning tool because they allow users to examine energy
futures using a self-consistent framework for evaluation. Temoa is implemented
as a linear program that minimizes the total cost of energy supply by optimizing
the installation and operation of energy technologies over a user-defined
planning horizon. Energy supply must meet end-use demands subject to physical
and technical constraints governing system operation, along with user-defined
policy scenarios.

The energy system on which Temoa and other ESOMs operate can be visualized as
a directed graph. Primary energy sources represent the points of origin, which
are transformed by a network of energy conversion and delivery technologies, and
ultimately produce consumable energy commodities that satisfy end-use demands.
[#esom_definition]_. Temoa provides tools to explicitly represent this network,
visualize system structure, and trace energy flows through time.

A defining strength of Temoa is its flexible treatment of time. Users may
define arbitrary model periods of varying length and represent intra-period
operations using seasonal and time-of-day slices, full chronological hours, or
representative days. Capacity expansion can be solved under perfect foresight
or using a rolling-horizon. In addition, Temoa supports technology
vintaging, separate loan periods and physical lifetimes, and both global and
technology-specific discount rates. Beyond deterministic optimization, Temoa
supports stochastic optimization as well as modeling-to-generate alternatives
(MGA) to explore near-optimal solution spaces. All of Temoa's features were
driven by specific analytic needs over a decade of model development and
policy-focused application.

Temoa is implemented within an open-source software stack and is released under
the MIT license, with source code available on GitHub [#open_source_realities]_.
The model is written in Python and seamlessly integrates with the broader Python
ecosystem. Input data are stored in a relational SQLite database, enabling
transparency, reproducibility, and easy modification. The model maintains a
strict distinction between source code and the input data on which it operates.
The model can be executed on single machines, multi-core systems, or
high-performance computing environments.

The name Temoa (Tools for Energy Model Optimization and Analysis) reflects the
project's broader scope. The platform comprises four interrelated components:
the underlying mathematical formulation, its software implementation, a suite
of supporting tools for data management, analysis, and visualization, and an
online presence that supports documentation, dissemination, and community
engagement. Together, these elements are designed to foster collaboration,
extensibility, and trust in energy system modeling results.



Why Temoa?
----------
In 2009, when the idea for Temoa was born, most options for energy systems
modeling were geared towards government institutions that could afford the
expensive commercial software licenses. Closed source code and data also
meant that it was impossible for third parties to verify published model
results, even though those results were being used to inform public policy
decisions involving significant transfers of wealth and direct consequences for
people's lives. In addition, models were typically used to run a limited number
of scenarios that did not address the true underlying uncertainty about the
future.

Today's vibrant open source energy modeling community did not exist at
that time. We were motivated to build Temoa around three high-level objectives:
(1) make the model code and data open source to enable third party replication
of results, (2) use an open source software stack to minimize the barriers to
entry in energy modeling, and (3) build a toolkit to evaluate future uncertainty
in different ways, depending on the question at hand.

Temoa remains one of the most fully-featured, open source energy system models
focused on projecting changes across the whole energy system.



Temoa Origin and Pronunciation
------------------------------

While we use 'Temoa' as an acronym, it is an actual word in the Nahuatl (Aztec)
language, meaning "to seek something."

.. figure:: images/temoa_definition.*
   :align: center
   :figclass: center
   :figwidth: 50%

One pronounces the word 'Temoa' as "teh", "moe", "uh". Though TEMOA is an acronym
for 'Tools for Energy Model Optimization and Analysis', we generally use 'Temoa'
as a proper noun, and so forgo the need for all-caps.


Bug Reporting
-------------

Temoa strives for correctness.  Unfortunately, as an energy system model and software
project there are plenty of levels and avenues for error.  If you spot a bug,
inconsistency, or general "that could be improved", we want to hear about it.

If you are a software developer-type, feel free to open an issue on our `GitHub
Issue tracker`_\ .  If you would rather not create a GitHub account, feel free
to let us know the issue on our `mailing list`_\ .

.. _PDF: https://temoacloud.com/wp-content/uploads/2020/02/toolsforenergymodeloptimizationandanalysistemoa.pdf
.. _HTML: http://temoaproject.org/docs/
.. _GitHub Issues: https://github.com/TemoaProject/temoa/issues
.. _GitHub Issue tracker: https://github.com/TemoaProject/temoa/issues
.. _mailing list: https://groups.google.com/forum/#!forum/temoa-project

