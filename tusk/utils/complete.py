import re

from textual import events
from textual.widgets import TextArea


class AutoComplete(TextArea):
    """A TextArea widget with enhanced auto-completion, smart editing, and productivity features.

    This class extends TextArea to provide:
    - Auto-completion for brackets, quotes, and markdown syntax
    - Smart quotes conversion
    - Auto-indentation for lists and code blocks
    - Line operations (duplicate, move up/down)
    - Enhanced auto-pairing with context awareness
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_indent_enabled = True

    def _get_current_line(self) -> str:
        """Get the content of the current line."""
        cursor_row, cursor_col = self.cursor_location
        lines = self.text.split("\n")
        if cursor_row < len(lines):
            return lines[cursor_row]
        return ""

    def _get_line_indent(self, line: str) -> str:
        """Get the indentation of a line."""
        match = re.match(r"^(\s*)", line)
        return match.group(1) if match else ""

    def _is_in_code_block(self) -> bool:
        """Check if cursor is inside a code block."""
        cursor_row, _ = self.cursor_location
        lines = self.text.split("\n")

        code_block_count = 0
        for i in range(cursor_row + 1):
            if i < len(lines):
                if lines[i].strip().startswith("```"):
                    code_block_count += 1

        return code_block_count % 2 == 1

    def _should_convert_quotes(self, quote_char: str) -> bool:
        """Smart quotes feature removed for minimalism."""
        return False

    def _handle_smart_quotes(self, event: events.Key) -> bool:
        """Smart quotes feature removed for minimalism."""
        return False

    def _handle_auto_indent(self, event: events.Key) -> bool:
        """Handle auto-indentation for lists and code blocks."""
        if not self.auto_indent_enabled or event.key != "enter":
            return False

        current_line = self._get_current_line()
        indent = self._get_line_indent(current_line)

        # Handle list items
        list_patterns = [
            (r"^(\s*)([-*+])\s+(.*)$", r"\1\2 "),  # Unordered lists
            (r"^(\s*)(\d+\.)\s+(.*)$", r"\1{}. "),  # Ordered lists
            (r"^(\s*)(>\s*)(.*)$", r"\1\2"),  # Blockquotes
            (r"^(\s*)(-\s*\[[ x]\])\s+(.*)$", r"\1- [ ] "),  # Todo lists
        ]

        for pattern, replacement in list_patterns:
            match = re.match(pattern, current_line.rstrip())
            if match:
                if pattern.startswith(r"^(\s*)(\d+\.)"):
                    # For ordered lists, increment the number
                    try:
                        num = int(match.group(2)[:-1]) + 1
                        new_indent = f"{match.group(1)}{num}. "
                    except ValueError:
                        new_indent = f"{indent}1. "
                else:
                    new_indent = re.sub(pattern, replacement, current_line.rstrip())

                # If the line is empty after the marker, remove the marker
                if len(current_line.strip()) <= len(match.group(2)) + 1:
                    self.insert("\n")
                else:
                    self.insert(f"\n{new_indent}")
                event.prevent_default()
                return True

        # Handle code blocks
        if current_line.strip().startswith("```"):
            self.insert(f"\n{indent}")
            event.prevent_default()
            return True

        # Default indentation
        if indent:
            self.insert(f"\n{indent}")
            event.prevent_default()
            return True

        return False

    def _handle_improved_auto_pair(self, event: events.Key) -> bool:
        """Handle improved auto-pairing with context awareness."""
        bracket_quote_pair = {
            "(": ")",
            "{": "}",
            "[": "]",
            "<": ">",
            "`": "`",
            "*": "*",
            "_": "_",
            "~": "~",
        }

        if event.character not in bracket_quote_pair:
            return False

        cursor_row, cursor_col = self.cursor_location
        current_line = self._get_current_line()

        # Don't auto-pair in certain contexts
        if self._is_in_code_block() and event.character in ["*", "_", "~"]:
            return False

        # Handle special markdown cases
        if event.character in ["*", "_"]:
            # Check for double characters for bold/strong
            before_cursor = current_line[:cursor_col]
            if before_cursor.endswith(event.character):
                # User is typing ** or __, complete with closing pair
                self.insert(event.character + event.character)
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
                return True

        # Handle backticks for code blocks
        if event.character == "`":
            before_cursor = current_line[:cursor_col]
            if before_cursor.endswith("``"):
                # User is typing ```, complete code block
                self.insert("`\n\n```")
                self.move_cursor_relative(rows=-1)
                event.prevent_default()
                return True

        # Regular auto-pairing
        self.insert(event.character + bracket_quote_pair[event.character])
        self.move_cursor_relative(columns=-1)
        event.prevent_default()
        return True

    def action_duplicate_line(self) -> None:
        """Duplicate the current line."""
        cursor_row, cursor_col = self.cursor_location
        lines = self.text.split("\n")

        if cursor_row < len(lines):
            current_line = lines[cursor_row]
            # Insert the duplicated line below current line
            lines.insert(cursor_row + 1, current_line)
            self.text = "\n".join(lines)
            # Move cursor to the duplicated line
            self.cursor_location = (cursor_row + 1, cursor_col)

    def action_move_line_up(self) -> None:
        """Move the current line up."""
        cursor_row, cursor_col = self.cursor_location
        lines = self.text.split("\n")

        if cursor_row > 0 and cursor_row < len(lines):
            # Swap current line with the line above
            lines[cursor_row], lines[cursor_row - 1] = (
                lines[cursor_row - 1],
                lines[cursor_row],
            )
            self.text = "\n".join(lines)
            # Move cursor up with the line
            self.cursor_location = (cursor_row - 1, cursor_col)

    def action_move_line_down(self) -> None:
        """Move the current line down."""
        cursor_row, cursor_col = self.cursor_location
        lines = self.text.split("\n")

        if cursor_row < len(lines) - 1:
            # Swap current line with the line below
            lines[cursor_row], lines[cursor_row + 1] = (
                lines[cursor_row + 1],
                lines[cursor_row],
            )
            self.text = "\n".join(lines)
            # Move cursor down with the line
            self.cursor_location = (cursor_row + 1, cursor_col)

    def toggle_auto_indent(self) -> None:
        """Toggle auto-indent feature."""
        self.auto_indent_enabled = not self.auto_indent_enabled

    def _on_key(self, event: events.Key) -> None:
        """Handle key events for enhanced auto-completion and smart editing.

        Args:
            event (events.Key): The key event containing the character pressed.
        """
        # Handle auto-indentation first
        if self._handle_auto_indent(event):
            return

        # Handle smart quotes
        if self._handle_smart_quotes(event):
            return

        # Handle improved auto-pairing
        if self._handle_improved_auto_pair(event):
            return

        # Handle markdown headers
        if event.character == "#":
            self.insert("# ")
            event.prevent_default()
            return

        # Let parent handle other events
        super()._on_key(event)
