# LLM 知识库 MVP 实施计划

> **给执行型 agent 的说明：** 如果当前环境支持子 agent，优先使用 `superpowers:subagent-driven-development`；否则使用 `superpowers:executing-plans`。本计划使用 `- [ ]` 复选框跟踪步骤。

**目标：** 实现第一版可工作的本地 LLM 知识库，使用户可以完成目录初始化、把一个链接或本地文件导入为标准化 `atomic` 卡片和 `registry` 条目，并通过 `registry` 优先的方式进行检索，而不需要每次重读整个知识库。

**架构：** 使用一个小型 Python 包在本地文件系统上管理知识库。系统以 Markdown 模板承载可读内容，以 YAML frontmatter 承载元数据，以轻量 `registry` 层承担路由和检索，再通过 CLI 入口让 Codex 调用 `init`、`ingest`、`ask`、`trace` 等动作。

**技术栈：** Python 3.11+、`PyYAML`、`pytest`、`argparse`、`pathlib`、Markdown 文件、本地文件系统

---

## 文件清单

### 新增文件

- `pyproject.toml`
- `.gitignore`
- `README.md`
- `docs/usage.md`
- `templates/atomic-note.md`
- `templates/registry-entry.md`
- `templates/topic-note.md`
- `templates/synthesis-note.md`
- `templates/source-record.md`
- `llm_kb/__init__.py`
- `llm_kb/__main__.py`
- `llm_kb/bootstrap.py`
- `llm_kb/cli.py`
- `llm_kb/frontmatter.py`
- `llm_kb/models.py`
- `llm_kb/slugify.py`
- `llm_kb/ingest.py`
- `llm_kb/registry.py`
- `llm_kb/retrieve.py`
- `tests/test_bootstrap.py`
- `tests/test_frontmatter.py`
- `tests/test_ingest.py`
- `tests/test_registry.py`
- `tests/test_retrieve.py`

### 可能修改

- `docs/superpowers/specs/2026-04-15-llm-knowledge-base-design.md`
  仅当实现过程中发现设计与落地方案存在明确冲突时再回写

---

## Chunk 1：基础骨架

### 任务 1：建立 Python 项目和初始化命令

**文件：**
- 新增：`pyproject.toml`
- 新增：`.gitignore`
- 新增：`llm_kb/__init__.py`
- 新增：`llm_kb/__main__.py`
- 新增：`llm_kb/cli.py`
- 新增：`llm_kb/bootstrap.py`
- 测试：`tests/test_bootstrap.py`

- [ ] **步骤 1：先写失败测试，约束初始化行为**

```python
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace


def test_initialize_workspace_creates_required_directories(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    expected = [
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
    for rel in expected:
        assert (tmp_path / rel).is_dir(), rel


def test_initialize_workspace_copies_templates_without_overwriting(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    template = tmp_path / "templates" / "atomic-note.md"
    template.write_text("custom", encoding="utf-8")

    initialize_workspace(tmp_path)

    assert template.read_text(encoding="utf-8") == "custom"
```

- [ ] **步骤 2：运行测试，确认当前确实失败**

运行：`python -m pytest tests/test_bootstrap.py -q`  
预期：出现 FAIL，原因是 `llm_kb` 模块或 `initialize_workspace` 尚不存在

- [ ] **步骤 3：补上项目打包配置和 CLI 骨架**

```toml
[project]
name = "llm-kb"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["PyYAML>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]
```

```python
# llm_kb/__main__.py
from llm_kb.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# llm_kb/cli.py
import argparse
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser(prog="llm-kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "init":
        initialize_workspace(args.root)
        return 0
    return 1
```

- [ ] **步骤 4：实现初始化逻辑和内置模板写入**

```python
# llm_kb/bootstrap.py
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
```

- [ ] **步骤 5：再次运行测试，确认通过**

运行：`python -m pytest tests/test_bootstrap.py -q`  
预期：PASS

- [ ] **步骤 6：验证 CLI 可以在当前目录初始化知识库**

运行：`python -m llm_kb init --root .`  
预期：退出码为 0，并在当前目录创建规划中的目录树和模板文件

