from textual import events
from textual.binding import Binding
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown

from vim_bindings import CustomKeyBindings


class AutoComplete(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    def _on_key(self, event: events.Key) -> None:
        bracket_quote_pair = {"(": ")", "{": "}", "[": "]", '"': '"', "'": "'"}
        if event.character in bracket_quote_pair.keys():
            self.insert(event.character + bracket_quote_pair[event.character])
            self.move_cursor_relative(columns=-1)
            event.prevent_default()


class CustomTextArea(CustomKeyBindings, AutoComplete):
    pass


class Tusk(App):
    BINDINGS = [
        Binding("ctrl+shift+q", "command_palette", "Command palette"),
    ]

    CSS = """
Screen {
    layout: horizontal;
}

#input-box {
    width: 50%;
    height: 100%;
    border: none;
    background: #0C0C0C;
    color: #d4d4d4;
}

#preview-box {
    width: 50%;
    height: 100%;
    border: none;
    background: #0C0C0C;
    color: #F1F1F1;
}
"""

    def __init__(self, markdown: str = "") -> None:
        self.markdown = markdown
        super().__init__()

    def compose(self) -> ComposeResult:
        input_box = CustomTextArea(show_line_numbers=True, id="input-box", language="markdown",
                                   tab_behavior="indent",
                                   theme="dracula")

        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle live updating of the markdown preview as the input changes."""
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)


if __name__ == "__main__":
    app = Tusk()
    app.run()
