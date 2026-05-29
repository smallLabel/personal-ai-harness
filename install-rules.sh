#!/usr/bin/env bash
# Install project-level AI rules from this harness's templates/ai-rules/ to a target project.
#
# Unlike install.sh (which manages the global ~/.agents/ + ~/.claude/ setup),
# this script is per-project and only copies plain Markdown rule files.
# Rule files live under <project>/.ai/rules/ (NOT .claude/rules/) so they are
# NOT auto-loaded into every Claude Code session — they get Read on-demand,
# keeping per-session token cost minimal.
#
# Usage:
#   ./install-rules.sh                   # install into current directory
#   ./install-rules.sh /path/to/project  # install into a specific project root

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/templates/ai-rules"
TARGET="${1:-.}"

if [ ! -d "$SRC/rules" ]; then
    echo "Error: templates/ai-rules/rules/ not found in $SRC" >&2
    echo "Are you running this from the harness repo root?" >&2
    exit 1
fi

ABS_TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || {
    echo "Error: target directory '$TARGET' does not exist" >&2
    exit 1
}

echo "→ Installing AI rules to: $ABS_TARGET"
echo ""

# Rules (always overwrite — canonical source is the harness)
mkdir -p "$TARGET/.ai/rules"
echo "Rules:"
for f in "$SRC/rules/"*.md; do
    name="$(basename "$f")"
    echo "  + .ai/rules/$name"
    cp "$f" "$TARGET/.ai/rules/$name"
done

# Entry files (never overwrite — they contain project-specific content)
echo ""
echo "Entry files:"

if [ ! -f "$TARGET/CLAUDE.md" ]; then
    echo "  + CLAUDE.md"
    cp "$SRC/CLAUDE.md" "$TARGET/CLAUDE.md"
else
    echo "  ~ CLAUDE.md already exists — skipped (merge manually if needed)"
fi

if [ ! -f "$TARGET/AGENTS.md" ]; then
    echo "  + AGENTS.md"
    cp "$SRC/AGENTS.md" "$TARGET/AGENTS.md"
else
    echo "  ~ AGENTS.md already exists — skipped (merge manually if needed)"
fi

cat <<EOF

✓ Done.

Next steps:
  1. Fill in CLAUDE.md / AGENTS.md 「项目专属」 section (tech stack, commands, etc.)
  2. Rewrite .ai/rules/code-boundary.md path globs to match this project
  3. (Optional) Adjust .ai/rules/coding-style.md to match Prettier / ESLint config

Token note:
  The 6 rule files live under .ai/rules/, not .claude/rules/, so they are NOT
  auto-loaded into every Claude Code session. Only CLAUDE.md (small entry file)
  is loaded by default; the rules themselves are Read on-demand when relevant.

EOF
