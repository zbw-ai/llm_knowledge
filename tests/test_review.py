from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.frontmatter import load_frontmatter
from llm_kb.review import create_pending_draft, should_require_review
from llm_kb.slugify import make_entry_id


def test_should_require_review_for_paper_content() -> None:
    assert should_require_review(
        content_type="paper",
        source_kind="pdf",
        text_length=100,
        force_review=False,
    ) is True


def test_should_require_review_for_long_text() -> None:
    assert should_require_review(
        content_type="note",
        source_kind="text",
        text_length=6000,
        force_review=False,
    ) is True


def test_should_require_review_for_forced_review() -> None:
    assert should_require_review(
        content_type="note",
        source_kind="text",
        text_length=10,
        force_review=True,
    ) is True


def test_create_pending_draft_writes_markdown_file(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    pending_source = tmp_path / "inbox" / "pending" / "sources" / "demo.html"
    pending_source.parent.mkdir(parents=True, exist_ok=True)
    pending_source.write_text("<html>demo</html>", encoding="utf-8")

    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="paper",
        title="Demo Paper",
        created_at="2026-04-15",
        pending_source_paths=[pending_source],
        suggested_topics=["agents", "memory"],
        suggested_tags=["planning", "evaluation"],
        summary="draft summary",
        core_claims=["claim 1"],
        preserve_source=True,
    )

    assert draft.draft_path.exists()
    metadata, body = load_frontmatter(draft.draft_path.read_text(encoding="utf-8"))

    assert metadata["status"] == "pending_review"
    assert metadata["suggested_topics"] == ["agents", "memory"]
    assert metadata["suggested_tags"] == ["planning", "evaluation"]
    assert metadata["proposed_entry_id"] == make_entry_id(
        "paper",
        "2026-04-15",
        "Demo Paper",
    )
    assert metadata["proposed_note_path"] == str(
        tmp_path / "notes" / "atomic" / "paper-2026-04-demo-paper.md"
    )
    assert metadata["proposed_registry_path"] == str(
        tmp_path / "registry" / "entries" / "paper-2026-04-demo-paper.md"
    )
    assert body.startswith("# Summary")
