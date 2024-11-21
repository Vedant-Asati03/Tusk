from textual import events
from textual.binding import Binding
from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Markdown, Static
from pathlib import Path
import sys
from textual.command import Hit, Hits, Provider
from functools import partial
import markdown
import pypandoc
import re

from tusk.auto_save import AutoSave

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


class ThemeCommand(Provider):
    """Provider for theme switching commands"""
    THEMES = [
        "dracula", "monokai", "github-dark", "one-dark", 
        "solarized-dark", "solarized-light", "nord"
    ]

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for theme in self.THEMES:
            command = f"theme {theme}"
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(self.app.change_theme, theme),
                    help=f"Switch to {theme} theme"
                )

class ExportCommand(Provider):
    """Provider for export commands"""
    FORMATS = ["html", "pdf", "docx"]

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for fmt in self.FORMATS:
            command = f"export {fmt}"
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(self.app.export_document, fmt),
                    help=f"Export as {fmt}"
                )

class Tusk(App):
    COMMANDS = App.COMMANDS | {ThemeCommand, ExportCommand}

    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command palette"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+@", "toggle_preview", "Toggle Preview"),
        Binding("ctrl+l", "expand_input_box", "Widen input"),
        Binding("ctrl+q", "shrink_input_box", "Shrink input"),
        Binding("ctrl+b", "insert_toc", "Insert TOC"),
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

    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text;
    }
    """

    SAVE_INTERVAL = 0.8

    def __init__(self, markdown: str = "", file_path: str | None = None) -> None:
        self.markdown = markdown
        self.file_path = Path(file_path) if file_path else None
        self.show_preview = True
        self.input_width = 50
        self.auto_save = AutoSave(self.file_path)
        super().__init__()

    def compose(self) -> ComposeResult:
        input_box = TextAreaExtended.code_editor(
            id="input-box", language="markdown", theme="dracula", soft_wrap=True
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)
        yield Static("Words: 0 | Chars: 0", id="status-bar")

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
        # Add word count update
        words = len(input_content.split())
        chars = len(input_content)
        self.query_one("#status-bar").update(f"Words: {words} | Chars: {chars}")

    def _do_save(self) -> None:
        """Save content directly to the opened file."""
        input_box = self.query_one("#input-box", TextArea)
        self.auto_save.autosave_content(input_box.text)  # Use AutoSave for saving

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

    def action_insert_toc(self) -> None:
        """Generate and insert table of contents."""
        input_box = self.query_one("#input-box", TextArea)
        content = input_box.text
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        toc = ["# Table of Contents\n"]
        for hashes, title in headers:
            level = len(hashes) - 1
            link = title.lower().replace(' ', '-')
            toc.append(f"{'  ' * level}* [{title}](#{link})\n")
        
        input_box.insert("\n".join(toc) + "\n")

    def change_theme(self, theme: str) -> None:
        """Switch editor theme."""
        input_box = self.query_one("#input-box", TextArea)
        input_box.theme = theme

    def export_document(self, format: str) -> None:
        """Export document to different formats."""
        if not self.file_path:
            self.notify("Please save the file first", severity="error")
            return

        content = self.query_one("#input-box").text
        output_file = self.file_path.with_suffix(f".{format}")
        
        try:
            if format == "html":
                html = markdown.markdown(content)
                output_file.write_text(html)
            else:
                pypandoc.convert_text(
                    content,
                    format,
                    format='md',
                    outputfile=str(output_file)
                )
            self.notify(f"Exported to {output_file}")
        except Exception as e:
            self.notify(f"Export failed: {str(e)}", severity="error")


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = Tusk(file_path=file_path)
    app.run()
