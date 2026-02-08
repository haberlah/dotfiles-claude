#!/bin/bash
# Auto-commit and push all changes when Claude finishes responding.
# Handles both the current project and the global dotfiles-claude config repo.
# Outputs the Replit pull command via stderr so Claude relays it to the user.

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

  # Commit — skip hooks for project repos, but run them for dotfiles
  # (the dotfiles pre-commit hook scans for secrets before pushing to a public repo)
  if [ "$label" = "Config" ]; then
    git commit -m "auto: ${CHANGED}" &>/dev/null || return 0
  else
    git commit -m "auto: ${CHANGED}" --no-verify &>/dev/null || return 0
  fi

  # Push to remote
  if git remote get-url origin &>/dev/null; then
    if git push origin "$BRANCH" &>/dev/null; then
      echo "${label}: committed and pushed to ${BRANCH}. Run in Replit: git pull origin ${BRANCH}" >&2
    else
      echo "${label}: committed locally but push failed. Run: git push origin ${BRANCH}" >&2
    fi
  else
    echo "${label}: committed locally (no remote configured)." >&2
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
