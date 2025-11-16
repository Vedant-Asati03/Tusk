import json
from pathlib import Path
from typing import Dict, NamedTuple, Optional

CONFIG_DIR = Path.home() / ".config" / "tusk"
CONFIG_PATH = CONFIG_DIR / "snippets.json"


class SnippetInfo(NamedTuple):
    content: str
    description: str


class AutoSnippets:
    """Handles markdown snippet expansion with advanced features."""

    def __init__(self):
        self.builtin_snippets: Dict[str, SnippetInfo] = {
            # Headers
            "h1": SnippetInfo("# ", "Level 1 heading"),
            "h2": SnippetInfo("## ", "Level 2 heading"),
            "h3": SnippetInfo("### ", "Level 3 heading"),
            # Formatting
            "bold": SnippetInfo("****", "Bold text"),
            "italic": SnippetInfo("**", "Italic text"),
            "strike": SnippetInfo("~~~~", "Strikethrough text"),
            "code": SnippetInfo("``", "Inline code"),
            "codeblock": SnippetInfo("```\n\n```", "Code block"),
            # Lists
            "ul": SnippetInfo("- ", "Unordered list item"),
            "ol": SnippetInfo("1. ", "Ordered list item"),
            # Links and Images
            "link": SnippetInfo("[]()", "Markdown link"),
            "img": SnippetInfo("![]()", "Image"),
            # Other
            "quote": SnippetInfo("> ", "Blockquote"),
            "hr": SnippetInfo("---", "Horizontal rule"),
            "todo": SnippetInfo("- [ ] ", "Todo item"),
            "done": SnippetInfo("- [x] ", "Completed todo item"),
        }
        self.custom_snippets: Dict[str, SnippetInfo] = {}
        self.load_custom_snippets()

    def load_custom_snippets(self) -> None:
        """Load custom snippets from JSON config file."""
        try:
            if CONFIG_PATH.exists():
                data = json.loads(CONFIG_PATH.read_text())
                self.custom_snippets = {
                    k: SnippetInfo(v["content"], v["description"])
                    for k, v in data.items()
                }
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Error loading custom snippets: {e}")

    def save_custom_snippets(self) -> None:
        """Save custom snippets to JSON config file."""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                k: {"content": v.content, "description": v.description}
                for k, v in self.custom_snippets.items()
            }
            CONFIG_PATH.write_text(json.dumps(data, indent=2))
        except OSError as e:
            print(f"Error saving custom snippets: {e}")

    def get_snippet_info(self, trigger: str) -> Optional[SnippetInfo]:
        """Get snippet info for a trigger."""
        return self.custom_snippets.get(trigger) or self.builtin_snippets.get(trigger)

    def expand_snippet(self, trigger: str) -> Optional[str]:
        """Expand a snippet trigger into its content.

        Args:
            trigger: The snippet trigger text

        Returns:
            The expanded snippet content or None if no match
        """
        info = self.get_snippet_info(trigger)
        if not info:
            return None

        if callable(info.content):
            return info.content()
        return info.content

    def list_snippets(self) -> str:
        """Get formatted string of all available snippets."""
        output = []

        output.append("Built-in snippets:")
        for trigger, info in sorted(self.builtin_snippets.items()):
            content = info.content() if callable(info.content) else info.content
            output.append(f"  {trigger}: {info.description} -> {content}")

        if self.custom_snippets:
            output.append("\nCustom snippets:")
            for trigger, info in sorted(self.custom_snippets.items()):
                output.append(f"  {trigger}: {info.description} -> {info.content}")

        return "\n".join(output)
