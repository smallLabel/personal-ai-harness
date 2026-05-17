#!/usr/bin/env python3
"""
UserPromptSubmit hook.

When the user's prompt mentions a directory path (that exists on disk) or
references prototype/mockup artifacts, inject a factual reminder pointing at
$personal-requirements-workflow. The skill itself contains the Activation Rule
that decides whether to actually use the heavy workflow — this hook just
ensures the rule is visible to Claude.

Phrasing is intentionally factual / non-imperative (anti prompt-injection per
Claude Code hook docs). It does NOT tell Claude what to do; it gives context.

Fail-open: any error → no injection, no block.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


HOOK_EVENT = "UserPromptSubmit"

# Heuristic keywords that suggest prototype-driven work (zh + en).
PROTOTYPE_KEYWORDS = re.compile(
    r"(?ix)(原型|草稿|设计稿|截图|线框|prototype|figma|sketch|mockup|wireframe|design\s*draft)"
)

# File extensions commonly seen in prototype directories.
DESIGN_FILE_HINTS = re.compile(
    r"(?i)\.(png|jpg|jpeg|webp|gif|svg|fig|sketch|xd|psd|html)\b"
)


def emit_no_op() -> None:
    """No additional context — exit silently with valid empty hook output."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": HOOK_EVENT}}))
    sys.exit(0)


def emit_context(text: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": HOOK_EVENT,
                    "additionalContext": text,
                }
            }
        )
    )
    sys.exit(0)


def fail_open(msg: str) -> None:
    print(f"[inject-skill-on-input] WARN: {msg}", file=sys.stderr)
    emit_no_op()


def extract_path_candidates(text: str) -> list[str]:
    """Heuristically pull out path-like tokens from the prompt."""
    # Look for things that contain a slash and could be a path. Loose on purpose.
    candidates = re.findall(r"(?<!\S)((?:~|\.{0,2}/|[A-Za-z]:[\\/])\S+)", text)
    # Also catch bare paths if user pasted them
    candidates += re.findall(r"(?<!\S)([A-Za-z0-9_\-\.]+/[A-Za-z0-9_\-\./]+)(?!\S)", text)
    return list(dict.fromkeys(c.rstrip(".,;:)") for c in candidates))


def resolve_path(raw: str, cwd: str) -> Path | None:
    """Expand ~ and resolve against cwd."""
    expanded = os.path.expanduser(raw)
    p = Path(expanded)
    if not p.is_absolute():
        p = Path(cwd) / p
    try:
        return p.resolve()
    except OSError:
        return None


def detect_directory_input(prompt: str, cwd: str) -> Path | None:
    for cand in extract_path_candidates(prompt):
        p = resolve_path(cand, cwd)
        if p and p.is_dir():
            return p
    return None


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        emit_no_op()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        fail_open(f"bad JSON on stdin: {e}")

    prompt = payload.get("prompt", "") or ""
    cwd = payload.get("cwd") or os.getcwd()

    if not prompt:
        emit_no_op()

    notes: list[str] = []

    directory = detect_directory_input(prompt, cwd)
    if directory:
        notes.append(
            f"The prompt references the directory {directory}, which exists on disk. "
            f"If it contains prototype files (mockups, design tokens, notes), the "
            f"skill `personal-requirements-workflow` defines a Directory Triage flow: "
            f"enumerate → categorize → propose module mapping → wait for user 'go' "
            f"BEFORE producing any spec. If the directory is source code or unrelated, "
            f"the skill should not be invoked."
        )

    if PROTOTYPE_KEYWORDS.search(prompt) or DESIGN_FILE_HINTS.search(prompt):
        notes.append(
            f"The prompt mentions prototype/design-related terms. The skill "
            f"`personal-requirements-workflow` defines an Activation Rule with three "
            f"buckets (new-module / incremental / local-mod). Classify first, ask the "
            f"user to confirm, then act. Do NOT default to the heavy workflow for "
            f"style tweaks or bug screenshots — those are `local-mod` and go straight "
            f"to Superpowers skills."
        )

    if not notes:
        emit_no_op()

    combined = "\n\n".join(notes)
    emit_context(combined)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        fail_open(f"unexpected error: {e!r}")
