# Bill Hub

A web-based bill management and data analysis tool supporting multi-platform bill import, AI-powered data extraction, cross-year summary reports, batch processing, and visual analytics.

See [PRD.md](PRD.md) for detailed requirements.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Prepare your bill files
mkdir input
# Place your WeChat Pay ZIP/PDF files in the input directory

# Run the analyzer
python main.py
```

## Testing

This project includes a comprehensive test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_utils.py
```

See [tests/README.md](tests/README.md) for more details.
# Test
