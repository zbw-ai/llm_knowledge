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
card_path: /Users/zengbw/Codebase/for_funny_code/llm_knowledge/notes/atomic/paper-2026-04-scalable-training-of-mixture-of-experts-models-with-megatron-core.md
source_paths:
- /Users/zengbw/Codebase/for_funny_code/llm_knowledge/sources/papers/paper-2026-04-scalable-training-of-mixture-of-experts-models-with-megatron-core.html
source_url: https://arxiv.org/html/2603.07685v2
summary: "\u8FD9\u7BC7\u6280\u672F\u62A5\u544A\u805A\u7126\u4E8E\u4F7F\u7528 Megatron\
  \ Core \u6269\u5C55 Mixture-of-Experts\uFF08MoE\uFF09\u6A21\u578B\u8BAD\u7EC3\u3002\
  \u4F5C\u8005\u5F3A\u8C03\uFF0CMoE \u7684\u7A00\u758F\u6FC0\u6D3B\u867D\u7136\u80FD\
  \u8BA9\u603B\u53C2\u6570\u91CF\u589E\u957F\u5F97\u8FDC\u5FEB\u4E8E\u6BCF token \u8BA1\
  \u7B97\u91CF\uFF0C\u4F46\u4E5F\u4F1A\u628A\u538B\u529B\u540C\u65F6\u63A8\u5230\u5185\
  \u5B58\u3001\u901A\u4FE1\u548C\u8BA1\u7B97\u4E09\u4E2A\u7CFB\u7EDF\u7EF4\u5EA6\uFF0C\
  \u56E0\u6B64\u4E0D\u80FD\u53EA\u4F18\u5316\u5355\u70B9\uFF0C\u800C\u9700\u8981\u6574\
  \u6808\u534F\u540C\u8BBE\u8BA1\u3002\n\n\u8BBA\u6587\u7ED9\u51FA\u7684\u65B9\u6848\
  \u8986\u76D6\u5185\u5B58\u3001\u901A\u4FE1\u3001\u8BA1\u7B97\u548C\u5E76\u884C\u7B56\
  \u7565\u591A\u4E2A\u5C42\u9762\uFF0C\u5305\u62EC\u66F4\u7EC6\u7C92\u5EA6\u7684\u91CD\
  \u8BA1\u7B97\u4E0E\u5378\u8F7D\u3001\u4F18\u5316\u540E\u7684 dispatcher \u4E0E\u91CD\
  \u53E0\u3001Grouped GEMM\u3001fusion\u3001CUDA Graphs\u3001\u591A\u7EF4\u5E76\u884C\
  \u7684 Parallel Folding\uFF0C\u4EE5\u53CA\u5BF9 FP8\u3001NVFP4 \u548C\u957F\u4E0A\
  \u4E0B\u6587\u8BAD\u7EC3\u7684\u652F\u6301\u3002\u6587\u4E2D\u628A\u8FD9\u4E9B\u80FD\
  \u529B\u7EC4\u7EC7\u6210\u9762\u5411\u751F\u4EA7\u7684\u5927\u89C4\u6A21 MoE \u8BAD\
  \u7EC3\u6846\u67B6\uFF0C\u5E76\u62A5\u544A\u4E86\u5728 NVIDIA GB300 / GB200 \u4E0A\
  \u8BAD\u7EC3 DeepSeek-V3-685B \u4E0E Qwen3-235B \u65F6\u7684\u9AD8\u541E\u5410\u7ED3\
  \u679C\u3002"
---

