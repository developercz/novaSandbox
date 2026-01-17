# Contributing to NovaSandbox

Thank you for your interest in contributing to NovaSandbox! This document provides guidelines for contributors.

## Getting Started

1. **Fork** the project on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/your-username/novasandbox.git
   cd novasandbox
   ```

3. **Install dev environment**:
   ```bash
   pip install -e .[dev]
   make install-dev
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

## Development

### Code Style

The project uses:
- **Black** for formatting (100 characters per line)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all tools:
```bash
make format lint
```

### Tests

Write tests for new functionality:

```bash
# Run tests
make test

# With coverage report
make coverage

# Benchmark tests
make test-bench
```

### Documentation

- Update README.md for new features
- Add docstrings to functions and classes
- Update CHANGELOG.md

## Pull Request Process

1. **Preparation**:
   ```bash
   # Ensure your code is formatted and linted
   make format lint test
   ```

2. **Push** your changes:
   ```bash
   git push origin feature/amazing-feature
   ```

3. **Create Pull Request** on GitHub with:
   - Clear description of changes
   - Link to related issues
   - Confirmation that tests passed

4. **Code review**: Wait for feedback from maintainers

## PR Rules

- ✅ Tests must pass
- ✅ Code must be formatted (Black/isort)
- ✅ No linting errors (flake8)
- ✅ Type hints for new functionality
- ✅ Documentation/docstrings
- ✅ CHANGELOG.md updated

## Reporting Bugs

Create an Issue with:
1. Problem description
2. Steps to reproduce
3. Expected vs. actual result
4. System information (OS, Python version, etc.)

## Feature Proposals

Open a Discussion or Issue with:
1. Use case and motivation
2. API proposal
3. Code examples

## Questions?

- Open a Discussion on GitHub
- Contact maintainers

Thank you for contributing! 🚀
