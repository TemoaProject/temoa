This directory contains the source files necessary to generate the Temoa documentation in [ReST](https://en.wikipedia.org/wiki/ReStructuredText) format.

## Required Software

The required software elements to produce the documentation are included in the Temoa [environment file](https://github.com/TemoaProject/temoa/blob/energysystem/environment.yml).

The only additional software element required is LaTex. On a Mac, [MacTeX](https://www.tug.org/mactex/mactex-download.html) is a good option, and must be installed manually. [MiKTeX](https://miktex.org/download) is also available across platforms and is installed manually. On a Windows machine, MikTeX can also be installed through `conda` with the following command:

```$ conda install -c conda-forge miktex```

## Producing documentation
The Temoa documentation draws from a couple of sources: (1) the static descriptions of model elements included in [Documentation.rst](source//Documentation.rst), and (2) the doc strings
embedded in [temoa_rules.py](../temoa_model/temoa_rules.py) that document the objective function and constraints. Sphinx retrieves these doc strings and generates LaTeX-formatted equations in the "Equations" section of the documentation.


From this folder, execute the following to generate the html documentation:

```$ make html```

To generate the PDF documentation, from the same folder, execute the following:

```$ make latexpdf```

Sometimes this automatic PDF generation fails. If that is the case, navigate to `/tmp/TemoaDocumentationBuild/` and manually generate the pdf:

```$ pdflatex toolsforenergymodeloptimizationandanalysistemoa.pdf```





