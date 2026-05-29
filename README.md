# personal-ai-harness

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**English** · [中文](./README.zh.md)

Personal AI-harness configuration (Claude Code + agent skills + enforcement hooks).
Single source of truth, syncable across machines via git.

> **Sharing this publicly?** This repo captures a single developer's workflow for
> driving Claude Code with skills that **classify input → write requirement specs →
> enforce code-edit boundaries via hooks**. It's not a polished product — it's a
> working personal harness. Fork it, copy parts, or use it as a reference for
> building your own.

## Why this exists

LLMs inside agentic tools are *not* reliable on their own — they need scaffolding
that:
1. **Routes** the right behavior for the right input (skill activation rules).
2. **Constrains** what edits AI can make (Code Boundary hooks block out-of-scope writes).
3. **Externalizes state** to files instead of relying on the chat context.
4. **Reproduces** across machines (this repo + `./install.sh`).

This is the harness paradigm: trust the framework, not the model. The repo
contains one personal take on it, focused on Claude Code.

## Prerequisites

- macOS / Linux / Windows (Windows needs Git Bash + Python 3; paths still use Unix-style `~/`. Hook handles Windows-specific encoding and path-separator quirks.)
- `git` and `python3` (3.10+, for the merger + hooks)
- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) installed
- Optional: an `~/.agents/skills/` directory if you use the Anthropic agent SDK
  layout. If you don't have it, `install.sh` creates it.

## What's managed

```
home/                                     # symlinked into ~ by install.sh
├── .claude/
│   ├── scripts/                          # hook scripts (executable)
│   │   ├── check-code-boundary.py        # PreToolUse: block edits outside Code Boundary
│   │   └── inject-skill-on-input.py      # UserPromptSubmit: hint when input is image/dir
│   └── settings.hooks.json               # hooks block merged into ~/.claude/settings.json
└── .agents/
    └── skills/
        ├── personal-requirements-workflow/
        └── code-boundary-enforcer/

examples/                                 # NOT symlinked — copy into your projects manually
└── code-boundary.md                      # single-file boundary example (superseded by templates/, kept for reference)

templates/                                # project-level templates (NOT symlinked — installed via install-rules.sh)
└── ai-rules/                             # cross-tool (Claude Code / Codex) AI rules
    ├── CLAUDE.md                         # project entry (Claude Code auto-loads)
    ├── AGENTS.md                         # project entry (Codex auto-loads)
    └── rules/                            # 6 rule files installed into <project>/.ai/rules/

scripts/                                  # repo tooling (not installed)
└── merge-settings.py                     # used by install.sh to merge hooks
```

## What's NOT managed (intentionally local)

- `~/.claude/settings.json` — contains API tokens. Hooks are merged in, secrets stay local.
- `~/.claude/settings.local.json` — local overrides.
- `~/.claude/sessions/`, `backups/`, `cache/`, `history.jsonl`, etc. — runtime state.
- `~/.claude/skills/` — community / Superpowers skills installed via package manager.
- Other skills in `~/.agents/skills/` not authored here.

## Install (first time on a machine)

```bash
git clone <this-repo> ~/personal-ai-harness
cd ~/personal-ai-harness
./install.sh
```

What `install.sh` does:
1. Symlinks each skill from `home/.agents/skills/` into `~/.agents/skills/` (backing up any conflict).
2. Symlinks each hook script from `home/.claude/scripts/` into `~/.claude/scripts/` (makes them executable).
3. Merges `home/.claude/settings.hooks.json`'s `hooks` block into `~/.claude/settings.json`, preserving all other keys (env, model, permissions). Backs up the original to `settings.json.backup.<timestamp>` next to it.

Conflict backups land in `~/.personal-ai-harness.backup.<timestamp>/`.

What `install.sh` does NOT do:
- Touch `~/.claude/rules/`. Boundaries are project-scoped (see "Add boundary protection to a project" below) — installing a global rule would mistakenly constrain edits across your home dir.
- Install community / Superpowers skills under `~/.claude/skills/` — those are managed separately by their own package manager.
- Modify `settings.local.json` or any state file.

## Update (after editing skills or scripts)

Just `git pull`. Because everything is symlinked, edits in the repo are live.

## Edit a skill or hook

Edit the file inside `~/personal-ai-harness/` (or follow the symlink — same thing). Commit and push when satisfied.

## Add boundary protection to a project

The `check-code-boundary.py` hook walks up from CWD looking for a project root
(a directory that contains `.ai/` or `.claude/`, but stops if it reaches `$HOME`).
Once found, it reads `## Code Boundary` from one of these (first hit wins):

1. `<project>/.ai/modules/<most-recently-modified>.md` — written by the
   `personal-requirements-workflow` skill.
2. `<project>/.claude/rules/code-boundary.md` — legacy location; auto-loaded
   into every Claude Code session as project instructions.
3. `<project>/.ai/rules/code-boundary.md` — preferred location; **not** auto-loaded
   (AI Reads on-demand), so it doesn't bloat session context. See `install-rules.sh`.

To add a project-wide boundary, copy the bundled example:

