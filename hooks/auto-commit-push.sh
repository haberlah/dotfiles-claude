#!/bin/bash
# Auto-commit and push all changes when Claude finishes responding.
# Handles both the current project and the global dotfiles-claude config repo.
#
# For project repos with .github/workflows/auto-pr.yml on main/master:
#   pushes to auto/YYYY-MM-DD branch (GitHub Action creates the PR).
# For everything else: pushes to the current branch (direct push).
#
# Outputs status via stderr so Claude relays it to the user.

auto_commit_push() {
  local dir="$1"
  local label="$2"

  cd "$dir" 2>/dev/null || return 0

  # Must be in a git repo
  git rev-parse --is-inside-work-tree &>/dev/null || return 0

  # Check for any uncommitted changes (staged, unstaged, or untracked)
  if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    return 0
  fi

  BRANCH=$(git branch --show-current 2>/dev/null)
  [ -z "$BRANCH" ] && return 0

  # Stage all changes
  git add -A 2>/dev/null

  # Build commit message from changed files
  CHANGED=$(git diff --cached --name-only 2>/dev/null | head -10 | tr '\n' ', ' | sed 's/,$//')
  [ -z "$CHANGED" ] && return 0

  # Commit (dotfiles pre-commit hook scans for secrets before pushing to public repo)
  git commit -m "auto: ${CHANGED}" &>/dev/null || return 0

  # Push to remote
  if ! git remote get-url origin &>/dev/null; then
    echo "${label}: committed locally (no remote configured)." >&2
    return 0
  fi

  # Project repos on main/master with auto-PR workflow: push to auto/ branch
  REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  if [ "$label" = "Project" ] \
     && [[ "$BRANCH" = "main" || "$BRANCH" = "master" ]] \
     && [ -f "${REPO_ROOT}/.github/workflows/auto-pr.yml" ]; then
    AUTO_BRANCH="auto/$(date +%Y-%m-%d)"
    if git push --force-with-lease origin "HEAD:refs/heads/${AUTO_BRANCH}" &>/dev/null; then
      echo "Project: pushed to ${AUTO_BRANCH}." >&2
    else
      echo "Project: push to ${AUTO_BRANCH} failed. Committed locally." >&2
    fi
    return 0
  fi

  # Default: push to current branch
  if git push origin "$BRANCH" &>/dev/null; then
    echo "${label}: committed and pushed to ${BRANCH}." >&2
  else
    echo "${label}: committed locally but push failed." >&2
  fi
}

# 1. Auto-commit the current project
auto_commit_push "$CLAUDE_PROJECT_DIR" "Project"

# 2. Auto-commit global Claude Code config (skills, hooks, settings)
DOTFILES_CLAUDE="$HOME/dotfiles-claude"
if [ -d "$DOTFILES_CLAUDE/.git" ]; then
  auto_commit_push "$DOTFILES_CLAUDE" "Config"
fi

exit 0
