from datetime import datetime
import logging
from pathlib import Path

class AutoSave:
    """Handles automatic saving of editor content to prevent data loss.
    
    Features:
    - Periodic auto-saving
    - Timestamp recording
    - Error logging
    - Last save recovery
    """

    def __init__(self, autosave_path: str = "auto_save.md") -> None:
        self.autosave_path = autosave_path
        
        log_dir = Path.home() / ".tusk" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "tusk.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("tusk")

    def autosave_content(self, content: str) -> None:
        """Save the current editor content with timestamp.
        
        Args:
            content (str): The text content to be saved.
            
        The save operation includes a timestamp comment and logs the save event.
        Errors during save are logged but don't interrupt the application.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(self.autosave_path, "w", encoding="utf-8") as file:
                file.write(f"<!-- Autosaved at {timestamp} -->\n")
                file.write(content)
            self.logger.info(f"Autosaved content at {timestamp} to {self.autosave_path}")
        except Exception as e:
            self.logger.error(f"Failed to autosave: {str(e)}")

    def load_last_save(self) -> str:
        """Retrieve the most recently saved content.
        
        Returns:
            str: The content of the last save file or empty string if no save exists.
        """
        try:
            with open(self.autosave_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return ""