- [ ] **步骤 7：如果仓库已初始化 git，则提交这一阶段**

```bash
git add pyproject.toml .gitignore llm_kb tests templates
git commit -m "feat: add knowledge base bootstrap command"
```


### 任务 2：补齐元数据模型、slug 规则和 frontmatter 工具

**文件：**
- 新增：`llm_kb/models.py`
- 新增：`llm_kb/slugify.py`
- 新增：`llm_kb/frontmatter.py`
- 测试：`tests/test_frontmatter.py`

- [ ] **步骤 1：先写失败测试，约束元数据格式**

```python
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
```

- [ ] **步骤 2：运行测试，确认尚未实现**

运行：`python -m pytest tests/test_frontmatter.py -q`  
预期：FAIL，提示缺少函数或模块

- [ ] **步骤 3：实现数据类和 frontmatter 读写**

```python
# llm_kb/models.py
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
```

```python
# llm_kb/frontmatter.py
import yaml


def dump_frontmatter(metadata: dict, body: str) -> str:
    return f"---\n{yaml.safe_dump(metadata, sort_keys=False).strip()}\n---\n\n{body}"


def load_frontmatter(text: str) -> tuple[dict, str]:
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw) or {}, body.lstrip("\n")
```

- [ ] **步骤 4：实现确定性的 slug 和条目 ID 生成规则**

```python
# llm_kb/slugify.py
import re


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", cleaned)


def make_entry_id(content_type: str, created_at: str, title: str) -> str:
    year_month = "-".join(created_at.split("-")[:2])
    return f"{content_type}-{year_month}-{slugify(title)}"
```

- [ ] **步骤 5：再次运行测试，确认通过**

运行：`python -m pytest tests/test_frontmatter.py -q`  
预期：PASS

- [ ] **步骤 6：如果仓库已初始化 git，则提交这一阶段**

```bash
git add llm_kb/models.py llm_kb/slugify.py llm_kb/frontmatter.py tests/test_frontmatter.py
git commit -m "feat: add metadata and frontmatter helpers"
```

---

## Chunk 2：入库主链路

### 任务 3：实现本地文件和粘贴文本的快速入库

**文件：**
- 新增：`llm_kb/ingest.py`
- 测试：`tests/test_ingest.py`
- 修改：`llm_kb/cli.py`

- [ ] **步骤 1：先写失败测试，约束本地入库行为**

```python
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
    assert "paper-2026-04-a-demo-paper" in result.entry_id


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
```

- [ ] **步骤 2：运行测试，确认当前失败**

运行：`python -m pytest tests/test_ingest.py -q`  
预期：FAIL，提示缺少入库函数

- [ ] **步骤 3：实现入库结果模型和来源目录映射**

```python
from dataclasses import dataclass
from pathlib import Path
import shutil
from datetime import date

from llm_kb.frontmatter import dump_frontmatter
from llm_kb.models import EntryMetadata
from llm_kb.slugify import make_entry_id


@dataclass
class IngestResult:
    entry_id: str
    note_path: Path
    registry_path: Path
    source_copy_path: Path
```

```python
TYPE_TO_SOURCE_DIR = {
    "paper": "sources/papers",
    "blog": "sources/blogs",
    "social": "sources/social",
    "github": "sources/github",
    "doc": "sources/snapshots",
    "note": "sources/snapshots",
}
```

- [ ] **步骤 4：实现 `ingest_local_file` 和 `ingest_text`**

```python
def ingest_local_file(root: Path, source_path: Path, title: str, content_type: str, source_kind: str,
                      topics: list[str], tags: list[str]) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    target_dir = root / TYPE_TO_SOURCE_DIR[content_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{entry_id}{source_path.suffix.lower()}"
    shutil.copy2(source_path, target_path)
    return _write_note_and_registry(root, entry_id, title, content_type, source_kind, created_at, target_path, topics, tags)


def ingest_text(root: Path, text: str, title: str, content_type: str, source_kind: str,
                topics: list[str], tags: list[str]) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    target_path = root / "sources" / "snapshots" / f"{entry_id}.md"
    target_path.write_text(text, encoding="utf-8")
    return _write_note_and_registry(root, entry_id, title, content_type, source_kind, created_at, target_path, topics, tags)
```

