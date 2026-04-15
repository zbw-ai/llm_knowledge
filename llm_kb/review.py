from dataclasses import dataclass
from pathlib import Path

from llm_kb.frontmatter import dump_frontmatter
from llm_kb.models import PendingDraftMetadata
from llm_kb.slugify import make_entry_id, slugify


REVIEW_TEXT_LENGTH_THRESHOLD = 5000


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


@dataclass
class PendingDraftResult:
    draft_id: str
    draft_path: Path
    metadata: PendingDraftMetadata


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
    claims = core_claims or ["TBD"]
    body = "\n".join(
        [
            "# Summary",
            "",
            summary,
            "",
            "# Core Claims",
            "",
            *[f"- {claim}" for claim in claims],
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
    draft_path = root / "inbox" / "pending" / "drafts" / f"{draft_id}.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(
        dump_frontmatter(metadata.to_dict(), body),
        encoding="utf-8",
    )
    return PendingDraftResult(draft_id=draft_id, draft_path=draft_path, metadata=metadata)
