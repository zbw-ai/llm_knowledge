from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.retrieve import lookup_entries, trace_entry


def _write_registry_entry(root: Path, entry_id: str, **metadata: object) -> None:
    fields = {
        "id": entry_id,
        "title": "Unrelated",
        "type": "paper",
        "topics": [],
        "tags": [],
        "source_kind": "arxiv",
        "created_at": "2026-04-15",
        "card_path": f"/tmp/{entry_id}.md",
        "source_paths": [f"/tmp/{entry_id}.pdf"],
        "summary": "unrelated",
    }
    fields.update(metadata)

    topics = fields["topics"]
    tags = fields["tags"]
    source_paths = fields["source_paths"]

    text = (
        "---\n"
        f"id: {fields['id']}\n"
        f"title: {fields['title']}\n"
        f"type: {fields['type']}\n"
        f"topics: {topics}\n"
        f"tags: {tags}\n"
        f"source_kind: {fields['source_kind']}\n"
        f"created_at: {fields['created_at']}\n"
        f"card_path: {fields['card_path']}\n"
        f"source_paths: {source_paths}\n"
        f"summary: {fields['summary']}\n"
        "---\n"
    )
    path = root / "registry" / "entries" / f"{entry_id}.md"
    path.write_text(text, encoding="utf-8")


def test_lookup_entries_prefers_title_then_topics_then_tags_then_summary(
    tmp_path: Path,
) -> None:
    initialize_workspace(tmp_path)
    _write_registry_entry(
        tmp_path,
        "paper-2026-04-title-hit",
        title="Agents in Practice",
    )
    _write_registry_entry(
        tmp_path,
        "paper-2026-04-topic-hit",
        topics=["agents"],
    )
    _write_registry_entry(
        tmp_path,
        "paper-2026-04-tag-hit",
        tags=["agents"],
    )
    _write_registry_entry(
        tmp_path,
        "paper-2026-04-summary-hit",
        summary="agents are useful",
    )

    results = lookup_entries(tmp_path, "agents", limit=5)

    assert [item["id"] for item in results] == [
        "paper-2026-04-title-hit",
        "paper-2026-04-topic-hit",
        "paper-2026-04-tag-hit",
        "paper-2026-04-summary-hit",
    ]
    assert all("card_path" in item for item in results)


def test_trace_entry_returns_note_path_and_source_paths(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    _write_registry_entry(
        tmp_path,
        "paper-2026-04-agent-memory",
        title="Agent Memory",
        topics=["agents"],
        tags=["memory"],
        summary="long-term agent memory",
        card_path="/tmp/a.md",
        source_paths=["/tmp/a.pdf"],
    )

    traced = trace_entry(tmp_path, "paper-2026-04-agent-memory")

    assert traced["note_path"] == "/tmp/a.md"
    assert traced["source_paths"] == ["/tmp/a.pdf"]
