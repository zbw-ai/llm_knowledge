from __future__ import annotations

from pathlib import Path
import re

from llm_kb.frontmatter import load_frontmatter


QUERY_TOKEN_RE = re.compile(r"[a-z0-9]+")


def lookup_entries(root: Path, query: str, limit: int = 5) -> list[dict]:
    registry_dir = root / "registry" / "entries"
    if not registry_dir.exists():
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scored: list[tuple[int, str, dict]] = []
    for path in sorted(registry_dir.glob("*.md")):
        metadata = _read_entry(path)
        score = _score_entry(metadata, query_terms)
        if score > 0:
            scored.append((score, str(metadata.get("id", "")), metadata))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [metadata for _, _, metadata in scored[:limit]]


def trace_entry(root: Path, entry_id: str) -> dict:
    path = root / "registry" / "entries" / f"{entry_id}.md"
    metadata = _read_entry(path)
    note_path = metadata.get("card_path") or str(root / "notes" / "atomic" / f"{entry_id}.md")
    source_paths = _coerce_list(metadata.get("source_paths"))
    traced = dict(metadata)
    traced["note_path"] = note_path
    traced["card_path"] = note_path
    traced["source_paths"] = source_paths
    return traced


def _read_entry(path: Path) -> dict:
    metadata, _ = load_frontmatter(path.read_text(encoding="utf-8"))
    return metadata


def _score_entry(metadata: dict, query_terms: list[str]) -> int:
    score = 0
    title = str(metadata.get("title", "")).lower()
    topics = " ".join(_coerce_list(metadata.get("topics"))).lower()
    tags = " ".join(_coerce_list(metadata.get("tags"))).lower()
    summary = str(metadata.get("summary", "")).lower()

    for term in query_terms:
        if term in title:
            score += 4
        if term in topics:
            score += 3
        if term in tags:
            score += 2
        if term in summary:
            score += 1
    return score


def _tokenize(text: str) -> list[str]:
    return QUERY_TOKEN_RE.findall(text.lower())


def _coerce_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value == "":
        return []
    return [str(value)]
