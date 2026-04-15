from dataclasses import dataclass
from pathlib import Path
import shutil

from llm_kb.frontmatter import dump_frontmatter, load_frontmatter
from llm_kb.models import EntryMetadata, PendingDraftMetadata
from llm_kb.registry import update_aggregates
from llm_kb.slugify import make_entry_id, slugify


REVIEW_TEXT_LENGTH_THRESHOLD = 5000


@dataclass
class PendingDraftResult:
    draft_id: str
    draft_path: Path
    metadata: PendingDraftMetadata


@dataclass
class ReviewDraftResult:
    draft_id: str
    draft_path: Path
    metadata: PendingDraftMetadata
    summary: str
    core_claims: list[str]
    body: str


@dataclass
class ConfirmDraftResult:
    draft_id: str
    draft_path: Path
    entry_id: str
    source_paths: list[Path]
    note_path: Path
    registry_path: Path


def should_require_review(
    *,
    content_type: str,
    source_kind: str,
    text_length: int,
    force_review: bool,
) -> bool:
    del source_kind
    if force_review:
        return True
    if content_type in {"paper", "github"}:
        return True
    return text_length > REVIEW_TEXT_LENGTH_THRESHOLD


def make_draft_id(*, created_at: str, content_type: str, title: str) -> str:
    return f"draft-{created_at}-{content_type}-{slugify(title)}"


def _draft_path(root: Path, draft_id: str) -> Path:
    root = Path(root).resolve()
    return root / "inbox" / "pending" / "drafts" / f"{draft_id}.md"


def _load_draft(root: Path, draft_id: str) -> tuple[Path, PendingDraftMetadata, str]:
    draft_path = _draft_path(root, draft_id)
    metadata, body = load_frontmatter(draft_path.read_text(encoding="utf-8"))
    return draft_path, PendingDraftMetadata(**metadata), body


def _save_draft(draft_path: Path, metadata: PendingDraftMetadata, body: str) -> None:
    draft_path.write_text(dump_frontmatter(metadata.to_dict(), body), encoding="utf-8")


def _ensure_pending(metadata: PendingDraftMetadata) -> None:
    if metadata.status == "confirmed":
        raise ValueError(f"Draft {metadata.draft_id} has already been confirmed")
    if metadata.status == "cancelled":
        raise ValueError(f"Draft {metadata.draft_id} has already been cancelled")
    if metadata.status != "pending_review":
        raise ValueError(
            f"Draft {metadata.draft_id} cannot be changed from status {metadata.status!r}"
        )


def _split_draft_body(body: str) -> tuple[str, list[str]]:
    summary_lines: list[str] = []
    core_claim_lines: list[str] = []
    current_section: str | None = None

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            current_section = stripped[2:].strip()
            continue
        if current_section == "Summary":
            summary_lines.append(line)
        elif current_section == "Core Claims":
            core_claim_lines.append(line)

    summary = "\n".join(summary_lines).strip()
    core_claims = [
        line.strip()[2:].strip()
        for line in core_claim_lines
        if line.strip().startswith("- ")
    ]
    if not core_claims:
        core_claims = [line.strip() for line in core_claim_lines if line.strip()]
    return summary, core_claims


def _build_draft_body(summary: str, core_claims: list[str]) -> str:
    lines = [
        "# Summary",
        "",
        summary.strip(),
        "",
        "# Core Claims",
        "",
    ]
    if core_claims:
        lines.extend(f"- {claim}" for claim in core_claims)
    else:
        lines.append("- TBD")
    lines.extend(
        [
            "",
            "# Review Actions",
            "",
            "- confirm",
            "- regenerate_summary",
            "- update_tags",
            "- change_type",
            "- cancel",
            "",
        ]
    )
    return "\n".join(lines)


