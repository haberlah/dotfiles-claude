---
name: obsidian-cli
description: Read, write, search, and manage David's Obsidian vault via the `obsidian` CLI installed at /opt/homebrew/bin/obsidian. Use when the user wants to save a note to Obsidian, read an existing note, search the vault, append to a daily note, manage vault content, or asks about Obsidian content. Vault path is `~/Documents/Obsidian Vault/`. The CLI is bundled with Obsidian.app and exposes 90+ commands covering files, folders, daily notes, tags, properties, search, bookmarks, templates, themes, plugins, and Obsidian Sync. CRITICAL: the CLI requires "Settings → Community plugins → Browse → install Obsidian CLI" to be enabled in Obsidian itself. Direct file write to the vault folder is the simpler fallback when scripted-vault automation is overkill.
---

# Obsidian CLI

David's Obsidian setup:

- **App**: `/Applications/Obsidian.app` (version 1.12.7).
- **CLI binary**: `/opt/homebrew/bin/obsidian` (symlinked from `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli`).
- **Vault**: `~/Documents/Obsidian Vault/` (vault name in CLI commands: `Obsidian Vault`).
- **CLI status**: enabled by David 2026-05-28 (Settings → Community plugins or equivalent setting).

## When to use the CLI vs direct file-write

**Use direct file-write (`Write` tool to `~/Documents/Obsidian Vault/<file>.md`)** when:
- Creating a new note from scratch with substantial content.
- The note can stand alone without needing Obsidian-internal links / properties / templates to resolve.
- You want the simplest write path.

**Use the CLI** when:
- Appending to an existing note (especially the daily note).
- Reading a note's resolved content (wikilinks, transclusions, embeds expanded).
- Searching across the vault.
- Managing properties, tags, bookmarks.
- Opening Obsidian to a specific file from script (`obsidian open file=...`).
- Inserting from templates.
- Triggering Obsidian Sync operations.

Direct file-write is fast and predictable; the CLI is richer but slower and requires Obsidian to be running for some commands (those that read/modify state in the running app).

## Command surface

90+ commands grouped by area. The complete list is `obsidian --help`. Most-used:

### Reading

```bash
obsidian read file="Note Name"             # by name (like wikilinks)
obsidian read path="folder/note.md"        # exact path
obsidian read                              # active file in Obsidian
obsidian outline file="Note Name"          # headings outline
obsidian properties file="Note Name"       # frontmatter properties
obsidian tags                              # all tags in vault
obsidian wordcount file="Note Name"
```

### Writing

```bash
obsidian create path="folder/new.md" content="# Title\n\nBody"
obsidian append file="Note" content="\n\n## New section"
obsidian prepend file="Note" content="Heads-up at top\n\n"
obsidian delete file="Note"
obsidian rename file="Old Name" name="New Name"
obsidian move file="Note" path="archive/Note.md"
```

Quoting rules:
- Quote values with spaces: `file="My Note"`.
- Use `\n` for newline, `\t` for tab in `content=` values.
- `file=<name>` resolves like a wikilink (first match in vault); `path=<path>` is exact from vault root.

### Daily notes

```bash
obsidian daily                             # opens / creates today's daily note
obsidian daily:append content="\n- New bullet"
obsidian daily:prepend content="Top entry\n"
obsidian daily:read
obsidian daily:path                        # prints the resolved path for today
```

### Search

```bash
obsidian search "RoPA"                     # full-text
obsidian search:context "RoPA"             # with surrounding lines
obsidian search:open "RoPA"                # open results in Obsidian
```

### Properties (frontmatter)

```bash
obsidian property:read file="Note" key="status"
obsidian property:set file="Note" key="status" value="reviewed"
obsidian property:remove file="Note" key="draft"
```

### Vaults + navigation

```bash
obsidian vaults                            # lists vaults (output: "Obsidian Vault")
obsidian open file="Note Name"             # opens the app to that file
obsidian tab:open file="Note Name"         # in a new tab
obsidian recents                           # recently opened files
obsidian bookmarks                         # vault bookmarks
```

### Linking + orphan detection

```bash
obsidian backlinks file="Note"             # who links here
obsidian links file="Note"                 # what this note links to
obsidian unresolved                        # broken wikilinks across vault
obsidian orphans                           # notes with no incoming links
obsidian deadends                          # notes with no outgoing links
```

### Templates

```bash
obsidian templates                         # list templates
obsidian template:insert file="Daily" template="meeting-notes"
obsidian template:read template="meeting-notes"
```

