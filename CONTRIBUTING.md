# Contributing to Tusk

Thank you for your interest in contributing to Tusk! Let's first walk through the guidelines and instructions for contributing in this project.

## Getting Started

### Code Structure
```
|
├── .github
|     ├──ISSUE_TEMPLATE
|     |      ├── bug_report.md
|     |      └── custom.md
|     └── feature_request.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── tusk
|     ├── __init__.py
|     ├── app.py
|     ├── auto_save.py
|     └── cli.py   
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
   git clone https://github.com/vedant-asati03/tusk.git
   cd tusk
   ```
3. Install Poetry if you haven't:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
4. Install dependencies:
   ```bash
   poetry install
   ```
5. Activate virtual environment:
   ```bash
   poetry shell
   ```
6. Run the application:
   ```bash
   poetry run tusk
   ```

**Again these are only guidelines not rules so just do everything to best of your knowledge.**

## Questions?

Feel free to open an issue for any questions about contributing.

## License

By contributing to Tusk, you agree that your contributions will be licensed under the project's license.
