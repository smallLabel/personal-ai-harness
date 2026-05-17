#!/usr/bin/env bash
# uninstall.sh — remove symlinks created by install.sh
# Does NOT delete the dotfiles-ai repo itself.
# Does NOT remove items that aren't symlinks pointing to this repo.

set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"

unlink_if_ours() {
  local dst="$1"
  if [[ -L "$dst" ]]; then
    local target
    target="$(readlink "$dst")"
    if [[ "$target" == "$DOTFILES/"* ]]; then
      rm "$dst"
      echo "  ✓ unlinked: $dst"
      return 0
    fi
  fi
  echo "  • skip (not ours or missing): $dst"
}

echo "Uninstalling dotfiles-ai symlinks. Repo at $DOTFILES is left intact."
echo

echo "▶ Skills"
for skill_dir in "$DOTFILES/home/.agents/skills/"*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "${skill_dir%/}")"
  unlink_if_ours "$HOME_DIR/.agents/skills/$name"
done
echo

echo "▶ Hook scripts"
for script in "$DOTFILES/home/.claude/scripts/"*; do
  [[ -f "$script" ]] || continue
  name="$(basename "$script")"
  unlink_if_ours "$HOME_DIR/.claude/scripts/$name"
done
echo

echo "▶ Settings hooks block"
python3 "$DOTFILES/scripts/merge-settings.py" \
  --target "$HOME_DIR/.claude/settings.json" \
  --source "$DOTFILES/home/.claude/settings.hooks.json" \
  --remove
echo

echo "✓ Done."
echo
echo "Note: any backups in ~/.dotfiles-ai.backup.* are NOT auto-restored."
echo "      Restore manually if needed:  mv ~/.dotfiles-ai.backup.<ts>/<name> <original-location>"
