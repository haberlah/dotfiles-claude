# Claude Code Configuration

My personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) setup, optimised for maximum output quality, hands-free version control, and parallel agent workflows. Clone this repo and run the setup script to replicate the configuration across multiple machines.

## Quick Start

```bash
git clone https://github.com/haberlah/dotfiles-claude.git ~/dotfiles-claude
~/dotfiles-claude/setup.sh
```

The setup script symlinks everything into `~/.claude/`, backing up any existing config first.

On update, just pull:

```bash
cd ~/dotfiles-claude && git pull
```

Changes take effect on the next `claude` session.

## What's Included

```
dotfiles-claude/
├── CLAUDE.md               # Global instructions (applied to every session)
├── settings.json           # Core settings, env vars, hooks
├── settings.local.json     # Tool permissions
├── hooks/
│   ├── auto-commit-push.sh           # Stop hook: auto-commit + push
│   └── pre-commit-secrets-check.sh   # Git hook: blocks secrets from commits
├── skills/                 # 17 installed skills
└── setup.sh                # Symlink installer for new machines
```

## Settings Explained

### `settings.json`

| Setting | Value | Why |
|---|---|---|
| `alwaysThinkingEnabled` | `true` | Enables extended thinking (chain-of-thought reasoning) on every response. Significantly improves quality for complex tasks — architecture decisions, debugging, multi-step refactors. |
| `showTurnDuration` | `true` | Displays how long each turn takes. Useful for identifying slow MCP tools or overly broad searches. |
| `teammateMode` | `"tmux"` | Agent teams display in tmux split panes rather than in-process. Gives visibility into what each teammate is doing in real time. |

### Environment Variables

| Variable | Value | Why |
|---|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enables agent teams — multiple Claude sessions working in parallel, coordinated by a team lead. |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `64000` | Maximises response length so Claude never truncates code generation mid-function. **Trade-off:** reserves ~40% of context window for output, leaving less room for input. Worth it for code-heavy workflows. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `80` | Triggers context auto-compaction at 80% usage (default is ~90%). Gives a larger buffer before hitting context limits during long sessions. |
| `MCP_TIMEOUT` | `30000` | 30s timeout for MCP server connections (up from default). Prevents false timeouts with slower servers. |
| `MCP_TOOL_TIMEOUT` | `60000` | 60s timeout for individual MCP tool calls. Some tools (file uploads, browser automation) need more time. |

### Permissions (`settings.local.json`)

The permissions follow a principle of **broad allow, targeted guardrails**:

- **Auto-allowed:** File operations (Read, Edit, Write, Glob, Grep), web access (WebSearch, WebFetch), all Bash commands, and MCP tools (Playwright, Brave Search, Stridula)
- **Require confirmation:** Destructive operations only — `rm -rf *`, `git push --force`, `git reset --hard`, `sudo rm`

This eliminates permission prompts during normal work while still catching genuinely dangerous commands.

## Auto-Commit Workflow

The `Stop` hook (`hooks/auto-commit-push.sh`) runs after every Claude response and:

1. Checks if you're in a git repo with uncommitted changes
2. Stages all changes
3. Commits with a message listing changed files
4. Pushes to the current branch
5. Outputs a `git pull` command for syncing to other environments (e.g., Replit)

This means you never need to think about version control while working with Claude. Every response is automatically saved and pushed.

**Note:** This hook operates on `$CLAUDE_PROJECT_DIR` (whatever project you're working in), not on this dotfiles repo. Settings changes need to be manually committed and pushed from `~/dotfiles-claude/`.

## Security

This repo includes a **git pre-commit hook** (`hooks/pre-commit-secrets-check.sh`) that scans staged files for:

- API keys and tokens (Anthropic, GitHub, AWS, Slack, JWTs)
- Browser session cookies and auth state
- Credential files (`.env`, `credentials.json`, `*.pem`, `*.key`)
- Private keys and passwords

If a potential secret is detected, the commit is blocked with a clear explanation. Override with `git commit --no-verify` if it's a false positive.

The hook is automatically installed by `setup.sh` and also protects against accidentally committing sensitive data from skills that store local state.

## Global Instructions (`CLAUDE.md`)

The `CLAUDE.md` file provides session-wide instructions:

- **Australian English** in comments and communication
- **Plan-first workflow** — Claude must outline its approach before implementing non-trivial tasks, using plan mode for multi-step work
- **Agent teams by default** for tasks that benefit from parallel work (research + implementation, frontend + backend, multi-file refactors)
- **Auto-commit awareness** — Claude knows not to ask about version control since it's handled by the Stop hook

## Agent Teams

With `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and `teammateMode: "tmux"`, Claude can spawn multiple agents that work in parallel:

- A **team lead** coordinates the work and assigns tasks
- **Teammates** work independently in separate tmux panes
- Each teammate has its own context window, so they don't compete for space
- Useful for: research while implementing, testing while coding, parallel file changes

To use: ask Claude to "use a team" or describe a task that benefits from parallel work. Claude will proactively suggest teams when appropriate.

## Skills

17 skills are included, extending Claude's capabilities:

| Skill | Purpose |
|---|---|
| `article-extractor` | Extract clean content from URLs |
| `csv-data-summarizer` | Analyse CSV files with pandas |
| `docx` | Create and edit Word documents |
| `file-organizer` | Organise files and folders |
| `image-enhancer` | Improve image quality |
| `lead-research-assistant` | Business lead research |
| `pdf` | PDF manipulation and form filling |
| `playwright` | Browser automation and testing |
| `pptx` | Create and edit presentations |
| `react-best-practices` | React/Next.js performance patterns |
| `replit-prd` | PRD generation for Replit Agent |
| `skill-creator` | Create new skills |
| `wcag-accessibility` | WCAG 2.2 AA compliance |
| `web-artifacts-builder` | Complex HTML artifacts |
| `web-design-guidelines` | UI review against best practices |
| `webapp-testing` | Test local web apps with Playwright |
| `xlsx` | Spreadsheet creation and analysis |

Skills are installed globally in `~/.claude/skills/` and available in every session.

## Syncing Across Machines

This repo is designed to be cloned on multiple machines:

1. **First machine:** Already set up with symlinks
2. **New machine:** Clone + run `setup.sh`
3. **Keeping in sync:** Pull on each machine after pushing changes

Settings changes made on any machine can be committed and pushed:

```bash
cd ~/dotfiles-claude
git add -A && git commit -m "Update settings" && git push
```

The pre-commit hook will block any accidental secret leaks before they reach GitHub.

## Customising for Your Own Use

Fork this repo and adjust:

1. **`CLAUDE.md`** — Replace with your own global instructions (language preferences, workflow conventions)
2. **`settings.json`** — Tune token limits, enable/disable thinking, adjust MCP timeouts
3. **`settings.local.json`** — Add your own MCP tool permissions, adjust safety guardrails
4. **`skills/`** — Remove skills you don't need, add your own from the [skill marketplace](https://claude.ai/skills) or create custom ones with the `skill-creator` skill

### Token Limit Considerations

The `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000` setting is aggressive. If you find Claude losing context in long sessions, consider reducing it to `32000` or `16000`. The trade-off is between response length and available input context.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed via npm: `npm install -g @anthropic-ai/claude-code`
- Git and GitHub CLI (`gh`) for the auto-commit workflow
- tmux for agent teams in split-pane mode (install with `brew install tmux` on macOS)
