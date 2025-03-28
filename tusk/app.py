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

from .utils import AutoSave, AutoSnippets, AutoComplete, CacheManager


class TextAreaExtended(AutoComplete):
    """Extended text area with snippet support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snippets = AutoSnippets()
        self.snippet_trigger = ""

    def _on_key(self, event: events.Key) -> None:
        """Handle key events including snippet expansion."""
        if event.key == "tab" and self.snippet_trigger:
            expanded = self.snippets.expand_snippet(self.snippet_trigger)
            if expanded:
                for _ in range(len(self.snippet_trigger)):
                    self.action_delete_left()
                self.insert(expanded)
                if expanded in ["****", "[]()", "![]()"]:
                    self.move_cursor_relative(columns=-2)
                event.prevent_default()
            self.snippet_trigger = ""
            return

        super()._on_key(event)

        if event.character and event.character.isalnum():
            self.snippet_trigger += event.character
        else:
            self.snippet_trigger = ""


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
                    help=f"Export as {fmt}",
                )


class Tusk(App):
    COMMANDS = App.COMMANDS | {ExportCommand}

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
        border: vkey;
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
        # Initialize cache manager with self reference
        super().__init__()  # Initialize App first so we can use notify
        self.cache_manager = CacheManager(self)
        self.file_path = Path(file_path) if file_path else None

        # Load settings for this specific file
        self.settings = self.cache_manager.load_settings(
            str(self.file_path) if self.file_path else None
        )

        self.markdown = markdown
        self.show_preview = self.settings["show_preview"]
        self.input_width = self.settings["input_width"]
        self.auto_save = AutoSave(self.file_path)

        # Add current file to recent files if provided
        if file_path:
            self.cache_manager.add_recent_file(str(file_path))

        super().__init__()

    def compose(self) -> ComposeResult:
        input_box = TextAreaExtended(
            id="input-box",
            language="markdown",
            soft_wrap=True,
            show_line_numbers=True,
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)
        initial_status = (
            f"--words 0-- "
            f"--chars 0-- "
            f"--theme {self.theme}-- "
            f"--autosave-enabled-- "
            f"{self.file_path or 'Untitled'}"
        )
        yield Static(initial_status, id="status-bar")

    def on_mount(self) -> None:
        """Initialize the application after mounting."""
        if self.file_path and self.file_path.is_file():
            input_box = self.query_one("#input-box", TextArea)
            try:
                input_box.text = self.auto_save.load_last_save()
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
        self.auto_save.autosave_content(input_content)

        words = len(input_content.split())
        chars = len(input_content)
        last_save = self.auto_save.get_last_save_time()

        status = (
            f"--last-saved {last_save}-- "
            f"--words {words}-- "
            f"--chars {chars}-- "
            f"--theme {self.theme}-- "
            f"--autosave-enabled-- "
            f"{self.file_path or 'Untitled'}"
        )
        self.query_one("#status-bar").update(status)

    def _do_save(self) -> None:
        """Save content directly to the opened file."""
        input_box = self.query_one("#input-box", TextArea)
        self.auto_save.autosave_content(input_box.text)

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

        self.on_text_area_changed(TextArea.Changed(self.query_one("#input-box")))

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
        headers = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)

        toc = ["## Table of Contents\n"]
        for hashes, title in headers:
            level = len(hashes) - 1
            link = title.lower().replace(" ", "-")
            toc.append(f"{'  ' * level}* [{title}](#{link})\n")

        input_box.insert("\n".join(toc) + "\n")

    def export_document(self, format: str) -> None:
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
                    content, format, format="md", outputfile=str(output_file)
                )
            self.notify(f"Exported to {output_file}")
        except Exception as e:
            self.notify(
                f"Export failed: {str(e)}",
                title="Export Failed!",
                severity="error",
                timeout=4,
            )

    def on_unmount(self) -> None:
        """Save settings when the application closes."""
        if self.file_path:
            try:
                input_box = self.query_one("#input-box", TextArea)
                settings = {
                    "theme": self.theme,
                    "input_width": self.input_width,
                    "show_preview": self.show_preview,
                    "cursor_location": input_box.cursor_location,
                }
                self.cache_manager.save_settings(str(self.file_path), settings)
            except Exception as e:
                print(f"Error saving settings on exit: {e}")


if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = Tusk(file_path=file_path)
    app.run()
