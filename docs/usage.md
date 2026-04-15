# 使用文档

这份文档给出一个完整的本地工作流：初始化工作区、走确认模式入库、确认草稿、再用 `trace` 回看来源链路。

## 1. 什么是确认模式

确认模式是“先生成草稿，再决定是否转正”的入库方式。它会先把来源写到 `inbox/pending/sources/`，把草稿写到 `inbox/pending/drafts/`，等你确认后才正式生成 `notes/atomic/` 和 `registry/entries/`。

它适合这些场景：

- `paper` 和 `github` 类型，默认就会进入确认模式。
- 纯文本或网页快照内容较长时，当前阈值超过 5000 字符会进入确认模式。
- 你手动加 `--review` 时，会强制进入确认模式，不再走自动判断。

## 2. 初始化工作区

```bash
python -m llm_kb init --root ./demo-kb
```

执行后会创建目录树和模板文件，例如 `notes/atomic/`、`registry/entries/`、`templates/`，并为确认模式准备好 `inbox/pending/`。

## 3. 走一遍完整的确认模式流程

### 第一步：导入 URL

```bash
python -m llm_kb ingest-url \
  --root ./demo-kb \
  --url "https://example.com/article" \
  --title "Example Article" \
  --type blog \
  --source-kind web \
  --review
```

如果命中确认模式，CLI 会输出类似下面的信息：

```text
draft_id: draft-2026-04-15-blog-example-article
draft_path: /absolute/path/to/demo-kb/inbox/pending/drafts/draft-2026-04-15-blog-example-article.md
next: 先运行 `python -m llm_kb review-draft --root <root> --id draft-2026-04-15-blog-example-article`，再根据需要使用 `confirm-draft`、`revise-draft` 或 `cancel-draft`。
```

这一步不会生成正式的 `notes/atomic/` 和 `registry/entries/`。

### 第二步：查看草稿

```bash
python -m llm_kb review-draft \
  --root ./demo-kb \
  --id draft-2026-04-15-blog-example-article
```

你会看到草稿的摘要、核心论点，以及草稿元数据。这个命令适合先检查内容是否可靠，再决定下一步。

### 第三步：确认草稿

```bash
python -m llm_kb confirm-draft \
  --root ./demo-kb \
  --id draft-2026-04-15-blog-example-article
```

确认后会生成正式条目。之后 `trace` 要使用正式的 `entry_id`，不是 `draft_id`。

### 第四步：追踪来源

```bash
python -m llm_kb trace --root ./demo-kb --id blog-2026-04-example-article
```

典型输出：

```text
card_path: /absolute/path/to/demo-kb/notes/atomic/blog-2026-04-example-article.md
source_paths: ['/absolute/path/to/demo-kb/sources/blogs/example-article.html']
```

`trace` 的作用是把 registry 条目映射回卡片和原始来源，方便你检查这条知识是从哪里来的。

## 4. 草稿的其他操作

### `revise-draft`

用于修改草稿的内容类型、主题、标签，或者让系统重新生成摘要。

```bash
python -m llm_kb revise-draft \
  --root ./demo-kb \
  --id draft-2026-04-15-blog-example-article \
  --type blog \
  --topic agents \
  --tag memory \
  --regenerate-summary
```

### `cancel-draft`

用于取消一份草稿，保留历史状态但不让它继续进入正式知识库。

```bash
python -m llm_kb cancel-draft \
  --root ./demo-kb \
  --id draft-2026-04-15-blog-example-article
```

## 5. 如果你想看普通快速入库

不加 `--review` 时，`ingest-text` 这类命令会按自动规则决定是否进入确认模式。比如下面这个文本导入，在文本不长且类型不是强制确认时，会直接写正式条目：

```bash
python -m llm_kb ingest-text \
  --root ./demo-kb \
  --text "We should keep long-term memory in a registry-first knowledge base." \
  --title "Registry-first memory note" \
  --type note \
  --source-kind manual \
  --topic memory \
  --topic registry \
  --tag mvp
```

如果没有命中确认模式，系统会写出：

- `notes/atomic/<entry-id>.md`
- `registry/entries/<entry-id>.md`
- `sources/snapshots/<entry-id>.md`

## 6. 常见检查点

- 如果 `ask` 没返回结果，先确认条目已经成功导入，并且查询词和 `title`、`topics`、`tags` 或 `summary` 有交集。
- 如果 `trace` 报错，优先确认 `registry/entries/<id>.md` 是否存在。
- 如果你想看命令参数，直接运行 `python -m llm_kb <command> --help`。
