#!/bin/bash
# Setup script for syncing Claude Code config to a new machine.
# Usage: git clone <repo-url> ~/dotfiles-claude && ~/dotfiles-claude/setup.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Setting up Claude Code config from $REPO_DIR..."

# Create ~/.claude if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Files/dirs to symlink
ITEMS=(CLAUDE.md settings.json settings.local.json hooks skills)

for item in "${ITEMS[@]}"; do
  target="$CLAUDE_DIR/$item"
  source="$REPO_DIR/$item"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "  Backing up existing $target -> ${target}.bak"
    mv "$target" "${target}.bak"
  fi

  if [ -L "$target" ]; then
    rm "$target"
  fi

  ln -s "$source" "$target"
  echo "  Linked $target -> $source"
done

echo "Done! Claude Code config is now synced."