- [ ] **步骤 5：用标准卡片模板实现 `_write_note_and_registry`**

```python
def _write_note_and_registry(root: Path, entry_id: str, title: str, content_type: str, source_kind: str,
                             created_at: str, source_path: Path, topics: list[str], tags: list[str]) -> IngestResult:
    metadata = EntryMetadata(
        id=entry_id,
        title=title,
        type=content_type,
        source_kind=source_kind,
        created_at=created_at,
        topics=topics,
        tags=tags,
        local_source_paths=[str(source_path.resolve())],
    )
    note_body = (
        "# Summary\n\n"
        "TBD\n\n"
        "# Core Claims\n\n"
        "- TBD\n\n"
        "# Evidence\n\n"
        "- TBD\n\n"
        "# Relevance\n\n"
        "TBD\n\n"
        "# My Thoughts\n\n"
        "TBD\n\n"
        "# Follow-ups\n\n"
        "- TBD\n"
    )
    note_path = root / "notes" / "atomic" / f"{entry_id}.md"
    note_path.write_text(dump_frontmatter(metadata.to_dict(), note_body), encoding="utf-8")
    registry_path = root / "registry" / "entries" / f"{entry_id}.md"
    registry_body = dump_frontmatter(
        {
            "id": entry_id,
            "title": title,
            "type": content_type,
            "topics": topics,
            "tags": tags,
            "source_kind": source_kind,
            "created_at": created_at,
            "card_path": str(note_path.resolve()),
            "source_paths": [str(source_path.resolve())],
            "summary": "TBD",
        },
        "",
    )
    registry_path.write_text(registry_body, encoding="utf-8")
    return IngestResult(entry_id, note_path, registry_path, source_path)
```

- [ ] **步骤 6：在 CLI 中暴露 `ingest-file` 与 `ingest-text` 子命令**

命令示例：

```bash
python -m llm_kb ingest-file --root . --source /tmp/demo.pdf --title "A Demo Paper" --type paper --source-kind pdf --topic agents --tag demo
python -m llm_kb ingest-text --root . --title "Pasted Note" --text "hello world" --type note --source-kind text --topic scratch --tag capture
```

- [ ] **步骤 7：再次运行测试，确认通过**

运行：`python -m pytest tests/test_ingest.py -q`  
预期：PASS

- [ ] **步骤 8：如果仓库已初始化 git，则提交这一阶段**

```bash
git add llm_kb/ingest.py llm_kb/cli.py tests/test_ingest.py
git commit -m "feat: add fast-path ingestion for local content"
```


### 任务 4：实现 URL 的快速入库和本地快照

**文件：**
- 修改：`llm_kb/ingest.py`
- 修改：`llm_kb/cli.py`
- 修改：`tests/test_ingest.py`

- [ ] **步骤 1：先补一个不依赖真实网络的失败测试**

```python
from unittest.mock import patch

from llm_kb.ingest import ingest_url


def test_ingest_url_writes_snapshot_and_note(tmp_path) -> None:
    initialize_workspace(tmp_path)

    with patch("llm_kb.ingest.fetch_url_text", return_value="<html><title>Demo</title></html>"):
        result = ingest_url(
            root=tmp_path,
            url="https://example.com/demo",
            title="Demo URL",
            content_type="blog",
            source_kind="web",
            topics=["retrieval"],
            tags=["url"],
        )

    assert result.source_copy_path.exists()
    assert result.source_copy_path.suffix == ".html"
    assert result.note_path.exists()
```

- [ ] **步骤 2：运行测试，确认当前失败**

运行：`python -m pytest tests/test_ingest.py -q`  
预期：FAIL，提示缺少 `ingest_url`

- [ ] **步骤 3：实现 `fetch_url_text` 和 `ingest_url`**

