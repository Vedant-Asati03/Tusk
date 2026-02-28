from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Markdown, Static
from vim_engine.adapters.textual.widget import VimEditor
from vim_engine.logging import NetworkLogStreamer

from tusk.utils import AutoSave, CacheManager

DRAFT_DIR = Path.home() / ".tusk" / "drafts"


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
            Input(
                value=self.initial, placeholder="/path/to/file.md", id="save-as-input"
            ),
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

    def __init__(
        self,
        file_path: Path | None = None,
        markdown: str = "",
        *,
        log_stream: bool = False,
        log_host: str = "127.0.0.1",
        log_port: int | None = None,
    ) -> None:
        self._draft_notice: str | None = None
        self.file_path = self._prepare_file_path(file_path)
        self.markdown = markdown
        self.show_preview = True
        self.input_width = 50
        self._last_save_state = "never"
        self._last_save_error: str | None = None
        self._editor_text = markdown
        self._last_preview_text: str | None = None
        self._last_word_count = 0
        self._last_char_count = 0
        self._vim_status_text = ""
        self._vim_command_text = ""
        self._vim_editor: VimEditor | None = None
        self._preview_widget: Markdown | None = None
        self._status_widget: Static | None = None
        self._suppress_vim_callback = False

        self._log_stream_requested = log_stream
        self._log_stream_host = log_host
        self._log_stream_port = log_port
        self._log_streamer: NetworkLogStreamer | None = None

        self.auto_save = AutoSave(self.file_path)

        super().__init__()

        self.cache_manager = CacheManager(self)

        # Load settings for this specific file
        self.settings = self.cache_manager.load_settings(str(self.file_path))
        self.show_preview = self.settings["show_preview"]
        self.input_width = self.settings["input_width"]

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
        self._vim_editor = VimEditor(
            initial_text=self.markdown,
            id="input-box",
            log_callback=self._log_line,
            on_text_change=self._handle_vim_text_change,
            on_status_change=self._handle_vim_status,
            on_command_change=self._handle_vim_command,
            on_event=self._handle_vim_event,
        )
        self._preview_widget = Markdown(self.markdown, id="preview-box")
        yield Horizontal(self._vim_editor, self._preview_widget)
        initial_status = self._build_status(words=0, chars=0)
        self._status_widget = Static(initial_status, id="status-bar")
        yield self._status_widget

    async def on_key(self, event: events.Key) -> None:
        target = getattr(event, "target", None)
        target_id = getattr(target, "id", None)
        self._log_state(
            "key ->",
            key=event.key,
            text=getattr(event, "character", None),
            target=target_id,
            ctrl=getattr(event, "ctrl", False),
            alt=getattr(event, "alt", False),
            shift=getattr(event, "shift", False),
        )
        # Base App has no on_key hook; logging only so skip super call.

    async def on_mount(self) -> None:
        """Initialize the application after mounting."""
        initial_content = self.markdown
        if self.file_path and self.file_path.is_file():
            try:
                initial_content = self.auto_save.load_last_save()
            except Exception as exc:
                initial_content = ""
                self.notify(f"Error loading file: {exc}", severity="error")

        self._editor_text = initial_content
        if self._preview_widget:
            self._preview_widget.update(initial_content)
        if self._vim_editor:
            buffer_name = str(self.file_path) if self.file_path else "draft"
            self._vim_editor.set_buffer_name(buffer_name)
            self._suppress_vim_callback = True
            self._vim_editor.load_text(initial_content)
            self._suppress_vim_callback = False

        self._on_editor_text_changed(initial_content, initial_load=True)

        if self._draft_notice:
            self.notify(self._draft_notice, severity="information")

        if self._log_stream_requested:
            await self._start_log_stream()

    def _do_save(self) -> None:
        """Save content directly to the opened file."""
        success, error = self.auto_save.autosave_content(self._editor_text)
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

        content = self._editor_text
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
        input_box = self._vim_editor
        preview = self._preview_widget
        if not input_box or not preview:
            return

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
        preview = self._preview_widget
        input_box = self._vim_editor
        if not preview or not input_box:
            return

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
            input_box = self._vim_editor
            preview_box = self._preview_widget
            if not input_box or not preview_box:
                return
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    def action_shrink_input_box(self) -> None:
        if self.input_width > 0:
            self.input_width -= 1
            input_box = self._vim_editor
            preview_box = self._preview_widget
            if not input_box or not preview_box:
                return
            input_box.styles.width = f"{self.input_width}%"
            preview_box.styles.width = f"{100 - self.input_width}%"

    async def _start_log_stream(self) -> None:
        if not NetworkLogStreamer:
            return
        port = self._log_stream_port if self._log_stream_port is not None else 8765
        streamer = NetworkLogStreamer(self._log_stream_host, port)
        await streamer.start()
        self._log_streamer = streamer
        bound = streamer.port
        self._log_line(f"log stream ready on {self._log_stream_host}:{bound}")

    async def _stop_log_stream(self) -> None:
        if self._log_streamer:
            await self._log_streamer.stop()
            self._log_streamer = None

    def _handle_vim_text_change(self, text: str) -> None:
        self._editor_text = text
        if self._suppress_vim_callback:
            return
        self._on_editor_text_changed(text)

    def _handle_vim_status(self, status: str) -> None:
        self._vim_status_text = status
        self._update_status_bar(self._last_word_count, self._last_char_count)

    def _handle_vim_command(self, command: str) -> None:
        self._vim_command_text = command
        self._update_status_bar(self._last_word_count, self._last_char_count)

    def _handle_vim_event(self, name: str, payload: object | None) -> None:
        if name.startswith("command"):
            detail = f"{name}:{payload}" if payload is not None else name
            self._vim_status_text = detail
            self._update_status_bar(self._last_word_count, self._last_char_count)

    def _on_editor_text_changed(self, text: str, *, initial_load: bool = False) -> None:
        if self._last_preview_text == text and not initial_load:
            return
        self._last_preview_text = text
        if self._preview_widget:
            self._preview_widget.update(text)
        previous_state = self._last_save_state
        if initial_load:
            success, error = True, None
        else:
            success, error = self.auto_save.autosave_content(text)
        self._record_save_result(success, error)
        if not initial_load:
            if not success and error and previous_state != "error":
                self.notify(error, severity="error")
            elif success and previous_state == "error":
                self.notify("Autosave restored", severity="information")
        words = len(text.split())
        chars = len(text)
        self._last_word_count = words
        self._last_char_count = chars
        self._update_status_bar(words, chars)
        self._log_state("text", words=words, chars=chars)

    def _log_line(self, message: str) -> None:
        if self._log_streamer:
            self._log_streamer.log(message)

    def _state_snapshot(self) -> Dict[str, object]:
        data: Dict[str, object] = {
            "file": str(self.file_path) if self.file_path else "<draft>",
            "save_state": self._format_save_state(),
            "preview": self.show_preview,
            "theme": self.theme,
        }
        text = self._editor_text or ""
        data.update(
            {
                "words": len(text.split()),
                "chars": len(text),
            }
        )
        if (
            self._vim_editor
            and self._vim_editor.manager
            and self._vim_editor.manager.active_mode
        ):
            data["vim_mode"] = self._vim_editor.manager.active_mode.name
        if self._vim_command_text:
            data["command"] = self._vim_command_text
        return data

    def _log_state(self, prefix: str, **fields: object) -> None:
        if not self._log_streamer:
            return
        snapshot = self._state_snapshot()
        snapshot.update({k: v for k, v in fields.items() if v is not None})
        parts = [prefix]
        for key, value in snapshot.items():
            parts.append(f"{key}={value!r}")
        self._log_streamer.log(" ".join(parts))

    def _refresh_preview(self) -> None:
        if self._preview_widget:
            self._preview_widget.update(self._editor_text)
        self._update_status_bar(self._last_word_count, self._last_char_count)

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
        if (
            self._vim_editor
            and self._vim_editor.manager
            and self._vim_editor.manager.active_mode
        ):
            status += f" --mode {self._vim_editor.manager.active_mode.name}--"
        if self._vim_status_text:
            status += f" --vim {self._vim_status_text}--"
        if self._vim_command_text:
            status += f" :{self._vim_command_text}"
        return status

    def _update_status_bar(self, words: int, chars: int) -> None:
        if self._status_widget:
            self._status_widget.update(self._build_status(words, chars))

    def _refresh_status_from_input(self) -> None:
        text = self._editor_text
        self._last_word_count = len(text.split())
        self._last_char_count = len(text)
        self._update_status_bar(self._last_word_count, self._last_char_count)

    def _record_save_result(self, success: bool, error: str | None) -> None:
        if success:
            self._last_save_state = "ok"
            self._last_save_error = None
        else:
            self._last_save_state = "error"
            self._last_save_error = error
        self._log_state("save", success=success, error=error)

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

    async def on_unmount(self) -> None:
        """Save settings and stop background helpers when the application closes."""
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

        await self._stop_log_stream()


if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    raw_path = sys.argv[1] if len(sys.argv) > 1 else None
    path_arg = Path(raw_path) if raw_path else None
    log_env = os.environ.get("TUSK_LOG_STREAM", "0").lower()
    log_stream_enabled = log_env not in {"0", "false", ""}
    log_host = os.environ.get("TUSK_LOG_HOST", "127.0.0.1")
    port_env = os.environ.get("TUSK_LOG_PORT")
    log_port = int(port_env) if port_env else None
    app = Tusk(
        file_path=path_arg,
        log_stream=log_stream_enabled,
        log_host=log_host,
        log_port=log_port,
    )
    app.run()
