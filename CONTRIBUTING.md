# Contributing to Temoa

Thank you for your interest in contributing to Temoa! Building a sustainable energy future with an open source energy system model takes a lot of effort, and we welcome all contributions.

## Resources

- **Documentation**: [https://docs.temoaproject.org/en/latest/](https://docs.temoaproject.org/en/latest/)
- **Project Website**: [https://temoaproject.org](https://temoaproject.org)
- **Issue Tracker**: [https://github.com/TemoaProject/temoa/issues](https://github.com/TemoaProject/temoa/issues)
- **Academic Paper**: Hunter et al. (2013) - [Modeling for insight using Tools for Energy Model Optimization and Analysis (Temoa)](https://doi.org/10.1016/j.eneco.2013.07.014)

## Getting Help

If you have questions or need help:
- **Bug Reports & Feature Requests**: Use our [GitHub Issues](https://github.com/TemoaProject/temoa/issues). Please use the provided templates for Bug Reports or Feature Requests.
- **General Questions**: Open an issue using the **Question** template. We have phased out the legacy Google Group forum in favor of GitHub-based discussions.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended)
- Git

### Setting Up Your Development Environment


1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR-USERNAME/temoa.git
   cd temoa
   ```

2. **Install dependencies using uv (recommended):**

   ```bash
   # Install all dependencies including development tools
   uv sync --all-extras --dev
   ```

3. **Install pre-commit hooks:**

   ```bash
   uv run pre-commit install
   ```

   This will automatically run code quality checks (Ruff, Mypy) before each commit.

## Infrastructure & Testing

We maintain a robust testing infrastructure to ensure model correctness and code reliability.

### Solvers
All core tests are designed to run using the **HiGHS** solver (provided by the `highspy` core dependency).

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=temoa --cov-report=html

# Run specific test file
uv run pytest tests/test_specific.py
```

### Testing Infrastructure
If you are writing a new feature, you **must** include tests that verify its functionality.
- Refer to `tests/conftest.py` for the available testing infrastructure.
- Use the `system_test_run` fixture for full model execution tests.
- Test databases are automatically refreshed from SQL scripts in `tests/testing_data/` during the test setup phase.

## Code Quality Tools

We use several tools to maintain high code standards:

### Type Checking with mypy
All new code must include type hints. We enforce strict typing for core modules.
```bash
uv run mypy temoa
```

### Linting and Formatting with Ruff
We use Ruff for both linting and formatting.
```bash
# Check and auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Making Changes

### Pull Request Process

1. **Open an Issue first**: For significant changes or new features, please open an issue to discuss the approach before starting work.
2. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Implement and Test**: Ensure your changes follow the [Code Style Guidelines](#code-style-guidelines) and include relevant tests.
4. **Verify Locally**: Run `pytest`, `mypy`, and `ruff` locally before pushing.
5. **Open a Pull Request**: Submit your PR against the `unstable` branch. Ensure the PR description clearly explains the changes and links to the relevant issue.

### Commit Message Guidelines

We advise following the [Conventional Commits](https://www.conventionalcommits.org/) style.

**Format:** `<type>: <subject>` (e.g., `feat: Add new carbon constraint`)

**Rules:**
1. Use the imperative mood ("Add feature" not "Added feature").
2. Limit the subject line to 50 characters.
3. Use the body to explain *what* and *why* vs. *how*.

## Code Style Guidelines

- **Type Hints**: Required for all public function signatures.
- **Docstrings**: Use Google-style docstrings.
- **Line Length**: Maximum 100 characters (enforced by Ruff).

---

Thank you for contributing to Temoa!