```python
from urllib.request import Request, urlopen


def fetch_url_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "llm-kb/0.1"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def ingest_url(root: Path, url: str, title: str, content_type: str, source_kind: str,
               topics: list[str], tags: list[str]) -> IngestResult:
    created_at = date.today().isoformat()
    entry_id = make_entry_id(content_type, created_at, title)
    html = fetch_url_text(url)
    target_dir = root / TYPE_TO_SOURCE_DIR[content_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{entry_id}.html"
    target_path.write_text(html, encoding="utf-8")
    result = _write_note_and_registry(root, entry_id, title, content_type, source_kind, created_at, target_path, topics, tags)
    _merge_source_url(result.registry_path, url)
    _merge_source_url(result.note_path, url)
    return result
```

- [ ] **步骤 4：明确失败策略，不要静默写入损坏条目**

实现要求：

- MVP 阶段如果抓取 URL 失败，应抛出清晰错误
- 不要在抓取失败时偷偷创建一个不完整条目
- 后续确认模式可以再补“抓取失败但仍允许手工确认入库”的分支

- [ ] **步骤 5：重新运行入库测试**

运行：`python -m pytest tests/test_ingest.py -q`  
预期：PASS

- [ ] **步骤 6：如果仓库已初始化 git，则提交这一阶段**

```bash
git add llm_kb/ingest.py llm_kb/cli.py tests/test_ingest.py
git commit -m "feat: add url ingestion with local snapshots"
```

---

## Chunk 3：`registry` 维护

### 任务 5：实现主题、标签、来源和时间线索引更新

**文件：**
- 新增：`llm_kb/registry.py`
- 测试：`tests/test_registry.py`
- 修改：`llm_kb/ingest.py`

- [ ] **步骤 1：先写失败测试，约束聚合索引行为**

```python
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.registry import update_aggregates


def test_update_aggregates_creates_topic_tag_source_and_timeline_files(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    entry_id = "paper-2026-04-demo"
    card_path = tmp_path / "notes" / "atomic" / f"{entry_id}.md"
    registry_path = tmp_path / "registry" / "entries" / f"{entry_id}.md"
    card_path.write_text("---\nid: paper-2026-04-demo\n---\n", encoding="utf-8")
    registry_path.write_text(
        "---\n"
        "id: paper-2026-04-demo\n"
        "title: Demo\n"
        "type: paper\n"
        "topics: [agents]\n"
        "tags: [memory]\n"
        "source_kind: arxiv\n"
        "created_at: 2026-04-15\n"
        "card_path: /tmp/card.md\n"
        "source_paths: [/tmp/source.pdf]\n"
        "summary: demo\n"
        "---\n",
        encoding="utf-8",
    )

    update_aggregates(tmp_path, registry_path)

    assert (tmp_path / "registry" / "topics" / "agents.md").exists()
    assert (tmp_path / "registry" / "tags" / "memory.md").exists()
    assert (tmp_path / "registry" / "sources" / "arxiv.md").exists()
    assert (tmp_path / "registry" / "timelines" / "2026.md").exists()
```

- [ ] **步骤 2：运行测试，确认当前失败**

运行：`python -m pytest tests/test_registry.py -q`  
预期：FAIL，提示缺少 `registry` 辅助函数

- [ ] **步骤 3：实现聚合索引写入器**

```python
from pathlib import Path

from llm_kb.frontmatter import load_frontmatter


def update_aggregates(root: Path, entry_registry_path: Path) -> None:
    metadata, _ = load_frontmatter(entry_registry_path.read_text(encoding="utf-8"))
    _write_topic_files(root, metadata)
    _write_tag_files(root, metadata)
    _write_source_file(root, metadata)
    _write_timeline_file(root, metadata)
```

```python
def _append_link_if_missing(path: Path, line: str, header: str) -> None:
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if line in content:
            return
    else:
        content = header
    path.write_text(f"{content.rstrip()}\n{line}\n", encoding="utf-8")
```

- [ ] **步骤 4：让所有成功入库路径都触发聚合更新**

实现要求：

- `ingest_local_file`
- `ingest_text`
- `ingest_url`

这三条路径在成功写入条目后都必须调用 `update_aggregates`

