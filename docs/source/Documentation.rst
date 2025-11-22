
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

.. include:: visualization.rst

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
