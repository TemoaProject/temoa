# Temoa Documentation

This directory contains the source files for generating the Temoa documentation in [ReStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) format.

## Building the Documentation

### Prerequisites

The documentation build requires Sphinx and related packages. These are included in the `docs` extra dependency group.

### Setup

Install the documentation dependencies using uv (recommended):

```bash
cd /path/to/temoa
uv sync --extra docs
```

Or using pip:

```bash
pip install -e ".[docs]"
```

### Generating HTML Documentation

From the `docs` directory, execute:

```bash
uv run sphinx-build source _build/html
```

Or from the repository root:

```bash
uv run sphinx-build docs/source docs/_build/html
```

The generated HTML files will be in `docs/_build/html/`. Open `index.html` in your browser to view the documentation.

### Generating PDF Documentation

To generate PDF documentation, you'll need LaTeX installed. latexmk is recommended for automatic PDF generation:
- **macOS**: [MacTeX](https://www.tug.org/mactex/mactex-download.html)
- **Windows/Linux**: [MiKTeX](https://miktex.org/download) or TeX Live

Then run:

```bash
uv run make latexpdf
```

The PDF will be generated in `docs/_build/latex/`.

If automatic PDF generation fails, navigate to the build directory and manually generate the PDF:

```bash
cd docs/_build/latex
pdflatex toolsforenergymodeloptimizationandanalysistemoa.tex
```

## Documentation Structure

The Temoa documentation draws from two main sources:

1. **Static descriptions** - Model elements and concepts described in `source/Documentation.rst`
2. **Code docstrings** - Objective function and constraint documentation from module docstrings in:
   - `temoa/components/costs.py` - Objective function
   - `temoa/components/*.py` - Constraint implementations

Sphinx retrieves these docstrings and generates LaTeX-formatted equations in the "Equations" section of the documentation.

## Checking for Issues

### Link Checking

To check for broken links in the documentation:

```bash
uv run sphinx-build -b linkcheck source _build/linkcheck
```

Review the output in `docs/_build/linkcheck/output.txt`.

### Build Warnings

To treat warnings as errors (useful for CI):

```bash
uv run sphinx-build -W -b html source _build/html
```

## Contributing to Documentation

When contributing to the documentation:

1. Follow ReStructuredText formatting guidelines
2. Ensure all code examples are tested and working
3. Build the documentation locally to check for warnings
4. Run the link checker to verify external links
5. Update docstrings in code when changing model equations

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.
