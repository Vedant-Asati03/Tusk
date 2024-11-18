# import os
from datetime import datetime
from textual import events
from textual.binding import Binding
from textual.command import CommandPalette, Command
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown

# import sys
# sys.path.append(os.path.expanduser("/code:/textual-vim-extended/"))

# from vim_bindings import HandleVimBindings
from command_palette import TuskCommandPalette
from auto_save import AutoSave


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


class TextAreaExtended(AutoComplete):
    pass


class Tusk(App):
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command palette"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+@", "toggle_preview", "Toggle Preview"),
        Binding("ctrl+l", "widen_input", "Widen input"),     # new binding
        Binding("ctrl+q", "shrink_input", "Shrink input"),   # new binding
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
        self.autosaver = AutoSave(autosave_path)
        self.show_preview = True
        self.input_width = 50  # Track input width percentage
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
        self.set_interval(self.AUTOSAVE_INTERVAL, self._do_autosave)
        # Load last save
        input_box = self.query_one("#input-box", TextArea)
        input_box.text = self.autosaver.load_last_save()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle live updating of the markdown preview as the input changes."""
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)

    def _do_autosave(self) -> None:
        """Perform autosave operation."""
        input_box = self.query_one("#input-box", TextArea)
        self.autosaver.autosave_content(input_box.text)

    async def action_command_palette(self) -> None:
        """Show the command palette."""
        await self.push_screen(TuskCommandPalette())

    def action_save(self) -> None:
        """Manually trigger a save."""
        self._do_autosave()

    def action_toggle_preview(self) -> None:
        """Toggle the preview pane."""
        preview = self.query_one("#preview-box")
        input_box = self.query_one("#input-box")
        
        self.show_preview = not self.show_preview
        if self.show_preview:
            preview.styles.width = f"{100 - self.input_width}%"
            input_box.styles.width = f"{self.input_width}%"
        else:
            preview.styles.width = "0%"
            input_box.styles.width = "100%"

    def action_widen_input(self) -> None:
        """Increase input box width."""
        if self.input_width < 100:  # Max width limit
            self.input_width += 1  # Smaller step size
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    def action_shrink_input(self) -> None:
        """Decrease input box width."""
        if self.input_width > 0:  # Min width limit
            self.input_width -= 1  # Smaller step size
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

if __name__ == "__main__":
    Tusk().run()
