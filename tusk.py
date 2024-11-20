from textual import events
from textual.binding import Binding
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown

from command_palette import TuskCommandPalette
from auto_save import AutoSave


class AutoComplete(TextArea):
    """A TextArea widget that automatically completes brackets and markdown syntax.
    
    This class extends TextArea to provide auto-completion for common programming
    and markdown syntax elements like brackets, quotes, and markdown formatting symbols.
    """

    def _on_key(self, event: events.Key) -> None:
        """Handle key events for auto-completion of brackets and markdown syntax.
        
        Args:
            event (events.Key): The key event containing the character pressed.
        """
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
    """A markdown editor application with live preview functionality.
    
    Features:
    - Split view with editor and preview pane
    - Auto-saving capability
    - Command palette for quick actions
    - Adjustable split view width
    - Vim-like keybindings
    """

    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command palette"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+@", "toggle_preview", "Toggle Preview"),
        Binding("ctrl+l", "widen_input", "Widen input"),
        Binding("ctrl+q", "shrink_input", "Shrink input"),
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

    AUTOSAVE_INTERVAL = 0.8

    def __init__(self, markdown: str = "", autosave_path: str = "autosave.md") -> None:
        self.markdown = markdown
        self.autosaver = AutoSave(autosave_path)
        self.show_preview = True
        self.input_width = 50
        super().__init__()

    def compose(self) -> ComposeResult:
        input_box = TextAreaExtended.code_editor(
            id="input-box", language="markdown", theme="dracula", soft_wrap=True
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)

    def on_mount(self) -> None:
        """Initialize the application after mounting.
        
        Sets up auto-save timer and loads the last saved content.
        """
        self.set_interval(self.AUTOSAVE_INTERVAL, self._do_autosave)
        input_box = self.query_one("#input-box", TextArea)
        input_box.text = self.autosaver.load_last_save()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Update the preview pane when text content changes.
        
        Args:
            event (TextArea.Changed): Event containing the updated text content.
        """
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)

    def _do_autosave(self) -> None:
        input_box = self.query_one("#input-box", TextArea)
        self.autosaver.autosave_content(input_box.text)

    async def action_command_palette(self) -> None:
        await self.push_screen(TuskCommandPalette())

    def action_save(self) -> None:
        self._do_autosave()

    def action_toggle_preview(self) -> None:
        """Toggle the visibility of the preview pane.
        
        When toggled off, the editor expands to full width.
        When toggled on, returns to split view with previous width ratio.
        """
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
        if self.input_width < 100:
            self.input_width += 1
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    def action_shrink_input(self) -> None:
        if self.input_width > 0:
            self.input_width -= 1
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"


if __name__ == "__main__":
    Tusk().run()