```bash
# Simple (single-file example):
mkdir -p <your-project>/.claude/rules
cp ~/personal-ai-harness/examples/code-boundary.md <your-project>/.claude/rules/code-boundary.md
# edit the paths to match the project

# Preferred: install the full rules template (see below)
```

Without any boundary file (or outside any project), the hook is a silent no-op
(allows). The skill prompts you to declare a boundary before editing if one is
expected but missing.

## Install project-wide AI rules

Beyond the single-file boundary, this repo ships a **cross-tool (Claude Code +
Codex) project-level rules template** at `templates/ai-rules/`, covering:

- Verification (don't auto-run check / lint / build)
- When to invoke AI skills / capabilities
- Coding style (Vue / TS baseline)
- Component reuse (search before implementing)
- Full code-boundary declaration (with Shared Code Change Protocol)
- UI style (how to treat design mockups)
- `CLAUDE.md` / `AGENTS.md` entry files (recognized by both Claude Code and Codex)

One-line install into a target project:

```bash
~/personal-ai-harness/install-rules.sh /path/to/your-project
# or from inside the project dir:
~/personal-ai-harness/install-rules.sh
```

**Why not under `.claude/rules/`?** Rule files land in `<project>/.ai/rules/`,
so they are **NOT auto-loaded into every Claude Code session** — they get Read
on-demand only when relevant. Saves ~2000 tokens per session. `CLAUDE.md` and
`AGENTS.md` are only created if missing (never overwrite a project's own entry).

After installing, you need to fill in:
1. The "project-specific" section in `CLAUDE.md` / `AGENTS.md` (stack, commands, layout).
2. The actual path globs in `.ai/rules/code-boundary.md`.
3. (Optional) Prettier / ESLint values in `.ai/rules/coding-style.md`.

### Let AI install + auto-configure (recommended)

Paste the prompt below to Claude Code / Codex inside a fresh project session. It will run the installer, read the project's actual structure, and fill in the project-specific bits for you:

```
Help me install personal-ai-harness AI rules into this project. 3 steps:

1. Run the installer: bash ~/personal-ai-harness/install-rules.sh .

2. The installer drops CLAUDE.md / AGENTS.md at the project root plus 6
   rule files under .ai/rules/. Read the actual project state and fill
   them in:

   a. Look at package.json, project root layout, and src/ structure. Replace
      the 'project-specific' placeholder section in CLAUDE.md with real
      content (stack, common commands, directory layout, path aliases).

   b. Simplify AGENTS.md to a one-line pointer at CLAUDE.md (single source
      of truth), or mirror the project-specific section across. Pick one.

   c. Rewrite the three path-glob buckets in .ai/rules/code-boundary.md to
      match this project's actual directories:
      - Owned:        view pages, domain-grouped api/store/i18n, docs, AI workspace
      - Read-only:    shared components, hooks, utils, layouts, global styles/
                      config/types/routes, entry files
      - Out-of-bounds: package.json/lockfiles, build configs (vite/webpack/
                      tsconfig), .env*, CI, scripts, dist, node_modules

   d. Look at .prettierrc / .eslintrc. If they differ from the template
      defaults, adjust numbers in .ai/rules/coding-style.md (printWidth,
      quotes, indent). If this is a React/Svelte/pure Node project, strip
      Vue-specific clauses and substitute the right stack's baseline.

3. When done, report:
   - Which files were created/modified
   - One-sentence summary of CLAUDE.md's project-specific section AND of
     each boundary bucket
   - Any edge files you can't confidently classify

Constraints:
- Don't proactively run npm install / build / lint (per .ai/rules/verification.md)
- Don't git commit before you're done
- For unclear classifications, list them and ask me — don't guess
```

Adjust for project type (add to the prompt):

| Project type | Add |
|---|---|
| Vue + Element/Antd | Nothing — defaults match |
| React + Next/Remix | In step 2.d, swap Vue clauses for React (Composition API → Hooks/Effects) |
| Node backend / pure lib | In step 2.d, drop UI-specific rules (component-reuse / ui-style), keep boundary / verification / coding-style |
| Monorepo | In step 2.c, scope the boundary per workspace — list each package's Owned separately |

## Uninstall

```bash
./uninstall.sh
```

Removes symlinks and (optionally, with `--restore`) puts backups back.

## Sync to another machine

```bash
# on machine A
git push

# on machine B
git clone <this-repo> ~/personal-ai-harness
cd ~/personal-ai-harness
./install.sh
```

Each machine keeps its own `~/.claude/settings.json` (with its own API tokens, env, proxy). Only the `hooks` block is touched by install.

## Conventions

- New skills: drop the directory into `home/.agents/skills/<name>/`, re-run `./install.sh`.
- New hooks: add script to `home/.claude/scripts/`, register in `home/.claude/settings.hooks.json`, re-run `./install.sh`.
- New example rule files: add to `examples/` (manual copy into projects — not symlinked).
- Modify / add shared rule templates: edit under `templates/ai-rules/rules/`. Any project that ran `install-rules.sh` can re-run it to pull the latest (re-runs only overwrite rule files, never `CLAUDE.md` / `AGENTS.md`).

## Why symlinks instead of copies

So that the repo is the single source of truth. Editing a skill in any editor edits the file in the repo, and `git status` shows you what changed. No two-place drift.
