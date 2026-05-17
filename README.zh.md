# personal-ai-harness

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[English](./README.md) · **中文**

个人 AI harness 配置（Claude Code + agent skills + 强制执行的 hooks）。
单一来源，通过 git 在多台机器间同步。

> **公开分享这个仓库做什么？** 这是一个单人开发者驱动 Claude Code 的工作流：
> 用 skills 完成 **输入分类 → 写需求 spec → 用 hooks 强制代码编辑边界**。
> 它不是一个打磨过的产品——是一套个人在用的 harness。
> 欢迎 fork、抽取片段，或作为搭建你自己 harness 的参考。

## 为什么需要这个

agentic 工具里的 LLM **靠自己不可靠**，需要外层脚手架做到：
1. **路由**——根据输入选择正确的行为（skill 激活规则）。
2. **约束**——限制 AI 能改什么（Code Boundary hook 阻止越界写入）。
3. **状态外化**——把状态写到文件，而不是依赖对话上下文。
4. **可复现**——在不同机器之间通过仓库 + `./install.sh` 一键还原。

这就是 harness 范式：**信任框架，不信任模型本身**。本仓库是其中一种个人实现，针对 Claude Code。

## 前置要求

- macOS 或 Linux（路径用 Unix 风格的 `~/`；Windows 未测试）
- `git` 和 `python3`（3.10+，merger 和 hooks 需要）
- 已安装 [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- 可选：如果你使用 Anthropic agent SDK 的 `~/.agents/skills/` 目录布局。如果没有，`install.sh` 会自动创建。

## 仓库管理了哪些文件

```
home/                                     # install.sh 把这里的内容符号链接到 ~
├── .claude/
│   ├── scripts/                          # hook 脚本（可执行）
│   │   ├── check-code-boundary.py        # PreToolUse: 阻止越界编辑
│   │   └── inject-skill-on-input.py      # UserPromptSubmit: 输入是图片/目录时提醒
│   └── settings.hooks.json               # hooks 块，合并进 ~/.claude/settings.json
└── .agents/
    └── skills/
        ├── personal-requirements-workflow/
        └── code-boundary-enforcer/

examples/                                 # 不被符号链接——按需手动拷进项目
└── code-boundary.md                      # 项目级 boundary 模板

scripts/                                  # 仓库自用工具（不安装到系统）
└── merge-settings.py                     # 被 install.sh 调用，合并 hooks
```

## 哪些文件刻意不管（保留本地）

- `~/.claude/settings.json`——含 API token，仓库不接管，仅合并 hooks 进去。
- `~/.claude/settings.local.json`——本地覆盖。
- `~/.claude/sessions/`、`backups/`、`cache/`、`history.jsonl` 等——运行时状态。
- `~/.claude/skills/`——通过包管理器安装的社区 / Superpowers skills。
- `~/.agents/skills/` 下不是本仓库作者的其他 skills。

## 首次在一台新机器上安装

```bash
git clone <仓库地址> ~/personal-ai-harness
cd ~/personal-ai-harness
./install.sh
```

`install.sh` 做的事：
1. 把 `home/.agents/skills/` 下的每个 skill 符号链接到 `~/.agents/skills/`（冲突的会被备份）。
2. 把 `home/.claude/scripts/` 下的每个 hook 脚本符号链接到 `~/.claude/scripts/`（并赋可执行权限）。
3. 把 `home/.claude/settings.hooks.json` 里的 `hooks` 块合并进 `~/.claude/settings.json`，保留其余所有键（env、model、permissions）。原文件备份到旁边的 `settings.json.backup.<时间戳>`。

冲突备份落在 `~/.personal-ai-harness.backup.<时间戳>/`。

`install.sh` **不做**的事：
- 不动 `~/.claude/rules/`。Boundaries 是项目级的（见下文"为项目添加边界保护"）——如果在全局放规则，会错误地约束整个家目录的编辑。
- 不安装 `~/.claude/skills/` 下的社区 / Superpowers skills——那些由它们各自的包管理器维护。
- 不修改 `settings.local.json` 或任何运行时状态文件。

## 更新（改了 skill 或脚本之后）

直接 `git pull`。因为是符号链接，仓库里的改动立即生效，不需要重新安装。

## 编辑 skill 或 hook

直接编辑 `~/personal-ai-harness/` 里的文件（或顺着符号链接编辑——同一个文件）。满意了就 commit + push。

## 为项目添加边界保护

`check-code-boundary.py` hook 从当前工作目录向上找项目根（含 `.ai/` 或 `.claude/` 的目录，但遇到 `$HOME` 就停）。找到后，按顺序读取 `## Code Boundary`（先命中先用）：

1. `<project>/.ai/modules/<最新修改的>.md`——由 `personal-requirements-workflow` skill 写入。
2. `<project>/.claude/rules/code-boundary.md`——项目级默认，适合 bug 修复 / 重构这类工作。

要给项目加一个项目级 boundary，拷贝示例：

```bash
mkdir -p <你的项目>/.claude/rules
cp ~/personal-ai-harness/examples/code-boundary.md <你的项目>/.claude/rules/code-boundary.md
# 根据项目实际结构改 Owned / Out-of-bounds 路径
```

如果找不到任何 boundary 文件（或者当前不在任何项目里），hook 静默放行（allow）。Skill 会在编辑前提醒你声明 boundary。

## 卸载

```bash
./uninstall.sh
```

移除符号链接，并从 `settings.json` 摘掉 hooks 块（其他键保留）。`.personal-ai-harness.backup.*` 备份不会自动还原，需要手动 `mv` 回原位。

## 同步到另一台机器

```bash
# 机器 A
git push

# 机器 B
git clone <仓库地址> ~/personal-ai-harness
cd ~/personal-ai-harness
./install.sh
```

每台机器保留各自的 `~/.claude/settings.json`（含各自的 API token、env、代理）。install 只动 `hooks` 块。

## 约定

- 新增 skill：把目录放到 `home/.agents/skills/<name>/`，重跑 `./install.sh`。
- 新增 hook：脚本放 `home/.claude/scripts/`，在 `home/.claude/settings.hooks.json` 里注册，重跑 `./install.sh`。
- 新增示例规则文件：放 `examples/`（手动拷进项目使用——不会被符号链接）。

## 为什么用符号链接而不是拷贝

让仓库成为唯一来源。在任何编辑器里改一个 skill，改的就是仓库里的文件，`git status` 立刻告诉你哪些变了。不会出现两个位置的内容漂移。
