# dotfiles-ai

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

- macOS or Linux (paths assume Unix-style `~/`; Windows not tested)
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
└── code-boundary.md                      # project-level boundary template

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
git clone <this-repo> ~/dotfiles-ai
cd ~/dotfiles-ai
./install.sh
```

What `install.sh` does:
1. Symlinks each skill from `home/.agents/skills/` into `~/.agents/skills/` (backing up any conflict).
2. Symlinks each hook script from `home/.claude/scripts/` into `~/.claude/scripts/` (makes them executable).
3. Merges `home/.claude/settings.hooks.json`'s `hooks` block into `~/.claude/settings.json`, preserving all other keys (env, model, permissions). Backs up the original to `settings.json.backup.<timestamp>` next to it.

Conflict backups land in `~/.dotfiles-ai.backup.<timestamp>/`.

What `install.sh` does NOT do:
- Touch `~/.claude/rules/`. Boundaries are project-scoped (see "Add boundary protection to a project" below) — installing a global rule would mistakenly constrain edits across your home dir.
- Install community / Superpowers skills under `~/.claude/skills/` — those are managed separately by their own package manager.
- Modify `settings.local.json` or any state file.

## Update (after editing skills or scripts)

Just `git pull`. Because everything is symlinked, edits in the repo are live.

## Edit a skill or hook

Edit the file inside `~/dotfiles-ai/` (or follow the symlink — same thing). Commit and push when satisfied.

## Add boundary protection to a project

The `check-code-boundary.py` hook walks up from CWD looking for a project root
(a directory that contains `.ai/` or `.claude/`, but stops if it reaches `$HOME`).
Once found, it reads `## Code Boundary` from one of these (first hit wins):

1. `<project>/.ai/modules/<most-recently-modified>.md` — written by the
   `personal-requirements-workflow` skill.
2. `<project>/.claude/rules/code-boundary.md` — project-wide default, useful for
   bug-fix / refactor work.

To add a project-wide boundary, copy the bundled example:

```bash
mkdir -p <your-project>/.claude/rules
cp ~/dotfiles-ai/examples/code-boundary.md <your-project>/.claude/rules/code-boundary.md
# edit the paths to match the project
```

Without any boundary file (or outside any project), the hook is a silent no-op
(allows). The skill prompts you to declare a boundary before editing if one is
expected but missing.

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
git clone <this-repo> ~/dotfiles-ai
cd ~/dotfiles-ai
./install.sh
```

Each machine keeps its own `~/.claude/settings.json` (with its own API tokens, env, proxy). Only the `hooks` block is touched by install.

## Conventions

- New skills: drop the directory into `home/.agents/skills/<name>/`, re-run `./install.sh`.
- New hooks: add script to `home/.claude/scripts/`, register in `home/.claude/settings.hooks.json`, re-run `./install.sh`.
- New rule files: add to `home/.claude/rules/`, re-run `./install.sh`.

## Why symlinks instead of copies

So that the repo is the single source of truth. Editing a skill in any editor edits the file in the repo, and `git status` shows you what changed. No two-place drift.
