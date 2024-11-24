# Contributing to Tusk

Thank you for your interest in contributing to Tusk! Let's first walk through the guidelines and instructions for contributing in this project.

## Getting Started

### Code Structure

```text
.
├── .github
│     ├──ISSUE_TEMPLATE
│     │      ├── bug_report.md
│     │      └── custom.md
│     └── feature_request.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── tusk
│     ├── __init__.py
│     ├── app.py
│     ├── cli.py
│     └── utils
│           ├── __init__.py
│           ├── complete.py
│           ├── save.py
│           └── snippets.py
└── assets
   └── tusk-logo.png
```

### Prerequisites

- Python 3.12 or higher
- Textual
- Pandoc (for export features)

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/tusk.git
   cd tusk
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install core dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

6. Install system dependencies:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install pandoc

   # On MacOS
   brew install pandoc

   # On Windows
   choco install pandoc
   ```

7. Start development server:
   ```bash
   python -m tusk
   ```

Note: Alternatively, you can use Poetry:

**Again these are only guidelines not rules so just do everything to best of your knowledge.**

## Questions?

Feel free to open an issue for any questions about contributing.

## License

By contributing to Tusk, you agree that your contributions will be licensed under the project's license.
