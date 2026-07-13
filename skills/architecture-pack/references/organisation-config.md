# Organisation config — BellaAssist architecture pack

## Local clone paths (default)

| Repo | Path |
| --- | --- |
| Architecture pack | `~/Documents/GitHub/bella-assist-architecture-pack` |
| BellaAssist V1 runtime | `~/Documents/GitHub/BellaAssist-V1` |
| Prefer clean worktrees for regen | `~/Documents/GitHub/.worktrees/BellaAssist-V1-main-for-archpack` (or equivalent) |
| Foundations (GCP FAST) | `~/Documents/GitHub/bella-gcp-foundations` (out of scope for this skill) |

## GitHub

| Resource | Value |
| --- | --- |
| Pack | `Bella-Slainte/bella-assist-architecture-pack` (private) |
| App | `Bella-Slainte/BellaAssist-V1` (private) |
| Org | Bella-Slainte |

## Environment overrides for pack generators

```bash
export BELLAASSIST_REPO_PATH=/path/to/BellaAssist-V1
export PRODUCT_CANON_PATH=/path/to/01_product-canon   # optional
export SCHEMA_VIEWER_HTML=/path/to/schema-viewer.html # optional
export ARCHITECTURE_PACK_REPO=/path/to/bella-assist-architecture-pack  # for V1 embed check
```

## Embed check (from BellaAssist-V1)

```bash
npm run check:architecture-pack
# or
npm run check:architecture-pack -- --source /path/to/bella-assist-architecture-pack
```

The check compares **`content/` and `generated/` only**. Pack-only `qa/` evidence files may legitimately diverge.

## Skill install

| Tool | Install |
| --- | --- |
| Claude Code | `~/.claude/skills` → `dotfiles-claude/skills` (whole tree) |
| Codex | symlink `~/.codex/skills/architecture-pack` → `../../dotfiles-claude/skills/architecture-pack` |
| Grok | symlink `~/.grok/skills/architecture-pack` → `../../dotfiles-claude/skills/architecture-pack` |

## Obsidian

- Vault: `~/Documents/Obsidian Vault/`
- Programme folder: `BellaAssist Architecture Pack/`
- Cross-surface map: `Document Map — What Lives Where.md`