def _build_atomic_note_body(summary: str, core_claims: list[str], source_paths: list[Path]) -> str:
    lines = [
        "# Summary",
        "",
        summary.strip() or "TBD",
        "",
        "# Core Claims",
        "",
    ]
    if core_claims:
        lines.extend(f"- {claim}" for claim in core_claims)
    else:
        lines.append("- TBD")
    lines.extend(
        [
            "",
            "# Evidence",
            "",
        ]
    )
    if source_paths:
        lines.extend(f"- {path}" for path in source_paths)
    else:
        lines.append("- TBD")
    lines.extend(
        [
            "",
            "# Relevance",
            "",
            "Confirmed from a pending draft.",
            "",
            "# My Thoughts",
            "",
            "TBD",
            "",
            "# Follow-ups",
            "",
            "- TBD",
            "",
        ]
    )
    return "\n".join(lines)


def _source_subdir(content_type: str) -> str:
    mapping = {
        "paper": "papers",
        "blog": "blogs",
        "social": "social",
        "github": "github",
    }
    return mapping.get(content_type, "snapshots")


def _resolve_path(root: Path, path_text: str) -> Path:
    candidate = Path(path_text)
    if candidate.is_absolute():
        return candidate
    return Path(root).resolve() / candidate


def _regenerate_body(metadata: PendingDraftMetadata) -> tuple[str, list[str]]:
    summary = f"Regenerated summary for {metadata.title}."
    core_claims = [
        f"Content type: {metadata.content_type}.",
        f"Suggested topics: {', '.join(metadata.suggested_topics) or 'none'}.",
        f"Suggested tags: {', '.join(metadata.suggested_tags) or 'none'}.",
    ]
    return summary, core_claims


def create_pending_draft(
    *,
    root: Path,
    source_input: str,
    source_kind: str,
    content_type: str,
    title: str,
    created_at: str,
    pending_source_paths: list[Path],
    suggested_topics: list[str],
    suggested_tags: list[str],
    summary: str,
    core_claims: list[str],
    preserve_source: bool,
) -> PendingDraftResult:
    root = Path(root).resolve()
    draft_id = make_draft_id(
        created_at=created_at,
        content_type=content_type,
        title=title,
    )
    entry_id = make_entry_id(content_type, created_at, title)
    proposed_note_path = root / "notes" / "atomic" / f"{entry_id}.md"
    proposed_registry_path = root / "registry" / "entries" / f"{entry_id}.md"
    metadata = PendingDraftMetadata(
        draft_id=draft_id,
        status="pending_review",
        source_input=source_input,
        source_kind=source_kind,
        content_type=content_type,
        title=title,
        created_at=created_at,
        pending_source_paths=[str(path) for path in pending_source_paths],
        suggested_topics=suggested_topics,
        suggested_tags=suggested_tags,
        proposed_entry_id=entry_id,
        proposed_note_path=str(proposed_note_path),
        proposed_registry_path=str(proposed_registry_path),
        preserve_source=preserve_source,
    )
    draft_path = _draft_path(root, draft_id)
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(
        dump_frontmatter(metadata.to_dict(), _build_draft_body(summary, core_claims)),
        encoding="utf-8",
    )
    return PendingDraftResult(draft_id=draft_id, draft_path=draft_path, metadata=metadata)


def review_draft(root: Path, draft_id: str) -> ReviewDraftResult:
    draft_path, metadata, body = _load_draft(root, draft_id)
    summary, core_claims = _split_draft_body(body)
    return ReviewDraftResult(
        draft_id=draft_id,
        draft_path=draft_path,
        metadata=metadata,
        summary=summary,
        core_claims=core_claims,
        body=body,
    )