另外要保证：

- 重复调用时保持幂等
- 不要在聚合文件中反复追加重复记录

- [ ] **步骤 5：运行 `registry` 测试和已有入库测试**

运行：`python -m pytest tests/test_registry.py tests/test_ingest.py -q`  
预期：PASS

- [ ] **步骤 6：如果仓库已初始化 git，则提交这一阶段**

```bash
git add llm_kb/registry.py llm_kb/ingest.py tests/test_registry.py tests/test_ingest.py
git commit -m "feat: maintain aggregate registry indexes"
```

---

## Chunk 4：检索

### 任务 6：实现 `registry` 优先的检索和追溯能力

**文件：**
- 新增：`llm_kb/retrieve.py`
- 测试：`tests/test_retrieve.py`
- 修改：`llm_kb/cli.py`

- [ ] **步骤 1：先写失败测试，约束检索行为**

```python
from pathlib import Path

from llm_kb.bootstrap import initialize_workspace
from llm_kb.retrieve import lookup_entries, trace_entry


def test_lookup_entries_prefers_topic_and_tag_matches(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    registry = tmp_path / "registry" / "entries"
    (registry / "paper-2026-04-agent-memory.md").write_text(
        "---\n"
        "id: paper-2026-04-agent-memory\n"
        "title: Agent Memory\n"
        "type: paper\n"
        "topics: [agents]\n"
        "tags: [memory]\n"
        "source_kind: arxiv\n"
        "created_at: 2026-04-15\n"
        "card_path: /tmp/a.md\n"
        "source_paths: [/tmp/a.pdf]\n"
        "summary: long-term agent memory\n"
        "---\n",
        encoding="utf-8",
    )

    results = lookup_entries(tmp_path, "agent memory", limit=5)

    assert results[0]["id"] == "paper-2026-04-agent-memory"


def test_trace_entry_returns_note_and_source_paths(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)
    registry_path = tmp_path / "registry" / "entries" / "paper-2026-04-agent-memory.md"
    registry_path.write_text(
        "---\n"
        "id: paper-2026-04-agent-memory\n"
        "title: Agent Memory\n"
        "type: paper\n"
        "topics: [agents]\n"
        "tags: [memory]\n"
        "source_kind: arxiv\n"
        "created_at: 2026-04-15\n"
        "card_path: /tmp/a.md\n"
        "source_paths: [/tmp/a.pdf]\n"
        "summary: long-term agent memory\n"
        "---\n",
        encoding="utf-8",
    )

    traced = trace_entry(tmp_path, "paper-2026-04-agent-memory")

    assert traced["card_path"] == "/tmp/a.md"
    assert traced["source_paths"] == ["/tmp/a.pdf"]
```

- [ ] **步骤 2：运行测试，确认当前失败**

运行：`python -m pytest tests/test_retrieve.py -q`  
预期：FAIL，提示缺少检索辅助函数

- [ ] **步骤 3：实现扫描 `registry` 和轻量打分逻辑**

```python
from pathlib import Path

from llm_kb.frontmatter import load_frontmatter


def lookup_entries(root: Path, query: str, limit: int = 5) -> list[dict]:
    query_terms = set(query.lower().split())
    scored = []
    for path in (root / "registry" / "entries").glob("*.md"):
        metadata, _ = load_frontmatter(path.read_text(encoding="utf-8"))
        haystack = " ".join(
            [
                metadata.get("title", ""),
                " ".join(metadata.get("topics", [])),
                " ".join(metadata.get("tags", [])),
                metadata.get("summary", ""),
            ]
        ).lower()
        score = sum(term in haystack for term in query_terms)
        if score:
            scored.append((score, metadata))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]]


def trace_entry(root: Path, entry_id: str) -> dict:
    path = root / "registry" / "entries" / f"{entry_id}.md"
    metadata, _ = load_frontmatter(path.read_text(encoding="utf-8"))
    return metadata
```

- [ ] **步骤 4：在 CLI 中暴露 `ask` 和 `trace`**

命令示例：

