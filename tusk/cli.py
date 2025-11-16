import argparse
import sys
from pathlib import Path

from tusk.app import Tusk
from tusk.utils.snippets import AutoSnippets


def list_snippets():
    snippets = AutoSnippets()
    print("Available Snippets:")
    for key, info in {**snippets.builtin_snippets, **snippets.custom_snippets}.items():
        print(f"{key}: {info.description}")


def main():
    parser = argparse.ArgumentParser(
        description="Tusk - A modern terminal-based Markdown editor"
    )
    parser.add_argument("file", nargs="?", help="File to edit (optional)")
    parser.add_argument(
        "--version", action="version", version="tusk-editor %(prog)s 0.1.1"
    )
    parser.add_argument("--new", action="store_true", help="Create a new file")
    parser.add_argument(
        "--snippets", action="store_true", help="List available snippets"
    )

    args = parser.parse_args()

    if args.new and not args.file:
        print("Error: --new requires a filename")
        sys.exit(1)

    if args.snippets:
        list_snippets()
        sys.exit(0)

    file_path: Path | None = None
    if args.file:
        file_path = Path(args.file)
        if args.new:
            if file_path.exists():
                print(f"Error: File {file_path} already exists")
                sys.exit(1)
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch(exist_ok=False)
            except OSError as exc:
                print(f"Error creating file {file_path}: {exc}")
                sys.exit(1)
        else:
            if not file_path.exists():
                print(f"File {file_path} does not exist. Use --new to create it.")
                sys.exit(1)

    app = Tusk(file_path=file_path)
    app.run()


if __name__ == "__main__":
    main()
