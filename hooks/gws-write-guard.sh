#!/bin/bash
# gws-write-guard.sh — PreToolUse hook
# Blocks gws CLI write operations unless the user explicitly approves.
# Read-only operations (list, get, search) pass through silently.

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

# Define write operation patterns (gws subcommands that modify data)
# Format: gws <service> <resource> <action>
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
  "batchUpdate"
  "batchDelete"
  "star"
  "unstar"
  "archive"
  "unarchive"
)
# NOTE: "export" is excluded — gws drive files export is read-only (downloads files).
# "import" is excluded — gws drive files import uploads but the hook for "create" covers new file creation.

# Check if the command contains any write pattern
for pattern in "${WRITE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "\b${pattern}\b"; then
    # Extract what looks like the gws command for the message
    GWS_CMD=$(echo "$COMMAND" | grep -oE 'gws [a-z]+ [a-z]+ [a-z]+' | head -1)
    ACTION=$(echo "$pattern" | tr '[:lower:]' '[:upper:]')

    echo '{"decision": "block", "reason": "⛔ GWS WRITE OPERATION DETECTED: '"$ACTION"' — Command: '"${GWS_CMD:-$COMMAND}"'. This action modifies Google Workspace data. Claude must present the action in ALL CAPS and get explicit user approval before retrying."}'
    exit 0
  fi
done

# Read-only operations pass through
exit 0
