# Bill Hub

A web-based bill management and data analysis tool supporting multi-platform bill import, AI-powered data extraction, cross-year summary reports, batch processing, and visual analytics.

See [PRD.md](PRD.md) for detailed requirements.

## ✨ Features

- 📦 **Batch Processing**: Process multiple ZIP archives and PDF files at once
- 🔐 **Password Support**: Handle password-protected ZIP files and PDFs
- 📊 **Visual Analytics**: Generate comprehensive HTML reports with interactive charts
- 📈 **Data Visualization**: Monthly trends, category breakdowns, merchant rankings
- 🎨 **Export Options**: Export to Excel and PNG images
- 🔍 **Data Validation**: Built-in data quality checks and validation
- 📝 **Logging**: Comprehensive logging for debugging and monitoring

## 📋 Requirements

- Python 3.11 or higher
- Chrome/Chromium browser (for PNG export, optional)

## 🚀 Installation

### Using pip

```bash
pip install -e .
```

### Development installation (includes testing tools)

```bash
pip install -e ".[dev]"
```

## 📖 Usage

### Basic Usage

1. Create an `input/` directory
2. Place your WeChat Pay bill ZIP files or PDFs in the directory
3. Run the analyzer:

```bash
python main.py
```

4. Find the results in the `output/` directory:
   - Excel files (`.xlsx`)
   - HTML reports (`.html`)
   - Full-page PNG screenshots (optional)

## 🧪 Testing

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

## 📊 Output Examples

The tool generates:

- **Excel files**: Transaction data in `.xlsx` format with proper datetime formatting
- **HTML reports**: Interactive visualizations including:
  - Financial summary dashboard
  - Monthly income/expense trends
  - Category breakdown (pie charts)
  - Top merchant rankings (bar charts)
  - Transaction time analysis
  - Merchant frequency analysis
- **PNG screenshots**: Full-page screenshots of reports (requires Chrome)

## 🔧 Configuration

### Logging

The tool uses Python's `logging` module. Default configuration outputs to console. You can customize logging by modifying `logger_config.py`.

### Data Validation

The tool automatically validates transaction data and checks for:
- Empty datasets
- Missing required columns (交易时间, 金额(元))
- Null transaction dates
- Negative amounts

## 📝 Development

### Code Style

- Uses type hints throughout for better IDE support
- Comprehensive error handling
- Logging instead of print statements for better debugging

### Adding New Features

1. Add type hints to new functions
2. Include unit tests in `tests/` directory
3. Update this README with new features
4. Ensure logging is used for debugging information

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Add your license here]
