# Tusk

A modern terminal-based Markdown editor with real-time preview.

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![Python](https://img.shields.io/badge/python-3.13+-blue)
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
    - [Vim Engine Controls](#vim-engine-controls)
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

Core Tusk bindings (everything else comes from Vim):

- `Ctrl+S`: Save file
- `Ctrl+Shift+S`: Save As / rename drafts
- `Ctrl+P`: Open command palette
- `Ctrl+!`: Toggle editor pane visibility
- `Ctrl+@`: Toggle preview pane
- `Ctrl+L`: Expand editor pane
- `Ctrl+Q`: Shrink editor pane

### Vim Engine Controls

Tusk now embeds the shared `vim_engine` Textual adapter. Once the app loads, editing works exactly like Vim:

- Press `i`, `a`, `o`, etc. to enter insert mode
- Press `Esc` to return to normal mode
- Use `:` commands (`:w`, `:q`, `:wq`, …) or any normal/visual operations supported by `vim_engine`
- Multi-key bindings (e.g. `dd`, `yy`, `/search`) behave just like the demo in `vim_engine/adapters/textual`

Refer to the [vim_engine project](https://github.com/Vedant-Asati03/vim-engine) for the full list of supported commands and keymaps. If you are developing locally, ensure the engine is installed into Tusk’s environment:

```bash
cd /home/vedant/code/tusk
poetry run pip install -e ../textual-vim-extended
```

This keeps Tusk and the vim engine in sync while developing both side by side.

### Configuration

- Snippets: `~/.config/tusk/snippets.json`
- Logs: `~/.tusk/logs/tusk.log`
- Auto-save: Enabled by default
- Live log stream (optional): `tusk --log-stream [--log-host HOST --log-port PORT]`

#### Live Log Streaming (experimental)

Tusk can expose its internal telemetry over a lightweight TCP stream for debugging Textual interactions in real time. Enable it via the CLI:

```bash
tusk notes.md --log-stream --log-host 0.0.0.0 --log-port 8765
```

Environment variables `TUSK_LOG_HOST` and `TUSK_LOG_PORT` provide defaults for the host/port. When no port is supplied (or `--log-port 0`), the OS picks an ephemeral port which is reported in Tusk's notification area.

Connect any TCP client (e.g. `nc 127.0.0.1 8765`) to follow structured log lines that mirror keystrokes, autosave results, and other editor events. The stream requires `vim_engine` (now a core dependency) so it shares the same telemetry module as the Textual demo.

## Contributing

Feel free to contribute by forking the repo and submitting a pull request! 🚀

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
