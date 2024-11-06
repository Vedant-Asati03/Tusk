from datetime import datetime


class AutoSave:

    def __init__(self, autosave_path: str = "auto_save.md") -> None:
        self.autosave_path = autosave_path
        super().__init__()

    def autosave_content(self, content) -> None:
        """Save the content of the input box to a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.autosave_path, "w", encoding="utf-8") as file:
            file.write(f"<!-- Autosaved at {timestamp} -->\n")
            file.write(content)

        # self.log(f"Autosaved content at {timestamp} to {self.autosave_path}")
