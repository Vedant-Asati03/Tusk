import json
from pathlib import Path
from typing import Any, Dict, Optional

from textual.app import App


CACHE_DIR = Path.home() / ".tusk" / "cache"
SETTINGS_FILE = CACHE_DIR / "settings.json"


class CacheManager:
    """Manages basic application settings."""

    def __init__(self, app: App):
        self.app = app
        self._ensure_cache_dir()

        if not SETTINGS_FILE.exists():
            self.save_settings("global", self._get_default_settings())

    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings dictionary."""
        default_settings = {
            "theme": "default",
            "input_width": 50,
            "show_preview": True,
        }

        return default_settings

    def save_settings(self, file_path: str, settings: Dict[str, Any]) -> None:
        """Save file-specific settings to cache."""
        try:
            # Ensure the cache directory exists
            self._ensure_cache_dir()

            # Load existing settings or create new
            all_settings = {}
            if SETTINGS_FILE.exists():
                try:
                    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                        all_settings = json.load(f)
                except json.JSONDecodeError:
                    self.app.notify(
                        "Settings file corrupted, creating new", severity="warning"
                    )

            # Update settings for this file
            all_settings[file_path] = settings

            # Save all settings
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(all_settings, f, indent=2)

            self.app.notify("Settings saved successfully", severity="information")
        except Exception as e:
            self.app.notify(f"Failed to save settings: {e}", severity="error")
            raise

    def load_settings(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load settings for a specific file or global settings."""
        default_settings = self._get_default_settings()

        try:
            if not SETTINGS_FILE.exists():
                self.app.notify(
                    "No settings file found, using defaults", severity="information"
                )
                return default_settings

            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
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
