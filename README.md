# Tusk

A modern terminal-based Markdown editor with real-time preview.

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

![tusk-logo](assets/tusk-logo.png)

## Table of Contents

- [Tusk](#tusk)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Via pip](#via-pip)
    - [From source](#from-source)
  - [Usage](#usage)
    - [Key Bindings](#key-bindings)
    - [Auto-Completion](#auto-completion)
    - [Snippets](#snippets)
    - [Export Options](#export-options)
    - [Configuration](#configuration)
    - [Dependencies](#dependencies)
    - [Common Issues](#common-issues)
    - [Roadmap](#roadmap)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

### Via pip

```bash
pip install tusk-editor
```

### From source

```bash
git clone https://github.com/vedant-asati03/tusk.git
cd tusk
pip install -e .
```

## Usage

To start the editor:

```bash
tusk filename.md
```

### Key Bindings

- `Ctrl+S`: Save file
- `Ctrl+P`: Open command palette
- `Ctrl+@`: Toggle preview pane
- `Ctrl+L`: Expand input-box
- `Ctrl+Q`: Shrink input-box
- `Ctrl+B`: Insert Table of Contents
- `Tab`: Expand snippet

### Auto-Completion

Automatic completion for:

- Brackets: (), [], {}, <>
- Quotes: "", '', ``
- Markdown: **, __, ~~, ```
- Headers: # automatically adds space

### Snippets

Built-in snippets:

- Headers: `h1`, `h2`, `h3`
- Formatting: `bold`, `italic`, `strike`, `code`
- Lists: `ul`, `ol`
- Links: `link`, `img`
- Others: `quote`, `hr`, `todo`, `done`

Custom snippets can be added via `~/.config/tusk/snippets.json`

### Export Options

Export your markdown to:

- HTML (`Ctrl+P` → "export html")
- PDF (`Ctrl+P` → "export pdf")
- DOCX (`Ctrl+P` → "export docx")

### Configuration

- Snippets: `~/.config/tusk/snippets.json`
- Logs: `~/.tusk/logs/tusk.log`
- Auto-save: Enabled by default

### Dependencies

- Python 3.10+
- textual>=0.38.1
- markdown>=3.4.3
- pypandoc>=1.11 (for exports)
- pandoc (system package)

### Common Issues

- **Export fails**: Ensure pandoc is installed on your system
- **Syntax highlighting issues**: Make sure you're using a compatible terminal
- **Unicode errors**: Set your terminal to UTF-8 encoding

### Roadmap

- [x] Vim keybindings (In testing phase)
- [ ] Custom themes support
- [ ] File browser
- [ ] Git integration
- [ ] Plugin system

## Contributing

Feel free to contribute by forking the repo and submitting a pull request! 🚀

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
