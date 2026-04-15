import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.ingest import ingest_local_file, ingest_text, ingest_url


def main() -> int:
    parser = argparse.ArgumentParser(prog="llm-kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", type=Path, default=Path.cwd())

    ingest_file_parser = subparsers.add_parser("ingest-file")
    ingest_file_parser.add_argument("--root", type=Path, default=Path.cwd())
    ingest_file_parser.add_argument("--source", type=Path, required=True)
    ingest_file_parser.add_argument("--title", required=True)
    ingest_file_parser.add_argument("--type", dest="content_type", required=True)
    ingest_file_parser.add_argument("--source-kind", required=True)
    ingest_file_parser.add_argument("--topic", action="append", default=[])
    ingest_file_parser.add_argument("--tag", action="append", default=[])

    ingest_text_parser = subparsers.add_parser("ingest-text")
    ingest_text_parser.add_argument("--root", type=Path, default=Path.cwd())
    ingest_text_parser.add_argument("--text", required=True)
    ingest_text_parser.add_argument("--title", required=True)
    ingest_text_parser.add_argument("--type", dest="content_type", required=True)
    ingest_text_parser.add_argument("--source-kind", required=True)
    ingest_text_parser.add_argument("--topic", action="append", default=[])
    ingest_text_parser.add_argument("--tag", action="append", default=[])

    ingest_url_parser = subparsers.add_parser("ingest-url")
    ingest_url_parser.add_argument("--root", type=Path, default=Path.cwd())
    ingest_url_parser.add_argument("--url", required=True)
    ingest_url_parser.add_argument("--title", required=True)
    ingest_url_parser.add_argument("--type", dest="content_type", required=True)
    ingest_url_parser.add_argument("--source-kind", required=True)
    ingest_url_parser.add_argument("--topic", action="append", default=[])
    ingest_url_parser.add_argument("--tag", action="append", default=[])

    args = parser.parse_args()
    if args.command == "init":
        initialize_workspace(args.root)
        return 0
    if args.command == "ingest-file":
        ingest_local_file(
            root=args.root,
            source_path=args.source,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
        )
        return 0
    if args.command == "ingest-text":
        ingest_text(
            root=args.root,
            text=args.text,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
        )
        return 0
    if args.command == "ingest-url":
        ingest_url(
            root=args.root,
            url=args.url,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
        )
        return 0
    return 1
