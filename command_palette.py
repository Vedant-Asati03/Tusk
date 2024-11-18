from textual.command import Command, CommandPalette
from typing import Iterable

class TuskCommandPalette(CommandPalette):
    """Custom command palette for Tusk."""

    COMMANDS = {
        "insert_heading": "Insert Heading",
        "insert_bold": "Insert Bold Text",
        "insert_italic": "Insert Italic Text",
        "insert_code": "Insert Code Block",
        "insert_link": "Insert Link",
        "save_file": "Save File",
        "toggle_preview": "Toggle Preview",
    }

    def get_commands(self) -> Iterable[Command]:
        """Get all available commands."""
        for command_id, title in self.COMMANDS.items():
            yield Command(command_id, title, key=None)
