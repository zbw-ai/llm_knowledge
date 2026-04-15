# 确认模式入库设计方案

**日期：** 2026-04-15  
**状态：** 已在对话中确认方向，现整理为书面评审稿  
**范围：** 为现有 LLM 知识库 MVP 增加“待确认草稿”式入库流程，用于处理复杂来源或长内容

---

## 1. 目标

在现有快速入库主链路之外，增加一个轻量、可恢复、可审计的“确认模式”。

这个模式主要解决以下问题：

- 论文、GitHub、长网页等复杂内容不适合直接自动入正式库
- 长文本和元信息不完整内容需要用户先看一眼再确认
- 对话中断时，不能丢失已解析出的中间结果
- 用户需要用低摩擦的方式做少量修订，而不是重做整个入库流程

确认模式应保持以下特性：

- 仍然完全基于当前项目目录和 Markdown 文件
- 不引入数据库或额外服务
- 与现有 `ingest-file` / `ingest-text` / `ingest-url` 主链路兼容
- 对用户来说尽量流畅，默认只暴露少量高频动作

---

## 2. 设计原则

### 2.1 待确认内容与正式知识库分离

待确认内容不能直接写进 `notes/atomic/` 或 `registry/entries/`，否则会污染正式知识库。

### 2.2 中间状态必须可恢复

确认模式不能只存在于一次对话里。无论是网页解析结果、摘要草稿还是建议标签，都必须落盘。

### 2.3 优先支持少量高频修改

第一版不做复杂审批 UI，也不做逐字段确认。只支持：

- 确认
- 重生成摘要
- 修改标签
- 改类型
- 取消

### 2.4 自动触发规则必须透明

系统应使用可解释的启发式触发确认模式，而不是黑盒判断。

### 2.5 与快速入库共享底层逻辑

确认模式只是多了一层“草稿审核”，不应复制正式入库的底层实现。最终转正仍应复用现有的 `sources`、`notes`、`registry` 写入逻辑。

---

## 3. 推荐方案

采用 `pending draft` 文件式确认流程：

1. 输入内容进入系统
2. 系统判断是否需要确认模式
3. 如果需要：
   - 保存待确认来源副本
   - 生成待确认草稿文件
   - 向用户展示审核摘要
4. 用户通过半结构化动作确认或修订
5. 系统把草稿转正，写入正式知识库

这是一个介于“纯对话确认”和“重型工作流系统”之间的方案。

优点：

- 保留项目内可追踪状态
- 即使中断也可恢复
- 交互仍然足够自然
- 易于复用现有 CLI 和文件结构

---

## 4. 目录扩展

建议在现有 `inbox/` 下增加一层待确认区域：

```text
inbox/
  links/
  files/
  pending/
    drafts/
    sources/
```

### 4.1 `inbox/pending/drafts/`

用途：保存待确认草稿文件。

每一条待确认任务对应一个 Markdown 草稿，包含：

- 解析后的标题
- 来源信息
- 内容类型
- 建议主题和标签
- 草稿摘要
- 拟落盘路径
- 当前状态

### 4.2 `inbox/pending/sources/`

用途：保存待确认阶段的原始资料副本或网页快照。

规则：

- 还没确认之前，不写入正式 `sources/`
- 一旦确认，通过转正动作移动或复制到正式 `sources/`
- 若用户取消，保留或清理由后续策略决定，第一版可先保留并标记取消状态

---

## 5. 待确认草稿格式

每个待确认草稿建议用 Markdown + YAML frontmatter 表示。

示例结构：

```md
---
draft_id: draft-2026-04-15-paper-demo
status: pending_review
source_input: https://example.com/paper
source_kind: web
content_type: paper
title: Demo Paper
created_at: 2026-04-15
pending_source_paths:
  - /abs/path/to/inbox/pending/sources/draft-xxx.html
suggested_topics: [agents, memory]
suggested_tags: [planning, evaluation]
proposed_entry_id: paper-2026-04-demo-paper
proposed_note_path: /abs/path/to/notes/atomic/paper-2026-04-demo-paper.md
proposed_registry_path: /abs/path/to/registry/entries/paper-2026-04-demo-paper.md
preserve_source: true
---

# Summary

待确认摘要。

# Core Claims

- 观点 1
- 观点 2

# Review Actions

- confirm
- regenerate_summary
- update_tags
- change_type
- cancel
```

### 5.1 必备字段

第一版建议强制包含：

- `draft_id`
- `status`
- `source_input`
- `source_kind`
- `content_type`
- `title`
- `created_at`
- `pending_source_paths`
- `suggested_topics`
- `suggested_tags`
- `proposed_entry_id`
- `proposed_note_path`
- `proposed_registry_path`
- `preserve_source`

### 5.2 状态字段

建议支持以下状态：

- `pending_review`
- `confirmed`
- `cancelled`
- `superseded`

其中：

- `pending_review`：待用户审核
- `confirmed`：已转正
- `cancelled`：用户取消
- `superseded`：被后续草稿替代，例如重生成摘要后旧版本失效

---

## 6. 触发规则

本功能采用“双条件触发”：

- 来源复杂时触发
- 内容过长时触发

### 6.1 默认触发确认模式的情况

第一版建议：

- `content_type == paper`
- `content_type == github`
- URL 正文长度超过阈值
- 本地文本或文档长度超过阈值
- 一次输入包含多份材料
- 标题抽取困难或元信息缺失较严重

### 6.2 默认走快速入库的情况

- 短文本笔记
- 普通短网页
- 简单单文件输入
- 元信息清晰且内容长度较短

### 6.3 阈值策略

第一版应避免复杂启发式，只使用少量可解释规则，例如：

- `paper/github` 默认确认
- 文本长度超过 `4000-6000` 字符进入确认
- 标题缺失或抽取结果不可信时进入确认

