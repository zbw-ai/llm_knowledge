import re


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", cleaned)


def make_entry_id(content_type: str, created_at: str, title: str) -> str:
    year_month = "-".join(created_at.split("-")[:2])
    return f"{content_type}-{year_month}-{slugify(title)}"

