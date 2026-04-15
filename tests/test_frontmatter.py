from llm_kb.frontmatter import dump_frontmatter, load_frontmatter
from llm_kb.models import EntryMetadata
from llm_kb.slugify import make_entry_id


def test_make_entry_id_normalizes_type_date_and_title() -> None:
    assert make_entry_id("paper", "2026-04-15", "Test-Time Compute Scaling") == (
        "paper-2026-04-test-time-compute-scaling"
    )


def test_frontmatter_round_trip_preserves_lists() -> None:
    entry = EntryMetadata(
        id="paper-2026-04-demo",
        title="Demo",
        type="paper",
        source_kind="arxiv",
        created_at="2026-04-15",
        topics=["agents", "reasoning"],
        tags=["memory"],
    )
    text = dump_frontmatter(entry.to_dict(), "# Summary\n")
    metadata, body = load_frontmatter(text)

    assert metadata["topics"] == ["agents", "reasoning"]
    assert metadata["tags"] == ["memory"]
    assert body == "# Summary\n"
