# LLM Knowledge Base MVP

这是一个面向本地知识沉淀的轻量 CLI 知识库。它的目标不是替代笔记软件，而是把来自文件、纯文本和 URL 的资料统一收进一个可检索、可追踪来源的 Markdown 知识库里，方便后续用 `ask` 和 `trace` 快速回溯。

## 仓库用途

这个仓库实现的是 LLM 知识库的 MVP：先把输入内容标准化为 `atomic` 卡片和 `registry` 条目，再用 `registry` 层做优先检索。它适合本地个人知识管理、研究素材整理、以及给后续的问答/总结流程提供稳定入口。

## 什么是确认模式

确认模式是一层“先落草稿、后转正”的保护网。命中确认模式后，`ingest-*` 不会直接写入正式的 `notes/atomic/` 和 `registry/entries/`，而是先生成 `inbox/pending/drafts/` 下的待确认草稿，并把原始来源放进 `inbox/pending/sources/`。你可以先用 `review-draft` 看内容，再决定要不要 `confirm-draft`、`revise-draft` 或 `cancel-draft`。

### 哪些场景会自动进入确认模式

当前 CLI 采用轻量规则自动判断：

- `paper` 和 `github` 类型默认进入确认模式。
- 纯文本或网页快照内容过长时会进入确认模式，当前阈值是 5000 个字符。
- 如果你显式加了 `--review`，一定进入确认模式，不再走自动判断。

如果没有命中上述规则，`ingest-*` 会继续按原来的快速入库路径直接写正式条目。

## 目录结构

初始化后，仓库会形成下面这些核心目录：

```text
inbox/               临时输入区，按链接和文件区分
sources/             原始来源副本，按类型分类存放
notes/atomic/        原子卡片，承载标准化摘要
notes/syntheses/     主题或阶段性的综合笔记
notes/topics/        主题笔记
registry/entries/    检索和追踪用的条目
registry/topics/     主题索引
registry/tags/       标签索引
registry/sources/    来源索引
registry/timelines/  时间线索引
templates/           初始化时写入的模板文件
docs/                使用说明和设计文档
```

## 快速开始

1. 初始化知识库目录：

```bash
python -m llm_kb init --root .
```

2. 把一份本地文件、文本或 URL 导入为标准化条目：

```bash
python -m llm_kb ingest-file --root . --source ./paper.pdf --title "Demo Paper" --type paper --source-kind arxiv
python -m llm_kb ingest-text --root . --text "..." --title "Demo Note" --type note --source-kind manual
python -m llm_kb ingest-url --root . --url "https://example.com" --title "Demo URL" --type blog --source-kind web
```

如果命中确认模式，命令会先打印 `draft_id` 和 `draft_path`，再提示你下一步先 `review-draft`。

3. 用 `ask` 查找最相关条目，用 `trace` 看来源链路：

```bash
python -m llm_kb ask --root . --query "demo paper"
python -m llm_kb trace --root . --id paper-2026-04-demo-paper
```

如果你是在当前仓库的开发环境里运行，通常会使用：

```bash
PYTHONPATH=./_vendor python -m llm_kb --help
```

## CLI 用法

### `init`

初始化工作区目录和模板文件。

```bash
python -m llm_kb init --root /path/to/kb
```

参数：

- `--root`：知识库根目录，默认是当前目录。

### `ingest-file`

导入本地文件，会复制原文件到 `sources/` 下，同时生成 `notes/atomic/` 和 `registry/entries/` 里的配套条目。

```bash
python -m llm_kb ingest-file \
  --root /path/to/kb \
  --source ./paper.pdf \
  --title "Scaling Laws for Demo" \
  --type paper \
  --source-kind arxiv \
  --topic agents \
  --tag memory
```

参数：

- `--source`：本地文件路径。
- `--title`：条目标题。
- `--type`：内容类型，当前实现会影响条目 ID 和来源目录。
- `--source-kind`：来源类型，例如 `arxiv`、`blog`、`manual`。
- `--topic`：可重复传入，写入 `topics`。
- `--tag`：可重复传入，写入 `tags`。
- `--review`：强制进入确认模式，直接生成待确认草稿。

### `ingest-text`

导入一段纯文本，适合把聊天记录、摘录、手工笔记直接收进知识库。

```bash
python -m llm_kb ingest-text \
  --root /path/to/kb \
  --text "This is a demo note." \
  --title "Demo Note" \
  --type note \
  --source-kind manual
```

参数与 `ingest-file` 类似，只是把 `--source` 换成了 `--text`。
- `--review`：强制进入确认模式。

### `ingest-url`

抓取 URL 内容并保存快照，同时生成对应卡片和 registry 条目。

```bash
python -m llm_kb ingest-url \
  --root /path/to/kb \
  --url "https://example.com/article" \
  --title "Example Article" \
  --type blog \
  --source-kind web
```

当前实现会把抓取到的页面内容存成快照文件，再写入知识库条目。
- `--review`：强制进入确认模式。

### `review-draft`

查看待确认草稿的摘要、核心论点和元数据。

```bash
python -m llm_kb review-draft --root /path/to/kb --id draft-2026-04-15-blog-demo-url
```

### `confirm-draft`

把待确认草稿正式转正，写入 `notes/atomic/`、`registry/entries/` 和对应的来源目录。

```bash
python -m llm_kb confirm-draft --root /path/to/kb --id draft-2026-04-15-blog-demo-url
```

### `revise-draft`

在草稿上调整内容类型、主题、标签，或者重新生成摘要。

```bash
python -m llm_kb revise-draft \
  --root /path/to/kb \
  --id draft-2026-04-15-blog-demo-url \
  --type blog \
  --topic agents \
  --tag memory \
  --regenerate-summary
```

### `cancel-draft`

取消一份待确认草稿，保留它的历史状态，避免误转正。

```bash
python -m llm_kb cancel-draft --root /path/to/kb --id draft-2026-04-15-blog-demo-url
```

### `ask`

按 `title`、`topics`、`tags`、`summary` 做本地检索，输出前几条匹配结果。

```bash
python -m llm_kb ask --root /path/to/kb --query "demo note" --limit 5
```

参数：

- `--query`：检索词。
- `--limit`：返回数量上限，默认 `5`。

### `trace`

根据条目 ID 查看对应卡片路径和来源路径。

```bash
python -m llm_kb trace --root /path/to/kb --id paper-2026-04-demo-paper
```

参数：

- `--id`：registry 条目 ID。

如果你刚刚走过确认模式，`trace` 要填的是 `confirm-draft` 之后生成的正式 `entry_id`，不是 `draft_id`。

## MVP 明确不做什么

这个版本刻意不做这些事情：

- 不做向量数据库，不做 embedding 检索。
- 不做多用户协作，不做权限管理。
- 不做自动同步到云端，不做在线服务。
- 不做复杂的编辑器插件集成。
- 不做自动生成高质量综述或自动验证内容正确性。
- 不把所有内容都变成“智能摘要”，而是先保证结构化收录和可追踪来源。

## 进一步阅读

- [使用文档](docs/usage.md)
- [实施计划](docs/superpowers/plans/2026-04-15-llm-knowledge-base-mvp.md)
