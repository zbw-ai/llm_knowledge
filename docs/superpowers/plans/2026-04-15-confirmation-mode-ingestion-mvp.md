# 确认模式入库 MVP 实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有快速入库主链路上增加“待确认草稿”式确认模式，使复杂来源或长内容能够先生成 pending draft，经用户确认或少量修订后再转正进入正式知识库。

**Architecture:** 复用现有 `ingest`/`registry`/`notes` 写入逻辑，在 `inbox/pending/` 下增加待确认来源和草稿落盘层，并增加一组 `review-draft` / `confirm-draft` / `revise-draft` / `cancel-draft` CLI 动作。自动触发规则采用轻量启发式，底层状态以 Markdown + YAML frontmatter 持久化。

**Tech Stack:** Python 3.11+、`PyYAML`、`pytest`、`argparse`、`pathlib`、Markdown 文件、本地文件系统

---

## 文件清单

### 新增文件

- `llm_kb/review.py`
- `tests/test_review.py`
- `templates/pending-draft.md`

### 修改文件

- `llm_kb/bootstrap.py`
- `llm_kb/cli.py`
- `llm_kb/ingest.py`
- `llm_kb/models.py`
- `tests/test_bootstrap.py`
- `tests/test_ingest.py`
- `README.md`
- `docs/usage.md`

### 可选新增文件

- `llm_kb/review_rules.py`
  只有在 `llm_kb/review.py` 过于膨胀时才拆出，不要提前拆分。

---

## Chunk 1：待确认基础设施

### 任务 1：扩展目录初始化和待确认模板

**Files:**
- Modify: `llm_kb/bootstrap.py`
- Modify: `tests/test_bootstrap.py`
- Create: `templates/pending-draft.md`

- [ ] **Step 1: 先写失败测试，约束 pending 目录和模板写入**

```python
def test_initialize_workspace_creates_pending_review_directories(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    assert (tmp_path / "inbox" / "pending" / "drafts").is_dir()
    assert (tmp_path / "inbox" / "pending" / "sources").is_dir()


def test_initialize_workspace_writes_pending_draft_template(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    template = tmp_path / "templates" / "pending-draft.md"
    assert template.exists()
    text = template.read_text(encoding="utf-8")
    assert "draft_id:" in text
    assert "# Summary" in text
```

- [ ] **Step 2: 运行 bootstrap 测试，确认先失败**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_bootstrap.py -q`  
Expected: FAIL，提示缺少 pending 目录或缺少 `pending-draft.md`

- [ ] **Step 3: 扩展 `initialize_workspace`，补齐 pending 目录**

实现要求：

- 在 `DEFAULT_DIRS` 中加入：
  - `inbox/pending/drafts`
  - `inbox/pending/sources`
- 保持现有模板“不覆盖用户已修改版本”的行为

- [ ] **Step 4: 新增 `templates/pending-draft.md`**

模板至少包含：

```md
---
draft_id: ""
status: pending_review
source_input: ""
source_kind: ""
content_type: ""
title: ""
created_at: ""
pending_source_paths: []
suggested_topics: []
suggested_tags: []
proposed_entry_id: ""
proposed_note_path: ""
proposed_registry_path: ""
preserve_source: true
---

# Summary

# Core Claims

# Review Actions

- confirm
- regenerate_summary
- update_tags
- change_type
- cancel
```

- [ ] **Step 5: 重跑 bootstrap 测试，确认转绿**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_bootstrap.py -q`  
Expected: PASS

- [ ] **Step 6: 提交这一阶段**

```bash
git add llm_kb/bootstrap.py tests/test_bootstrap.py templates/pending-draft.md
git commit -m "feat: add pending draft workspace structure"
```

---

## Chunk 2：待确认草稿模型与触发规则

### 任务 2：实现草稿模型、触发规则和草稿落盘

**Files:**
- Modify: `llm_kb/models.py`
- Create: `llm_kb/review.py`
- Create: `tests/test_review.py`

- [ ] **Step 1: 先写失败测试，约束 review-mode 判定和草稿生成**

