---
name: code-boundary-enforcer
description: Use on ANY task that edits source code — feature work, bug fixes, refactors, tests, or implementation triggered by another skill (e.g. $personal-requirements-workflow). Enforces a declared Code Boundary so AI cannot silently modify shared components, other modules, or out-of-bounds files. Skip ONLY for pure documentation edits, config files explicitly scoped by the user, or tasks that touch zero source files.
---

# Code Boundary Enforcer

## Overview

A discipline for keeping AI edits inside a declared scope. The risk this defends against: AI is asked to change module A, "helpfully" modifies a shared util or another module's file, and silently breaks unrelated screens.

**Two layers of defense:**
1. **Skill (this file)**: the SOP — list files before editing, route shared-code changes through a proposal, audit diff before completing.
2. **Hook (`check-code-boundary.py`)**: the enforcement — `PreToolUse(Edit|Write|NotebookEdit)` blocks edits outside boundary even if AI forgets the SOP.

This skill is the contract; the hook is the guard. Both read the same boundary declaration.

## Activation Rule

Activate whenever you are about to write or modify source code, regardless of the trigger:

| Trigger | What to do |
| --- | --- |
| Asked to implement a module spec (from $personal-requirements-workflow) | Use the module spec's `## Code Boundary` |
| Asked for a bug fix, refactor, or small change without a module spec | Look for project-level boundary at `.claude/rules/code-boundary.md` |
| No boundary declared anywhere | Pause: ask the user to declare boundary, or to explicitly waive enforcement for this task |

Skip activation only for:
- Pure markdown/doc edits with no code change
- Editing `.ai/` notes (private workspace, not source code)
- Tasks the user explicitly bounds ("just edit this single file: X")

## Boundary Sources (search order)

When activated, find the active Code Boundary in this order:

1. **Module spec**: `.ai/modules/<active-module>.md` → `## Code Boundary` section
   - "Active module" = the one the current task is implementing. If a module name was named in the task, use it. Otherwise look at the most recently modified spec in `.ai/modules/`.
2. **Project-level rule**: `.claude/rules/code-boundary.md`
   - Used when no module spec exists or the task is module-agnostic (bug fix, refactor).
3. **None found**: STOP, ask the user one of:
   - "What files am I allowed to edit for this task?" (then offer to write a quick `.ai/boundary.md` for this session)
   - "Is this task scoped to a single file? Confirm the path." (single-file waiver)
   - "Skip boundary enforcement this time? (Y/N — default N)"

Never proceed with edits when boundary is undeclared. The hook will block anyway; better to ask up front than be blocked mid-edit.

## Boundary Declaration Format

Whether in a module spec or `.claude/rules/code-boundary.md`, the boundary block looks like:

```md
## Code Boundary
- Owned (free to edit):
  - src/views/<module>/**
  - src/api/<module>.{js,ts}
  - src/types/<module>.{ts}
  - tests for the above
- Read-only references (use, but never modify):
  - src/components/**            # shared UI
  - src/utils/**, src/composables/**, src/hooks/**, src/store/**
  - any file outside src/views/<module>/
- Out-of-bounds (must not touch):
  - src/views/<other-modules>/**
  - package.json, build/config files, migrations, env files
  - any shared file — modifying these requires Shared Code Change Protocol
```

Patterns are glob-style relative to the directory containing the spec (or project root for `.claude/rules/code-boundary.md`). `**` matches recursively; `*` matches a single path segment.

## During Implementation — Three Rules

1. **List files before editing.** Before any `Edit` / `Write` / `NotebookEdit`, output:
   ```
   [PRE-EDIT FILE LIST]
   I plan to modify:
     - <abs path 1>
     - <abs path 2>
   Boundary source: <path to spec or rule>
   Boundary check: all in Owned ✓
   ```
   If any path is outside Owned, STOP and switch to the Shared Code Change Protocol.

2. **Treat shared as read-only by default.** Components in `src/components/`, utils in `src/utils/`, hooks/composables/store/types — all read-only unless you have explicit approval (via the protocol below). If the module needs different behavior, wrap with a module-local adapter.

3. **No drive-by edits.** Spotted a bug or smell in shared code or another module while working? Write one line to `.ai/inbox.md` and keep coding the current task. Do not "fix while you're there".

## Shared Code Change Protocol

When the task makes it genuinely necessary to modify a shared component, util, hook, store, type — or to add a new file inside any shared directory — STOP and run this protocol. Never edit silently.

**Why this matters**: shared code is a contract between modules. Changing it without review is the most common way a "small UI tweak" silently breaks unrelated screens.

### Steps

1. **Halt the edit.** Do not touch the shared file.
2. **Emit a proposal** in this exact shape:

