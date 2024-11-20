from textual import events
from textual.binding import Binding
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown
from pathlib import Path
import sys

from auto_save import AutoSave  # Add this import

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
        Binding("ctrl+l", "expand_input_box", "Widen input"),
        Binding("ctrl+q", "shrink_input_box", "Shrink input"),
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
    color: #F1F1F1;
    scrollbar-size-vertical: 1;
}
"""

    SAVE_INTERVAL = 0.8

    def __init__(self, markdown: str = "", file_path: str | None = None) -> None:
        self.markdown = markdown
        self.file_path = Path(file_path) if file_path else None
        self.show_preview = True
        self.input_width = 50
        self.auto_save = AutoSave(self.file_path)  # This is the only saving mechanism we'll use
        super().__init__()

    def compose(self) -> ComposeResult:
        input_box = TextAreaExtended.code_editor(
            id="input-box", language="markdown", theme="dracula", soft_wrap=True
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)

    def on_mount(self) -> None:
        """Initialize the application after mounting."""
        self.theme = "tokyo-night"

        if self.file_path and self.file_path.is_file():
            input_box = self.query_one("#input-box", TextArea)
            try:
                input_box.text = self.auto_save.load_last_save()  # Use AutoSave's load method
            except Exception as e:
                input_box.text = f"Error loading file: {str(e)}"

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Update the preview pane when text content changes.
        
        Args:
            event (TextArea.Changed): Event containing the updated text content.
        """
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)
        # Add autosave on content change
        self.auto_save.autosave_content(input_content)

    def _do_save(self) -> None:
        """Save content directly to the opened file."""
        input_box = self.query_one("#input-box", TextArea)
        self.auto_save.autosave_content(input_box.text)  # Use AutoSave for saving

    # async def action_command_palette(self) -> None:
    #     await self.push_screen(TuskCommandPalette())

    def action_save(self) -> None:
        """Manual save action."""
        self._do_save()

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

    def action_expand_input_box(self) -> None:
        if self.input_width < 100:
            self.input_width += 1
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    def action_shrink_input_box(self) -> None:
        if self.input_width > 0:
            self.input_width -= 1
            input_box = self.query_one("#input-box")
            preview_box = self.query_one("#preview-box")
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"


if __name__  == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = Tusk(file_path=file_path)
    app.run()
