import os
from datetime import datetime
from textual import events
from textual.binding import Binding
from textual.command import CommandPalette, Command
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown

import sys

sys.path.append("D:/textual-vim-extended")
from vim_bindings import HandleVimBindings


class AutoComplete(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    def _on_key(self, event: events.Key) -> None:
        bracket_quote_pair = {
            "(": ")",
            "{": "}",
            "[": "]",
            '"': '"',
            "'": "'",
            "<": ">",
            "`": "`",
            "*": "*",
            "_": "_",
            "__": "__",
            "~": "~",
            "```": "```",
        }
        if event.character in bracket_quote_pair.keys():
            self.insert(event.character + bracket_quote_pair[event.character])
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        elif event.character == "#":
            self.insert("# ")
            event.prevent_default()


class TextAreaExtended(AutoComplete, HandleVimBindings):
    pass


class Tusk(App):
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command palette"),
    ]

    CSS = """
Screen {
    layout: horizontal;
}


#input-box {
    width: 50%;
    height: 100%;
    border: blank;
    scrollbar-color: #C7C8CC;
    scrollbar-size-vertical: 1;

}

#preview-box {
    width: 50%;
    height: 104%;
    border: blank;
    background: #0C0C0C;
    color: #F1F1F1;
    scrollbar-color: #C7C8CC;
    scrollbar-size-vertical: 1;
}
"""

    AUTOSAVE_INTERVAL = 0.8  # seconds

    def __init__(self, markdown: str = "", autosave_path: str = "autosave.md") -> None:
        self.markdown = markdown
        self.autosave_path = autosave_path
        super().__init__()

    def compose(self) -> ComposeResult:
        # self.border_subtitle = "--Autosave--"
        input_box = TextAreaExtended.code_editor(
            id="input-box", language="markdown", theme="dracula", soft_wrap=True
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)

    def on_mount(self) -> None:
        """Start the autosave timer when the app is mounted."""
        self.set_interval(self.AUTOSAVE_INTERVAL, self.autosave_content)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle live updating of the markdown preview as the input changes."""
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)

    def autosave_content(self) -> None:
        """Save the content of the input box to a file."""
        input_box = self.query_one("#input-box", TextArea)
        content = input_box.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.autosave_path, "w", encoding="utf-8") as file:
            file.write(f"<!-- Autosaved at {timestamp} -->\n")
            file.write(content)

        self.log(f"Autosaved content at {timestamp} to {self.autosave_path}")


if __name__ == "__main__":
    Tusk().run()
