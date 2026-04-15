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

