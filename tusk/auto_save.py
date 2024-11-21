import logging
from pathlib import Path

class AutoSave:
    """Handles automatic saving of editor content to prevent data loss."""

    def __init__(self, file_path: Path | None = None) -> None:
        # Configure logging
        log_dir = Path.home() / ".tusk" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "tusk.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        self.logger = logging.getLogger("tusk")
        self.file_path = file_path
        self.logger.info("AutoSave initialized")

    def autosave_content(self, content: str) -> None:
        """Save the current editor content."""
        if not self.file_path:
            return
            
        try:
            self.file_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Autosaved content to {self.file_path}")
        except Exception as e:
            self.logger.error(f"Failed to autosave: {str(e)}")

    def load_last_save(self) -> str:
        """Retrieve the content from the file."""
        if not self.file_path:
            return ""
            
        try:
            return self.file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            return ""
