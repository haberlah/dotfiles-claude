# Claude Code Configuration

An opinionated [Claude Code](https://docs.anthropic.com/en/docs/claude-code) setup optimised for **deep reasoning**, **maximum output length**, and **minimal interruption**. Extended thinking is always on, output tokens are set to 64k, agent teams run in parallel across tmux panes, and every response is auto-committed and pushed — no manual version control.

## What This Optimises For

| Priority | How |
|---|---|
| **Output quality** | Extended thinking (chain-of-thought) enabled on every response |
| **No truncation** | 64k output tokens — Claude never cuts off mid-function |
| **Long sessions** | Auto-compaction at 80% context prevents abrupt context loss |
| **Parallel work** | Agent teams with tmux split panes for real-time visibility |
| **Zero friction** | Auto-commit + push on every response, broad tool permissions |
| **Data science** | dbt + Snowflake skills via plugin, SQL/notebook conventions in CLAUDE.md |
| **Google Workspace** | 43 GWS skills + 41 recipe workflows for Gmail, Drive, Sheets, Docs, Calendar, and more |
| **Safety** | 5 hooks (secret scanning, write guards, auth checks), deny rules protect sensitive files |

## Quick Start

### Fork and customise (recommended)

```bash
# 1. Fork this repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/dotfiles-claude.git ~/dotfiles-claude
cd ~/dotfiles-claude
git remote add upstream https://github.com/haberlah/dotfiles-claude.git

# 2. Run setup (symlinks config into ~/.claude/, copies permission template)
~/dotfiles-claude/setup.sh
```

### Or clone directly (if you don't plan to track upstream updates)

```bash
git clone https://github.com/haberlah/dotfiles-claude.git ~/dotfiles-claude
~/dotfiles-claude/setup.sh
```

The setup script:
- Symlinks `CLAUDE.md`, `settings.json`, `hooks/`, and `skills/` into `~/.claude/`
- Copies `settings.local.example.json` to `settings.local.json` (your machine-specific permissions — gitignored, never pushed)
- Installs a pre-commit hook that blocks secrets
- Backs up any existing config before overwriting

## Subscribe to Updates

Pull new skills, hook improvements, and settings changes from upstream:

```bash
cd ~/dotfiles-claude && git fetch upstream && git merge upstream/main
```

Changes take effect on the next `claude` session.

**Auto-pull daily** — add to `~/.zshrc`:

```sh
if [ -d "$HOME/dotfiles-claude/.git" ] && [[ ! -f /tmp/.dotfiles-claude-pulled-$(date +%Y%m%d) ]]; then
  (cd "$HOME/dotfiles-claude" && git pull --ff-only upstream main 2>/dev/null || git pull --ff-only origin main &>/dev/null &)
  touch /tmp/.dotfiles-claude-pulled-$(date +%Y%m%d)
fi
```

Runs silently in the background on first terminal open each day. `--ff-only` ensures it never overwrites local customisations.

## Repo Structure

```
dotfiles-claude/
├── CLAUDE.md                       # Global instructions for every session
├── settings.json                   # Core settings, env vars, hooks, plugins
├── settings.local.example.json     # Permission template (copied on setup)
├── .gitignore                      # Blocks secrets and machine-specific config
├── hooks/
│   ├── auto-commit-push.sh         # Stop: auto-commit + push (or auto-PR)
│   ├── check-cli-auth.sh           # SessionStart: verify GitHub + gws CLI auth
│   ├── gws-write-guard.sh          # PreToolUse: block GWS writes without approval
│   ├── brave-fallback-notify.sh    # PreToolUse: notify on Perplexity → Brave fallback
│   └── pre-commit-secrets-check.sh # Git: scan for secrets before public commits
├── workflows/
│   └── auto-pr.yml                 # Optional GitHub Action for self-hosted review fallback
├── install-workflows.sh            # Install self-hosted review workflow into a project repo
├── skills/                         # 123 local skills across 8 categories
├── setup.sh                        # One-command installer
└── LICENSE                         # MIT
```

> `settings.local.json` is gitignored — your machine-specific permissions and tokens stay local and are never pushed.

## Settings Reference

### Core settings (`settings.json`)

| Setting | Value | Effect |
|---|---|---|
| `alwaysThinkingEnabled` | `true` | Extended thinking on every response. Better architecture decisions, debugging, and multi-step refactors. |
| `effortLevel` | `"high"` | High reasoning effort on every turn. |
| `showTurnDuration` | `true` | Shows per-turn timing. Helps spot slow MCP tools or overly broad searches. |
| `teammateMode` | `"tmux"` | Agent teams in tmux split panes. Watch each agent work in real time. |

### Environment variables

| Variable | Value | Effect |
|---|---|---|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `64000` | Double the default (32k). Increase to `128000` if responses are still truncating, at the cost of more frequent auto-compaction. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `80` | Auto-compacts at 80% context usage (default 90%). Larger buffer before context limits. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enables parallel agent teams. Ask Claude to "use a team" for multi-file tasks. |
| `MCP_TIMEOUT` | `30000` | 30s MCP server connection timeout (up from default 10s). |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | Maximum reasoning effort via environment variable (supplements `effortLevel` setting). |
| `MCP_TOOL_TIMEOUT` | `180000` | 3-minute per-tool timeout. Needed for browser automation, file uploads, and deep research tools. |

### Permissions (`settings.local.example.json`)

Three-tier permission model: **deny > ask > allow**.

| Tier | What it covers |
|---|---|
| **deny** | Reading `.env` files, SSH keys, AWS credentials, `.pem`/`.key` files — always blocked |
| **ask** | Destructive ops: `rm -rf`, `sudo`, `git push --force`, `git reset --hard`, `git checkout --`, `git clean`, `git branch -D`, `chmod 777`, piped curl installs — requires confirmation |
| **allow** | Everything else: file ops, Bash, web access, Playwright, Brave Search, Perplexity, GitHub read tools — runs without prompting |

> **Note:** `Bash(*)` auto-allows all shell commands not matched by deny or ask rules. This is for power users who trust Claude to operate autonomously. For tighter control, remove it from the allow list — Claude will then prompt before each command.

## Hooks

5 automation scripts, configured in `settings.json` and installed by `setup.sh`:

| Script | Trigger | Purpose |
|---|---|---|
| `auto-commit-push.sh` | Stop | Stages, commits (`auto: <files>`), and pushes after every Claude response. For opted-in project repos, pushes to `auto/` branches for PR review instead of main. |
| `check-cli-auth.sh` | SessionStart | Verifies GitHub CLI (`gh`) and Google Workspace CLI (`gws`) tokens are valid. Prompts for re-auth if expired. |
| `gws-write-guard.sh` | PreToolUse (Bash) | Intercepts Google Workspace CLI write operations (create, update, delete, send, etc.) and blocks them unless explicitly approved in ALL CAPS. Read-only operations pass silently. |
| `brave-fallback-notify.sh` | PreToolUse (brave-search) | Alerts when Perplexity is unavailable and Brave Search is being used as a fallback. |
| `pre-commit-secrets-check.sh` | Git pre-commit | Scans staged files for API keys, JWTs, private keys, session cookies, and credential files before committing to this public repo. |

### Auto-commit detail

The Stop hook runs after every Claude response and handles two repos:

**Your project** — on `main`/`master`, pushes to an `auto/YYYY-MM-DD` branch and creates a PR via `gh` CLI. The Claude GitHub App reviews the PR automatically. On feature branches, pushes directly.

**This config repo** (`~/dotfiles-claude/`) — auto-commits directly to main. The pre-commit secrets hook runs before pushing. If secrets are detected, the push is blocked.

### Auto-PR workflow

All project repos on `main`/`master` get automatic PRs. No per-repo setup needed.

**One-time setup (org level):**

Install the Claude GitHub App on your GitHub org — handles review on all repos, uses your Teams/Max subscription:

```bash
# In Claude Code CLI:
/install-github-app

# Or visit: https://github.com/apps/claude
```

**How it works:**

1. Stop hook commits changes to local `main` as usual
2. Pushes to `auto/YYYY-MM-DD` branch instead of `main`
3. Hook creates a PR via `gh` CLI (one PR per day, accumulates commits)
4. Claude GitHub App reviews the PR automatically
5. You approve and merge — use **regular merge** (not squash) to keep local and remote in sync
6. To re-request review, comment `@claude review` on the PR

**Feature branches** push directly — the auto-PR flow only applies to `main`/`master`.

**Self-hosted review alternative:** Add the `workflows/auto-pr.yml` template to a repo and uncomment the `claude-code-action` review job. Requires `ANTHROPIC_API_KEY` repo secret.

## Security

**Pre-commit hook** scans every dotfiles commit for:
- API keys (Anthropic, GitHub, AWS, Stripe, Slack, SendGrid, Vercel, npm, PyPI)
- JWTs and session cookies
- Google Cloud service account keys
- Private keys and certificate files
- Credential files (`.env`, `credentials.json`, `.npmrc`, `.pypirc`)

**Gitignore** provides defence in depth — sensitive file types are blocked at both the git and hook level.

**Deny rules** in permissions prevent Claude from reading `.env` files, SSH keys, and cloud credentials during sessions.

**Write guard** hook intercepts all Google Workspace write operations and requires explicit ALL CAPS approval before execution.

## Skills

123 local skills organised into 8 categories, plus 9 via plugin:

| Category | Count | What's included |
|---|---|---|
| **Google Workspace** | 43 | Core service access (Gmail, Drive, Sheets, Docs, Slides, Calendar, Chat, Tasks, Forms, Keep, Meet, Classroom, People), action variants (`gws-gmail-send`, `gws-sheets-append`, `gws-calendar-insert`), multi-service workflows (`gws-workflow-meeting-prep`, `gws-workflow-weekly-digest`), admin and security (`gws-admin-reports`, `gws-modelarmor`) |
| **Recipes** | 41 | Pre-built multi-step workflows: email automation, calendar management, Drive operations, Sheets data tasks, cross-service workflows (`recipe-post-mortem-setup`, `recipe-send-team-announcement`, `recipe-create-events-from-sheet`) |
| **Personas** | 10 | Role-based assistants: `persona-exec-assistant`, `persona-team-lead`, `persona-project-manager`, `persona-sales-ops`, `persona-researcher`, `persona-content-creator`, `persona-customer-support`, `persona-event-coordinator`, `persona-hr-coordinator`, `persona-it-admin` |
| **Design & Creative** | 10 | `frontend-design`, `canvas-design`, `algorithmic-art`, `wardley-mapping`, `web-artifacts-builder`, `web-design-guidelines`, `brand-guidelines`, `theme-factory`, `image-enhancer`, `slack-gif-creator` |
| **Content & Research** | 7 | `article-extractor`, `doc-coauthoring`, `csv-data-summarizer`, `lead-research-assistant`, `notebooklm-skill-master`, `internal-comms`, `file-organizer` |
| **Development** | 6 | `claude-api`, `mcp-builder`, `react-best-practices`, `skill-creator`, `wcag-accessibility`, `replit-prd` |
| **Office Formats** | 4 | `docx`, `pdf`, `pptx`, `xlsx` — create, edit, extract, and convert office files |
| **Browser & Testing** | 2 | `playwright`, `webapp-testing` — browser automation and local web app testing |

All skills are invoked with `/<skill-name>` (e.g., `/pdf`, `/xlsx`, `/recipe-find-free-time`). Browse `skills/` for the full list. To remove a skill, delete its directory.

### Plugin skills ([AltimateAI/data-engineering-skills](https://github.com/AltimateAI/data-engineering-skills))

Installed via `claude plugin`, not stored in this repo. Run after setup:

1. Add the marketplace:
   ```bash
   claude plugin marketplace add AltimateAI/data-engineering-skills
   ```
2. Install both skill packs:
   ```bash
   claude plugin install dbt-skills@data-engineering-skills
   claude plugin install snowflake-skills@data-engineering-skills
   ```

Skills are available immediately in your next Claude Code session.

| Plugin | Skills |
|---|---|
| `dbt-skills` | creating-dbt-models, debugging-dbt-errors, testing-dbt-models, documenting-dbt-models, migrating-sql-to-dbt, refactoring-dbt-models |
| `snowflake-skills` | finding-expensive-queries, optimizing-query-by-id, optimizing-query-text |

## Customising After Forking

| File | What to change |
|---|---|
| `CLAUDE.md` | Language preference, workflow conventions, tool selection rules |
| `settings.local.json` | Your tokens, MCP server permissions, Bash permission level (gitignored — edit locally) |
| `settings.json` | Token limits, auto-commit behaviour, MCP timeouts, enabled plugins |
| `skills/` | Remove skills you don't use, add your own |
| `hooks/` | Remove or modify hooks (e.g., disable auto-commit, add custom guards) |

Shared settings (`settings.json`, `CLAUDE.md`, hooks, skills) sync via git. Machine-specific permissions and tokens (`settings.local.json`) stay local.

### Known caveat: symlink breakage

`setup.sh` symlinks `settings.json` into `~/.claude/`. Claude Code occasionally replaces symlinks with regular files via atomic writes (temp file → rename). If your active settings drift from the repo, re-run `setup.sh` to restore the symlinks.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code): `npm install -g @anthropic-ai/claude-code`
- Anthropic API key or Max subscription (Claude Code prompts on first run)
- Git and [GitHub CLI](https://cli.github.com/) (`gh auth login` — needed for auto-push)
- tmux: `brew install tmux` (macOS) or `apt install tmux` (Linux) — used by agent teams for split-pane visibility
- Node.js 18+

Tested on macOS. Should work on Linux with no changes.
