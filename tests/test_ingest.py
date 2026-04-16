from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.ingest import ingest_local_file, ingest_text, ingest_url


def test_ingest_local_file_creates_source_note_and_registry(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"%PDF-1.4 test")

    result = ingest_local_file(
        root=tmp_path,
        source_path=source,
        title="A Demo Paper",
        content_type="paper",
        source_kind="pdf",
        topics=["agents"],
        tags=["demo"],
        review_mode="off",
    )

    assert result.note_path.exists()
    assert result.registry_path.exists()
    assert result.source_copy_path.exists()
    assert result.entry_id.startswith("paper-")
    assert result.entry_id.endswith("a-demo-paper")
    assert (tmp_path / "registry" / "topics" / "agents.md").exists()
    assert (tmp_path / "registry" / "tags" / "demo.md").exists()
    assert (tmp_path / "registry" / "sources" / "pdf.md").exists()
    assert (tmp_path / "registry" / "timelines" / "2026.md").exists()


def test_ingest_text_creates_snapshot_record_for_pasted_content(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    result = ingest_text(
        root=tmp_path,
        text="hello world",
        title="Pasted Note",
        content_type="note",
        source_kind="text",
        topics=["scratch"],
        tags=["capture"],
        review_mode="off",
    )

    assert result.source_copy_path.read_text(encoding="utf-8") == "hello world"
    assert result.note_path.exists()
    assert (tmp_path / "registry" / "topics" / "scratch.md").exists()
    assert (tmp_path / "registry" / "tags" / "capture.md").exists()
    assert (tmp_path / "registry" / "sources" / "text.md").exists()
    assert (tmp_path / "registry" / "timelines" / "2026.md").exists()


def test_ingest_text_with_force_review_creates_pending_draft_not_final_entry(
    tmp_path: Path,
) -> None:
    initialize_workspace(tmp_path)

    result = ingest_text(
        root=tmp_path,
        text="hello world",
        title="Pasted Note",
        content_type="note",
        source_kind="text",
        topics=["scratch"],
        tags=["capture"],
        review_mode="force",
    )

    assert result.mode == "pending_review"
    assert result.draft_id is not None
    assert result.draft_path is not None
    assert result.draft_path.exists()
    assert result.source_copy_path.parent == tmp_path / "inbox" / "pending" / "sources"
    assert not (tmp_path / "notes" / "atomic" / f"{result.entry_id}.md").exists()
    assert not (tmp_path / "registry" / "entries" / f"{result.entry_id}.md").exists()


def test_ingest_url_creates_html_snapshot_and_note(
    tmp_path: Path, monkeypatch
) -> None:
    initialize_workspace(tmp_path)

    calls: list[str] = []

    def fake_fetch_url_text(url: str) -> str:
        calls.append(url)
        return "<html><body>demo page</body></html>"

    monkeypatch.setattr("llm_kb.ingest.fetch_url_text", fake_fetch_url_text)

    result = ingest_url(
        root=tmp_path,
        url="https://example.com/demo",
        title="Web Demo",
        content_type="blog",
        source_kind="url",
        topics=["web"],
        tags=["demo"],
        review_mode="off",
    )

    assert calls == ["https://example.com/demo"]
    assert result.source_copy_path.suffix == ".html"
    assert result.source_copy_path.parent == tmp_path / "sources" / "blogs"
    assert result.source_copy_path.read_text(encoding="utf-8") == (
        "<html><body>demo page</body></html>"
    )
    assert result.note_path.exists()
    assert result.registry_path.exists()
    assert (tmp_path / "registry" / "topics" / "web.md").exists()
    assert (tmp_path / "registry" / "tags" / "demo.md").exists()
    assert (tmp_path / "registry" / "sources" / "url.md").exists()
    assert (tmp_path / "registry" / "timelines" / "2026.md").exists()


def test_ingest_url_with_paper_content_auto_enters_review_mode(
    tmp_path: Path, monkeypatch
) -> None:
    initialize_workspace(tmp_path)

    calls: list[str] = []

    def fake_fetch_url_text(url: str) -> str:
        calls.append(url)
        return "<html><body>paper</body></html>"

    monkeypatch.setattr("llm_kb.ingest.fetch_url_text", fake_fetch_url_text)

    result = ingest_url(
        root=tmp_path,
        url="https://example.com/paper",
        title="Web Paper",
        content_type="paper",
        source_kind="url",
        topics=["web"],
        tags=["demo"],
        review_mode="auto",
    )

    assert calls == ["https://example.com/paper"]
    assert result.mode == "pending_review"
    assert result.draft_id is not None
    assert result.draft_path is not None
    assert result.draft_path.exists()
    assert result.source_copy_path.parent == tmp_path / "inbox" / "pending" / "sources"
    assert not (tmp_path / "notes" / "atomic" / f"{result.entry_id}.md").exists()
    assert not (tmp_path / "registry" / "entries" / f"{result.entry_id}.md").exists()


def test_ingest_text_with_review_off_keeps_final_ingest_path(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    result = ingest_text(
        root=tmp_path,
        text="hello world",
        title="Pasted Note",
        content_type="note",
        source_kind="text",
        topics=["scratch"],
        tags=["capture"],
        review_mode="off",
    )

    assert result.mode == "finalized"
    assert result.draft_id is None
    assert result.draft_path is None
    assert result.note_path.exists()
    assert result.registry_path.exists()
