# Project-level Code Boundary (example)

Copy this file to `<your-project>/.claude/rules/code-boundary.md` and edit the
paths to match the project. The `check-code-boundary.py` hook will read it as
a fallback when no `.ai/modules/<module>.md` is active.

This declaration is project-wide — useful for bug-fix / refactor work where no
single module owns the change.

## Code Boundary

- Owned (free to edit):
  - src/**
  - tests/**
  - docs/**

- Read-only references (use, but never modify):
  - node_modules/**
  - vendor/**
  - public/**

- Out-of-bounds (must not touch):
  - package.json
  - package-lock.json
  - pnpm-lock.yaml
  - yarn.lock
  - tsconfig.json
  - vite.config.*
  - .env, .env.*
  - migrations/**

Patterns are glob-relative to the project root (the directory that contains
the `.claude/` folder). `**` matches recursively; `*` matches a single path
segment.
