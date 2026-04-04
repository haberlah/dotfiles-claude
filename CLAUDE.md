# Global Claude Code Instructions

## Language preferences

Always use Australian English spelling when:
- Writing comments in code (not the code itself, only comments)
- Communicating with me in chat

Examples: colour, behaviour, organisation, initialise, centre, analyse, favourite, honour.

## Planning workflow

Before implementing any non-trivial task:
1. Plan the approach first — outline what files will be changed and why
2. Present the plan for my review
3. Only proceed with implementation after I approve

Use EnterPlanMode for multi-step tasks. Always think through the full approach before writing code.

## Agent teams

Use agent teams for tasks that benefit from parallel work:
- Research + implementation in parallel
- Frontend + backend changes
- Multi-file refactors
- Testing while implementing

## Web search and browsing

### Tool selection — Perplexity

Use the Perplexity MCP tools as the primary search and research engine. Select the right tool based on query complexity:

| Tool | When to use | Context size | Speed |
|------|-------------|-------------|-------|
| **perplexity_ask** | **DEFAULT** for all standard queries: factual lookups, API docs, error messages, recent changes, procedural guidance. | `medium` always. Add `search_recency_filter` for evolving topics | ~3s |
| **perplexity_reason** | Comparisons, architectural analysis, current-state synthesis, anything requiring multi-source reasoning. Use `strip_thinking: true` when context window is getting full. | `high` | ~5s |
| **perplexity_search** | URL discovery only — when you need raw links to show the user or feed into another tool. NOT needed alongside ask/reason. | N/A | ~2s |
| **perplexity_research** | ONLY when user explicitly requests "deep research" or "comprehensive investigation". Never use autonomously. Always use `reasoning_effort: "high"` and `strip_thinking: true`. Warn user it takes 90-120s before calling. | N/A | 90-120s |

**Decision tree (use for all web queries):**
1. Does it require comparing alternatives, synthesising multiple sources, or analysing tradeoffs? → `perplexity_reason` + `high` context
2. Is it a strategic/migration/adoption decision the user explicitly wants researched in depth? → Warn about 90-120s, then `perplexity_research`
3. Everything else (the default) → `perplexity_ask` + `medium` context. Add `search_recency_filter: "week"` or `"month"` for recent or evolving topics

**Quality settings for ask and reason:**
- Use `search_recency_filter: "day"` or `"week"` for current events (applied to `perplexity_ask` as needed)
- Use `search_domain_filter` to restrict to authoritative sources when appropriate
- Use `strip_thinking: true` on reason when context window is getting full

### Escalation chain — never give up after one tool fails

1. **Perplexity** (ask or reason as above) — first choice
2. **Brave Search** — fallback if Perplexity fails or times out (user will be notified via hook)
3. **WebFetch** — simple public page retrieval
4. **Playwright** — local browser automation, JS-rendered pages
5. **Browserbase** — fallback for pages that block local access. Do not use `stagehand_agent`

Always try multiple tools before reporting failure. Run search and browsing in parallel when possible.

## Auto-commit workflow

Changes are automatically committed and pushed to GitHub by a Stop hook after each response. Do NOT ask about version control — it is handled automatically.

## Google Workspace access

The `gws` CLI (Google Workspace CLI) is installed globally and authenticated as `david@bellamed.ai`. Use it via Bash to access Google Workspace services:

- **Google Drive**: `gws drive files list`, create folders, move/copy/delete files
- **Gmail**: `gws gmail users messages list` (also available via MCP Gmail tools)
- **Google Sheets**: `gws sheets spreadsheets get`, create/edit spreadsheets
- **Google Docs**: `gws docs documents get`, create/edit documents
- **Google Slides**: `gws slides presentations get`, create/edit presentations
- **Google Calendar**: `gws calendar events list` (also available via MCP Calendar tools)
- **Google Tasks**: `gws tasks tasklists list`
- **Google Forms**: `gws forms forms get`
- **Contacts**: `gws people people connections list`
- **Google Chat**: `gws chat spaces list`

Key usage patterns:
- Always pass parameters as JSON: `--params '{"pageSize": 5}'`
- For shared drives, add: `"includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives"`
- Credentials are at `~/.config/gws/credentials.enc` (encrypted)
- If auth fails, run `gws auth login` to re-authenticate
- Setup guide for team members: `/Users/haberlah/Documents/bella_assist/claude_gws-cli_setup.md`

### Google Workspace safety rules — MANDATORY

**Read-only operations** (list, get, search) can run freely without asking.

**Any operation that creates, modifies, sends, moves, or deletes data** in Google Workspace requires **explicit user approval BEFORE execution**. This includes but is not limited to:
- Sending or drafting emails (Gmail)
- Creating, editing, or deleting files (Drive, Docs, Sheets, Slides)
- Moving or renaming files/folders (Drive)
- Creating, updating, or deleting calendar events
- Sending Chat messages
- Modifying contacts
- Editing form content
- Updating task status
- Any `create`, `update`, `patch`, `delete`, `send`, `trash`, `move`, `copy` operation

**Approval format** — always present the action like this before running:

```
I'm about to perform the following action:

ACTION: DELETE FILE "quarterly-report.docx" FROM SHARED DRIVE
Target: [file ID or name]
Account: david@bellamed.ai

Proceed? (yes/no)
```

The ACTION line must always be in ALL CAPS and clearly describe what will happen. Never combine multiple write operations into a single approval — ask for each one separately.

**Never** run a destructive gws command speculatively, in background agents, or as part of a batch without individual approval for each write action.

## Data Science Projects

These are default preferences for new projects — override in project-level CLAUDE.md files as needed.

When working in projects with notebooks, SQL, or data pipelines:
- Check for a project-level CLAUDE.md with schema documentation first
- Use MCP database tools to inspect schemas before writing SQL — never guess column names
- For exploratory work, use Plan Mode (Shift+Tab) before writing queries
- Prefer marimo notebooks (.py) over Jupyter (.ipynb) for new projects — they're plain Python, git-friendly, and reproducible
- When writing .ipynb: generate the ENTIRE notebook in one shot, don't build cell-by-cell
- Separate data processing from visualisation into different files
- Keep reusable logic in `src/` modules that notebooks import
- Prefer polars over pandas for new projects (lazy evaluation, better performance)
- Use DuckDB for local analytical queries on parquet/CSV files
- Use CTEs in SQL, never nested subqueries. Qualify all column names with table aliases.
- Run `pytest -q --maxfail=1` after creating data transformation code
