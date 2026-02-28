import argparse
import os
import sys
from pathlib import Path

from tusk.app import Tusk


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
        "--log-stream",
        action="store_true",
        help="Enable TCP log streaming for debugging",
    )
    parser.add_argument(
        "--log-host",
        default=os.environ.get("TUSK_LOG_HOST", "127.0.0.1"),
        help="Host/interface for the log stream (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--log-port",
        type=int,
        default=int(os.environ.get("TUSK_LOG_PORT", "8765")),
        help="Port for the log stream (use 0 for ephemeral)",
    )

    args = parser.parse_args()

    if args.new and not args.file:
        print("Error: --new requires a filename")
        sys.exit(1)

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

    log_port = args.log_port if args.log_stream else None
    app = Tusk(
        file_path=file_path,
        log_stream=args.log_stream,
        log_host=args.log_host,
        log_port=log_port,
    )
    app.run()


if __name__ == "__main__":
    main()
