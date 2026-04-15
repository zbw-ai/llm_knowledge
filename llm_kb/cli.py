import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser(prog="llm-kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "init":
        initialize_workspace(args.root)
        return 0
    return 1