### Plugins, themes, snippets

```bash
obsidian plugins                           # all installed
obsidian plugins:enabled
obsidian plugin:enable id="dataview"
obsidian plugin:install id="dataview"
obsidian themes
obsidian theme:set name="Solarized"
obsidian snippets
```

### Obsidian Sync (if licensed)

```bash
obsidian sync:status
obsidian sync:history
obsidian sync:deleted
obsidian sync:restore file="Deleted note"
```

### Dev (rarely needed)

```bash
obsidian dev:screenshot path="/tmp/shot.png"
obsidian dev:console                       # JS console
obsidian eval "<js expression>"
```

### Reload / restart / hotkey

```bash
obsidian reload                            # reload current vault
obsidian restart                           # restart Obsidian app
obsidian hotkey name="Open quick switcher"
obsidian command name="Some command"       # run any registered command
```

## Vault-specific knowledge

David's `~/Documents/Obsidian Vault/` is currently lightly organised. As of 2026-05-28 the vault contains:

- `Welcome.md` (default Obsidian welcome)
- `2026-05-20.md` (daily note)
- `Untitled.base`, `Untitled.canvas` (untitled artefacts)
- `WS6 — Dry-Run Observation Runbook.md` (authored 2026-05-28 — operational runbook for the WS6 retention worker dry-run period)

When writing into the vault, prefer titles that lead with a programme acronym so they sort and search well: `WS6 — …`, `PR G — …`, `RoPA — …`, etc.

## Operational notes and gotchas

**The CLI talks to a running Obsidian instance for most commands.** Read/search/property commands work when Obsidian is open. If Obsidian is not running, file-system-level commands (create/append/prepend on direct paths) still work because they edit the vault folder, but the running app won't see the change until next refresh.

**File resolution via `file=` is wikilink-style.** It searches the whole vault for the first match. If you have two notes with the same name in different folders, use `path=` to disambiguate.

**Frontmatter YAML is parsed.** When using `property:set`, the value is stored as YAML; quote strings and use proper YAML types (arrays as `["a", "b"]` or block lists, etc.). For complex properties, write to the markdown directly via `append` or by editing the file.

**Daily notes use the user's daily-note plugin settings.** If David has the daily-notes plugin disabled, `obsidian daily` will fail. Standard install has it enabled by default.

**Direct file write is sometimes preferable.** For example, creating a 200-line technical runbook is cleaner via the `Write` tool to `~/Documents/Obsidian Vault/<title>.md` than via repeated `obsidian append` calls. The file is markdown either way; Obsidian picks it up on next refresh.

**Vault name with spaces.** Address as `vault="Obsidian Vault"` if multiple vaults exist. Single-vault setups (the current state) can omit `vault=`.

## Typical patterns

### Pattern: write a new long-form note

```bash
# Direct file-write is simpler than chained CLI calls.
Write tool → ~/Documents/Obsidian Vault/<title>.md
# Optionally open it after:
obsidian open file="<title>"
```

### Pattern: append a quick observation to today's daily note

```bash
obsidian daily:append content="\n- [[WS6 dry-run]] Gate 3 query returned 3 rows, all clean"
```

### Pattern: read a note for reference and quote into the conversation

```bash
obsidian read file="WS6 — Dry-Run Observation Runbook" > /tmp/ws6.md
# Then read /tmp/ws6.md or grep it.
```

### Pattern: confirm a note exists before referencing it

```bash
obsidian search "WS6 dry-run" 2>&1 | head -5
```

### Pattern: lock a property at end of authoring

```bash
obsidian property:set file="<title>" key="status" value="published"
obsidian property:set file="<title>" key="reviewed" value="2026-05-28"
```

### Pattern: cross-reference programme docs

Most Bella Slainte programme docs live as canonical sources in arch-pack (`docs/architecture-pack/`) and Drive Docs (Compliance > ISO 27001 > Procedures). The Obsidian vault is the personal working copy. When duplicating a doc into Obsidian for personal annotation, the standard frontmatter is:

```yaml
---
title: <Title>
tags: [<programme-acronym>, <topic>]
created: <YYYY-MM-DD>
canonical_source: <path/url to authoritative version>
status: draft | reviewed | published
---
```

## Reference

Full command list: `obsidian --help` (476 lines, copy to file if you want grep-able).

Obsidian CLI documentation upstream: bundled with Obsidian.app; the binary is built by the Obsidian team rather than a third-party project.
