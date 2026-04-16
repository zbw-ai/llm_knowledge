from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import shutil
from urllib.error import URLError
from urllib.request import Request, urlopen

from llm_kb.frontmatter import dump_frontmatter
from llm_kb.models import EntryMetadata
from llm_kb.review import create_pending_draft, should_require_review
from llm_kb.registry import update_aggregates
from llm_kb.slugify import make_entry_id

TYPE_TO_SOURCE_DIR = {
    "paper": "sources/papers",
    "blog": "sources/blogs",
    "social": "sources/social",
    "github": "sources/github",
    "doc": "sources/snapshots",
    "note": "sources/snapshots",
}


@dataclass
class IngestResult:
    entry_id: str
    note_path: Path
    registry_path: Path
    source_copy_path: Path
    mode: str = "finalized"
    draft_id: str | None = None
    draft_path: Path | None = None


def fetch_url_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "llm-kb/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
    except (URLError, OSError) as exc:
        raise RuntimeError(f"Failed to fetch URL snapshot for {url}: {exc}") from exc

    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def ingest_local_file(
    root: Path,
    source_path: Path,
    title: str,
    content_type: str,
    source_kind: str,
    topics: list[str],
    tags: list[str],
    review_mode: str = "auto",
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    source_copy_path = _copy_local_source(
        root=root,
        source_path=source_path,
        entry_id=entry_id,
        content_type=content_type,
        source_kind=source_kind,
        review_mode=review_mode,
    )
    if _should_use_review_mode(
        review_mode=review_mode,
        content_type=content_type,
        source_kind=source_kind,
        text_length=source_path.stat().st_size,
    ):
        return _write_pending_ingest(
            root=root,
            entry_id=entry_id,
            title=title,
            content_type=content_type,
            source_kind=source_kind,
            created_at=created_at,
            source_input=str(source_path.resolve()),
            source_copy_path=source_copy_path,
            topics=topics,
            tags=tags,
        )
    return _write_finalized_ingest(
        root=root,
        entry_id=entry_id,
        title=title,
        content_type=content_type,
        source_kind=source_kind,
        created_at=created_at,
        source_path=source_copy_path,
        topics=topics,
        tags=tags,
    )


def ingest_text(
    root: Path,
    text: str,
    title: str,
    content_type: str,
    source_kind: str,
    topics: list[str],
    tags: list[str],
    review_mode: str = "auto",
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    if _should_use_review_mode(
        review_mode=review_mode,
        content_type=content_type,
        source_kind=source_kind,
        text_length=len(text),
    ):
        source_copy_path = _write_pending_source_copy(
            root=root,
            entry_id=entry_id,
            suffix=".md",
            text=text,
        )
        return _write_pending_ingest(
            root=root,
            entry_id=entry_id,
            title=title,
            content_type=content_type,
            source_kind=source_kind,
            created_at=created_at,
            source_input="pasted text",
            source_copy_path=source_copy_path,
            topics=topics,
            tags=tags,
        )
    source_copy_path = root / "sources" / "snapshots" / f"{entry_id}.md"
    source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    source_copy_path.write_text(text, encoding="utf-8")
    return _write_finalized_ingest(
        root=root,
        entry_id=entry_id,
        title=title,
        content_type=content_type,
        source_kind=source_kind,
        created_at=created_at,
        source_path=source_copy_path,
        topics=topics,
        tags=tags,
    )


def ingest_url(
    root: Path,
    url: str,
    title: str,
    content_type: str,
    source_kind: str,
    topics: list[str],
    tags: list[str],
    review_mode: str = "auto",
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    snapshot_text = fetch_url_text(url)
    if _should_use_review_mode(
        review_mode=review_mode,
        content_type=content_type,
        source_kind=source_kind,
        text_length=len(snapshot_text),
    ):
        source_copy_path = _write_pending_source_copy(
            root=root,
            entry_id=entry_id,
            suffix=".html",
            text=snapshot_text,
        )
        return _write_pending_ingest(
            root=root,
            entry_id=entry_id,
            title=title,
            content_type=content_type,
            source_kind=source_kind,
            created_at=created_at,
            source_input=url,
            source_copy_path=source_copy_path,
            topics=topics,
            tags=tags,
        )
    source_copy_path = root / TYPE_TO_SOURCE_DIR[content_type] / f"{entry_id}.html"
    source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    source_copy_path.write_text(snapshot_text, encoding="utf-8")
    return _write_finalized_ingest(
        root=root,
        entry_id=entry_id,
        title=title,
        content_type=content_type,
        source_kind=source_kind,
        created_at=created_at,
        source_path=source_copy_path,
        topics=topics,
        tags=tags,
        source_url=url,
    )


def _should_use_review_mode(
    *,
    review_mode: str,
    content_type: str,
    source_kind: str,
    text_length: int,
) -> bool:
    if review_mode == "force":
        return True
    if review_mode == "off":
        return False
    if review_mode != "auto":
        raise ValueError(f"Unsupported review_mode: {review_mode}")
    return should_require_review(
        content_type=content_type,
        source_kind=source_kind,
        text_length=text_length,
        force_review=False,
    )


def _write_pending_source_copy(
    *,
    root: Path,
    entry_id: str,
    suffix: str,
    text: str,
) -> Path:
    source_copy_path = root / "inbox" / "pending" / "sources" / f"{entry_id}{suffix}"
    source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    source_copy_path.write_text(text, encoding="utf-8")
    return source_copy_path


def _copy_local_source(
    *,
    root: Path,
    source_path: Path,
    entry_id: str,
    content_type: str,
    source_kind: str,
    review_mode: str,
) -> Path:
    if review_mode == "force":
        target_dir = root / "inbox" / "pending" / "sources"
    elif review_mode == "off":
        target_dir = root / TYPE_TO_SOURCE_DIR[content_type]
    elif review_mode == "auto":
        target_dir = root / "inbox" / "pending" / "sources"
        if not should_require_review(
            content_type=content_type,
            source_kind=source_kind,
            text_length=source_path.stat().st_size,
            force_review=False,
        ):
            target_dir = root / TYPE_TO_SOURCE_DIR[content_type]
    else:
        raise ValueError(f"Unsupported review_mode: {review_mode}")
    target_dir.mkdir(parents=True, exist_ok=True)
    source_copy_path = target_dir / f"{entry_id}{source_path.suffix.lower()}"
    shutil.copy2(source_path, source_copy_path)
    return source_copy_path


def _write_finalized_ingest(
    root: Path,
    entry_id: str,
    title: str,
    content_type: str,
    source_kind: str,
    created_at: str,
    source_path: Path,
    topics: list[str],
    tags: list[str],
    source_url: str | None = None,
) -> IngestResult:
    note_path = root / "notes" / "atomic" / f"{entry_id}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path = root / "registry" / "entries" / f"{entry_id}.md"
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = EntryMetadata(
        id=entry_id,
        title=title,
        type=content_type,
        source_kind=source_kind,
        created_at=created_at,
        topics=topics,
        tags=tags,
        source_url=source_url,
        local_source_paths=[str(source_path.resolve())],
    )
    note_body = (
        "# Summary\n\n"
        "TBD\n\n"
        "# Core Claims\n\n"
        "- TBD\n\n"
        "# Evidence\n\n"
        "- TBD\n\n"
        "# Relevance\n\n"
        "TBD\n\n"
        "# My Thoughts\n\n"
        "TBD\n\n"
        "# Follow-ups\n\n"
        "- TBD\n"
    )
    note_path.write_text(dump_frontmatter(metadata.to_dict(), note_body), encoding="utf-8")

    registry_body = dump_frontmatter(
        {
            "id": entry_id,
            "title": title,
            "type": content_type,
            "topics": topics,
            "tags": tags,
            "source_kind": source_kind,
            "created_at": created_at,
            "card_path": str(note_path.resolve()),
            "source_paths": [str(source_path.resolve())],
            "source_url": source_url,
            "summary": "TBD",
        },
        "",
    )
    registry_path.write_text(registry_body, encoding="utf-8")
    update_aggregates(root, registry_path)

    return IngestResult(
        entry_id=entry_id,
        note_path=note_path,
        registry_path=registry_path,
        source_copy_path=source_path,
    )


def _write_pending_ingest(
    *,
    root: Path,
    entry_id: str,
    title: str,
    content_type: str,
    source_kind: str,
    created_at: str,
    source_input: str,
    source_copy_path: Path,
    topics: list[str],
    tags: list[str],
) -> IngestResult:
    draft = create_pending_draft(
        root=root,
        source_input=source_input,
        source_kind=source_kind,
        content_type=content_type,
        title=title,
        created_at=created_at,
        pending_source_paths=[source_copy_path],
        suggested_topics=topics,
        suggested_tags=tags,
        summary="TBD",
        core_claims=["TBD"],
        preserve_source=True,
    )
    note_path = root / "notes" / "atomic" / f"{entry_id}.md"
    registry_path = root / "registry" / "entries" / f"{entry_id}.md"
    return IngestResult(
        entry_id=entry_id,
        note_path=note_path,
        registry_path=registry_path,
        source_copy_path=source_copy_path,
        mode="pending_review",
        draft_id=draft.draft_id,
        draft_path=draft.draft_path,
    )
