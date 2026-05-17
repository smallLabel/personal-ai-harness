---
name: personal-requirements-workflow
description: Use when the user introduces a new module, a new feature for an existing module, or any change that touches a contract (data shape, API, shared component). Inputs may be a single image, a Figma/screenshot, plain text, OR a directory of prototype files (mockups, design tokens, notes). Trigger is "new structure / contract change", NOT "input is an image" — style tweaks, bug screenshots, and copy fixes go straight to Superpowers with no spec. On any input, classify first (and triage if a directory) before producing a micro-spec or OpenSpec proposal. Implementation phase delegates code-edit discipline (boundary, shared-change protocol, diff audit) to $code-boundary-enforcer. Single-developer workflow, not team collaboration.
---

# Personal Requirements Workflow

## Overview

A private, lightweight requirements loop for a solo developer. Keep messy discovery local in `.ai/`, turn only stable decisions into code and tests. Nothing here is meant for team coordination — there are no escalations, PR-note promotions, or "share with team" gates.

Core rule: do not mix requirement discovery with implementation flow. Capture discoveries quickly, batch decisions, and implement from a small module micro-spec.

**Scope of this skill**: requirements capture + spec authoring. **Code-edit discipline (boundary checks, shared-change protocol, diff audit) is delegated to `$code-boundary-enforcer`** — this skill writes the `## Code Boundary` section in each module spec, and the enforcer reads it during implementation.

## Activation Rule (when to use this skill at all)

The trigger is **change nature**, not input type. Images are not enough — a screenshot can be "new feature" or "color tweak", they need different treatment.

**Step 0 (mandatory): classify first, confirm with me, then proceed.**

On any input (text, image, or both), produce one sentence:

```
Classification: [new-module | incremental | local-mod | unsure] — <one-line reason>
Proposed path: <full skill flow | update existing spec | straight to Superpowers | need your decision>
```

Wait for my "go" before doing anything else. Never assume.

### The three buckets

| Bucket | What it looks like | What you do |
| --- | --- | --- |
| **new-module** | Brand new page / module / feature with no existing `.ai/modules/<name>.md`; introduces new data shape, API, or interaction flow | Full skill flow → create `.ai/modules/<name>.md` → **produce OpenSpec proposal** → wait for approval |
| **incremental** | Existing module already has `.ai/modules/<name>.md`; this change adds a field, filter, action, or behavior to it | **Update the existing micro-spec** (add to `## Change Log`, extend Hidden Requirements / Acceptance / States as needed). **Do NOT open a new OpenSpec proposal** unless this change modifies a contract (data shape, API, shared component, cross-module behavior) — in that case open OpenSpec |
| **local-mod** | Style tweak, color/spacing/copy change, single bug fix, refactor with no new requirement, visual diff comparison | **Do NOT use this skill.** Skip spec entirely. Go straight to the relevant Superpowers skill (test-driven-development, systematic-debugging, webapp-testing, verification-before-completion, etc.) |

### Key rules

- **OpenSpec opens only when a contract changes.** Data shape, API surface, shared component behavior, cross-module impact = contract. Adding a filter to a private module table is NOT a contract change.
- **"Image input" ≠ "use this skill".** A screenshot showing a button color problem is `local-mod`; a Figma draft of a brand new page is `new-module`.
- **Directory input is different — triage first, then classify per module.** If the input is a folder path (mockup directory, Figma export, prototype project), run the Directory Triage flow (see below) BEFORE Step 0 classification. Triage splits the directory into one-or-more module candidates plus any project-level content; you then classify each candidate separately.
- **When in doubt, output `unsure` and list the two paths so I can pick.** Never silently default to the heavier path.

## Directory Triage (when input is a folder of prototype files)

When the input is a directory path rather than a single image or text, do NOT skip ahead to Step 0 classification. The directory may map to multiple modules or contain project-level content that does not belong in a module spec. Triage first.

### Steps

1. **Enumerate** — list files without reading their content yet:
   ```bash
   find <dir> -type f | head -200
   ```
   If the listing exceeds 200 entries, ask me whether to scope down (subdirectory, file extension, name pattern) before continuing.

