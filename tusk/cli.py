import argparse
import sys
from pathlib import Path
from .app import Tusk

def main():
    parser = argparse.ArgumentParser(
        description="Tusk - A modern terminal-based Markdown editor"
    )
    parser.add_argument(
        "file", 
        nargs="?", 
        help="File to edit (optional)"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 0.1.0"
    )
    parser.add_argument(
        "--new", 
        action="store_true",
        help="Create a new file"
    )

    args = parser.parse_args()
    
    if args.new and not args.file:
        print("Error: --new requires a filename")
        sys.exit(1)

    file_path = None
    if args.file:
        file_path = Path(args.file)
        if args.new and file_path.exists():
            print(f"Error: File {file_path} already exists")
            sys.exit(1)
        elif not args.new and not file_path.exists():
            print(f"File {file_path} does not exist. Use --new to create it.")
            sys.exit(1)

    app = Tusk(file_path=file_path)
    app.run()

if __name__ == "__main__":
    main()
