import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from textual.app import App


class CacheManager:
    """Manages the caching of application settings and state."""

    def __init__(self, app: App):
        self.app = app
        self.cache_dir = Path.home() / ".tusk" / "cache"
        self.settings_path = self.cache_dir / "settings.json"
        self._ensure_cache_dir()
        # Create default settings file if it doesn't exist
        if not self.settings_path.exists():
            self.save_settings("global", self._get_default_settings())

    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings dictionary."""
        return {
            "cursor_location": (0, 0),
            "theme": "default",
            "input_width": 50,
            "show_preview": True,
            "last_directory": str(Path.home()),
            "recent_files": [],
        }

    def save_settings(self, file_path: str, settings: Dict[str, Any]) -> None:
        """Save file-specific settings to cache."""
        try:
            # Ensure the cache directory exists
            self._ensure_cache_dir()

            # Load existing settings or create new
            all_settings = {}
            if self.settings_path.exists():
                try:
                    with open(self.settings_path, "r", encoding="utf-8") as f:
                        all_settings = json.load(f)
                except json.JSONDecodeError:
                    self.app.notify(
                        "Settings file corrupted, creating new", severity="warning"
                    )

            # Update settings for this file
            all_settings[str(file_path)] = settings

            # Save all settings
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(all_settings, f, indent=2)

            self.app.notify("Settings saved successfully", severity="information")
        except Exception as e:
            self.app.notify(f"Failed to save settings: {e}", severity="error")
            raise

    def load_settings(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load settings for a specific file or global settings."""
        default_settings = self._get_default_settings()

        try:
            if not self.settings_path.exists():
                self.app.notify(
                    "No settings file found, using defaults", severity="information"
                )
                return default_settings

            with open(self.settings_path, "r", encoding="utf-8") as f:
                all_settings = json.load(f)

            if file_path:
                # Get file-specific settings or defaults
                file_settings = all_settings.get(str(file_path), {})
                return {**default_settings, **file_settings}
            else:
                # Get global settings or defaults
                global_settings = all_settings.get("global", {})
                return {**default_settings, **global_settings}

        except Exception as e:
            self.app.notify(f"Error loading settings: {e}", severity="error")
            return default_settings

    def add_recent_file(self, file_path: str, max_recent: int = 10) -> None:
        """Add a file to the recent files list.

        Args:
            file_path: Path to the file to add
            max_recent: Maximum number of recent files to store
        """
        if not file_path:
            return

        # Load global settings (use None to get global)
        global_settings = self.load_settings()

        recent_files = global_settings.get("recent_files", [])

        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to front of list
        recent_files.insert(0, file_path)

        # Trim list if needed
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]

        # Save back to global settings
        global_settings["recent_files"] = recent_files
        self.save_settings("global", global_settings)

    def save_cursor_position(self, file_path: str, position: Tuple[int, int]) -> None:
        """Save cursor position for a specific file.

        Args:
            file_path: Path to the file
            position: Tuple of (row, column) representing cursor position
        """
        if not file_path:
            return

        settings = self.load_settings(file_path)
        settings["cursor_location"] = position
        self.save_settings(file_path, settings)

    def get_cursor_position(self, file_path: str) -> Optional[Tuple[int, int]]:
        """Get saved cursor position for a file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (row, column) if found, None otherwise
        """
        if not file_path:
            return None

        settings = self.load_settings(file_path)
        return settings.get("cursor_location")
