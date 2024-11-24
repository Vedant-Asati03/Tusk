from textual import events
from textual.widgets import TextArea

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