```python
def test_should_require_review_for_paper_content() -> None:
    assert should_require_review(
        content_type="paper",
        source_kind="pdf",
        text_length=100,
        force_review=False,
    ) is True


def test_should_require_review_for_long_text() -> None:
    assert should_require_review(
        content_type="note",
        source_kind="text",
        text_length=6000,
        force_review=False,
    ) is True


def test_create_pending_draft_writes_markdown_file(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    draft = create_pending_draft(
        root=tmp_path,
        source_input="https://example.com/paper",
        source_kind="web",
        content_type="paper",
        title="Demo Paper",
        pending_source_paths=[tmp_path / "inbox" / "pending" / "sources" / "demo.html"],
        suggested_topics=["agents"],
        suggested_tags=["memory"],
        summary="draft summary",
        core_claims=["claim 1"],
        preserve_source=True,
    )

    assert draft.draft_path.exists()
    text = draft.draft_path.read_text(encoding="utf-8")
    assert "status: pending_review" in text
    assert "suggested_topics:" in text
    assert "# Summary" in text
```

- [ ] **Step 2: 运行 review 测试，确认先失败**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_review.py -q`  
Expected: FAIL，提示缺少模型、函数或模块

- [ ] **Step 3: 在 `llm_kb/models.py` 增加待确认草稿元数据模型**

建议增加：

```python
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
```

- [ ] **Step 4: 在 `llm_kb/review.py` 实现轻量 review 规则和草稿落盘**

至少实现：

- `should_require_review(...) -> bool`
- `make_draft_id(...) -> str`
- `create_pending_draft(...) -> PendingDraftResult`

约束：

- `paper` 和 `github` 默认返回 `True`
- 文本长度超过阈值时返回 `True`
- `force_review=True` 时一定进入确认模式
- 草稿文件写入 `inbox/pending/drafts/<draft_id>.md`

- [ ] **Step 5: 让阈值保持可解释且简单**

实现要求：

- 阈值先写成清晰常量，例如 `REVIEW_TEXT_LENGTH_THRESHOLD = 5000`
- 不做复杂模型或启发式打分

- [ ] **Step 6: 重跑 review 测试，确认转绿**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_review.py -q`  
Expected: PASS

- [ ] **Step 7: 提交这一阶段**

```bash
git add llm_kb/models.py llm_kb/review.py tests/test_review.py
git commit -m "feat: add pending draft review model and rules"
```

---

## Chunk 3：把确认模式接入现有 ingest 主链路

### 任务 3：为 `ingest-file` / `ingest-text` / `ingest-url` 增加 review-mode 分流

**Files:**
- Modify: `llm_kb/ingest.py`
- Modify: `tests/test_ingest.py`

- [ ] **Step 1: 先写失败测试，约束进入确认模式时的行为**

```python
def test_ingest_text_with_force_review_creates_pending_draft_not_final_entry(tmp_path: Path) -> None:
    initialize_workspace(tmp_path)

    result = ingest_text(
        root=tmp_path,
        text="x" * 100,
        title="Needs Review",
        content_type="note",
        source_kind="text",
        topics=["draft"],
        tags=["review"],
        review_mode="force",
    )

    assert result.mode == "pending_review"
    assert result.draft_path.exists()
    assert not (tmp_path / "notes" / "atomic" / "note-2026-04-needs-review.md").exists()


def test_ingest_url_auto_enters_review_for_paper(tmp_path: Path, monkeypatch) -> None:
    initialize_workspace(tmp_path)
    monkeypatch.setattr("llm_kb.ingest.fetch_url_text", lambda _: "body")

    result = ingest_url(
        root=tmp_path,
        url="https://example.com/paper",
        title="Paper URL",
        content_type="paper",
        source_kind="web",
        topics=[],
        tags=[],
    )

    assert result.mode == "pending_review"
    assert result.draft_path.exists()
```

