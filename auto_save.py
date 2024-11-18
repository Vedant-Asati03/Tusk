from datetime import datetime
import logging

class AutoSave:
    def __init__(self, autosave_path: str = "auto_save.md") -> None:
        self.autosave_path = autosave_path
        self.logger = logging.getLogger("tusk")

    def autosave_content(self, content: str) -> None:
        """Save the content of the input box to a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(self.autosave_path, "w", encoding="utf-8") as file:
                file.write(f"<!-- Autosaved at {timestamp} -->\n")
                file.write(content)
            self.logger.info(f"Autosaved content at {timestamp} to {self.autosave_path}")
        except Exception as e:
            self.logger.error(f"Failed to autosave: {str(e)}")

    def load_last_save(self) -> str:
        """Load the last saved content."""
        try:
            with open(self.autosave_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return ""