def confirm_draft(root: Path, draft_id: str) -> ConfirmDraftResult:
    root = Path(root).resolve()
    draft_path, metadata, body = _load_draft(root, draft_id)
    _ensure_pending(metadata)

    entry_id = metadata.proposed_entry_id or make_entry_id(
        metadata.content_type,
        metadata.created_at,
        metadata.title,
    )
    summary, core_claims = _split_draft_body(body)
    source_paths: list[Path] = []
    for pending_source in metadata.pending_source_paths:
        pending_path = _resolve_path(root, pending_source)
        final_path = root / "sources" / _source_subdir(metadata.content_type) / pending_path.name
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if metadata.preserve_source:
            shutil.copy2(pending_path, final_path)
        else:
            shutil.move(str(pending_path), final_path)
        source_paths.append(final_path.resolve())

    note_path = root / "notes" / "atomic" / f"{entry_id}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_metadata = EntryMetadata(
        id=entry_id,
        title=metadata.title,
        type=metadata.content_type,
        source_kind=metadata.source_kind,
        created_at=metadata.created_at,
        topics=metadata.suggested_topics,
        tags=metadata.suggested_tags,
        source_url=(
            metadata.source_input
            if metadata.source_input.startswith(("http://", "https://"))
            else None
        ),
        local_source_paths=[str(path) for path in source_paths],
    )
    note_path.write_text(
        dump_frontmatter(
            note_metadata.to_dict(),
            _build_atomic_note_body(summary, core_claims, source_paths),
        ),
        encoding="utf-8",
    )

    registry_path = root / "registry" / "entries" / f"{entry_id}.md"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_metadata = {
        "id": entry_id,
        "title": metadata.title,
        "type": metadata.content_type,
        "source_kind": metadata.source_kind,
        "created_at": metadata.created_at,
        "topics": metadata.suggested_topics,
        "tags": metadata.suggested_tags,
        "card_path": str(note_path.resolve()),
        "source_paths": [str(path) for path in source_paths],
        "source_url": (
            metadata.source_input
            if metadata.source_input.startswith(("http://", "https://"))
            else None
        ),
        "summary": summary or "TBD",
    }
    registry_path.write_text(
        dump_frontmatter(registry_metadata, ""),
        encoding="utf-8",
    )
    update_aggregates(root, registry_path)

    metadata.status = "confirmed"
    metadata.proposed_entry_id = entry_id
    metadata.proposed_note_path = str(note_path.resolve())
    metadata.proposed_registry_path = str(registry_path.resolve())
    _save_draft(draft_path, metadata, body)

    return ConfirmDraftResult(
        draft_id=draft_id,
        draft_path=draft_path,
        entry_id=entry_id,
        source_paths=source_paths,
        note_path=note_path,
        registry_path=registry_path,
    )


def cancel_draft(root: Path, draft_id: str) -> PendingDraftMetadata:
    draft_path, metadata, body = _load_draft(root, draft_id)
    _ensure_pending(metadata)
    metadata.status = "cancelled"
    _save_draft(draft_path, metadata, body)
    return metadata


def revise_draft(
    root: Path,
    draft_id: str,
    *,
    content_type: str | None = None,
    topics: list[str] | None = None,
    tags: list[str] | None = None,
    regenerate_summary: bool = False,
) -> PendingDraftMetadata:
    root = Path(root).resolve()
    draft_path, metadata, body = _load_draft(root, draft_id)
    _ensure_pending(metadata)

    if content_type:
        metadata.content_type = content_type
        entry_id = make_entry_id(metadata.content_type, metadata.created_at, metadata.title)
        metadata.proposed_entry_id = entry_id
        metadata.proposed_note_path = str(
            (root / "notes" / "atomic" / f"{entry_id}.md").resolve()
        )
        metadata.proposed_registry_path = str(
            (root / "registry" / "entries" / f"{entry_id}.md").resolve()
        )

    if topics is not None:
        metadata.suggested_topics = topics
    if tags is not None:
        metadata.suggested_tags = tags

    if regenerate_summary:
        summary, core_claims = _regenerate_body(metadata)
        body = _build_draft_body(summary, core_claims)

    _save_draft(draft_path, metadata, body)
    return metadata
