#!/usr/bin/env python3
"""
PreToolUse hook for Edit | Write | NotebookEdit.

Reads the active Code Boundary declaration and blocks edits to files
outside the Owned glob patterns.

Boundary discovery order (first hit wins):
  1. <project>/.ai/modules/<most-recently-modified>.md  →  ## Code Boundary
  2. <project>/.claude/rules/code-boundary.md          →  ## Code Boundary  (legacy)
  3. <project>/.ai/rules/code-boundary.md              →  ## Code Boundary  (preferred)
  4. None found → allow silently (the skill prompts user to declare one)

Note on (2) vs (3): `.claude/rules/*.md` is auto-loaded into every Claude Code
session as project instructions. Projects that want to save tokens move rules
under `.ai/rules/` (which is NOT auto-loaded) and rely on AI to Read on-demand.
This hook checks both so a project can migrate at its own pace.

Where <project> = the nearest ancestor of CWD that contains .ai/ or .claude/.

Decision is emitted as JSON on stdout per the Claude Code hook protocol:
  exit 0 + {"hookSpecificOutput": {"permissionDecision": "allow|deny", ...}}

Blocked edits get a "deny" with a message telling AI to switch to the
Shared Code Change Protocol from the code-boundary-enforcer skill.

Designed to fail open: any parse/IO error logs to stderr and returns "allow".
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


HOOK_EVENT = "PreToolUse"


def emit(decision: str, reason: str = "") -> None:
    """Print JSON decision and exit 0. Per Claude Code hook protocol."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": HOOK_EVENT,
            "permissionDecision": decision,
        }
    }
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(out))
    sys.exit(0)


def fail_open(msg: str) -> None:
    """On internal error, log to stderr and allow (don't break the user's flow)."""
    print(f"[check-code-boundary] WARN: {msg}", file=sys.stderr)
    emit("allow")


# -----------------------------------------------------------------------------
# Glob → regex translation (with ** and {a,b} brace expansion)
# -----------------------------------------------------------------------------

def expand_braces(pattern: str) -> list[str]:
    """foo.{js,ts} → ['foo.js', 'foo.ts']. Recursive for nested patterns."""
    m = re.search(r"\{([^{}]+)\}", pattern)
    if not m:
        return [pattern]
    options = [opt.strip() for opt in m.group(1).split(",")]
    expanded = [pattern[: m.start()] + opt + pattern[m.end():] for opt in options]
    out: list[str] = []
    for e in expanded:
        out.extend(expand_braces(e))
    return out


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """src/views/foo/** → ^src/views/foo/.*$, with * not crossing /."""
    parts = pattern.split("**")
    escaped = [re.escape(p) for p in parts]
    # within an escaped part, \* is the escaped single-star; replace it with [^/]*
    parts_converted = [p.replace(r"\*", "[^/]*").replace(r"\?", "[^/]") for p in escaped]
    body = ".*".join(parts_converted)
    return re.compile(f"^{body}$")


# -----------------------------------------------------------------------------
# Boundary file discovery + parsing
# -----------------------------------------------------------------------------

def find_project_root(start: Path) -> Path | None:
    """Walk up looking for a directory that contains .ai/ or .claude/.

    The user's $HOME usually has ~/.claude/ for user-level Claude config — that
    is NOT a project. Skip it so a stray boundary file there cannot accidentally
    constrain edits across the entire home directory.
    """
    home = Path(os.path.expanduser("~")).resolve()
    p = start.resolve()
    for ancestor in [p, *p.parents]:
        if ancestor == home:
            return None  # reached $HOME without finding a project
        if (ancestor / ".ai").is_dir() or (ancestor / ".claude").is_dir():
            return ancestor
    return None


