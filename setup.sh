#!/bin/bash
# Setup script for syncing Claude Code config to a new machine.
# Usage: git clone <repo-url> ~/dotfiles-claude && ~/dotfiles-claude/setup.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
REPO_PARENT="$(dirname "$REPO_DIR")"
REPO_NAME="$(basename "$REPO_DIR")"

echo "Setting up Claude Code config from $REPO_DIR..."

# Create ~/.claude if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Compute the symlink target for an item in the repo.
# Relative (../<repo>/<item>) when the repo sits directly under $HOME alongside
# ~/.claude (the documented layout) so the links are username-agnostic and survive
# being cloned by another user; absolute otherwise so an unusual clone location
# still resolves.
link_target() {
  local item="$1"
  if [ "$REPO_PARENT" = "$HOME" ] && [ "$CLAUDE_DIR" = "$HOME/.claude" ]; then
    printf '../%s/%s' "$REPO_NAME" "$item"
  else
    printf '%s/%s' "$REPO_DIR" "$item"
  fi
}

# Files/dirs to symlink (shared config, tracked in git)
SYMLINK_ITEMS=(CLAUDE.md settings.json hooks skills commands agents rules)

for item in "${SYMLINK_ITEMS[@]}"; do
  target="$CLAUDE_DIR/$item"

  # Back up a real (non-symlink) file/dir before replacing it with a link
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "  Backing up existing $target -> ${target}.bak"
    mv "$target" "${target}.bak"
  fi

  # -s symbolic, -f replace existing, -n don't descend into an existing dir symlink
  ln -sfn "$(link_target "$item")" "$target"
  echo "  Linked $target -> $(readlink "$target")"
done

# settings.local.json is machine-specific (permissions, MCP tools).
# Copy from template if no local file exists; never overwrite existing.
LOCAL_SETTINGS="$REPO_DIR/settings.local.json"
LOCAL_SETTINGS_CLAUDE="$CLAUDE_DIR/settings.local.json"

if [ ! -e "$LOCAL_SETTINGS" ]; then
  cp "$REPO_DIR/settings.local.example.json" "$LOCAL_SETTINGS"
  echo "  Created settings.local.json from template (customise your permissions here)"
else
  echo "  settings.local.json already exists (kept as-is)"
fi

# Symlink the local settings into ~/.claude/ (backing up a real file first)
if [ -e "$LOCAL_SETTINGS_CLAUDE" ] && [ ! -L "$LOCAL_SETTINGS_CLAUDE" ]; then
  echo "  Backing up existing $LOCAL_SETTINGS_CLAUDE -> ${LOCAL_SETTINGS_CLAUDE}.bak"
  mv "$LOCAL_SETTINGS_CLAUDE" "${LOCAL_SETTINGS_CLAUDE}.bak"
fi
ln -sfn "$(link_target settings.local.json)" "$LOCAL_SETTINGS_CLAUDE"
echo "  Linked $LOCAL_SETTINGS_CLAUDE -> $(readlink "$LOCAL_SETTINGS_CLAUDE")"

# Ensure hook scripts are executable (some systems strip execute bits on clone)
chmod +x "$REPO_DIR/hooks/"*.sh

# Install pre-commit hook to prevent accidental secret leaks.
# Relative target (repo-internal) so it survives the repo being moved.
GIT_HOOKS_DIR="$REPO_DIR/.git/hooks"
mkdir -p "$GIT_HOOKS_DIR"
ln -sfn ../../hooks/pre-commit-secrets-check.sh "$GIT_HOOKS_DIR/pre-commit"
echo "  Installed pre-commit secrets check hook"

echo ""
echo "Done! Claude Code config is now synced."
echo ""
echo "Next steps:"
echo "  - Edit ~/dotfiles-claude/settings.local.json to add your MCP tool permissions"
echo "  - Edit ~/dotfiles-claude/CLAUDE.md to set your language and workflow preferences"
