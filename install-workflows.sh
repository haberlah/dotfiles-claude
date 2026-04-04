#!/bin/bash
# Install the auto-PR workflow into a project repo.
# The workflow creates PRs from auto/* branches pushed by the auto-commit hook.
# Review is handled by the Claude GitHub App (install via /install-github-app).
#
# Usage: ~/dotfiles-claude/install-workflows.sh [/path/to/project]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-.}"

cd "$TARGET"

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Error: $(pwd) is not a git repository." >&2
  exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"

mkdir -p "$WORKFLOWS_DIR"
cp "$SCRIPT_DIR/workflows/auto-pr.yml" "$WORKFLOWS_DIR/auto-pr.yml"

echo "Installed ${WORKFLOWS_DIR}/auto-pr.yml"
echo ""
echo "Next steps:"
echo "  1. Install Claude GitHub App: run /install-github-app in Claude Code"
echo "     (or visit https://github.com/apps/claude)"
echo "  2. Commit and push the workflow file to your default branch:"
echo "       git add .github/workflows/auto-pr.yml"
echo "       git commit -m 'Add auto-PR workflow for Claude Code'"
echo "       git push"
echo "  3. The auto-commit hook will now create PRs for this repo"
echo "  4. Use regular merge (not squash) when merging PRs"
