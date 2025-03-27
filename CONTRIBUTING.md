# Contributing to Radio France Podcast Explorer MCP

Thank you for your interest in contributing to this project! Here are some guidelines to help you get started.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to maintain a welcoming and inclusive community.

## Getting Started

1. Fork the repository
2. Clone your fork to your local machine
3. Create a virtual environment and install dependencies
4. Create a new branch for your feature or bug fix
5. Make your changes
6. Run tests to ensure your changes don't break existing functionality
7. Commit your changes
8. Push to your fork
9. Open a pull request

## Development Environment

Set up your development environment:

```bash
# Clone your fork
git clone https://github.com/yourusername/radiofrance-podcast-explorer-mcp.git
cd radiofrance-podcast-explorer-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "RADIOFRANCE_API_KEY=your_api_key_here" > .env
```

## Testing

Always run tests before submitting a pull request:

```bash
python run_tests.py
```

If you add new functionality, please add appropriate tests in the `tests` directory.

## Pull Request Process

1. Update the README.md and documentation with details of changes if applicable
2. Update the version number in any relevant files if applicable
3. Your pull request will be reviewed by maintainers
4. Address any feedback from code reviews
5. Once approved, your pull request will be merged

## Coding Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Include docstrings for all functions and classes
- Write clear commit messages

## Adding New Tools

If you're adding a new tool:

1. Add the function to `server.py` using the `@mcp.tool()` decorator
2. Provide clear documentation in the function docstring
3. Add error handling to gracefully handle API errors
4. Update the usage documentation in `docs/usage.md`
5. Add tests for the new tool

## Web Scraping Guidelines

When implementing web scraping functionality:

1. Use CSS selectors that are as robust as possible
2. Add fallback selectors where appropriate
3. Include extensive error handling
4. Be mindful of Radio France's terms of service
5. Consider rate limiting to avoid excessive scraping

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions or need help, please open an issue for discussion before making significant changes.
