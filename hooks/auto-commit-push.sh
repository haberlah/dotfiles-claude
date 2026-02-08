#!/bin/bash
# Auto-commit and push all changes when Claude finishes responding.
# Outputs the Replit pull command via stderr so Claude relays it to the user.

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Must be in a git repo
git rev-parse --is-inside-work-tree &>/dev/null || exit 0

# Check for any uncommitted changes (staged, unstaged, or untracked)
if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  exit 0
fi

BRANCH=$(git branch --show-current 2>/dev/null)
[ -z "$BRANCH" ] && exit 0

# Stage all changes
git add -A 2>/dev/null

# Build commit message from changed files
CHANGED=$(git diff --cached --name-only 2>/dev/null | head -10 | tr '\n' ', ' | sed 's/,$//')
[ -z "$CHANGED" ] && exit 0

git commit -m "Update: ${CHANGED}" --no-verify &>/dev/null || exit 0

# Push to remote
if git remote get-url origin &>/dev/null; then
  if git push origin "$BRANCH" &>/dev/null; then
    echo "Committed and pushed to ${BRANCH}. Run in Replit: git pull origin ${BRANCH}" >&2
  else
    echo "Committed locally but push failed. Run: git push origin ${BRANCH}" >&2
  fi
else
  echo "Committed locally (no remote configured)." >&2
fi

exit 0
