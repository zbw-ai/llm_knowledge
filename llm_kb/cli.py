import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.ingest import ingest_local_file, ingest_text, ingest_url
from llm_kb.retrieve import lookup_entries, trace_entry


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

    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument("--root", type=Path, default=Path.cwd())
    ask_parser.add_argument("--query", required=True)
    ask_parser.add_argument("--limit", type=int, default=5)

    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("--root", type=Path, default=Path.cwd())
    trace_parser.add_argument("--id", required=True)

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
    if args.command == "ask":
        _print_lookup_results(lookup_entries(args.root, args.query, limit=args.limit))
        return 0
    if args.command == "trace":
        _print_trace_result(trace_entry(args.root, args.id))
        return 0
    return 1


def _print_lookup_results(results: list[dict]) -> None:
    for index, item in enumerate(results):
        if index:
            print()
        print(f"id: {item.get('id', '')}")
        print(f"title: {item.get('title', '')}")
        print(f"summary: {item.get('summary', '')}")
        print(f"card_path: {item.get('card_path', '')}")


def _print_trace_result(result: dict) -> None:
    print(f"card_path: {result.get('card_path', '')}")
    print(f"source_paths: {result.get('source_paths', [])}")
