from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.registry import update_aggregates


def test_update_aggregates_creates_topic_tag_source_and_timeline_files(
    tmp_path: Path,
) -> None:
    initialize_workspace(tmp_path)
    entry_id = "paper-2026-04-demo"
    card_path = tmp_path / "notes" / "atomic" / f"{entry_id}.md"
    registry_path = tmp_path / "registry" / "entries" / f"{entry_id}.md"
    card_path.write_text("---\nid: paper-2026-04-demo\n---\n", encoding="utf-8")
    registry_path.write_text(
        "---\n"
        "id: paper-2026-04-demo\n"
        "title: Demo\n"
        "type: paper\n"
        "topics: [agents]\n"
        "tags: [memory]\n"
        "source_kind: arxiv\n"
        "created_at: 2026-04-15\n"
        "card_path: /tmp/card.md\n"
        "source_paths: [/tmp/source.pdf]\n"
        "summary: demo\n"
        "---\n",
        encoding="utf-8",
    )

    update_aggregates(tmp_path, registry_path)

    assert (tmp_path / "registry" / "topics" / "agents.md").exists()
    assert (tmp_path / "registry" / "tags" / "memory.md").exists()
    assert (tmp_path / "registry" / "sources" / "arxiv.md").exists()
    assert (tmp_path / "registry" / "timelines" / "2026.md").exists()


def test_update_aggregates_is_idempotent(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    entry_id = "paper-2026-04-demo"
    registry_path = tmp_path / "registry" / "entries" / f"{entry_id}.md"
    registry_path.write_text(
        "---\n"
        "id: paper-2026-04-demo\n"
        "title: Demo\n"
        "type: paper\n"
        "topics: [agents]\n"
        "tags: [memory]\n"
        "source_kind: arxiv\n"
        "created_at: 2026-04-15\n"
        "card_path: /tmp/card.md\n"
        "source_paths: [/tmp/source.pdf]\n"
        "summary: demo\n"
        "---\n",
        encoding="utf-8",
    )

    update_aggregates(tmp_path, registry_path)
    first_snapshot = {
        rel: (tmp_path / rel).read_text(encoding="utf-8")
        for rel in [
            "registry/topics/agents.md",
            "registry/tags/memory.md",
            "registry/sources/arxiv.md",
            "registry/timelines/2026.md",
        ]
    }

    update_aggregates(tmp_path, registry_path)

    for rel, content in first_snapshot.items():
        assert (tmp_path / rel).read_text(encoding="utf-8") == content
