#!/bin/bash
# brave-fallback-notify.sh — PreToolUse hook for brave-search tools
# Alerts the user when Claude falls back from Perplexity to Brave Search.

set -euo pipefail

# Read tool input from stdin (required by hook protocol)
INPUT=$(cat)

# Extract the tool name for the notification message
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "brave_web_search"' 2>/dev/null)

# Allow the call but inject a visible notification
echo "{\"decision\": \"allow\", \"reason\": \"SEARCH FALLBACK: Perplexity unavailable or failed. Falling back to Brave Search (${TOOL_NAME}). Results may be less comprehensive.\"}"
exit 0
