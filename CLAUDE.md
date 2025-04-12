# BatchImageProcessor Development Guide

## Build/Test Commands
- Install: `pip install .`
- Run unit tests: `python -m unittest discover`
- Run single test: `python -m unittest python/test/path/to/test_file.py`
- Run tests with coverage: `coverage run -m unittest discover && coverage report -i -m --fail-under=95`
- Generate HTML coverage: `coverage html`
- Format code: `black .`
- Lint code: `pylint python`
- Run all checks: `./run_checks.sh`

## Code Style Guidelines
- Follow PEP 8 and Black formatting standards with 100 char line length
- Naming: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- Use type hints for function parameters and return values
- Organize imports: standard library, third-party libraries, project imports (alphabetically in groups)
- Error handling: Use try/except blocks with specific exceptions
- Exception handling: Use specific exception types and handle with appropriate recovery actions
- Classes should follow single responsibility principle and proper encapsulation
- Use factory pattern for creating processors
- 95%+ test coverage required for all code