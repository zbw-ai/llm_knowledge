from __future__ import annotations

from pathlib import Path

from llm_kb.frontmatter import load_frontmatter


def update_aggregates(root: Path, entry_registry_path: Path) -> None:
    metadata, _ = load_frontmatter(entry_registry_path.read_text(encoding="utf-8"))
    _write_topic_files(root, metadata)
    _write_tag_files(root, metadata)
    _write_source_file(root, metadata)
    _write_timeline_file(root, metadata)


def _write_topic_files(root: Path, metadata: dict) -> None:
    for topic in _coerce_list(metadata.get("topics")):
        path = root / "registry" / "topics" / f"{topic}.md"
        _append_link_if_missing(path, _entry_line(metadata), f"# Topic: {topic}\n\n")


def _write_tag_files(root: Path, metadata: dict) -> None:
    for tag in _coerce_list(metadata.get("tags")):
        path = root / "registry" / "tags" / f"{tag}.md"
        _append_link_if_missing(path, _entry_line(metadata), f"# Tag: {tag}\n\n")


def _write_source_file(root: Path, metadata: dict) -> None:
    source_kind = metadata.get("source_kind")
    if not source_kind:
        return
    path = root / "registry" / "sources" / f"{source_kind}.md"
    _append_link_if_missing(path, _entry_line(metadata), f"# Source: {source_kind}\n\n")


def _write_timeline_file(root: Path, metadata: dict) -> None:
    created_at = metadata.get("created_at", "")
    year = str(created_at).split("-", 1)[0] if created_at else "unknown"
    path = root / "registry" / "timelines" / f"{year}.md"
    _append_link_if_missing(path, _entry_line(metadata), f"# Timeline: {year}\n\n")


def _entry_line(metadata: dict) -> str:
    title = metadata.get("title", "Untitled")
    entry_id = metadata.get("id", "unknown")
    card_path = metadata.get("card_path", "")
    return f"- [{title}]({card_path}) ({entry_id})"


def _append_link_if_missing(path: Path, line: str, header: str) -> None:
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if line in content:
            return
    else:
        content = header
    path.write_text(f"{content.rstrip()}\n{line}\n", encoding="utf-8")


def _coerce_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value == "":
        return []
    return [str(value)]
