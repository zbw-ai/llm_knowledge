import yaml


def dump_frontmatter(metadata: dict, body: str) -> str:
    dumped = yaml.safe_dump(metadata, sort_keys=False).strip()
    return f"---\n{dumped}\n---\n\n{body}"


def load_frontmatter(text: str) -> tuple[dict, str]:
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw) or {}, body.lstrip("\n")
