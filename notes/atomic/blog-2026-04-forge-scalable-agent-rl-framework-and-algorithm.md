---
id: blog-2026-04-forge-scalable-agent-rl-framework-and-algorithm
title: 'Forge: Scalable Agent RL Framework and Algorithm'
type: blog
source_kind: web
created_at: '2026-04-15'
topics:
- agents
- post-training
tags:
- agent-rl
- context-management
- cispo
- training-systems
authors: []
source_url: https://www.minimax.io/news/forge-scalable-agent-rl-framework-and-algorithm
local_source_paths:
- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/blogs/blog-2026-04-forge-scalable-agent-rl-framework-and-algorithm.html
status: distilled
importance: medium
related: []
---

# Summary

这篇 MiniMax 博文介绍了内部 Agent RL 框架 Forge，核心目标是同时优化系统吞吐、训练稳定性和 agent 灵活性，解决复杂真实世界 agent 场景下的大规模强化学习“三难困境”。

文中给出的主线是：用中间件式架构把 agent 侧与训练/推理侧解耦，支持 white-box 与 black-box agent；再通过 Windowed FIFO、Prefix Tree Merging、推理加速和 CISPO 等设计，提升长时程 agent 训练的吞吐、稳定性和泛化能力。文章还强调将 Context Management 直接纳入 RL 交互环路，以减少 inference-training mismatch，并支撑 MiniMax M2.5 在大规模真实 agent scaffold 上训练。

# Core Claims

- 复杂 agent 的大规模 RL 训练受制于系统吞吐、训练稳定性和 agent 灵活性三者之间的结构性张力，Forge 的目标是同时缓解这三方面约束。
- Forge 采用中间件式架构，把 Agent Side、Middleware、Training/Inference Side 解耦，从而支持 white-box 与 black-box agent，并提升跨 scaffold 的泛化能力。
- 在 white-box agent 场景下，文章主张把 Context Management 作为显式动作纳入 RL 训练环路，以减少上下文切换带来的训练-推理分布偏移。
- 在 black-box agent 场景下，Forge 通过对 agent 内部实现保持无侵入，支持异构 agent scaffold、复杂内部 loop 和上下文改写策略。
- 工程层面通过 Windowed FIFO、Prefix Tree Merging 和极致推理加速来缓解 rollout 时延差异、前缀冗余和训练效率问题。
- 算法层面以 CISPO 和效率感知奖励为核心，尝试在长时程 agent 任务中改善 credit assignment、优化稳定性和训练效率。

# Evidence

- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/blogs/blog-2026-04-forge-scalable-agent-rl-framework-and-algorithm.html

# Relevance

Confirmed from a pending draft.

# My Thoughts

TBD

# Follow-ups

- TBD
