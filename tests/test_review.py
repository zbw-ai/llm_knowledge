from pathlib import Path

import pytest

from llm_kb.bootstrap import initialize_workspace
from llm_kb.frontmatter import load_frontmatter
from llm_kb.review import (
    cancel_draft,
    confirm_draft,
    create_pending_draft,
    revise_draft,
    should_require_review,
)
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


def test_confirm_draft_promotes_pending_source_and_writes_formal_files(tmp_path: Path) -> None:
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
        suggested_topics=["agents"],
        suggested_tags=["planning"],
        summary="draft summary",
        core_claims=["claim 1", "claim 2"],
        preserve_source=True,
    )

    result = confirm_draft(tmp_path, draft.draft_id)

    assert result.entry_id == "paper-2026-04-demo-paper"
    assert result.note_path == tmp_path / "notes" / "atomic" / "paper-2026-04-demo-paper.md"
    assert result.registry_path == tmp_path / "registry" / "entries" / "paper-2026-04-demo-paper.md"
    assert result.source_paths == [tmp_path / "sources" / "papers" / "demo.html"]

    draft_metadata, _ = load_frontmatter(draft.draft_path.read_text(encoding="utf-8"))
    assert draft_metadata["status"] == "confirmed"

    assert (tmp_path / "sources" / "papers" / "demo.html").exists()
    assert result.note_path.exists()
    assert result.registry_path.exists()
    assert (tmp_path / "registry" / "sources" / "web.md").exists()
    assert (tmp_path / "registry" / "tags" / "planning.md").exists()
    assert (tmp_path / "registry" / "topics" / "agents.md").exists()


def test_confirm_draft_rejects_non_pending_states(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="paper",
        title="Demo Paper",
        created_at="2026-04-15",
        pending_source_paths=[],
        suggested_topics=[],
        suggested_tags=[],
        summary="draft summary",
        core_claims=["claim 1"],
        preserve_source=True,
    )

    confirm_draft(tmp_path, draft.draft_id)

    with pytest.raises(ValueError, match="confirmed"):
        confirm_draft(tmp_path, draft.draft_id)


def test_cancel_draft_marks_draft_cancelled(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="note",
        title="Demo Note",
        created_at="2026-04-15",
        pending_source_paths=[],
        suggested_topics=[],
        suggested_tags=[],
        summary="draft summary",
        core_claims=["claim 1"],
        preserve_source=True,
    )

    result = cancel_draft(tmp_path, draft.draft_id)
    draft_metadata, _ = load_frontmatter(draft.draft_path.read_text(encoding="utf-8"))

    assert result.status == "cancelled"
    assert draft_metadata["status"] == "cancelled"


def test_revise_draft_recomputes_type_paths_and_tags(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="paper",
        title="Demo Paper",
        created_at="2026-04-15",
        pending_source_paths=[],
        suggested_topics=["agents"],
        suggested_tags=["planning"],
        summary="draft summary",
        core_claims=["claim 1"],
        preserve_source=True,
    )

    result = revise_draft(
        tmp_path,
        draft.draft_id,
        content_type="blog",
        topics=["memory"],
        tags=["evaluation"],
        regenerate_summary=False,
    )
    draft_metadata, _ = load_frontmatter(draft.draft_path.read_text(encoding="utf-8"))

    assert result.content_type == "blog"
    assert draft_metadata["content_type"] == "blog"
    assert draft_metadata["proposed_entry_id"] == make_entry_id(
        "blog",
        "2026-04-15",
        "Demo Paper",
    )
    assert draft_metadata["proposed_note_path"] == str(
        (tmp_path / "notes" / "atomic" / "blog-2026-04-demo-paper.md").resolve()
    )
    assert draft_metadata["proposed_registry_path"] == str(
        (tmp_path / "registry" / "entries" / "blog-2026-04-demo-paper.md").resolve()
    )
    assert draft_metadata["suggested_tags"] == ["evaluation"]
    assert draft_metadata["suggested_topics"] == ["memory"]


def test_revise_draft_regenerate_summary_rewrites_body_sections(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="paper",
        title="Demo Paper",
        created_at="2026-04-15",
        pending_source_paths=[],
        suggested_topics=["agents"],
        suggested_tags=["planning"],
        summary="original summary",
        core_claims=["original claim"],
        preserve_source=True,
    )

    revise_draft(
        tmp_path,
        draft.draft_id,
        regenerate_summary=True,
    )
    _, body = load_frontmatter(draft.draft_path.read_text(encoding="utf-8"))

    assert "Regenerated summary" in body
    assert "original summary" not in body
    assert "Core Claims" in body
