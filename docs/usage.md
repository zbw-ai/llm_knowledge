# 使用文档

下面给出一个从初始化到查询再到 `trace` 的完整 happy path。这个示例只依赖当前 CLI 已实现的命令。

## Happy Path

### 1. 初始化工作区

```bash
python -m llm_kb init --root ./demo-kb
```

执行后会创建目录树和模板文件，例如 `notes/atomic/`、`registry/entries/`、`templates/`。

### 2. 导入一段文本

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

导入完成后，系统会写出：

- `notes/atomic/<entry-id>.md`
- `registry/entries/<entry-id>.md`
- `sources/snapshots/<entry-id>.md`

### 3. 查询相关条目

```bash
python -m llm_kb ask --root ./demo-kb --query "registry memory"
```

一个典型输出大概长这样：

```text
id: note-2026-04-registry-first-memory-note
title: Registry-first memory note
summary: TBD
card_path: /absolute/path/to/demo-kb/notes/atomic/note-2026-04-registry-first-memory-note.md
```

`ask` 当前是对 `registry/entries/` 做本地文本匹配，优先看 `title`、`topics`、`tags` 和 `summary`。

### 4. 追踪来源

拿上一步输出的 `id`，或者直接用你知道的条目 ID：

```bash
python -m llm_kb trace --root ./demo-kb --id note-2026-04-registry-first-memory-note
```

典型输出：

```text
card_path: /absolute/path/to/demo-kb/notes/atomic/note-2026-04-registry-first-memory-note.md
source_paths: ['/absolute/path/to/demo-kb/sources/snapshots/note-2026-04-registry-first-memory-note.md']
```

`trace` 的作用就是把 registry 条目映射回卡片和原始来源，方便你检查这条知识是从哪里来的。

## 常见检查点

- 如果 `ask` 没返回结果，先确认条目已经成功导入，并且查询词和 `title`、`topics`、`tags` 或 `summary` 有交集。
- 如果 `trace` 报错，优先确认 `registry/entries/<id>.md` 是否存在。
- 如果你想看命令参数，直接运行 `python -m llm_kb <command> --help`。
