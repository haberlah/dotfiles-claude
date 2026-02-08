# Claude Code Configuration

A battle-tested [Claude Code](https://docs.anthropic.com/en/docs/claude-code) setup that removes friction from AI-assisted development. Extended thinking, maximum output tokens, parallel agent teams, hands-free version control, and 17 productivity skills — all pre-configured.

**What you get:**
- Claude thinks deeper (extended thinking always on) and writes longer (64k output tokens)
- Agent teams work in parallel across tmux panes
- Every Claude response is auto-committed and pushed — no manual version control
- 17 skills for documents, spreadsheets, browser automation, accessibility, and more
- A pre-commit hook that blocks secrets from reaching your public repo

## Should You Use This?

This config is opinionated. It's designed for developers who want Claude to work autonomously with minimal interruption. Before adopting it, consider whether these trade-offs suit your workflow:

| Decision | This config | Alternative |
|---|---|---|
| Output tokens | 64k (never truncates, but uses ~40% of context for output) | 16k default (more room for input context in long sessions) |
| Thinking | Always on (better reasoning, slightly slower) | On-demand with `ultrathink` or `think hard` |
| Auto-compact | 80% (compacts earlier, preserves more buffer) | 90% default (more context before compacting) |
| Bash permissions | All commands auto-allowed | Require confirmation for each command |
| Version control | Fully automatic (every response = commit + push) | Manual commits for more control over history |
| Agent teams | Enabled with tmux split panes | Disabled (single-agent mode) |

If you want maximum autonomy and don't mind aggressive token usage, clone it. If you prefer tighter control, fork it and dial back the settings you disagree with.

## Quick Start

### Option 1: Clone directly (track upstream changes)

```bash
git clone https://github.com/haberlah/dotfiles-claude.git ~/dotfiles-claude
~/dotfiles-claude/setup.sh
```

### Option 2: Fork first (recommended — lets you customise)

1. Fork this repo on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/dotfiles-claude.git ~/dotfiles-claude
cd ~/dotfiles-claude
git remote add upstream https://github.com/haberlah/dotfiles-claude.git
~/dotfiles-claude/setup.sh
```

The setup script symlinks config files into `~/.claude/`, backing up any existing config. It also installs a pre-commit hook that scans for secrets.

## Subscribing to Updates

If you've forked the repo, you can pull new skills, settings changes, and hook improvements from upstream:

```bash
cd ~/dotfiles-claude
git fetch upstream
git merge upstream/main
```

Changes take effect on the next `claude` session.

To auto-pull daily (similar to auto-updating Claude Code itself), add this to your `~/.zshrc`:

```sh
# Auto-pull dotfiles-claude updates daily
if [ -d "$HOME/dotfiles-claude/.git" ] && [[ ! -f /tmp/.dotfiles-claude-pulled-$(date +%Y%m%d) ]]; then
  (cd "$HOME/dotfiles-claude" && git pull --ff-only origin main &>/dev/null &)
  touch /tmp/.dotfiles-claude-pulled-$(date +%Y%m%d)
fi
```

This runs silently in the background on your first terminal open each day. The `--ff-only` flag ensures it won't overwrite any local customisations — if there's a conflict, it simply skips the pull and you can resolve manually.

## What's Included

```
dotfiles-claude/
├── CLAUDE.md                       # Global instructions (applied to every session)
├── settings.json                   # Core settings, env vars, hooks
├── settings.local.example.json     # Template for machine-specific permissions
├── hooks/
│   ├── auto-commit-push.sh         # Stop hook: auto-commit + push
│   └── pre-commit-secrets-check.sh # Git hook: blocks secrets from commits
├── skills/                         # 17 installed skills
└── setup.sh                        # Symlink installer for new machines
```

> **Note:** `settings.local.json` is gitignored — it stays on your machine and is never pushed. The repo includes `settings.local.example.json` as a starting template. The setup script copies it automatically on first run.

## Settings Explained

### `settings.json`

| Setting | Value | What it does |
|---|---|---|
| `alwaysThinkingEnabled` | `true` | Enables extended thinking (chain-of-thought reasoning) on every response. Claude reasons through the problem before responding, producing significantly better results for architecture decisions, debugging, and multi-step refactors. |
| `showTurnDuration` | `true` | Shows how long each turn takes. Useful for spotting slow MCP tools or overly broad searches. |
| `teammateMode` | `"tmux"` | Agent teams display in tmux split panes rather than in-process. You can watch each teammate work in real time and scroll their output independently. Requires `tmux` installed. |

### Environment Variables

| Variable | Value | What it does |
|---|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enables agent teams — multiple Claude sessions that work in parallel, coordinated by a team lead. Ask Claude to "use a team" or describe a task that benefits from parallel work. |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `64000` | Sets maximum response length to 64k tokens. Prevents Claude from truncating long code generation mid-function. **Trade-off:** this reserves ~40% of the context window for output, leaving less room for input. If you find Claude losing context in long sessions, reduce to `32000` or `16000`. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `80` | Triggers automatic context compaction at 80% usage (default ~90%). This gives a larger buffer before hitting context limits, reducing the chance of abrupt compaction during complex reasoning. |
| `MCP_TIMEOUT` | `30000` | 30-second timeout for MCP server connections (up from default). Prevents false timeouts when MCP servers are slow to start. |
| `MCP_TOOL_TIMEOUT` | `60000` | 60-second timeout for individual MCP tool calls. Some tools (file uploads, browser automation, large searches) need more time than the default allows. |

### Permissions (`settings.local.example.json`)

This file is a **template** — the setup script copies it to `settings.local.json` on first run, and the local copy is gitignored so your machine-specific permissions never reach GitHub.

The template follows a principle of **broad allow, targeted guardrails**:

- **Auto-allowed:** All file operations (`Read`, `Edit`, `Write`, `Glob`, `Grep`), all web access (`WebSearch`, `WebFetch`), all Bash commands, Playwright browser automation, and Brave Search
- **Require confirmation:** Only destructive operations — `rm -rf *`, `git push --force`, `git reset --hard`, `sudo rm`

This eliminates permission prompts during normal work while catching genuinely dangerous commands. If you prefer tighter control, remove `Bash(*)` from the allow list and Claude will ask before running shell commands.

**Adding your own MCP tools:** Edit your local `settings.local.json` (not the template) and add permissions to the `allow` array. The naming pattern is `mcp__SERVER_NAME__tool_name`.

## Auto-Commit Workflow

The `Stop` hook (`hooks/auto-commit-push.sh`) runs after every Claude response and handles two repos:

**1. Your current project** (`$CLAUDE_PROJECT_DIR`):
- Stages all changes, commits with a message listing changed files, and pushes
- Uses `--no-verify` to skip project-level pre-commit hooks (speed over ceremony)
- Outputs a `git pull` command for syncing to other environments

**2. Your global Claude config** (`~/dotfiles-claude/`):
- Detects changes to settings, skills, hooks, or CLAUDE.md
- Commits and pushes automatically — **with** the pre-commit secrets hook enabled
- If the secrets hook blocks the commit, you'll see a warning and the push is skipped

This means installing a new skill, tweaking a setting, or adding a hook is automatically synced to GitHub without any manual git commands.

## Security

The **pre-commit secrets hook** (`hooks/pre-commit-secrets-check.sh`) runs on every commit to the dotfiles repo and scans for:

- API keys and tokens (Anthropic `sk-ant-`, GitHub `ghp_`, AWS `AKIA`, Slack `xox`)
- JWTs (`eyJ...`)
- Browser session cookies (`SAPISID`, `SSID`, `httpOnly`)
- Credential files (`.env`, `credentials.json`, `*.pem`, `*.key`)
- Private keys and passwords

If a match is found, the commit is blocked with a clear explanation of what was detected. Override with `git commit --no-verify` if it's a false positive.

This is particularly important because some skills store local authentication state (browser sessions, API tokens) that should never reach a public repo.

## Global Instructions (`CLAUDE.md`)

The included `CLAUDE.md` sets session-wide behaviour. **You should customise this for your own preferences.** The included version demonstrates:

- **Language preference** — Australian English in comments and chat (change to your locale)
- **Plan-first workflow** — Claude outlines its approach before implementing non-trivial tasks, using plan mode for multi-step work
- **Agent teams guidance** — Claude proactively uses teams for research + implementation, frontend + backend, multi-file refactors, and parallel testing
- **Auto-commit awareness** — Claude doesn't ask about version control since the Stop hook handles it
- **Replit integration** — Claude relays pull commands for syncing a Replit deployment (remove if you don't use Replit)

## Skills

17 skills are included, extending Claude with specialised capabilities:

| Skill | What it does |
|---|---|
| `article-extractor` | Extracts clean article content from URLs, stripping ads and navigation |
| `csv-data-summarizer` | Analyses CSV files with pandas — summary stats and visualisations |
| `docx` | Creates and edits Word documents with tracked changes and comments |
| `file-organizer` | Intelligently organises files, finds duplicates, suggests folder structures |
| `image-enhancer` | Improves screenshot and image quality for documentation |
| `lead-research-assistant` | Identifies business leads with contact strategies |
| `pdf` | PDF manipulation — text extraction, merging, splitting, form filling |
| `playwright` | Full browser automation — testing, screenshots, form filling, link checking |
| `pptx` | Creates and edits PowerPoint presentations |
| `react-best-practices` | Vercel Engineering's React/Next.js performance patterns |
| `replit-prd` | Generates PRD prompt sequences for Replit Agent |
| `skill-creator` | Guide for creating new Claude Code skills |
| `wcag-accessibility` | WCAG 2.2 AA compliance for React Native and Next.js |
| `web-artifacts-builder` | Multi-component HTML artifacts with React, Tailwind, shadcn/ui |
| `web-design-guidelines` | Reviews UI code against Web Interface Guidelines |
| `webapp-testing` | Tests local web applications with Playwright |
| `xlsx` | Creates and analyses spreadsheets with formulas and formatting |

Skills are installed globally in `~/.claude/skills/` and available in every session. To add more, use `/install-skill` in Claude Code or copy skill folders into the `skills/` directory.

## Customising After Forking

After forking, these are the files you'll want to personalise:

| File | What to change |
|---|---|
| `CLAUDE.md` | Replace language preference, remove Replit references, add your own workflow conventions |
| `settings.local.json` | Already gitignored — edit your local copy to add MCP server permissions and adjust Bash permission level |
| `settings.local.example.json` | Update the template if you want to share your permission patterns with others |
| `skills/` | Remove skills you don't use, add your own |
| `settings.json` | Adjust token limits, disable auto-commit hook if you prefer manual control |

Everything else (thinking mode, auto-compact, agent teams, MCP timeouts) works well as-is for most developers.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed via npm: `npm install -g @anthropic-ai/claude-code`
- Git and GitHub CLI (`gh`) for the auto-commit workflow
- tmux for agent teams in split-pane mode: `brew install tmux` (macOS)
- Node.js 18+ (required by Claude Code)
