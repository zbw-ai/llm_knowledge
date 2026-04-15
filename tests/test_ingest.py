from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.ingest import ingest_local_file, ingest_text


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
    )

    assert result.note_path.exists()
    assert result.registry_path.exists()
    assert result.source_copy_path.exists()
    assert result.entry_id.startswith("paper-")
    assert result.entry_id.endswith("a-demo-paper")


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
    )

    assert result.source_copy_path.read_text(encoding="utf-8") == "hello world"
    assert result.note_path.exists()
