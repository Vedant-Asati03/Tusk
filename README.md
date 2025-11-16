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
    - [Configuration](#configuration)
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

#### Basic Operations

- `Ctrl+S`: Save file
- `Ctrl+Shift+S`: Save As / rename drafts
- `Ctrl+P`: Open command palette
- `Ctrl+@`: Toggle preview pane
- `Ctrl+L`: Expand input-box
- `Ctrl+Q`: Shrink input-box
- `Ctrl+B`: Insert Table of Contents
- `Tab`: Expand snippet

#### Line Operations

- `Ctrl+D`: Duplicate current line
- `Alt+↑`: Move line up
- `Alt+↓`: Move line down

#### Editor Features

- `Ctrl+Alt+I`: Toggle auto-indent

### Auto-Completion

Automatic completion for:

- **Smart Brackets**: (), [], {}, <> with context awareness
- **Markdown Formatting**: **, __, ~~, ``` with improved pairing
- **Headers**: # automatically adds space
- **Auto-indent**: Maintains indentation for lists, code blocks, and quotes

### Snippets

Built-in snippets:

- Headers: `h1`, `h2`, `h3`
- Formatting: `bold`, `italic`, `strike`, `code`
- Lists: `ul`, `ol`
- Links: `link`, `img`
- Others: `quote`, `hr`, `todo`, `done`

Custom snippets can be added via `~/.config/tusk/snippets.json`

### Configuration

- Snippets: `~/.config/tusk/snippets.json`
- Logs: `~/.tusk/logs/tusk.log`
- Auto-save: Enabled by default

## Contributing

Feel free to contribute by forking the repo and submitting a pull request! 🚀

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