- [ ] **Step 2: 运行 ingestion 相关测试，确认先失败**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_ingest.py tests/test_review.py -q`  
Expected: FAIL，提示 `review_mode` / `mode` / `draft_path` 尚未实现

- [ ] **Step 3: 扩展 `IngestResult` 以支持 pending 状态**

建议新增字段：

- `mode: str = "finalized"`
- `draft_id: str | None = None`
- `draft_path: Path | None = None`

### 任务 4：在 `llm_kb/ingest.py` 中实现 review 分流

**Files:**
- Modify: `llm_kb/ingest.py`

- [ ] **Step 1: 为三个 ingest 函数增加 `review_mode` 参数**

推荐取值：

- `"auto"`
- `"force"`
- `"off"`

默认：

- `review_mode="auto"`

- [ ] **Step 2: 在写正式条目之前做统一分流**

实现要求：

- `force`：一定创建 pending draft
- `off`：一定走现有正式入库
- `auto`：调用 `should_require_review(...)`

- [ ] **Step 3: review 模式下的来源文件写入策略**

要求：

- 来源副本先写到 `inbox/pending/sources/`
- 草稿写到 `inbox/pending/drafts/`
- 不创建正式 `notes/atomic/` 和 `registry/entries/`

- [ ] **Step 4: 正式模式保持现有行为不变**

必须确认：

- 原有 `ingest-file`
- 原有 `ingest-text`
- 原有 `ingest-url`

在 `review_mode="off"` 或无需确认时仍按原样写入正式库

- [ ] **Step 5: 运行 ingestion 相关测试**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_ingest.py tests/test_review.py -q`  
Expected: PASS

- [ ] **Step 6: 提交这一阶段**

```bash
git add llm_kb/ingest.py tests/test_ingest.py
git commit -m "feat: route complex ingests into pending drafts"
```

---

## Chunk 4：确认、修订、取消命令

### 任务 5：实现 `review-draft` / `confirm-draft` / `revise-draft` / `cancel-draft`

**Files:**
- Modify: `llm_kb/review.py`
- Modify: `llm_kb/cli.py`
- Modify: `tests/test_review.py`

- [ ] **Step 1: 先写失败测试，约束四个动作**

```python
def test_confirm_draft_promotes_pending_files_into_final_knowledge_base(tmp_path: Path) -> None:
    ...


def test_cancel_draft_marks_status_cancelled(tmp_path: Path) -> None:
    ...


def test_revise_draft_updates_type_and_tags(tmp_path: Path) -> None:
    ...
```

最少要覆盖：

- `confirm-draft` 会：
  - 把 pending source 复制或移动到正式 `sources/`
  - 写正式 `notes/atomic/`
  - 写正式 `registry/entries/`
  - 更新草稿状态为 `confirmed`
- `cancel-draft` 会把状态改成 `cancelled`
- `revise-draft --type` 会重算目标路径和 `proposed_entry_id`
- `revise-draft --tag` 会更新 `suggested_tags`
- `revise-draft --regenerate-summary` 至少能重写 `Summary` / `Core Claims` 占位内容

