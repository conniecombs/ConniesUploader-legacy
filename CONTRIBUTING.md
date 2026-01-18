# Contributing to Connie's Uploader

Thank you for considering contributing to Connie's Uploader! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:
- Check the existing issues to avoid duplicates
- Collect information about the bug (OS, Python version, error messages, etc.)

When submitting a bug report, include:
- A clear and descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable
- Your environment details (OS, Python version, dependencies)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:
- Use a clear and descriptive title
- Provide a detailed description of the proposed functionality
- Explain why this enhancement would be useful
- Include mockups or examples if applicable

### Contributing Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (see commit guidelines below)
6. Push to your branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ConniesUploader-legacy.git
   cd ConniesUploader-legacy
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

5. Create a config file:
   ```bash
   cp config.example.yaml config.yaml
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following specifics:

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Prefer double quotes for strings
- **Imports**: Organize in three groups (standard library, third-party, local)

### Code Formatting

We use `black` for code formatting:

```bash
black main.py modules/ tests/
```

### Linting

Run `flake8` before committing:

```bash
flake8 main.py modules/ tests/ --max-line-length=100
```

### Type Hints

Use type hints for function signatures where practical:

```python
def upload_file(filepath: str, service: str, api_key: str) -> tuple[str, str]:
    """Upload a file to the specified service."""
    pass
```

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    pass
```

## Testing Guidelines

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=modules --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_upload_manager.py -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested
- Aim for at least 70% code coverage for new code

Example test:
```python
import pytest
from modules.path_validator import PathValidator

class TestPathValidator:
    def test_validate_safe_path_accepts_valid_file(self):
        """Test that valid file paths are accepted."""
        result = PathValidator.validate_safe_path("/tmp/test.jpg")
        assert result is not None

    def test_validate_safe_path_rejects_traversal(self):
        """Test that path traversal attempts are blocked."""
        result = PathValidator.validate_safe_path("../../etc/passwd")
        assert result is None
```

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(upload): Add support for custom image hosting plugins

Implement plugin system that allows users to create custom uploaders
for image hosting services not natively supported.

Closes #123
```

```
fix(security): Prevent path traversal in file validation

Add comprehensive path validation to block directory traversal
attacks and symlink exploits.
```

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Run linting and formatting tools
5. Update CHANGELOG.md with your changes

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] CHANGELOG.md updated
```

### Review Process

1. At least one maintainer review is required
2. All CI checks must pass
3. Resolve all review comments
4. Squash commits if requested
5. Maintainer will merge when approved

### After Your PR is Merged

- Delete your feature branch
- Pull the latest changes from main
- Celebrate your contribution!

## Project Structure

```
ConniesUploader-legacy/
├── main.py              # Application entry point
├── modules/             # Core modules
│   ├── api.py          # Upload service implementations
│   ├── upload_manager.py
│   ├── config_loader.py
│   └── ...
├── tests/              # Test suite
├── plugins/            # Plugin system
├── docs/               # Additional documentation
└── config.example.yaml # Example configuration
```

## Getting Help

- Check existing documentation
- Search through existing issues
- Ask questions in GitHub Discussions
- Contact maintainers

## Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- README.md credits section

Thank you for contributing to Connie's Uploader!
