from dataclasses import asdict, dataclass, field


@dataclass
class EntryMetadata:
    id: str
    title: str
    type: str
    source_kind: str
    created_at: str
    topics: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)
    source_url: str | None = None
    local_source_paths: list[str] = field(default_factory=list)
    status: str = "distilled"
    importance: str = "medium"
    related: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PendingDraftMetadata:
    draft_id: str
    status: str
    source_input: str
    source_kind: str
    content_type: str
    title: str
    created_at: str
    pending_source_paths: list[str] = field(default_factory=list)
    suggested_topics: list[str] = field(default_factory=list)
    suggested_tags: list[str] = field(default_factory=list)
    proposed_entry_id: str = ""
    proposed_note_path: str = ""
    proposed_registry_path: str = ""
    preserve_source: bool = True

    def to_dict(self) -> dict:
        return asdict(self)
