from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import shutil
from urllib.error import URLError
from urllib.request import Request, urlopen

from llm_kb.frontmatter import dump_frontmatter
from llm_kb.models import EntryMetadata
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
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    target_dir = root / TYPE_TO_SOURCE_DIR[content_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    source_copy_path = target_dir / f"{entry_id}{source_path.suffix.lower()}"
    shutil.copy2(source_path, source_copy_path)
    return _write_note_and_registry(
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
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    source_copy_path = root / "sources" / "snapshots" / f"{entry_id}.md"
    source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    source_copy_path.write_text(text, encoding="utf-8")
    return _write_note_and_registry(
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
) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    snapshot_text = fetch_url_text(url)
    source_copy_path = root / TYPE_TO_SOURCE_DIR[content_type] / f"{entry_id}.html"
    source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    source_copy_path.write_text(snapshot_text, encoding="utf-8")
    return _write_note_and_registry(
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


def _write_note_and_registry(
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
