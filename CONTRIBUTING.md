# Contributing to WithSecure Elements MCP

Thank you for your interest in contributing to WithSecure Elements MCP! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- uv (recommended) or pip

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/elements-mcp.git
   cd elements-mcp
   ```

2. **Set up development environment**
   ```bash
   # Using uv (recommended)
   uv sync --all-extras
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your WithSecure Elements credentials
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## Development Process

### Branch Naming

Use descriptive branch names:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add OAuth2 token refresh mechanism
fix(incidents): handle empty response from API
docs: update installation instructions
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest
   ```

2. **Run linting**
   ```bash
   ruff check withsecure_elements_mcp tests examples
   mypy withsecure_elements_mcp
   ```

3. **Format code**
   ```bash
   black withsecure_elements_mcp tests examples
   isort withsecure_elements_mcp tests examples
   ```

4. **Update documentation** if needed

5. **Add tests** for new functionality

### Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes were made and why
3. **Link issues**: Reference any related issues
4. **Screenshots**: Include screenshots for UI changes
5. **Testing**: Describe how you tested the changes

### Review Process

- All PRs require at least one review
- Address feedback promptly
- Keep PRs focused and reasonably sized
- Respond to review comments

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs

### Feature Requests

Use the feature request template and include:
- Clear description of the feature
- Use case and motivation
- Proposed solution
- Alternative solutions considered

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for all public methods
- Use meaningful variable and function names
- Keep functions focused and reasonably sized

### Code Organization

- Place related functionality in modules
- Use appropriate design patterns
- Keep imports organized
- Avoid circular dependencies

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Handle edge cases gracefully

## Testing

### Test Requirements

- All new code must have tests
- Aim for high test coverage
- Write both unit and integration tests
- Test error conditions and edge cases

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=withsecure_elements_mcp

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure

- Unit tests in `tests/` directory
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

## Documentation

### Code Documentation

- Write clear docstrings
- Include type hints
- Document complex algorithms
- Provide usage examples

### User Documentation

- Update README for user-facing changes
- Add examples for new features
- Keep documentation current
- Use clear, concise language

## Release Process

### Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared

## Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Contact maintainers for urgent issues
- Review documentation and examples

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to WithSecure Elements MCP!
