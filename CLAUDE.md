# Global Claude Code Instructions

## Language preferences

Always use Australian English spelling in comments and chat (not code itself).
Examples: colour, behaviour, organisation, initialise, centre, analyse.

## Planning workflow

Before implementing any non-trivial task:
1. Plan the approach first — outline what files will be changed and why
2. Present the plan for my review
3. Only proceed with implementation after I approve

Use EnterPlanMode for multi-step tasks.

## Web search and browsing

### Perplexity — primary search engine

- **Default** → `perplexity_ask` with `search_context_size: "medium"` (always pass explicitly). Add `search_recency_filter` for evolving topics.
- **Multi-source reasoning/comparisons** → `perplexity_reason` with `high` context. Use `strip_thinking: true` when context is getting full.
- **URL discovery only** → `perplexity_search`. Not needed alongside ask/reason.
- **Deep research** → `perplexity_research` ONLY when user explicitly requests it. Always `reasoning_effort: "high"`, `strip_thinking: true`, run in a **background agent**, warn about 5-15 min wait.

### Escalation chain

Perplexity first (retry once) → Brave Search (only if Perplexity MCP is down, not for query failures) → WebFetch → Playwright → Browserbase (never `stagehand_agent`). Try multiple tools before reporting failure.

## Commit and PR workflow

A Stop hook auto-commits the dotfiles-claude config repo after every response. For project repos, the hook does NOT auto-commit.

After completing work that changes files in a project repo, invoke the `claude-pr-review` skill. Do NOT commit or push project repo changes outside the skill. If the user's intent is clear ("push it", "create a PR", "review it"), skip the prompt and proceed.

## Google Workspace access

The `gws` CLI is authenticated against David's Bella Slainte Workspace account (primary: david@bellaslainte.com; david@bellamed.ai is now an alias of the same account). Use via Bash.

**Key patterns:**
- Pass parameters as JSON: `--params '{"pageSize": 5}'`
- For shared drives: `"includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives"`
- If auth fails: `gws auth login`

### Safety rules — MANDATORY

Read-only operations (list, get, search) run freely.

**Any write operation** (create, update, patch, delete, send, trash, move, copy) requires **explicit user approval BEFORE execution**. Present as: `ACTION: <DESCRIPTION IN ALL CAPS>` with target and account. One approval per write operation — never batch. Never run destructive gws commands in background agents.
