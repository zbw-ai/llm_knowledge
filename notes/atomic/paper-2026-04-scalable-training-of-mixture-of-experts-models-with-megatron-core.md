---
id: paper-2026-04-scalable-training-of-mixture-of-experts-models-with-megatron-core
title: Scalable Training of Mixture-of-Experts Models with Megatron Core
type: paper
source_kind: arxiv
created_at: '2026-04-15'
topics:
- moe
- training-systems
tags:
- mixture-of-experts
- megatron-core
- distributed-training
- fp8
- long-context
authors: []
source_url: https://arxiv.org/html/2603.07685v2
local_source_paths:
- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/papers/paper-2026-04-scalable-training-of-mixture-of-experts-models-with-megatron-core.html
status: distilled
importance: medium
related: []
---

# Summary

这篇技术报告聚焦于使用 Megatron Core 扩展 Mixture-of-Experts（MoE）模型训练。作者强调，MoE 的稀疏激活虽然能让总参数量增长得远快于每 token 计算量，但也会把压力同时推到内存、通信和计算三个系统维度，因此不能只优化单点，而需要整栈协同设计。

论文给出的方案覆盖内存、通信、计算和并行策略多个层面，包括更细粒度的重计算与卸载、优化后的 dispatcher 与重叠、Grouped GEMM、fusion、CUDA Graphs、多维并行的 Parallel Folding，以及对 FP8、NVFP4 和长上下文训练的支持。文中把这些能力组织成面向生产的大规模 MoE 训练框架，并报告了在 NVIDIA GB300 / GB200 上训练 DeepSeek-V3-685B 与 Qwen3-235B 时的高吞吐结果。

# Core Claims

- MoE 训练的核心系统难点不只是模型变大，而是稀疏激活导致内存、通信和计算之间形成耦合约束，必须做跨层协同优化。
- Megatron Core 通过整合内存优化、通信优化和计算优化，提供了一套面向大规模 MoE 训练的系统化实现。
- 这套框架支持更灵活的多维并行组织，包括 Parallel Folding，以及对低精度训练格式 FP8 和 NVFP4 的支持。
- 除了吞吐提升，作者也把长上下文训练作为一等公民纳入系统设计，而不是只针对常规上下文长度做优化。
- 作者将该系统定位为开源、可生产使用的 MoE 训练方案，适用于从数十亿到万亿参数、从小规模到数千 GPU 集群的训练场景。
- 论文的价值不只是单个技巧，而是解释这些技巧之间在系统层面的权衡和相互作用，给出可落地的扩展经验。

# Evidence

- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/papers/paper-2026-04-scalable-training-of-mixture-of-experts-models-with-megatron-core.html

# Relevance

Confirmed from a pending draft.

# My Thoughts

TBD

# Follow-ups

- TBD
