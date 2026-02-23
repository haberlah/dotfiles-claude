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

When searching or retrieving web content, escalate through this chain — never give up after one tool fails:

1. **Perplexity** (`perplexity_search` or `perplexity_ask`) — first choice for all search queries, fact-finding, and quick answers
2. **Brave Search** — fallback if Perplexity fails or returns no results
3. **WebFetch** — for simple page retrieval (public pages, no JS rendering needed)
4. **Playwright** — for local browser automation, JS-rendered pages, or interactive workflows
5. **Browserbase** — last resort for pages that block local access (login walls, anti-bot, geo-restricted sites). Use `act`, `extract`, `observe`, and `screenshot` tools — the `stagehand_agent` tool requires a Gemini API key and should be avoided

Key rules:
- Always try multiple tools before reporting failure — escalate through the chain
- For authenticated/gated sites (LinkedIn, etc.), go to Browserbase early since simpler tools will be blocked
- When using Browserbase, prefer the `au.linkedin.com` subdomain pattern for public profile views
- Run search and browser session creation in parallel when you know browsing will be needed

## Auto-commit workflow

Changes are automatically committed and pushed to GitHub by a Stop hook after each response. Do NOT ask about version control — it is handled automatically.

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
