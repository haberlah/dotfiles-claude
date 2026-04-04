#!/bin/bash
# Auto-commit and push all changes when Claude finishes responding.
# Handles both the current project and the global dotfiles-claude config repo.
#
# Project repos on main/master: pushes to auto/YYYY-MM-DD branch and creates a PR.
# Config repo (dotfiles-claude): pushes directly to main.
# Feature branches: pushes directly to the branch.
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

  # Project repos on main/master: push to auto/ branch and create PR
  if [ "$label" = "Project" ] && [[ "$BRANCH" = "main" || "$BRANCH" = "master" ]]; then
    AUTO_BRANCH="auto/$(date +%Y-%m-%d)"
    if git push --force-with-lease origin "HEAD:refs/heads/${AUTO_BRANCH}" &>/dev/null; then
      # Create PR if one doesn't already exist for this branch
      if command -v gh &>/dev/null; then
        EXISTING_PR=$(gh pr list --head "$AUTO_BRANCH" --state open --json number --jq '.[0].number' 2>/dev/null)
        if [ -z "$EXISTING_PR" ]; then
          PR_URL=$(gh pr create \
            --head "$AUTO_BRANCH" \
            --base "$BRANCH" \
            --title "auto: changes $(date +%Y-%m-%d)" \
            --body "Automated PR from Claude Code session.

Files: ${CHANGED}

To request review, comment \`@claude review\`." 2>/dev/null)
          if [ -n "$PR_URL" ]; then
            echo "Project: pushed to ${AUTO_BRANCH} — PR created: ${PR_URL}" >&2
          else
            echo "Project: pushed to ${AUTO_BRANCH} (PR creation failed)." >&2
          fi
        else
          echo "Project: pushed to ${AUTO_BRANCH} (PR #${EXISTING_PR})." >&2
        fi
      else
        echo "Project: pushed to ${AUTO_BRANCH} (gh CLI not found — create PR manually)." >&2
      fi
    else
      echo "Project: push to ${AUTO_BRANCH} failed. Committed locally." >&2
    fi
    return 0
  fi

  # Default: push to current branch (config repo, feature branches)
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
