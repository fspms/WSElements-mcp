# Development Guide - WithSecure Elements MCP

This guide explains how to contribute to the development of the WithSecure Elements MCP server.

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- uv (recommended) or pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fspms/WSElements-mcp.git
   cd WSElements-mcp
   ```

2. **Create virtual environment**
   ```bash
   # With uv (recommended)
   uv sync --all-extras
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Or with pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Environment variables configuration**
   ```bash
   cp env.example .env
   # Edit .env with your WithSecure Elements information
   ```

## Project Structure

```
withsecure_elements_mcp/
├── __init__.py              # Main package
├── config.py                # Configuration
├── auth.py                  # OAuth2 authentication
├── server.py                # Main MCP server
└── modules/                 # MCP modules
    ├── __init__.py
    ├── base.py              # Base class for modules
    ├── incidents.py         # Incidents module (BCDs)
    ├── events.py            # Security events module
    ├── organizations.py     # Organizations module
    └── devices.py           # Devices module

tests/                       # Unit tests
examples/                    # Usage examples
docs/                        # Documentation
```

## Developing New Modules

### 1. Create a New Module

Create a new file in `withsecure_elements_mcp/modules/`:

```python
from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig

class MyNewModule(BaseModule):
    @property
    def name(self) -> str:
        return "my_module"
    
    @property
    def description(self) -> str:
        return "Description of my module"
    
    def _register_resources(self) -> None:
        # Register resources
        pass
    
    def _register_tools(self) -> None:
        # Register tools
        pass
```

### 2. Register the Module

Add the module in `withsecure_elements_mcp/modules/__init__.py`:

```python
from .my_new_module import MyNewModule

__all__ = [
    # ... other modules
    "MyNewModule"
]
```

### 3. Add Module to Configuration

Modify `withsecure_elements_mcp/server.py` to include the new module:

```python
available_modules = {
    # ... other modules
    "my_module": MyNewModule
}
```

## Tests

### Running Tests

```bash
# All tests
pytest

# Tests with coverage
pytest --cov=withsecure_elements_mcp

# Specific tests
pytest tests/test_auth.py

# Tests with detailed output
pytest -v -s
```

### Writing Tests

Tests should be placed in the `tests/` directory and follow the `test_*.py` convention.

Test example:

```python
import pytest
from withsecure_elements_mcp.config import WithSecureConfig

def test_config_validation():
    config = WithSecureConfig(
        client_id="test",
        client_secret="secret"
    )
    assert config.client_id == "test"
```

## Formatting and Linting

### Automatic Formatting

```bash
# Formatting with black
black withsecure_elements_mcp tests examples

# Import sorting with isort
isort withsecure_elements_mcp tests examples
```

### Linting

```bash
# Linting with ruff
ruff check withsecure_elements_mcp tests examples

# Type checking with mypy
mypy withsecure_elements_mcp
```

## Documentation

### Module Documentation

Each module should include:
- Class docstring describing the module
- Docstring for each public method
- Type hints for all parameters and return values

### Usage Examples

Add examples in the `examples/` directory for each new feature.

## Deployment

### Docker Build

```bash
# Build image
docker build -t withsecure-elements-mcp .

# Test image
docker run --env-file .env withsecure-elements-mcp --help
```

### Deployment with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Contributing

### Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-feature`)
3. **Commit** your changes (`git commit -m 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/new-feature`)
5. **Create** a Pull Request

### Code Standards

- Follow PEP 8
- Use type hints
- Write tests for new code
- Document new features
- Use descriptive commit messages

### Commits

Use conventional commit messages:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `style:` formatting
- `refactor:` refactoring
- `test:` add tests
- `chore:` maintenance tasks

Examples:
- `feat: add user management module`
- `fix: fix OAuth2 authentication`
- `docs: update README`

## Support

For any questions or issues:

1. Check existing documentation
2. Consult existing issues
3. Create a new issue if necessary
4. Contact the development team