```md
[SHARED CHANGE PROPOSAL]
File: <path, e.g. src/components/BaseTable.vue>
Change kind: modify | add-new-shared-file | remove | rename
Why this task needs it: <one line>
Proposed change: <code-level summary, not full diff>
Callers (run grep and paste):
  - src/views/order/OrderList.vue:42
  - src/views/user/UserList.vue:88
  - src/views/audit/AuditList.vue:15
Risk to each caller: <per-caller assessment — break, behavior change, or backward-compatible?>
Alternatives considered (without changing shared code):
  - Option A: wrap shared component in a task-local adapter
  - Option B: subclass / extend with task-local props
  - Option C: copy-paste the relevant code into the task scope
Recommendation: alternative | modify-shared | modify-shared + OpenSpec
Awaiting user decision.
```

3. **Wait for explicit approval.** Do not assume "no objection" = yes.
4. **If approved to modify shared code, OpenSpec is mandatory** for that change. Shared = contract = OpenSpec, even if the original task didn't need a spec.
5. **After modification, verify every caller still works** (build, type-check, smoke test). Record the verification in the OpenSpec proposal and (if a module spec exists) in its `## Change Log`.

### When the protocol applies

| Action | Protocol required? |
| --- | --- |
| Edit any file under `src/components/`, `src/utils/`, `src/composables/`, `src/hooks/`, `src/store/`, `src/types/` | Yes |
| Add a new file inside any shared directory above | Yes (new shared API surface = new contract) |
| Edit any file under another module's `src/views/<other>/**` | Yes (cross-module change is even stricter than shared) |
| Edit anything in `src/views/<current-module>/**` | No — that's Owned |
| Add a new file inside `src/views/<current-module>/**` | No — module-local |
| Edit `package.json`, build config, migrations, env files | Yes, always treat as shared/contract |

### Anti-patterns to refuse

- "It's just a tiny change to the shared util, no caller will notice." — Run the protocol anyway. AI cannot reliably predict caller behavior.
- "I'll add an optional prop with a default, so old callers are unaffected." — Still run the protocol. Optional props change type signatures and may surprise type-checkers downstream.
- "I'll create a new variant of the shared component for this task." — That's fine, but the variant lives inside `src/views/<module>/components/`, not in `src/components/`. If it must be shared from day one, run the protocol.

## Before Completion — Diff Audit

Before declaring the task complete:

1. Run `git diff --name-only`.
2. Cross-check every changed file against the active `## Code Boundary > Owned` patterns.
3. If any file is outside Owned, STOP and report:
   - Which files crossed boundary
   - Why
   - Whether to revert or formalize as a Shared Code Change Proposal (retroactively, with the protocol)
4. Only then declare done.

This is the bottom-line catch — even if you skipped the pre-edit check or the hook didn't fire, this audit catches silent crossings.

## How This Skill Cooperates with the Hook

The companion `check-code-boundary.py` hook (registered under `PreToolUse` for `Edit|Write|NotebookEdit`) reads the same boundary sources and blocks edits outside Owned. The relationship:

- **Skill present, hook present** (recommended): redundant safety. Skill keeps the workflow disciplined; hook catches lapses.
- **Skill present, hook missing**: the SOP still applies — you should self-audit before each edit. The hook is just the safety net.
- **Skill missing, hook present**: hook blocks but gives no graceful workflow. AI should still reason about boundaries even without the skill loaded.

If the hook blocks an edit, AI should read the stderr message, then immediately switch to the Shared Code Change Protocol — do not try to "work around" the block.

## Common Mistakes

- Starting to edit before listing files and confirming all are inside Owned.
- Treating "the hook blocked me" as a problem to bypass instead of a signal to run the Shared Code Change Protocol.
- Editing a shared component / util / hook / store inside task work without running the protocol. This is the #1 way a "simple feature" silently breaks other screens.
- Adding a new file under `src/components/` or `src/utils/` while implementing a task — new shared API surface is a contract addition; run the protocol.
- "Drive-by improvements" to files outside `Code Boundary > Owned`. If you spot a bug there, write it to `.ai/inbox.md` and keep coding the current task.
- Skipping the `git diff --name-only` self-audit before declaring done.
- Trying to enforce boundary without a declaration anywhere — ask the user to declare instead of guessing.

## Quick Reference

```
Before any edit:           List files → check against Owned → if outside, protocol
Need shared change:        Halt → [SHARED CHANGE PROPOSAL] → wait approval → OpenSpec
New file in shared dir:    Same as shared change (new API surface)
Other module's file:       Same as shared change (cross-module impact)
Hook blocks you:           Read stderr → switch to protocol → don't bypass
Before completion:         git diff --name-only → cross-check Owned → done
```
