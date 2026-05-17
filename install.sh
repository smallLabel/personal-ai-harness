#!/usr/bin/env bash
# install.sh — symlink dotfiles-ai content into ~
# Idempotent: re-run safely, existing correct symlinks are left alone.
# Conflicting files are moved to ~/.dotfiles-ai.backup.<timestamp>/

set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"
BACKUP_DIR="${HOME_DIR}/.dotfiles-ai.backup.$(date +%Y%m%d_%H%M%S)"
BACKUP_USED=0

link() {
  local src="$1"
  local dst="$2"
  if [[ -L "$dst" ]]; then
    local current_target
    current_target="$(readlink "$dst")"
    if [[ "$current_target" == "$src" ]]; then
      echo "  ✓ already linked: $dst"
      return 0
    fi
  fi
  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ "$BACKUP_USED" -eq 0 ]]; then
      mkdir -p "$BACKUP_DIR"
      BACKUP_USED=1
    fi
    mv "$dst" "$BACKUP_DIR/"
    echo "  ⚠ backed up: $dst → $BACKUP_DIR/"
  fi
  mkdir -p "$(dirname "$dst")"
  ln -s "$src" "$dst"
  echo "  ✓ linked:    $dst"
}

echo "Installing dotfiles-ai from: $DOTFILES"
echo

echo "▶ Skills (~/.agents/skills/)"
mkdir -p "$HOME_DIR/.agents/skills"
for skill_dir in "$DOTFILES/home/.agents/skills/"*/; do
  [[ -d "$skill_dir" ]] || continue
  skill_dir="${skill_dir%/}"  # strip trailing slash
  name="$(basename "$skill_dir")"
  link "$skill_dir" "$HOME_DIR/.agents/skills/$name"
done
echo

echo "▶ Hook scripts (~/.claude/scripts/)"
mkdir -p "$HOME_DIR/.claude/scripts"
for script in "$DOTFILES/home/.claude/scripts/"*; do
  [[ -f "$script" ]] || continue
  name="$(basename "$script")"
  chmod +x "$script"
  link "$script" "$HOME_DIR/.claude/scripts/$name"
done
echo

echo "▶ Merging settings.json hooks (preserves env/model/permissions, only touches \"hooks\" key)"
python3 "$DOTFILES/scripts/merge-settings.py" \
  --target "$HOME_DIR/.claude/settings.json" \
  --source "$DOTFILES/home/.claude/settings.hooks.json"
echo

if [[ "$BACKUP_USED" -eq 1 ]]; then
  echo "✓ Done. Conflicts backed up to: $BACKUP_DIR"
else
  echo "✓ Done. No conflicts; no backup needed."
fi
echo
echo "Verify with:"
echo "  ls -la ~/.agents/skills/ ~/.claude/scripts/ ~/.claude/rules/"
echo "  python3 -c 'import json; print(json.dumps(json.load(open(\"$HOME_DIR/.claude/settings.json\"))[\"hooks\"], indent=2))'"
