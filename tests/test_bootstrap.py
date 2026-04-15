from pathlib import Path

from llm_kb.bootstrap import initialize_workspace


def test_initialize_workspace_creates_required_directories(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    expected = [
        "inbox/links",
        "inbox/files",
        "sources/papers",
        "sources/blogs",
        "sources/social",
        "sources/github",
        "sources/snapshots",
        "notes/atomic",
        "notes/syntheses",
        "notes/topics",
        "registry/entries",
        "registry/topics",
        "registry/tags",
        "registry/sources",
        "registry/timelines",
        "templates",
    ]
    for rel in expected:
        assert (tmp_path / rel).is_dir(), rel


def test_initialize_workspace_copies_templates_without_overwriting(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    template = tmp_path / "templates" / "atomic-note.md"
    template.write_text("custom", encoding="utf-8")

    initialize_workspace(tmp_path)

    assert template.read_text(encoding="utf-8") == "custom"


def test_initialize_workspace_creates_pending_review_directories(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    assert (tmp_path / "inbox" / "pending" / "drafts").is_dir()
    assert (tmp_path / "inbox" / "pending" / "sources").is_dir()


def test_initialize_workspace_writes_pending_draft_template(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    template = tmp_path / "templates" / "pending-draft.md"
    assert template.exists()
    text = template.read_text(encoding="utf-8")
    assert "draft_id:" in text
    assert "# Summary" in text
