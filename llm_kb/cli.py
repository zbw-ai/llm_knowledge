import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.review import cancel_draft, confirm_draft, review_draft, revise_draft


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", type=Path, default=Path.cwd())

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

    return parser


def _print_review(result) -> None:
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


def _print_confirm(result) -> None:
    print(f"entry_id: {result.entry_id}")
    print(f"note_path: {result.note_path}")
    print(f"registry_path: {result.registry_path}")
    print("source_paths:")
    for path in result.source_paths or [Path("-")]:
        print(f"- {path}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        initialize_workspace(args.root)
        return 0
    if args.command == "review-draft":
        _print_review(review_draft(args.root, args.id))
        return 0
    if args.command == "confirm-draft":
        _print_confirm(confirm_draft(args.root, args.id))
        return 0
    if args.command == "revise-draft":
        result = revise_draft(
            args.root,
            args.id,
            content_type=args.type,
            topics=args.topic,
            tags=args.tag,
            regenerate_summary=args.regenerate_summary,
        )
        print(f"draft_id: {result.draft_id}")
        print(f"status: {result.status}")
        print(f"content_type: {result.content_type}")
        print(f"proposed_entry_id: {result.proposed_entry_id}")
        print(f"proposed_note_path: {result.proposed_note_path}")
        print(f"proposed_registry_path: {result.proposed_registry_path}")
        return 0
    if args.command == "cancel-draft":
        result = cancel_draft(args.root, args.id)
        print(f"draft_id: {result.draft_id}")
        print(f"status: {result.status}")
        return 0
    return 1