- [ ] **Step 2: 运行 review 测试，确认先失败**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_review.py -q`  
Expected: FAIL

- [ ] **Step 3: 在 `llm_kb/review.py` 中实现草稿读取与状态流转**

建议实现：

- `load_pending_draft(root, draft_id)`
- `review_draft(root, draft_id)`
- `confirm_draft(root, draft_id)`
- `cancel_draft(root, draft_id)`
- `revise_draft(root, draft_id, ...)`

约束：

- 只有 `pending_review` 状态允许转正
- 已 `confirmed` 或 `cancelled` 的草稿再次操作应给出清晰错误

- [ ] **Step 4: `confirm_draft` 必须复用现有正式写入逻辑**

实现建议：

- 尽量调用一个共享的“最终写入”辅助函数
- 不要复制整段 `note/registry` 写入逻辑两份

如果当前 `llm_kb/ingest.py` 没有合适复用点，可先提取一个小型私有 helper，再由正式路径和确认路径共享

- [ ] **Step 5: 在 `llm_kb/cli.py` 暴露四个子命令**

至少支持：

```bash
python -m llm_kb review-draft --root . --id draft-xxx
python -m llm_kb confirm-draft --root . --id draft-xxx
python -m llm_kb revise-draft --root . --id draft-xxx --tag memory --tag agents
python -m llm_kb revise-draft --root . --id draft-xxx --type blog
python -m llm_kb revise-draft --root . --id draft-xxx --regenerate-summary
python -m llm_kb cancel-draft --root . --id draft-xxx
```

- [ ] **Step 6: 运行 review 全量测试**

Run: `PYTHONPATH=./_vendor python -m pytest tests/test_review.py tests/test_ingest.py -q`  
Expected: PASS

- [ ] **Step 7: 提交这一阶段**

```bash
git add llm_kb/review.py llm_kb/cli.py tests/test_review.py
git commit -m "feat: add draft review confirmation workflow"
```

---

## Chunk 5：CLI 接口与文档

### 任务 6：把 review-mode 接入 CLI，并更新文档

**Files:**
- Modify: `llm_kb/cli.py`
- Modify: `README.md`
- Modify: `docs/usage.md`

- [ ] **Step 1: 为现有 ingest 命令增加 `--review`**

要求：

- `--review` 触发 `review_mode="force"`
- 不传则默认 `review_mode="auto"`

- [ ] **Step 2: 让 CLI 在 pending 结果下打印可操作信息**

至少输出：

- `draft_id`
- `draft_path`
- 推荐下一步动作，例如：
  - `review-draft`
  - `confirm-draft`
  - `revise-draft`
  - `cancel-draft`

- [ ] **Step 3: 更新 README**

新增内容：

- 什么是确认模式
- 什么时候会自动进入确认模式
- 如何用 `--review` 强制进入确认模式
- 如何 `review/confirm/revise/cancel`

- [ ] **Step 4: 更新 `docs/usage.md`**

至少增加一个完整示例：

```bash
python -m llm_kb ingest-url --root ./demo-kb --url "https://example.com/paper" --title "Demo Paper" --type paper --source-kind web
python -m llm_kb review-draft --root ./demo-kb --id draft-...
python -m llm_kb confirm-draft --root ./demo-kb --id draft-...
python -m llm_kb trace --root ./demo-kb --id paper-2026-04-demo-paper
```

- [ ] **Step 5: 核对 CLI help 与文档一致**

Run:

```bash
PYTHONPATH=./_vendor python -m llm_kb --help
PYTHONPATH=./_vendor python -m llm_kb review-draft --help
PYTHONPATH=./_vendor python -m llm_kb confirm-draft --help
PYTHONPATH=./_vendor python -m llm_kb revise-draft --help
PYTHONPATH=./_vendor python -m llm_kb cancel-draft --help
```

Expected: 所有命令和参数都真实存在，并与文档一致

- [ ] **Step 6: 提交这一阶段**

```bash
git add llm_kb/cli.py README.md docs/usage.md
git commit -m "docs: document pending draft review workflow"
```

---

## 验证清单

- [ ] `PYTHONPATH=./_vendor python -m pytest tests/test_bootstrap.py tests/test_frontmatter.py tests/test_ingest.py tests/test_registry.py tests/test_retrieve.py tests/test_review.py -q`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb init --root /tmp/llm-kb-review-smoke`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb ingest-text --root /tmp/llm-kb-review-smoke --title "Long Draft" --text "$(python - <<'PY'\nprint('x' * 6000)\nPY\n)" --type note --source-kind text`
- [ ] 确认输出包含 `draft_id` 和 `draft_path`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb review-draft --root /tmp/llm-kb-review-smoke --id <draft-id>`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb confirm-draft --root /tmp/llm-kb-review-smoke --id <draft-id>`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb ask --root /tmp/llm-kb-review-smoke --query "long draft"`
- [ ] `PYTHONPATH=./_vendor python -m llm_kb trace --root /tmp/llm-kb-review-smoke --id <final-entry-id>`
- [ ] 确认正式 `sources/`、`notes/atomic/`、`registry/entries/` 已生成，且 draft 状态变为 `confirmed`

---

## 本计划暂不覆盖的内容

- 批量列出所有待确认草稿
- 自动清理已取消草稿和待确认来源
- 多版本草稿 diff 展示
- 更复杂的自动摘要质量评估
- 图形化审批界面

这些能力应在确认模式主链路稳定后再单独规划。

---

## 交接说明

- 本计划默认在当前工作树 `.worktrees/llm-kb-mvp` 中实施。
- 实现时优先复用现有正式入库逻辑，不要为了确认模式复制整个 `ingest` 写入流程。
- 如果某一步发现 `llm_kb/ingest.py` 过于臃肿，可以做小规模提取，但不要顺手重构无关模块。
- 所有新增文档仍需保持中文，与当前仓库文档风格一致。