这个阈值后续可以再调，但第一版应先保持简单且可解释。

---

## 7. 用户确认视图

你已经选择确认模式展示采用“标准版”：

- 标题
- 来源
- 摘要
- 建议主题 / 标签
- 核心观点
- 拟落盘路径
- 是否保留原文

因此，Codex 在展示待确认草稿时，默认应包含：

1. 草稿 ID
2. 标题与来源
3. 摘要
4. 核心观点
5. 建议主题与标签
6. 拟写入路径
7. 原始资料保留方式
8. 可执行动作

---

## 8. 用户动作设计

你已经选择确认交互采用“半结构化动作”。

第一版支持以下动作：

- `确认`
- `重生成摘要`
- `修改标签: ...`
- `改类型: ...`
- `取消`

### 8.1 `确认`

作用：

- 把待确认来源复制或移动到正式 `sources/`
- 生成正式 `notes/atomic/`
- 生成正式 `registry/entries/`
- 更新聚合索引
- 把草稿状态改为 `confirmed`

### 8.2 `重生成摘要`

作用：

- 保留原始资料和大部分元信息
- 仅重新生成 `Summary` 和 `Core Claims`
- 旧版本草稿可标为 `superseded`，新版本继续 `pending_review`

### 8.3 `修改标签`

作用：

- 仅更新 `suggested_tags`
- 不改变原始资料和内容类型

### 8.4 `改类型`

作用：

- 修改 `content_type`
- 重新计算 `proposed_entry_id`
- 重新计算正式 `sources/` 和条目落盘路径

### 8.5 `取消`

作用：

- 草稿状态改为 `cancelled`
- 不进入正式库
- 待确认来源文件保留或后续清理由第二阶段再决定

---

## 9. CLI 扩展建议

为了保持 MVP 轻量，只补充最小命令集合。

### 9.1 入库命令扩展

现有命令：

- `ingest-file`
- `ingest-text`
- `ingest-url`

建议增加一个通用参数：

- `--review`

含义：

- 强制进入确认模式
- 无论自动规则是否命中，都只生成待确认草稿，不直接转正

### 9.2 自动确认模式

如果用户没有显式传 `--review`，系统也可以根据规则自动决定：

- 若不需要确认：走现有快速入库
- 若需要确认：写入 `inbox/pending/` 并返回 `draft_id`

### 9.3 待确认草稿命令

建议增加：

- `review-draft --id <draft_id>`
- `confirm-draft --id <draft_id>`
- `revise-draft --id <draft_id> ...`
- `cancel-draft --id <draft_id>`

其中：

#### `review-draft`

展示草稿内容，用于重新查看待确认项。

#### `confirm-draft`

执行转正，写入正式知识库。

#### `revise-draft`

第一版只支持少量参数：

- `--regenerate-summary`
- `--type`
- `--topic`
- `--tag`

#### `cancel-draft`

把草稿状态改为 `cancelled`。

---

## 10. 与对话式交互的关系

虽然底层是 CLI + 文件工作流，但你主要仍会通过 Codex 对话来驱动。

因此建议这样映射：

- 用户说“先让我确认一下”  
  Codex 使用 `--review` 或自动进入确认模式

- 用户说“确认”  
  Codex 调用 `confirm-draft`

- 用户说“改标签为 xxx”  
  Codex 调用 `revise-draft --tag ...`

- 用户说“改成 blog 类型”  
  Codex 调用 `revise-draft --type blog`

- 用户说“重生成摘要”  
  Codex 调用 `revise-draft --regenerate-summary`

- 用户说“取消”  
  Codex 调用 `cancel-draft`

也就是说，对用户来说仍是自然对话；对系统来说，则是一个具备状态和落盘能力的工作流。

---

## 11. 推荐实现顺序

### 第一阶段：生成 draft

实现：

- 判断是否进入确认模式
- 保存待确认来源
- 生成 `inbox/pending/drafts/*.md`

### 第二阶段：确认 / 取消

实现：

- `confirm-draft`
- `cancel-draft`
- 草稿状态流转

### 第三阶段：修订

实现：

- `重生成摘要`
- `修改标签`
- `改类型`

这样既能快速建立闭环，也不会一次做太重。

---

## 12. 风险与缓解

### 风险 1：待确认区堆积

如果用户长期不确认，`pending` 区可能越积越多。

缓解方式：

- 第一版先接受这个现实
- 后续再补“列出所有待确认草稿”和简单清理能力

### 风险 2：草稿和正式条目重复

如果确认时没有做好状态控制，可能会重复转正。

缓解方式：

- 只允许 `pending_review` 状态转正
- 转正后将草稿状态更新为 `confirmed`

### 风险 3：重生成摘要导致版本混乱

如果反复重生成，草稿版本可能变乱。

缓解方式：

- 第一版可以原地覆盖
- 或把旧版本标成 `superseded`

### 风险 4：自动触发过多或过少

阈值设置不合适会让确认模式打扰用户，或漏掉复杂材料。

缓解方式：

- 第一版保持简单规则
- 后续根据实际使用再调阈值

---

## 13. 最终建议

确认模式入库的第一版，应是：

- 项目内落盘
- Markdown 草稿
- 半结构化用户动作
- 启发式触发
- 与现有快速入库共享转正逻辑

这是一个足够轻、但已经有状态管理和恢复能力的方案。

它能在不把系统做重的前提下，显著提高复杂内容入库的质量和可控性。

---

## 14. 下一步

在评审通过后，把本设计拆成新的中文实施计划，明确：

- 需要新增的目录和模板
- `draft` 数据模型
- 自动触发逻辑
- `review/confirm/revise/cancel` 命令
- 测试与 smoke path
