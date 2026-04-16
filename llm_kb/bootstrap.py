from pathlib import Path


DEFAULT_DIRS = [
    "inbox/links",
    "inbox/files",
    "inbox/pending/drafts",
    "inbox/pending/sources",
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

DEFAULT_TEMPLATES = {
    "atomic-note.md": "# Summary\n\n# Core Claims\n\n# Evidence\n\n# Relevance\n\n# My Thoughts\n\n# Follow-ups\n",
    "registry-entry.md": "---\nsummary: \n---\n",
    "topic-note.md": "# Topic Overview\n\n# Key Entries\n\n# Open Questions\n",
    "synthesis-note.md": "# Scope\n\n# Synthesis\n\n# Tensions\n\n# Next Steps\n",
    "source-record.md": "---\nsource_url: \nsource_kind: \n---\n",
    "pending-draft.md": "---\ndraft_id: \"\"\nstatus: pending_review\nsource_input: \"\"\nsource_kind: \"\"\ncontent_type: \"\"\ntitle: \"\"\ncreated_at: \"\"\npending_source_paths: []\nsuggested_topics: []\nsuggested_tags: []\nproposed_entry_id: \"\"\nproposed_note_path: \"\"\nproposed_registry_path: \"\"\npreserve_source: true\n---\n\n# Summary\n\n# Core Claims\n\n# Review Actions\n\n- confirm\n- regenerate_summary\n- update_tags\n- change_type\n- cancel\n",
}


def initialize_workspace(root: Path) -> None:
    for rel in DEFAULT_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)

    for name, content in DEFAULT_TEMPLATES.items():
        target = root / "templates" / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")
