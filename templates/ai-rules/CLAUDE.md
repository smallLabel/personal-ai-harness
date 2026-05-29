# CLAUDE.md

本文件为 Claude Code 在此仓库中工作时提供指导。

## 通用规则

以下规则适用于所有 AI 助手（Claude Code、Codex 等），位于 `.ai/rules/`：

- [验证与检查](.ai/rules/verification.md) — 不主动跑 check / build / lint
- [AI 能力调用时机](.ai/rules/skills-invocation.md) — 新功能 / 调试前先检查可用能力
- [编码风格](.ai/rules/coding-style.md) — Vue / TS 通用约定
- [组件复用](.ai/rules/component-reuse.md) — 先搜后用，禁止重复实现
- [代码边界](.ai/rules/code-boundary.md) — Owned / Read-only / Out-of-bounds + 共享改动协议
- [UI 风格](.ai/rules/ui-style.md) — 原型图处理与视觉规范

## 项目专属

<!-- 按目标项目实际情况填写以下内容 -->

### 项目概述

技术栈、业务领域、关键依赖、后端 API 网关等。

### 常用命令

```bash
npm run dev              # 开发服务器
npm run build            # 构建
# ...
```

### 目录结构

```
src/
├── api/         # API 调用
├── views/       # 业务页面
├── components/  # 共享组件
├── stores/      # 状态管理
└── ...
```

### 组件清单

详细组件列表、props、暴露方法等。

### 模式：新增页面

按项目约定的新页面创建流程说明。

### 路径别名

`@` → `src/` 等别名说明。
