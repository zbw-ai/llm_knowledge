import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.ingest import ingest_local_file, ingest_text, ingest_url
from llm_kb.review import cancel_draft, confirm_draft, review_draft, revise_draft
from llm_kb.retrieve import lookup_entries, trace_entry


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m llm_kb")
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
    ingest_file_parser.add_argument(
        "--review",
        action="store_true",
        help="强制进入确认模式",
    )

    ingest_text_parser = subparsers.add_parser("ingest-text")
    ingest_text_parser.add_argument("--root", type=Path, default=Path.cwd())
    ingest_text_parser.add_argument("--text", required=True)
    ingest_text_parser.add_argument("--title", required=True)
    ingest_text_parser.add_argument("--type", dest="content_type", required=True)
    ingest_text_parser.add_argument("--source-kind", required=True)
    ingest_text_parser.add_argument("--topic", action="append", default=[])
    ingest_text_parser.add_argument("--tag", action="append", default=[])
    ingest_text_parser.add_argument(
        "--review",
        action="store_true",
        help="强制进入确认模式",
    )

    ingest_url_parser = subparsers.add_parser("ingest-url")
    ingest_url_parser.add_argument("--root", type=Path, default=Path.cwd())
    ingest_url_parser.add_argument("--url", required=True)
    ingest_url_parser.add_argument("--title", required=True)
    ingest_url_parser.add_argument("--type", dest="content_type", required=True)
    ingest_url_parser.add_argument("--source-kind", required=True)
    ingest_url_parser.add_argument("--topic", action="append", default=[])
    ingest_url_parser.add_argument("--tag", action="append", default=[])
    ingest_url_parser.add_argument(
        "--review",
        action="store_true",
        help="强制进入确认模式",
    )

    review_parser = subparsers.add_parser("review-draft")
    review_parser.add_argument("--root", type=Path, default=Path.cwd())
    review_parser.add_argument("--id", required=True)

    confirm_parser = subparsers.add_parser("confirm-draft")
    confirm_parser.add_argument("--root", type=Path, default=Path.cwd())
    confirm_parser.add_argument("--id", required=True)

    revise_parser = subparsers.add_parser("revise-draft")
    revise_parser.add_argument("--root", type=Path, default=Path.cwd())
    revise_parser.add_argument("--id", required=True)
    revise_parser.add_argument("--regenerate-summary", action="store_true")
    revise_parser.add_argument("--type")
    revise_parser.add_argument("--topic", action="append")
    revise_parser.add_argument("--tag", action="append")

    cancel_parser = subparsers.add_parser("cancel-draft")
    cancel_parser.add_argument("--root", type=Path, default=Path.cwd())
    cancel_parser.add_argument("--id", required=True)

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
        result = ingest_local_file(
            root=args.root,
            source_path=args.source,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
            review_mode="force" if args.review else "auto",
        )
        _maybe_print_pending_ingest_result(result)
        return 0
    if args.command == "ingest-text":
        result = ingest_text(
            root=args.root,
            text=args.text,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
            review_mode="force" if args.review else "auto",
        )
        _maybe_print_pending_ingest_result(result)
        return 0
    if args.command == "ingest-url":
        result = ingest_url(
            root=args.root,
            url=args.url,
            title=args.title,
            content_type=args.content_type,
            source_kind=args.source_kind,
            topics=args.topic,
            tags=args.tag,
            review_mode="force" if args.review else "auto",
        )
        _maybe_print_pending_ingest_result(result)
        return 0
    if args.command == "review-draft":
        _print_review_result(review_draft(args.root, args.id))
        return 0
    if args.command == "confirm-draft":
        _print_confirm_result(confirm_draft(args.root, args.id))
        return 0
    if args.command == "revise-draft":
        _print_revise_result(
            revise_draft(
                args.root,
                args.id,
                content_type=args.type,
                topics=args.topic,
                tags=args.tag,
                regenerate_summary=args.regenerate_summary,
            )
        )
        return 0
    if args.command == "cancel-draft":
        _print_cancel_result(cancel_draft(args.root, args.id))
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


def _print_review_result(result) -> None:
    print(f"draft_id: {result.draft_id}")
    print(f"status: {result.metadata.status}")
    print(f"title: {result.metadata.title}")
    print(f"source_input: {result.metadata.source_input}")
    print(f"content_type: {result.metadata.content_type}")
    print(f"suggested_topics: {', '.join(result.metadata.suggested_topics) or '-'}")
    print(f"suggested_tags: {', '.join(result.metadata.suggested_tags) or '-'}")
    print(f"proposed_entry_id: {result.metadata.proposed_entry_id}")
    print(f"proposed_note_path: {result.metadata.proposed_note_path}")
    print(f"proposed_registry_path: {result.metadata.proposed_registry_path}")
    print("summary:")
    print(result.summary or "-")
    print("core_claims:")
    for claim in result.core_claims or ["-"]:
        print(f"- {claim}")


def _print_confirm_result(result) -> None:
    print(f"entry_id: {result.entry_id}")
    print(f"note_path: {result.note_path}")
    print(f"registry_path: {result.registry_path}")
    print("source_paths:")
    for path in result.source_paths or [Path("-")]:
        print(f"- {path}")


def _print_revise_result(result) -> None:
    print(f"draft_id: {result.draft_id}")
    print(f"status: {result.status}")
    print(f"content_type: {result.content_type}")
    print(f"proposed_entry_id: {result.proposed_entry_id}")
    print(f"proposed_note_path: {result.proposed_note_path}")
    print(f"proposed_registry_path: {result.proposed_registry_path}")


def _print_cancel_result(result) -> None:
    print(f"draft_id: {result.draft_id}")
    print(f"status: {result.status}")


def _maybe_print_pending_ingest_result(result) -> None:
    if getattr(result, "mode", "") != "pending_review":
        return
    print(f"draft_id: {result.draft_id}")
    print(f"draft_path: {result.draft_path}")
    print(
        "next: 先运行 `python -m llm_kb review-draft --root <root> --id "
        f"{result.draft_id}`，再根据需要使用 `confirm-draft`、`revise-draft` 或 `cancel-draft`。"
    )
