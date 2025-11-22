

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

Temoa is an energy system optimization model (ESOM).  Briefly, ESOMs optimize the
installation and utilization of energy technology capacity over a user-defined
time horizon. Optimal decisions are driven by an objective function that minimizes
the cost of energy supply. Conceptually, one may think of an ESOM as a "left-to-right"
network graph, with a set of energy sources on the lefthand side of the graph that
are transformed into consumable energy commodities by a set of energy technologies,
which are ultimately used to meet demands on the righthand side of the network graph.
[#esom_definition]_

Key features of the core Temoa model include:

  * Flexible time slicing by season and time-of-day
  * Variable length model time periods
  * Technology vintaging
  * Separate technology loan periods and lifetimes
  * Global and technology-specific discount rates
  * Capability to perform stochastic optimization
  * Capability to perform modeling-to-generate alternatives (MGA)


Temoa design features include:

  * Source code licensed under MIT, available through Github [#open_source_realities]_
  * Open source software stack
  * Part of a rich Python ecosystem
  * Data stored in a relational database system (sqlite)
  * Ability to utilize multi-core and compute cluster environments

The word 'Temoa' is actually an acronym for "Tools for Energy Model Optimization
and Analysis," currently composed of four (major) pieces of infrastructure:

   * The mathematical model
   * The implemented model (code)
   * Surrounding tools
   * An online presence

Each of these pieces is fundamental to creating a transparent and usable model
with a community oriented around collaboration.


Why Temoa?
----------

In short, because we believe that ESOM-based analyses should be repeatable by
independent third parties.  The only way to make this happen is to
have a freely available model, and to create an ecosystem of freely shared data
and model inputs.

For a longer explanation, please see :cite:`Hunter_etal_2013`.  In summary,
ESOM-based analyses are (1) impossible to validate, (2) complex enough as to be
non-repeatable without electronic access to **exact** versions of code *and* data
input, and (3) often do a poor job addressing uncertainty. We believe that
ESOM-based analyses should be completely open, independently reproducible,
electronically available, and address uncertainty about the future.


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