def find_active_spec(project_root: Path) -> Path | None:
    """Most recently modified .ai/modules/*.md, or None."""
    modules_dir = project_root / ".ai" / "modules"
    if not modules_dir.is_dir():
        return None
    specs = sorted(
        (p for p in modules_dir.glob("*.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return specs[0] if specs else None


def find_project_rule(project_root: Path) -> Path | None:
    """Look for a project-wide boundary file.

    Checks .claude/rules/ first (legacy / auto-loaded location), then
    .ai/rules/ (preferred / on-demand location). First hit wins so a
    project mid-migration with both files still gets deterministic behavior.
    """
    for candidate in (
        project_root / ".claude" / "rules" / "code-boundary.md",
        project_root / ".ai" / "rules" / "code-boundary.md",
    ):
        if candidate.is_file():
            return candidate
    return None


def parse_boundary(md_text: str) -> dict[str, list[str]]:
    """
    Extract patterns from the ## Code Boundary section.
    Returns {"owned": [...], "read_only": [...], "out_of_bounds": [...]}.
    """
    lines = md_text.splitlines()

    # Find the ## Code Boundary section
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^##\s+Code\s+Boundary\s*$", ln, re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return {"owned": [], "read_only": [], "out_of_bounds": []}

    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break

    section = lines[start:end]

    buckets = {"owned": [], "read_only": [], "out_of_bounds": []}
    current: str | None = None
    bucket_header_re = re.compile(r"^-\s+(Owned|Read-only|Out-of-bounds)", re.IGNORECASE)
    pattern_re = re.compile(r"^\s+-\s+(\S+)")  # nested list item

    for ln in section:
        h = bucket_header_re.match(ln)
        if h:
            name = h.group(1).lower()
            current = {"owned": "owned", "read-only": "read_only", "out-of-bounds": "out_of_bounds"}[name]
            continue
        if current is None:
            continue
        m = pattern_re.match(ln)
        if not m:
            continue
        raw = m.group(1)
        # strip trailing comment after #
        raw = raw.split("#", 1)[0].strip().rstrip(",")
        if not raw:
            continue
        # skip prose-like entries with no glob-meta and no path separator
        if "/" not in raw and "*" not in raw and "." not in raw:
            continue
        buckets[current].extend(expand_braces(raw))

    return buckets


def relpath(file_abs: Path, root: Path) -> str | None:
    """Return file_abs relative to root, or None if outside root."""
    try:
        return str(file_abs.resolve().relative_to(root.resolve()))
    except ValueError:
        return None


def matches_any(rel: str, patterns: list[str]) -> bool:
    return any(glob_to_regex(p).match(rel) for p in patterns)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        fail_open("empty stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        fail_open(f"bad JSON on stdin: {e}")

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        emit("allow")  # not our matcher

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        emit("allow")  # nothing to check

    file_abs = Path(file_path)
    if not file_abs.is_absolute():
        cwd = payload.get("cwd") or os.getcwd()
        file_abs = Path(cwd) / file_abs

    # Find project root (relative to cwd, which is where the user is working)
    cwd = Path(payload.get("cwd") or os.getcwd())
    project_root = find_project_root(cwd)
    if project_root is None:
        emit("allow")  # not inside a project with .ai or .claude

    # Find boundary source
    spec = find_active_spec(project_root)
    rule = find_project_rule(project_root) if spec is None else None
    boundary_path = spec or rule
    if boundary_path is None:
        emit("allow")  # no declaration → no enforcement

    try:
        # Explicit UTF-8: Windows defaults to system codepage (e.g. GBK on zh-CN)
        # which fails on UTF-8 boundary files with non-ASCII content.
        buckets = parse_boundary(boundary_path.read_text(encoding="utf-8"))
    except OSError as e:
        fail_open(f"cannot read {boundary_path}: {e}")
    except UnicodeDecodeError as e:
        fail_open(f"cannot decode {boundary_path} as UTF-8: {e}")

    if not (buckets["owned"] or buckets["read_only"] or buckets["out_of_bounds"]):
        emit("allow")  # Code Boundary section is empty / malformed

    rel = relpath(file_abs, project_root)
    if rel is None:
        # editing a file outside the project root entirely — block
        emit(
            "deny",
            f"File '{file_abs}' is outside the project root '{project_root}'. "
            f"Run the Shared Code Change Protocol (see $code-boundary-enforcer) "
            f"or scope the task to a single file explicitly.",
        )

    # Decision
    if matches_any(rel, buckets["owned"]):
        emit("allow")

    # Anything not Owned is denied. Distinguish error messages by bucket for clarity.
    if matches_any(rel, buckets["out_of_bounds"]):
        bucket_label = "Out-of-bounds"
    elif matches_any(rel, buckets["read_only"]):
        bucket_label = "Read-only reference"
    else:
        bucket_label = "Not in Owned"

    emit(
        "deny",
        (
            f"[code-boundary-enforcer] BLOCKED\n\n"
            f"File:    {rel}\n"
            f"Bucket:  {bucket_label}\n"
            f"Source:  {boundary_path}\n\n"
            f"This edit is outside the active Code Boundary > Owned patterns. "
            f"Do NOT bypass this block. Instead, run the Shared Code Change Protocol "
            f"from $code-boundary-enforcer:\n"
            f"  1. Halt this edit.\n"
            f"  2. Emit a [SHARED CHANGE PROPOSAL] (file, why, callers, alternatives).\n"
            f"  3. Wait for the user's explicit approval.\n"
            f"  4. If approved, open an OpenSpec entry (shared code = contract).\n\n"
            f"If this task legitimately needs to edit outside the module, ask the user "
            f"to update {boundary_path}'s `## Code Boundary > Owned` first."
        ),
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        fail_open(f"unexpected error: {e!r}")
