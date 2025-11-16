import re
import sys
from datetime import datetime
from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Markdown, Static, TextArea

from tusk.utils import AutoComplete, AutoSave, AutoSnippets, CacheManager


DRAFT_DIR = Path.home() / ".tusk" / "drafts"


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


class SaveAsScreen(ModalScreen[Path | None]):
    """Modal dialog that collects a destination path for Save As."""

    CSS = """
    #save-as-modal {
        padding: 1 2;
        border: round $accent;
        width: 60%;
        max-width: 80;
        background: $panel;
    }

    #save-as-input {
        width: 100%;
        margin: 1 0;
    }

    #save-as-actions {
        width: 100%;
        align-horizontal: right;
        gap: 1;
    }
    """

    def __init__(self, initial: str) -> None:
        super().__init__()
        self.initial = initial

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Save current document as:", id="save-as-title"),
            Input(value=self.initial, placeholder="/path/to/file.md", id="save-as-input"),
            Horizontal(
                Button("Cancel", id="cancel"),
                Button("Save", id="save", variant="primary"),
                id="save-as-actions",
            ),
            id="save-as-modal",
        )

    def on_mount(self) -> None:
        self.query_one("#save-as-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._submit()
        else:
            self.dismiss(None)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit()

    def _submit(self) -> None:
        value = self.query_one("#save-as-input", Input).value.strip()
        if not value:
            self.dismiss(None)
            return
        self.dismiss(Path(value))


class Tusk(App):
    COMMANDS = App.COMMANDS

    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command palette"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+shift+s", "save_as", "Save As"),
        Binding("ctrl+!", "toggle_input", "Toggle Input"),
        Binding("ctrl+@", "toggle_preview", "Toggle Preview"),
        Binding("ctrl+l", "expand_input_box", "Widen input"),
        Binding("ctrl+q", "shrink_input_box", "Shrink input"),
        Binding("ctrl+b", "insert_toc", "Insert TOC"),
        # Line operations
        Binding("ctrl+d", "duplicate_line", "Duplicate line"),
        Binding("alt+up", "move_line_up", "Move line up"),
        Binding("alt+down", "move_line_down", "Move line down"),
        # Editor features
        Binding("ctrl+alt+i", "toggle_auto_indent", "Toggle auto-indent"),
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

    def __init__(self, file_path: Path | None = None, markdown: str = "") -> None:
        self._draft_notice: str | None = None
        self.cache_manager = CacheManager(self)
        self.file_path = self._prepare_file_path(file_path)

        # Load settings for this specific file
        self.settings = self.cache_manager.load_settings(str(self.file_path))

        self.markdown = markdown
        self.show_preview = self.settings["show_preview"]
        self.input_width = self.settings["input_width"]
        self._last_save_state = "never"
        self._last_save_error: str | None = None

        self.auto_save = AutoSave(self.file_path)

        super().__init__()

    def _prepare_file_path(self, file_path: Path | None) -> Path:
        if file_path and file_path != Path():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return file_path

        draft_dir = DRAFT_DIR
        draft_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        draft_path = draft_dir / f"draft-{timestamp}.md"
        counter = 1
        while draft_path.exists():
            draft_path = draft_dir / f"draft-{timestamp}-{counter}.md"
            counter += 1
        draft_path.touch()
        self._draft_notice = f"Working in draft: {draft_path}"
        return draft_path

    def compose(self) -> ComposeResult:
        input_box = TextAreaExtended(
            id="input-box",
            language="markdown",
            soft_wrap=True,
            show_line_numbers=True,
        )
        preview_box = Markdown(self.markdown, id="preview-box")
        yield Horizontal(input_box, preview_box)
        initial_status = self._build_status(words=0, chars=0)
        yield Static(initial_status, id="status-bar")

    def on_mount(self) -> None:
        """Initialize the application after mounting."""
        if self.file_path and self.file_path.is_file():
            input_box = self.query_one("#input-box", TextArea)
            try:
                # Load file content
                content = self.auto_save.load_last_save()
                input_box.text = content

            except Exception as e:
                input_box.text = f"Error loading file: {str(e)}"

        if self._draft_notice:
            self.notify(self._draft_notice, severity="information")

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Update the preview pane when text content changes.

        Args:
            event (TextArea.Changed): Event containing the updated text content.
        """
        input_content = event.control.text
        preview_box = self.query_one("#preview-box", Markdown)
        preview_box.update(input_content)
        previous_state = self._last_save_state
        success, error = self.auto_save.autosave_content(input_content)
        self._record_save_result(success, error)
        if not success and error and previous_state != "error":
            self.notify(error, severity="error")
        elif success and previous_state == "error":
            self.notify("Autosave restored", severity="information")

        words = len(input_content.split())
        chars = len(input_content)
        self._update_status_bar(words, chars)

    def _do_save(self) -> None:
        """Save content directly to the opened file."""
        input_box = self.query_one("#input-box", TextArea)
        success, error = self.auto_save.autosave_content(input_box.text)
        self._record_save_result(success, error)
        self._refresh_status_from_input()
        if success:
            self.notify("File saved", severity="information")
        else:
            self.notify(error or "Failed to save file", severity="error")

    def action_save(self) -> None:
        """Manual save action."""
        self._do_save()

    def action_save_as(self) -> None:
        """Prompt for a new destination and save the document there."""
        default_path = str(self.file_path) if self.file_path else ""
        self.push_screen(SaveAsScreen(default_path), self._save_as_result)

    def _save_as_result(self, destination: Path | None) -> None:
        if destination:
            self._save_to_path(destination)

    def _save_to_path(self, destination: Path) -> None:
        target = destination.expanduser()
        if not target.is_absolute():
            target = Path.cwd() / target

        input_box = self.query_one("#input-box", TextArea)
        content = input_box.text
        previous_path = self.file_path

        self.file_path = target
        self.auto_save.set_file_path(target)
        success, error = self.auto_save.autosave_content(content)

        if success:
            if (
                previous_path
                and previous_path != target
                and self._is_draft_path(previous_path)
            ):
                try:
                    previous_path.unlink()
                except OSError:
                    pass
            self._draft_notice = None
            self._record_save_result(True, None)
            self.notify(f"Saved to {target}", severity="information")
            self._refresh_status_from_input()
        else:
            if previous_path:
                self.file_path = previous_path
                self.auto_save.set_file_path(previous_path)
            self._record_save_result(False, error)
            self._refresh_status_from_input()
            self.notify(error or "Save As failed", severity="error")

    def action_toggle_input(self) -> None:
        """Toggle the visibility of the input pane.

        When toggled off, the preview expands to full width.
        When toggled on, returns to split view with previous width ratio.
        """
        input_box = self.query_one("#input-box", TextArea)
        preview = self.query_one("#preview-box", Markdown)

        if input_box.styles.width == "0%":
            input_box.styles.width = f"{self.input_width}%"
            preview.styles.width = f"{100 - self.input_width}%"
        else:
            input_box.styles.width = "0%"
            preview.styles.width = "100%"

        self._refresh_preview()

    def action_toggle_preview(self) -> None:
        """Toggle the visibility of the preview pane.

        When toggled off, the editor expands to full width.
        When toggled on, returns to split view with previous width ratio.
        """
        preview = self.query_one("#preview-box", Markdown)
        input_box = self.query_one("#input-box", TextArea)

        self.show_preview = not self.show_preview
        if self.show_preview:
            preview.styles.width = f"{100 - self.input_width}%"
            input_box.styles.width = f"{self.input_width}%"
        else:
            preview.styles.width = "0%"
            input_box.styles.width = "100%"

        self._refresh_preview()

    def action_expand_input_box(self) -> None:
        if self.input_width < 100:
            self.input_width += 1
            input_box = self.query_one("#input-box", TextArea)
            preview_box = self.query_one("#preview-box", Markdown)
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    def action_shrink_input_box(self) -> None:
        if self.input_width > 0:
            self.input_width -= 1
            input_box = self.query_one("#input-box", TextArea)
            preview_box = self.query_one("#preview-box", Markdown)
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

    def action_duplicate_line(self) -> None:
        """Duplicate the current line."""
        input_box = self.query_one("#input-box", TextAreaExtended)
        input_box.action_duplicate_line()

    def action_move_line_up(self) -> None:
        """Move current line up."""
        input_box = self.query_one("#input-box", TextAreaExtended)
        input_box.action_move_line_up()

    def action_move_line_down(self) -> None:
        """Move current line down."""
        input_box = self.query_one("#input-box", TextAreaExtended)
        input_box.action_move_line_down()

    def action_toggle_auto_indent(self) -> None:
        """Toggle auto-indent feature."""
        input_box = self.query_one("#input-box", TextAreaExtended)
        input_box.toggle_auto_indent()
        status = "enabled" if input_box.auto_indent_enabled else "disabled"
        self.notify(f"Auto-indent {status}")

    def _refresh_preview(self) -> None:
        input_box = self.query_one("#input-box", TextArea)
        self.on_text_area_changed(TextArea.Changed(input_box))

    def _build_status(self, words: int, chars: int) -> str:
        last_save = self.auto_save.get_last_save_time()
        save_state = self._format_save_state()
        status = (
            f"--last-saved {last_save}-- "
            f"--save {save_state}-- "
            f"--words {words}-- "
            f"--chars {chars}-- "
            f"--theme {self.theme}-- "
            f"--autosave-enabled-- "
            f"{self.file_path}"
        )
        return status

    def _update_status_bar(self, words: int, chars: int) -> None:
        self.query_one("#status-bar", Static).update(
            self._build_status(words, chars)
        )

    def _refresh_status_from_input(self) -> None:
        input_box = self.query_one("#input-box", TextArea)
        text = input_box.text
        self._update_status_bar(len(text.split()), len(text))

    def _record_save_result(self, success: bool, error: str | None) -> None:
        if success:
            self._last_save_state = "ok"
            self._last_save_error = None
        else:
            self._last_save_state = "error"
            self._last_save_error = error

    def _format_save_state(self) -> str:
        if self._last_save_state == "ok":
            return "ok"
        if self._last_save_state == "error":
            return "error"
        return "never"

    def _is_draft_path(self, path: Path) -> bool:
        try:
            return path.is_relative_to(DRAFT_DIR)
        except ValueError:
            return False

    def on_unmount(self) -> None:
        """Save settings when the application closes."""
        if self.file_path:
            try:
                # Save basic settings only
                settings = {
                    "theme": self.theme,
                    "input_width": self.input_width,
                    "show_preview": self.show_preview,
                }
                self.cache_manager.save_settings(str(self.file_path), settings)

            except Exception as e:
                print(f"Error saving settings on exit: {e}")


if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    raw_path = sys.argv[1] if len(sys.argv) > 1 else None
    path_arg = Path(raw_path) if raw_path else None
    app = Tusk(file_path=path_arg)
    app.run()
