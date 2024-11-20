from textual.command import Command, CommandPalette
from typing import Iterable

class TuskCommandPalette(CommandPalette):
    """A command palette for quick access to markdown editing actions.
    
    Provides commands for:
    - Text formatting (bold, italic)
    - Structure (headings, code blocks)
    - Links and references
    - View management (preview toggle)
    - File operations (save)
    """
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
        for command_id, title in self.COMMANDS.items():
            yield Command(command_id, title, key=None)
