# AI 能力 / 技能调用规则

## 核心要求

开发任何新功能、页面、组件或修改业务行为前，先检查是否有适用的 AI 能力（Claude Code 的 Skill、Codex 的工具集、其它 MCP 工具等），再开始实现。

## 调用时机

- 收到新功能开发、页面搭建、组件实现、行为修改、问题修复等任务时，先判断是否有相关能力。
- 只要有可能适用，就先按该能力的流程执行，不要跳过。
- 多个能力同时适用时，**先流程类**（如 brainstorming、systematic-debugging、writing-plans），**再实现类**。

## 常见匹配

| 任务类型 | 优先使用 |
|---|---|
| 新功能 / UI 页面 | 先用 brainstorming 类能力对齐需求，再进入实现 |
| Vue 组件 / 页面 | Composition API + `<script setup lang="ts">` 规范 |
| 调试缺陷 | systematic-debugging：先复现 → 二分定位 → 修复 → 验证 |
| 多步任务 | writing-plans / planning：列计划再执行 |
| 大量并行子任务 | dispatching-parallel-agents 或类似并行能力 |
| 验证改动结果 | verification-before-completion |

> 具体能力名以 AI 工具当下提供的为准；本规则强调「调用时机」，不绑定特定工具。

## 与项目规则的关系

- AI 能力约束的是**工作流程**。
- 项目内的 `CLAUDE.md` / `AGENTS.md` 和 `.ai/rules/*.md` 是仓库**实现规范**。
- 冲突时优先级：**用户明确要求 > 项目规则 > AI 能力流程**。