```bash
python -m llm_kb ask --root . --query "agent memory"
python -m llm_kb trace --root . --id paper-2026-04-agent-memory
```

实现要求：

- `ask` 输出候选条目的 `id`、标题、摘要和卡片路径
- `trace` 输出卡片路径和来源路径
- MVP 阶段不要在这里直接做生成式综合，先把“检索优先”这一步走通

- [ ] **步骤 5：运行检索测试和全量测试**

运行：`python -m pytest -q`  
预期：PASS

- [ ] **步骤 6：如果仓库已初始化 git，则提交这一阶段**

```bash
git add llm_kb/retrieve.py llm_kb/cli.py tests/test_retrieve.py
git commit -m "feat: add registry-first retrieval and trace commands"
```

---

## Chunk 5：文档与使用体验

### 任务 7：补齐操作文档和端到端示例

**文件：**
- 新增：`README.md`
- 新增：`docs/usage.md`
- 修改：`templates/atomic-note.md`
- 修改：`templates/registry-entry.md`
- 修改：`templates/topic-note.md`
- 修改：`templates/synthesis-note.md`
- 修改：`templates/source-record.md`

- [ ] **步骤 1：围绕真实工作流编写 README**

README 至少应包含：

- 这个仓库是什么
- 目录结构说明
- 快速开始方式
- `init`、`ingest-file`、`ingest-text`、`ingest-url`、`ask`、`trace` 的用法
- MVP 明确不做什么

- [ ] **步骤 2：编写 `docs/usage.md`，给出一条完整 happy path**

需要包含以下示例：

```bash
python -m llm_kb init --root .
python -m llm_kb ingest-text --root . --title "Karpathy Notes" --text "..." --type note --source-kind text --topic llm-kb --tag methodology
python -m llm_kb ask --root . --query "methodology"
python -m llm_kb trace --root . --id note-2026-04-karpathy-notes
```

- [ ] **步骤 3：把模板文件从占位内容补成可直接使用的版本**

`templates/atomic-note.md` 至少应为：

```md
---
id:
title:
type:
source_kind:
authors: []
created_at:
source_url:
local_source_paths: []
topics: []
tags: []
status: distilled
importance: medium
related: []
---

# Summary

# Core Claims

# Evidence

# Relevance

# My Thoughts

# Follow-ups
```

- [ ] **步骤 4：检查文档与 CLI 是否一致**

运行：

```bash
python -m llm_kb --help
python -m llm_kb ask --help
python -m llm_kb trace --help
```

预期：文档中提到的命令和参数都真实存在，并且帮助信息与文档描述一致

- [ ] **步骤 5：如果仓库已初始化 git，则提交这一阶段**

```bash
git add README.md docs/usage.md templates
git commit -m "docs: add usage guide for knowledge base workflow"
```

---

## 验证清单

- [ ] `python -m pytest -q`
- [ ] `python -m llm_kb init --root .`
- [ ] `python -m llm_kb ingest-text --root . --title "Smoke Test" --text "example" --type note --source-kind text --topic smoke --tag smoke`
- [ ] `python -m llm_kb ask --root . --query "smoke"`
- [ ] `python -m llm_kb trace --root . --id note-<yyyy-mm>-smoke-test`
- [ ] 确认 `sources/`、`notes/atomic/`、`registry/entries/` 以及至少一个聚合索引目录下都有生成文件

---

## 本计划暂不覆盖的内容

- 长文档或复杂资料的确认模式入库
- 自动生成综合页
- 语义检索或向量检索
- SQLite 或图数据库持久化
- Web UI 或后台服务
- 高级 HTML 清洗与正文抽取

这些内容应在“快速入库 + 检索主链路”稳定后再单独规划。

---

## 交接说明

- 如果执行时这个目录仍然不是 git 仓库，请在第一个提交步骤之前初始化 git，或者跳过提交步骤并在执行日志中记录阶段性里程碑。
- 实现上尽量保持标准库优先；运行时外部依赖暂时只计划 `PyYAML`。
- MVP 不要过早把排序、抽取、解析做复杂，当前目标是先得到一个可用、可查、可维护的第一版。
