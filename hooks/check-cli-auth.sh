#!/bin/bash
# check-cli-auth.sh — SessionStart hook
# Checks CLI tool authentication and reports status.

NEEDS_AUTH=""

# GitHub CLI
if command -v gh &>/dev/null; then
  if ! gh auth status &>/dev/null 2>&1; then
    NEEDS_AUTH="${NEEDS_AUTH}
- GitHub CLI (gh) needs authentication. Command: ! gh auth login --web"
  fi
fi

# Google Workspace CLI
if command -v gws &>/dev/null; then
  TOKEN_VALID=$(gws auth status 2>/dev/null | jq -r '.token_valid // false')
  if [ "$TOKEN_VALID" != "true" ]; then
    NEEDS_AUTH="${NEEDS_AUTH}
- Google Workspace CLI (gws) needs authentication. Command: ! gws auth login"
  fi
fi

if [ -n "$NEEDS_AUTH" ]; then
  cat <<EOF
# CLI Auth Check

The following tools need re-authentication:
${NEEDS_AUTH}

Prompt the user for EACH tool individually: "X needs auth. Want to authenticate now? (y/n)". If yes, tell them to type the ! command shown above. Wait for each auth to complete before prompting for the next.
EOF
else
  echo "CLI auth check: all tools authenticated."
fi
