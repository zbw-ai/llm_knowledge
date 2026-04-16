---
id: paper-2026-04-relax-an-asynchronous-reinforcement-learning-engine-for-omni-modal-post-training-at-scale
title: 'Relax: An Asynchronous Reinforcement Learning Engine for Omni-Modal Post-Training
  at Scale'
type: paper
source_kind: arxiv
created_at: '2026-04-16'
topics:
- post-training
- training-systems
tags:
- reinforcement-learning
- asynchronous-training
- multimodal
- omni-modal
authors: []
source_url: https://arxiv.org/html/2604.11554v2
local_source_paths:
- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/papers/paper-2026-04-relax-an-asynchronous-reinforcement-learning-engine-for-omni-modal-post-training-at-scale.html
status: distilled
importance: medium
related: []
---

# Summary

这篇论文提出了 Relax，一个面向 omni-modal 后训练的大规模异步强化学习引擎。作者认为，当 RL 从纯文本推理扩展到图像、音频、视频和多轮 agent workflow 时，训练系统会同时遇到三类耦合挑战：异构模态数据流、系统级鲁棒性，以及 staleness 与吞吐之间的权衡。

Relax 的核心思路是把这几个问题放到统一系统里协同解决：在全栈层面原生支持多模态数据和并行策略；把 rollout、训练等角色做成可独立扩缩容和故障隔离的服务；再通过 TransferQueue 和一个可调 staleness 参数，在 on-policy、near-on-policy 和 fully async 之间平滑切换。论文还报告了相对 veRL 和 colocate 模式的端到端加速，以及在 Qwen3-Omni 上的稳定收敛结果。

# Core Claims

- 当 RL 后训练扩展到 omni-modal 与 agentic 场景时，系统瓶颈不再只是算法本身，而是异构数据流、运行稳定性和异步训练一致性三者的联动问题。
- Relax 通过“omni-native 架构 + 服务化解耦 + 异步训练总线”的三层协同设计来解决这些问题，而不是在文本 RL 系统上做局部打补丁。
- TransferQueue 与 staleness 参数让系统能在 on-policy、near-on-policy 和 fully async 之间连续切换，从而显式管理吞吐和策略新鲜度之间的权衡。
- 相比 veRL 与 colocate 方案，Relax 在多个设置下实现了更高的端到端吞吐，同时保持相近的收敛奖励水平。
- Relax 不只面向文本 RL，也强调对图像、音频、视频和多轮 agent 任务的统一支撑，因此更接近“omni-modal post-training engine”而不是单一算法实现。

# Evidence

- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/papers/paper-2026-04-relax-an-asynchronous-reinforcement-learning-engine-for-omni-modal-post-training-at-scale.html

# Relevance

这篇论文适合放在“post-training / training systems / multimodal RL”这条知识脉络里，尤其适合对比同步式 RL 框架与异步服务化架构的取舍。

# My Thoughts

TBD

# Follow-ups

- TBD
