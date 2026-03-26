#!/bin/bash
# gws-write-guard.sh — PreToolUse hook
# Blocks gws CLI write operations unless the user explicitly approves.
# Read-only operations (list, get, search, export) pass through silently.

set -euo pipefail

# Read the tool input from stdin
INPUT=$(cat)

# Only check Bash tool calls
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
if [[ "$TOOL_NAME" != "Bash" ]]; then
  exit 0
fi

# Extract the command
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Only check commands that involve gws
if ! echo "$COMMAND" | grep -q '\bgws\b'; then
  exit 0
fi

# Extract only the gws invocations from the command (e.g. "gws drive files delete")
# Some gws commands have 3 subcommands (gws gmail users messages send), so capture up to 5 words
# This avoids matching write-like words in bash comments, variable names, or other commands
GWS_INVOCATIONS=$(echo "$COMMAND" | grep -oE 'gws [a-z]+ [a-z]+ [a-z]+ [a-z]+' 2>/dev/null || true)
if [ -z "$GWS_INVOCATIONS" ]; then
  GWS_INVOCATIONS=$(echo "$COMMAND" | grep -oE 'gws [a-z]+ [a-z]+ [a-z]+' 2>/dev/null || true)
fi

if [ -z "$GWS_INVOCATIONS" ]; then
  exit 0
fi

# Define write operation patterns (gws subcommand actions that modify data)
WRITE_PATTERNS=(
  "create"
  "update"
  "patch"
  "delete"
  "remove"
  "trash"
  "send"
  "modify"
  "move"
  "copy"
  "insert"
  "batchupdate"
  "batchdelete"
  "star"
  "unstar"
  "archive"
  "unarchive"
)

# Check if any gws invocation ends with a write action
while IFS= read -r invocation; do
  # Get the last word (the action) from the gws invocation
  ACTION_WORD=$(echo "$invocation" | awk '{print tolower($NF)}')

  for pattern in "${WRITE_PATTERNS[@]}"; do
    if [[ "$ACTION_WORD" == "$pattern" ]]; then
      ACTION_UPPER=$(echo "$pattern" | tr '[:lower:]' '[:upper:]')
      echo '{"decision": "block", "reason": "⛔ GWS WRITE OPERATION DETECTED: '"$ACTION_UPPER"' — Command: '"$invocation"'. This action modifies Google Workspace data. Claude must present the action in ALL CAPS and get explicit user approval before retrying."}'
      exit 0
    fi
  done
done <<< "$GWS_INVOCATIONS"

# Read-only operations (list, get, export, search, etc.) pass through
exit 0