2. **Categorize** each file by extension and naming pattern — still without deep-reading:
   | Category | Examples | What to do with it |
   | --- | --- | --- |
   | Mockup images | `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | Group into module candidates |
   | Static prototype | `index.html`, `*.html`, accompanying `.css` | Group by page → module candidates |
   | Design specs / notes | `README.md`, `*.md`, `*.txt` | Read once for module hints |
   | Design tokens / style guide | `design-tokens.json`, `tokens.css`, `variables.scss`, `theme.*` | Route to `project-ui-rules.md`, NOT to a module spec |
   | Source design files | `.fig`, `.sketch`, `.xd`, `.psd` | Cannot read directly — list them and ask me to export PNG/HTML |
   | Code / other | `.vue`, `.tsx`, `.ts`, `.js`, etc. | Note as "reference implementation"; not authoritative requirements |

3. **Propose module mapping** — group images by:
   - Subdirectory (e.g., `orders/list/*.png` → `order-list` module)
   - Filename prefix (e.g., `order_list_*.png`, `order_detail_*.png` → two modules)
   - User flow hints from README

4. **Identify project-level content** — design tokens, color palettes, typography rules, spacing scales, icon sets, naming conventions found in the directory belong in `project-ui-rules.md`, not in any module spec. Mark these separately.

5. **Output the triage report** in this shape, then STOP and wait for my "go":

   ```
   [DIRECTORY TRIAGE]
   Scanned: <dir> (<N> files total)
   
   Module candidates (proposed):
     1. order-list — 5 images (order_list_*.png), 1 note (README section "列表页")
     2. order-detail — 3 images (order_detail_*.png)
     3. order-create — 4 images (order_create_*.png)
   
   Project-level (proposed → project-ui-rules.md):
     - design-tokens.json (new color palette + spacing scale)
     - icons/ (24 SVGs for icon library)
   
   Cannot read directly (need your action):
     - flow.fig (Figma source — export PNG/HTML for each frame)
   
   Skipped (noted as reference, not requirements):
     - src/views/legacy-order/ (existing implementation for reference)
   
   Default plan: SERIAL — produce one module micro-spec at a time, wait for approval between modules.
   Override: say "batch" to produce all module specs in one pass.
   Awaiting your go on the split + execution mode.
   ```

6. **After "go"**, by default process modules **serially**:
   - Pick the first module candidate. Run Step 0 classification on it. Wait for my "go" again.
   - Produce its micro-spec. Wait for my approval.
   - Only then move to the next module.
   - This lets discoveries in earlier modules inform later ones, and keeps each spec small enough to review carefully.

7. **Batch mode** (only when I explicitly say "batch"):
   - Produce all module micro-specs in one pass.
   - Still classify each module separately (do not assume they are all `new-module`).
   - Output them as a single combined summary with section headers per module, and wait for my one consolidated approval.

8. **Project-level content** is applied first (before any module spec), since module specs may reference the new tokens/rules. Update `project-ui-rules.md` per Project Rules Discovery resolution order; ask me before overwriting any existing rules.

### Triage boundaries

- Do NOT deep-read all mockup images during triage — only enough to confirm the grouping (filename + maybe a glance at one image per group).
- Do NOT start any `.ai/modules/*.md` file during triage.
- Do NOT touch `project-ui-rules.md` during triage — propose changes, apply only after approval.
- If you cannot confidently group a file, list it under "uncertain" in the triage report and ask me.

## Project Rules Discovery

Project UI rules may already live outside `.ai/`. Before creating new ones, search in this order:

1. `.claude/rules/project-ui-rules.md`
2. `.ai/project-ui-rules.md`
3. Root `CLAUDE.md` and other files under `.claude/` (project-wide conventions — naming, routing, API patterns, ElementUI usage)

Use the first existing file as the source of truth. Only create `.ai/project-ui-rules.md` when none of the above exist. Always also scan `CLAUDE.md` and `.claude/` for related conventions that complement the UI rules.

Record the resolved rules path at the top of each module spec (`Source Context > UI rules:`) so later runs do not need to search again.

## Invocation Prompts

Use these prompts to make an AI follow this workflow consistently.

### First-Time Project Setup

```text
Use $personal-requirements-workflow.

I work from prototype screenshots and ask AI to generate ElementUI-based UI that matches this project's existing visual and code conventions.

Before implementing any feature:
1. Resolve the project UI rules by searching in this order and using the first match:
   - .claude/rules/project-ui-rules.md
   - .ai/project-ui-rules.md
   - CLAUDE.md and other files under .claude/ (project-wide conventions)
2. If no UI rules file is found, inspect the project structure, existing pages, shared components, ElementUI usage, styles, routing, API patterns, and naming conventions, then create .ai/project-ui-rules.md summarizing what you learned.
3. Create or update my private notes under .ai/.
4. Do not write production code yet. First report the resolved rules path, the discovered UI rules, and any missing context.
```

### Prototype-to-Spec Prompt

```text
Use $personal-requirements-workflow.

I will provide an input (prototype image, screenshot, text description, OR a directory path containing prototype files) for <module-name-or-domain>.
Do not write code yet — organize requirements first.

Please:

0a. **If the input is a directory path, run Directory Triage first** (see that section). Output the triage report (file enumeration → module candidates → project-level content → uncertain items), then STOP and wait for my "go" + execution mode (serial default, "batch" to override).

0b. **For each module candidate (or for the single non-directory input), classify it.** Output one sentence per the Activation Rule:
   `Classification: [new-module | incremental | local-mod | unsure] — <reason>`
   `Proposed path: <full flow | update existing spec | straight to Superpowers | need your decision>`
   Then STOP and wait for my "go". Do nothing else until I confirm. In serial mode, do this per module before moving to the next.

1. After I confirm, resolve the project UI rules by searching in this order and using the first match:
   - .claude/rules/project-ui-rules.md
   - .ai/project-ui-rules.md
   - CLAUDE.md and other files under .claude/
   If none exist, inspect the project and create .ai/project-ui-rules.md first.
2. Analyze the input against the project's ElementUI conventions and existing component patterns.
3. Branch by classification:
   - **new-module**: Create `.ai/modules/<module-name>.md` from the Module Micro-Spec Template, filling Visible Requirements, Hidden Requirements, Page States, ElementUI Component Mapping, Code Boundary, Acceptance Checklist. **Produce an OpenSpec proposal** (the micro-spec captures UI detail; OpenSpec captures the contract).
   - **incremental**: Read existing `.ai/modules/<module-name>.md`. Append to `## Change Log` (date + what changes). Extend Hidden Requirements, States, Acceptance, Code Boundary deltas. **Open OpenSpec only if this change touches a contract** (data shape, API, shared component, cross-module behavior); otherwise note "no OpenSpec — internal change only" in the change log.
4. Classify every open question as blocking, defaultable, or deferrable.
5. Output a summary (classification taken, resolved rules path, what was added/updated, OpenSpec status, blocking questions) and wait for my approval before implementation.
6. **In serial mode (directory input)**: after my approval of one module's spec, do NOT auto-start the next module. Wait for my explicit "next" or "implement <module>" instruction. Discoveries from this module may change how you classify or scope the next.
```

### Implementation Prompt

```text
Use $personal-requirements-workflow, AND activate $code-boundary-enforcer for the implementation phase (boundary checks, shared-change protocol, diff audit). Also follow the relevant Superpowers skills (test-driven-development, systematic-debugging, webapp-testing, verification-before-completion, requesting-code-review).

Implement <module-name> from .ai/modules/<module-name>.md and the resolved project UI rules file (.claude/rules/project-ui-rules.md or .ai/project-ui-rules.md — whichever was recorded in the module spec's Source Context).

UI rules:
1. Follow existing project patterns and ElementUI conventions.
2. Prefer existing shared components before creating new ones; honor the ElementUI component mapping section in the module spec.
3. Do not invent a new visual style.
4. Implement required loading, empty, error, success, permission, and partial-data states.

Discovery rules:
5. If a hidden requirement appears while coding, add it to `.ai/inbox.md` unless it is blocking.
6. Pause and ask only for blocking questions.

Code edit discipline: delegated to $code-boundary-enforcer.
7. The module spec's `## Code Boundary` section is the authoritative declaration for the enforcer.
8. Before each Edit/Write, $code-boundary-enforcer requires you to list files and confirm they are in Owned. If you need to touch shared / out-of-bounds files, follow its Shared Code Change Protocol.
9. Before completion, $code-boundary-enforcer requires `git diff --name-only` audit against Owned. Cite that audit in your completion summary alongside the Superpowers verification skill used.
```

### Completion Prompt

```text
Use $personal-requirements-workflow.

Before calling <module-name> complete:
1. Check .ai/modules/<module-name>.md acceptance checklist.
2. Run the $code-boundary-enforcer diff audit (`git diff --name-only` cross-checked against `## Code Boundary > Owned`). Report the audit result; any out-of-Owned file must already have an approved Shared Code Change Proposal.
3. Drain related items from .ai/inbox.md into decisions, non-goals, or remaining open questions.
4. Identify any new decisions surfaced during implementation that should amend the existing OpenSpec proposal, or be logged in `.ai/decisions.md` if they cross modules.
5. Verify UI against the resolved project UI rules file and the original prototype.
6. Summarize what was implemented, what was intentionally not included, what remains risky, the boundary audit result, and the verification steps performed (link the Superpowers skills used).
```

## Storage

Prefer a private workspace folder:

```text
.ai/
  inbox.md
  decisions.md
  project-ui-rules.md    # only created when no UI rules exist elsewhere
  modules/
    <module-name>.md
```

Project UI rules live in **one** of these places (search order — see Project Rules Discovery above):

```text
.claude/rules/project-ui-rules.md   # preferred when already present
.ai/project-ui-rules.md             # fallback location, created only if nothing exists
CLAUDE.md / .claude/*               # general conventions that supplement UI rules
```

Never duplicate rules into `.ai/` if `.claude/rules/project-ui-rules.md` already exists — read from it and only record extra private notes that augment it.

Keep `.ai/` out of any repo that gets pushed somewhere shared. Prefer `.git/info/exclude` (local-only, does not pollute `.gitignore` if the repo has one):

```bash
echo ".ai/" >> .git/info/exclude
```

## Workflow

1. **Triage if directory, then classify.** If the input is a directory, run Directory Triage first (enumerate → categorize → propose module mapping → wait for "go" + execution mode). Then for each module candidate (or the single non-directory input), classify per the Activation Rule (`new-module` / `incremental` / `local-mod` / `unsure`) and wait for "go".
2. After "go", create or update the private notes area; resolve project UI rules per Project Rules Discovery.
3. For `new-module`: create `.ai/modules/<module-name>.md` including `## Code Boundary`. For `incremental`: load the existing spec, append to `## Change Log`, extend the relevant sections.
4. Walk the prototype/input by page, state, action, data, and integration.
5. Classify every discovered question as blocking, defaultable, or deferrable.
6. Decide OpenSpec status: open if contract changes (new-module always; incremental only when contract-touching).
7. During coding: activate `$code-boundary-enforcer` for boundary checks and shared-change protocol. Append non-blocking discoveries to `.ai/inbox.md` in one line each.
8. At a natural checkpoint, drain the inbox into the module spec, the decisions log, or `Non-Goals`.
9. Before calling the module done: verify the acceptance checklist, run the enforcer's diff audit, fold any newly-surfaced decisions back into the existing OpenSpec proposal or `.ai/decisions.md`.

## Module Micro-Spec Template

```md
# <Module Name>

## Goal
What user or business outcome this module supports.

## Source Context
- Prototype:
- UI rules: <resolved path, e.g. .claude/rules/project-ui-rules.md>
- Related code:
- Related API/data:

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

Adjust paths above to match the actual project structure (read from project-ui-rules.md / CLAUDE.md). If unsure, ask before coding.

## Change Log
- <YYYY-MM-DD> initial creation from <prototype source>
- <YYYY-MM-DD> incremental: <what was added/changed; OpenSpec status: opened / not needed>

## Scope
- What this iteration includes.

## Non-Goals
- What is intentionally not included.

## Prototype Facts (Visible Requirements)
- What is explicitly visible or stated in the prototype/brief.

## Hidden Requirements
- Requirements inferred from states, edge cases, user flow, data, or integration.

## ElementUI Component Mapping
- <Region or element>: <component / shared wrapper to use> — <notes, e.g. variant, props, slot>
- Gaps: <regions with no obvious existing component, and the proposed approach>

## OpenSpec Proposal
- Path / title: <link to the OpenSpec proposal produced alongside this micro-spec>
- Scope handed to OpenSpec: <one line — what contract / data shape / behavior OpenSpec is locking down>

(OpenSpec is always produced when this skill runs; do not leave this section blank.)

## Decisions
- Decision:
  - Reason:
  - Impact:

## Open Questions
- [blocking] Question and why it blocks.
- [defaultable] Question and proposed default.
- [deferrable] Question and when to revisit.

## States
- Loading:
- Empty:
- Success:
- Error:
- Permission denied:
- Partial/missing data:

## Data and API
- Inputs:
- Outputs:
- Validation:
- Pagination/filter/sort:
- Caching/refresh:
- Backend assumptions:

## UX Behavior
- Navigation:
- Form behavior:
- Confirmation/destructive actions:
- Feedback/toasts:
- Disabled states:

## Acceptance Checklist
- [ ] Happy path works.
- [ ] Empty, loading, error, and permission states are handled.
- [ ] Validation and destructive actions are clear.
- [ ] API/data assumptions are documented.
- [ ] Blocking questions are resolved.
- [ ] `$code-boundary-enforcer` diff audit passed (all changed files inside `Code Boundary > Owned`; any shared change went through the Shared Code Change Protocol).
- [ ] New decisions surfaced during implementation are folded into the OpenSpec proposal; cross-module ones also logged in `.ai/decisions.md`.
```

## Discovery Checklist

Use this when looking at a prototype or screenshot:

| Area | Questions |
| --- | --- |
| User goal | What is the user trying to finish here? What happens before and after? |
| Entry/exit | How does the user arrive? Where can they go next? Can they cancel/back out? |
| Actions | What can be clicked, edited, submitted, retried, deleted, or undone? |
| States | What appears for loading, empty, success, error, permission, and partial data? |
| Data | Which fields are required, optional, derived, formatted, or missing? |
| Validation | What prevents submit? Are errors field-level, page-level, or both? |
| Permissions | Who can view, create, edit, delete, approve, export, or configure? |
| Boundaries | What happens at limits: long text, many rows, no image, expired data? |
| Integration | Which APIs, events, routes, stores, or external services are implied? |
| Observability | Is logging, analytics, audit trail, or error reporting expected? |
| Reversibility | Is the change hard to undo later (data shape, persisted format, public URL)? |

## Question Classification

Use three buckets to avoid constant context switching:

| Bucket | Meaning | Action |
| --- | --- | --- |
| blocking | A wrong choice can break API, data model, permission, security, or core flow. | Pause and ask me before coding that part. |
| defaultable | A standard product default is safe and reversible. | Record the default and continue. |
| deferrable | Nice-to-have, optimization, polish, or future workflow. | Put in inbox or non-goals. |

Safe defaults usually include: preserve form input after submit failure, show retry on fetch failure, require confirmation for destructive actions, disable submit while saving, show empty states instead of blank screens, and avoid implementing export/import/bulk actions unless explicitly in scope.

## Inbox Format

Keep `.ai/inbox.md` fast to write:

```md
# Requirements Inbox

## New
- [ ] [module] [defaultable] Failed submit should preserve form input.
- [ ] [module] [blocking] Need to know whether deletion is soft or permanent.
- [ ] [module] [deferrable] Consider bulk export later.

## Drained
- [x] [module] Decision moved to module spec: destructive delete requires confirmation.
```

When draining the inbox:

- Move stable choices to `## Decisions`.
- Move requirements to `## Hidden Requirements` or `## Acceptance Checklist`.
- Move out-of-scope ideas to `## Non-Goals`.
- Surface remaining blocking questions back to me before continuing.

## Decisions Log

Use `.ai/decisions.md` for choices that may repeat across modules:

```md
# Decisions

## YYYY-MM-DD - <Decision>
Context:
Decision:
Reason:
Applies to:
```

Do not over-document obvious one-off choices. Log decisions that prevent future confusion across modules.

## When to Pause and Ask Me

Pause and ask before coding when a question affects:

- API shape, database fields, permission rules, security, or auth.
- A decision that is expensive to reverse (persisted data shape, public URL, migration).
- Core user-facing behavior where guessing would mean rework.

Keep the question short — one paragraph, with a proposed default so I can just say "go":

```md
For <module>, one blocking question:
Should delete be soft-delete or permanent? It affects API behavior and undo.
Proposed default: soft-delete with an `archived_at` column. OK to proceed?
```

## Before Implementation

Before writing code for a module, make sure the micro-spec has:

- Goal, scope, and non-goals.
- Blocking questions resolved or clearly isolated.
- ElementUI component mapping filled in.
- State handling expectations.
- Data/API assumptions.
- Acceptance checklist.

If already mid-implementation, do not restart the whole process. Create the spec from current knowledge, capture open questions, and continue.

## During Implementation

When a hidden requirement appears:

1. If blocking, pause only that part and ask me.
2. If defaultable, record the decision in the module spec and continue.
3. If deferrable, append one line to `.ai/inbox.md` and keep coding.

Code-edit discipline (file listing, shared-change protocol, boundary checks) is delegated to `$code-boundary-enforcer` — follow its rules during coding.

Avoid rewriting the micro-spec repeatedly during deep coding. Batch cleanup at checkpoints.

## Before Completion

Before saying the module is complete:

- Check the acceptance checklist.
- Run the `$code-boundary-enforcer` diff audit (`git diff --name-only` against `## Code Boundary > Owned`).
- Run relevant tests or manual checks (cite the Superpowers skill used).
- Drain or intentionally defer inbox items for this module.
- Amend the existing OpenSpec proposal with any decisions that emerged during coding; log cross-module ones in `.ai/decisions.md`.
- Leave private uncertainty in `.ai/` rather than hiding it in code comments.

## Common Mistakes

Classification & scope
- Running this skill for `local-mod` work (style tweak, color/spacing change, bug fix, copy edit). The Activation Rule says: classify first, and `local-mod` goes straight to Superpowers with no spec.
- Assuming "input is an image → use this skill". An image can be a style problem, a bug report, or a new module — classify first, never default to the heaviest path.
- Skipping Step 0 (classification + wait for go) and jumping straight to producing a spec.
- Asking "do we need OpenSpec?" once the classification is `new-module`. The answer is yes. For `incremental`, only open OpenSpec if a contract changes.

Directory input
- Treating a directory of prototype files as a single module without running Directory Triage. Multi-module directories must be split first and approved by me.
- Putting design tokens, color palettes, typography rules, or icon sets into a module spec. Those are project-level and belong in `project-ui-rules.md`.
- Deep-reading every mockup image during triage. Read filenames + maybe one image per group; defer deep reads until after split approval.
- In serial mode, auto-advancing to the next module after one spec is approved. Always stop and wait for explicit "next" / "implement <module>".

Code boundary
- Forgetting to activate `$code-boundary-enforcer` during implementation. The module spec writes `## Code Boundary`; the enforcer reads it. Both must be in play.
- Leaving `## Code Boundary` empty or vague in the module spec — the enforcer cannot protect against patterns it cannot read.

Spec hygiene
- Turning private notes into a second product spec system. Keep them small and useful.
- Treating every question as blocking. Most UI state and copy choices can use defaults.
- Letting `.ai/inbox.md` become a graveyard. Drain it at module checkpoints.
- Skipping the ElementUI component mapping step and inventing new UI patterns.
- Coding from the prototype only. Always add state, data, permission, and edge-case checks.
