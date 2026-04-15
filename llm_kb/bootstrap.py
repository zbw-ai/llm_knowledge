from pathlib import Path


DEFAULT_DIRS = [
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

DEFAULT_TEMPLATES = {
    "atomic-note.md": "# Summary\n\n# Core Claims\n\n# Evidence\n\n# Relevance\n\n# My Thoughts\n\n# Follow-ups\n",
    "registry-entry.md": "---\nsummary: \n---\n",
    "topic-note.md": "# Topic Overview\n\n# Key Entries\n\n# Open Questions\n",
    "synthesis-note.md": "# Scope\n\n# Synthesis\n\n# Tensions\n\n# Next Steps\n",
    "source-record.md": "---\nsource_url: \nsource_kind: \n---\n",
}


def initialize_workspace(root: Path) -> None:
    for rel in DEFAULT_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)

    for name, content in DEFAULT_TEMPLATES.items():
        target = root / "templates" / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")
