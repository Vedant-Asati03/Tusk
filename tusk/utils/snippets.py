import json
from typing import Dict, Optional, NamedTuple
from pathlib import Path


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
            "done": SnippetInfo("- [x] ", "Completed todo item")
        }
        self.custom_snippets: Dict[str, SnippetInfo] = {}
        self.config_path = Path.home() / '.config' / 'tusk' / 'snippets.json'
        self.load_custom_snippets()

    def load_custom_snippets(self) -> None:
        """Load custom snippets from JSON config file."""
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text())
                self.custom_snippets = {
                    k: SnippetInfo(v['content'], v['description'])
                    for k, v in data.items()
                }
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Error loading custom snippets: {e}")

    def save_custom_snippets(self) -> None:
        """Save custom snippets to JSON config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                k: {'content': v.content, 'description': v.description}
                for k, v in self.custom_snippets.items()
            }
            self.config_path.write_text(json.dumps(data, indent=2))
        except OSError as e:
            print(f"Error saving custom snippets: {e}")

    def add_custom_snippet(self, trigger: str, content: str, description: str = "") -> bool:
        """Add a new custom snippet."""
        if trigger in self.builtin_snippets:
            return False
        self.custom_snippets[trigger] = SnippetInfo(content, description)
        self.save_custom_snippets()
        return True

    def remove_custom_snippet(self, trigger: str) -> bool:
        """Remove a custom snippet."""
        if trigger in self.custom_snippets:
            del self.custom_snippets[trigger]
            self.save_custom_snippets()
            return True
        return False

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

    def get_all_triggers(self) -> list[str]:
        """Return list of all available snippet triggers."""
        return list(self.builtin_snippets.keys()) + list(self.custom_snippets.keys())

    def get_all_snippets(self) -> Dict[str, Dict[str, SnippetInfo]]:
        """Get all snippets organized by type."""
        return {
            'builtin': self.builtin_snippets,
            'custom': self.custom_snippets
        }

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