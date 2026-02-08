# Claude Code Configuration

An opinionated [Claude Code](https://docs.anthropic.com/en/docs/claude-code) setup optimised for **deep reasoning**, **maximum output length**, and **minimal interruption**. Extended thinking is always on, output tokens are maxed at 64k, agent teams run in parallel across tmux panes, and every response is auto-committed and pushed — no manual version control.

## What This Optimises For

| Priority | How |
|---|---|
| **Output quality** | Extended thinking (chain-of-thought) enabled on every response |
| **No truncation** | 64k output tokens — Claude never cuts off mid-function |
| **Long sessions** | Auto-compaction at 80% context prevents abrupt context loss |
| **Parallel work** | Agent teams with tmux split panes for real-time visibility |
| **Zero friction** | Auto-commit + push on every response, broad tool permissions |
| **Safety** | Pre-commit hook blocks secrets, deny rules protect sensitive files |

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

### Or clone directly

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
  (cd "$HOME/dotfiles-claude" && git pull --ff-only origin main &>/dev/null &)
  touch /tmp/.dotfiles-claude-pulled-$(date +%Y%m%d)
fi
```

Runs silently in the background on first terminal open each day. `--ff-only` ensures it never overwrites local customisations.

## Repo Structure

```
dotfiles-claude/
├── CLAUDE.md                       # Global instructions for every session
├── settings.json                   # Core settings, env vars, hooks
├── settings.local.example.json     # Permission template (copied on setup)
├── hooks/
│   ├── auto-commit-push.sh         # Stop hook: auto-commit + push
│   └── pre-commit-secrets-check.sh # Git hook: blocks secrets from commits
├── skills/                         # 16 productivity skills
└── setup.sh                        # One-command installer
```

> `settings.local.json` is gitignored — your machine-specific permissions stay local and are never pushed.

## Settings Reference

### Core settings (`settings.json`)

| Setting | Value | Effect |
|---|---|---|
| `alwaysThinkingEnabled` | `true` | Extended thinking on every response. Better architecture decisions, debugging, and multi-step refactors. |
| `showTurnDuration` | `true` | Shows per-turn timing. Helps spot slow MCP tools or overly broad searches. |
| `teammateMode` | `"tmux"` | Agent teams in tmux split panes. Watch each agent work in real time. |

### Environment variables

| Variable | Value | Effect |
|---|---|---|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `64000` | Maximum response length. Prevents truncated code generation. **Trade-off:** uses ~40% of context for output. Reduce to `32000` if context is tight. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `80` | Auto-compacts at 80% context usage (default 90%). Larger buffer before context limits. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enables parallel agent teams. Ask Claude to "use a team" for multi-file tasks. |
| `MCP_TIMEOUT` | `30000` | 30s MCP server connection timeout (up from default 10s). |
| `MCP_TOOL_TIMEOUT` | `60000` | 60s per-tool timeout. Needed for browser automation and file uploads. |

### Permissions (`settings.local.example.json`)

Three-tier permission model: **deny > ask > allow**.

| Tier | What it covers |
|---|---|
| **deny** | Reading `.env` files, SSH keys, AWS credentials, `.pem`/`.key` files — always blocked |
| **ask** | Destructive ops: `rm -rf`, `git push --force`, `git reset --hard`, `git branch -D`, `chmod 777` — requires confirmation |
| **allow** | Everything else: file ops, Bash, web access, Playwright, Brave Search — runs without prompting |

> **Note:** `Bash(*)` auto-allows all shell commands. This is for power users who trust Claude to operate autonomously. For tighter control, remove it from the allow list — Claude will then prompt before each command.

## Auto-Commit Workflow

The Stop hook runs after every Claude response and handles two repos:

**Your project** — stages, commits (`auto: <files>`), and pushes. Uses `--no-verify` for speed.

**This config repo** (`~/dotfiles-claude/`) — detects changes to settings, skills, or hooks and auto-commits. Runs the pre-commit secrets hook before pushing. If secrets are detected, the push is blocked.

This means installing a skill, tweaking a setting, or adding a hook is automatically synced to GitHub.

## Security

**Pre-commit hook** scans every dotfiles commit for:
- API keys (Anthropic, GitHub, AWS, Stripe, Slack, SendGrid, Vercel, npm, PyPI)
- JWTs and session cookies
- Google Cloud service account keys
- Private keys and certificate files
- Credential files (`.env`, `credentials.json`, `.npmrc`, `.pypirc`)

**Gitignore** provides defence in depth — sensitive file types are blocked at both the git and hook level.

**Deny rules** in permissions prevent Claude from reading `.env` files, SSH keys, and cloud credentials during sessions.

## Skills

16 skills included:

| Skill | Purpose |
|---|---|
| `article-extractor` | Extract clean content from URLs |
| `docx` | Create/edit Word documents with tracked changes |
| `file-organizer` | Organise files, find duplicates |
| `image-enhancer` | Improve screenshot quality |
| `lead-research-assistant` | Business lead research |
| `pdf` | Extract, merge, split, fill PDF forms |
| `playwright` | Browser automation and testing |
| `pptx` | Create/edit presentations |
| `react-best-practices` | Vercel's React/Next.js performance patterns |
| `replit-prd` | PRD generation for Replit Agent |
| `skill-creator` | Create new Claude Code skills |
| `wcag-accessibility` | WCAG 2.2 AA compliance |
| `web-artifacts-builder` | Multi-component HTML artifacts |
| `web-design-guidelines` | UI review against best practices |
| `webapp-testing` | Test local web apps with Playwright |
| `xlsx` | Create/analyse spreadsheets |

## Customising After Forking

| File | What to change |
|---|---|
| `CLAUDE.md` | Language preference, workflow conventions, remove Replit references |
| `settings.local.json` | Your MCP server permissions, Bash permission level (gitignored — edit locally) |
| `settings.json` | Token limits, auto-commit behaviour, MCP timeouts |
| `skills/` | Remove skills you don't use, add your own |

Shared settings (`settings.json`, `CLAUDE.md`, hooks, skills) sync via git. Machine-specific permissions (`settings.local.json`) stay local.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code): `npm install -g @anthropic-ai/claude-code`
- Git and [GitHub CLI](https://cli.github.com/) (`gh`)
- tmux: `brew install tmux` (macOS) or `apt install tmux` (Linux)
- Node.js 18+

Tested on macOS. Should work on Linux with no changes.
