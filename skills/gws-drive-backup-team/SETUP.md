# Claude Code Setup Guide — GWS Drive Backup

This guide walks you through the one-time configuration needed to use the `gws-drive-backup-team` skill with Claude Code. Follow all steps before running your first backup.

## 1. Install system dependencies

```bash
# macOS
brew install jq pandoc
pip3 install openpyxl

# Verify
jq --version
pandoc --version
python3 -c "import openpyxl; print(openpyxl.__version__)"
```

## 2. Authenticate the gws CLI

```bash
gws auth login
```

Follow the browser-based OAuth flow to authenticate with your Google Workspace account. Then verify:

```bash
gws drive files list --params '{"pageSize": 1}'
```

You should see a JSON response with one file. If you get an auth error, run `gws auth login` again.

## 3. Install the skill

Unzip the skill package to your Claude Code user skills directory:

```bash
mkdir -p ~/dotfiles-claude/skills
unzip gws-drive-backup-team.zip -d ~/dotfiles-claude/skills/
```

Verify the skill is detected by starting a Claude Code session and checking that `gws-drive-backup-team` appears in the available skills. You can test by asking Claude to "back up my Google Drive".

> **Note:** If your skills directory is elsewhere, adjust the path accordingly. Claude Code looks for skills in the `skills/` subdirectory of your dotfiles-claude repo, or in `.claude/skills/` within any project directory.

## 4. Install the gws-write-guard hook (recommended)

The write-guard hook is a safety net that intercepts every Bash tool call and warns before any `gws` command that could modify Drive data (create, update, delete, send, etc.). Read-only operations pass through silently.

### Step 4a — Copy the hook script

```bash
mkdir -p ~/.claude/hooks
cp ~/dotfiles-claude/skills/gws-drive-backup-team/hooks/gws-write-guard.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/gws-write-guard.sh
```

### Step 4b — Register the hook in settings.json

Open (or create) `~/.claude/settings.json` and add the PreToolUse hook entry. If you already have a `hooks` section, merge the `PreToolUse` array — don't replace existing hooks.

**If you have no existing hooks:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/gws-write-guard.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**If you already have hooks:** Add the PreToolUse entry alongside your existing hooks. Example with an existing SessionStart hook:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "your-existing-hook.sh" }] }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/gws-write-guard.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### How the hook works

The hook reads the JSON payload that Claude Code sends before each Bash tool call. It:

1. Ignores non-Bash tool calls
2. Ignores Bash commands that don't contain `gws`
3. Extracts `gws` subcommands from the command string
4. Checks the action word against a blocklist: `create`, `update`, `patch`, `delete`, `remove`, `trash`, `send`, `modify`, `move`, `copy`, `insert`, `batchupdate`, `batchdelete`, `star`, `unstar`, `archive`, `unarchive`
5. If a write action is detected, returns a warning message that Claude must show to the user
6. Read-only actions (`list`, `get`, `export`, `search`) pass through silently

This provides defence-in-depth: even if Claude is instructed to modify Drive data, the hook will flag it before execution.

## 5. Add the GWS safety rule to CLAUDE.md (recommended)

Add the following to your global Claude Code instructions at `~/.claude/CLAUDE.md`:

```markdown
## Google Workspace access

The `gws` CLI is authenticated with your Google account. All backup operations are read-only.

### Safety rules

Read-only operations (list, get, search, export) run freely.

**Any write operation** (create, update, patch, delete, send, trash, move, copy) requires
**explicit user approval BEFORE execution**. Present as: `ACTION: <DESCRIPTION IN ALL CAPS>`
with target and account. One approval per write operation — never batch.
```

This instruction-level rule complements the hook. The hook catches the tool call mechanically; the CLAUDE.md rule shapes Claude's behaviour so it asks for approval before even attempting a write.

## 6. Test the setup

Run a small backup to confirm everything works end-to-end:

```
> Back up my personal Drive to ~/gws_test_backup — limit to 5 files so we can verify the setup works.
```

Check that:
- Files are downloaded to `~/gws_test_backup/`
- `.docx` files are converted to `.md`
- `.xlsx` files are converted to `.csv` per tab
- No write-guard warnings appeared (all ops should be read-only)

Clean up after testing:

```bash
rm -rf ~/gws_test_backup
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `gws: command not found` | Install the gws CLI and ensure it's on your PATH |
| Auth errors from `gws` | Run `gws auth login` to re-authenticate |
| `pandoc: command not found` | `brew install pandoc` |
| `ModuleNotFoundError: openpyxl` | `pip3 install openpyxl` |
| Hook not firing | Check `~/.claude/settings.json` has the PreToolUse entry with `"matcher": "Bash"` |
| Hook blocks read-only ops | This shouldn't happen — the hook only flags write actions. Check the command being run |
| Skill not detected by Claude | Verify the skill is in a directory Claude scans (user skills dir or project `.claude/skills/`) |
