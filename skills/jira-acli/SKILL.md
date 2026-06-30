---
name: jira-acli
description: Operate David's Jira Cloud (bellaslainte.atlassian.net) from the terminal with the official Atlassian CLI `acli`. Use whenever the task involves reading or writing a Jira board/project, creating/editing/transitioning/deleting work items, populating a Kanban board (e.g. from a Google Sheet), running JQL searches, or installing/authenticating acli. Captures the non-obvious gotchas: search defaults to 30 results, create-bulk caps at 50 and silently drops labels + ignores description in JSON, edit --labels appends, and the KAN board's columns are Idea/In Progress/Done.
---

# Jira via Atlassian CLI (`acli`)

The official Atlassian CLI. Binary: `/opt/homebrew/bin/acli` (on PATH). Verify with `acli --version`.

## Environment (David's Jira)
- **Site:** `bellaslainte.atlassian.net`
- **Project `KAN`** ("Team Bella", software, team-managed) — **board id 2**. Also `SAM1` (id 1, example, ignore).
- **KAN columns/statuses: `Idea` → `In Progress` → `Done`.** New items land in **`Idea`** (the backlog column), NOT "To Do". Transition by the exact status name.
- **Work item types on KAN:** `Task`, `Feature` (also standard: Epic, Story, Bug, Subtask).
- Owners in the sheets are people's names, not Jira accounts — only `david` is a real user, so owners go in the description, not `--assignee`.

## Install (already done; for a fresh machine)
```bash
brew tap atlassian/homebrew-acli
brew trust atlassian/acli      # Homebrew 6.x refuses untrusted taps without this
brew install acli
```
Direct download alternative: `curl -LO "https://acli.atlassian.com/darwin/latest/acli_darwin_arm64/acli"` (Apple Silicon), then `chmod +x` + move to PATH.

## Auth — browser OAuth, David runs it himself
```bash
acli jira auth login --web     # opens browser, authorises against bellaslainte.atlassian.net; token cached locally
```
Per David's standing preference, hand him the command (pbcopy it) and let him run it — don't invoke the browser login from the Bash tool. Once cached, I can drive all read/write commands. Auth is NOT API-token based here.

## Command map
| Action | Command |
|--------|---------|
| List boards | `acli jira board search` |
| Project info | `acli jira project view --key KAN` |
| Search items | `acli jira workitem search --jql "project = KAN ORDER BY status" --limit 100 --json` |
| View one item | `acli jira workitem view KAN-7 --fields summary,labels,status --json` |
| Create one | `acli jira workitem create --summary "..." --project KAN --type Task --description "..." --label "consent" --assignee @me` |
| Bulk create | `acli jira workitem create-bulk --from-csv issues.csv --yes` |
| Edit | `acli jira workitem edit --key "KAN-1,KAN-2" --summary "..." --description "..." --labels "x" --yes` |
| Transition (status/column) | `acli jira workitem transition --key "KAN-1,KAN-2" --status "In Progress" --yes` (or `--jql "..."`) |
| Assign | `acli jira workitem assign --key "KAN-1,KAN-2" --assignee "@me" --yes` (`@me`, an email, or `default`) |
| Delete | `acli jira workitem delete --key "KAN-1,KAN-2" --yes` |

## What acli CANNOT do (use the Jira web UI or REST API instead)
- **Create, rename, reorder, or delete board columns / workflow statuses.** There is no `workflow`/`status` command and no raw-API passthrough. `board create` only builds a board from a filter; `project update` doesn't touch statuses. Board columns in team-managed projects = statuses. Do column/status changes in the web UI (or drive Claude-in-Chrome), THEN use `acli transition --status "<col name>"` to move cards in — once a column exists, its name IS a valid transition target.
- **Approving a user's access/join request** (e.g. "X needs to join Jira") — not in `acli admin` (which only activate/deactivate/delete managed accounts). It's an access-control grant: leave it to the user via the email approve link or admin.atlassian.com. (Also a hard safety rule: don't grant access on someone's behalf.)
- Verify a user got access (read-only): `home.atlassian.com/o/<orgId>/people/search?query=<name>` — they show in "People you work with" with a recent-activity timestamp once active.

### Driving the team-managed board UI in Chrome (column ops) — what actually works
Board URL: `bellaslainte.atlassian.net/jira/software/projects/KAN/boards/2`.
- **Rename a column:** double-click the column header title → it becomes an input → `cmd+a`, type new name, `Return`. (Single-click on an *empty* new column also opens rename; single-click on an established column instead surfaces a "…" kebab.)
- **Create a column:** click the **+** at the far right of the column row. The floating name input has flaky focus — the reliable sequence is: click **+**, then **explicitly click the input field**, type the name, then click the ✓ check (or `Return` + click empty board area). Verify with a screenshot; if no column appears, retry (first attempt often no-ops). New columns always append at the far right.
- **Reorder a column:** the "…" kebab has **Move column left / Move column right** (clean, click-based — preferred). Drag-the-header also works (`left_click_drag` header→target x) BUT throws a transient "Something went wrong" error and blanks the board — it actually persisted; just `navigate` to reload and the new order is there. The kebab is hard to summon on freshly-created empty columns, so drag-then-reload was what worked for new columns.
- KAN's status set after the 2026-06-30 build: **Idea, Pilot, Beta, RC1, In Progress, In Review, Done** (Pilot/Beta/RC1 are phase columns split out of the old "To Do"). Phase is also mirrored on every card as a `phase-pilot`/`phase-beta`/`phase-rc1` label so it survives once a card moves into In Progress.

## GOTCHAS (all learned the hard way — trust these)
1. **`search` defaults to only 30 results.** Always pass `--limit 100` (or `--paginate`) or you silently miss rows. Output is a JSON array; fields are nested under each item's `.fields` (`.fields.summary`, `.fields.status.name`, `.fields.labels`).
2. **`view` takes the key positionally** (`acli jira workitem view KAN-7`), NOT `--key`. `--key` errors with "unknown flag".
3. **`create-bulk` caps at 50 issues per call.** More → `must have at most 50 items`. Split into batches.
4. **`create-bulk --from-json` rejects a `description` field** → 400 `request body is missing or invalid`. JSON only reliably takes `summary, projectKey, issueType, label, assignee`.
5. **`create-bulk --from-csv` accepts `description` but SILENTLY IGNORES the `label` column.** The call reports success; labels just never attach. Apply labels afterwards via `edit`.
6. **`create-bulk` does NOT print the created keys, and `--json` is not supported on it.** To get keys after a bulk create, `search` the project and match cards back to source rows by a prefix you embedded in the summary (e.g. `A1 — ...`).
7. **`edit --labels` APPENDS labels, it does not replace.** To change a label set, `--remove-labels "old"` then (or in another call) `--labels "new"`. Re-running `--labels` to "fix" a label just stacks them.
8. **Flag name differs between create and edit:** `create` uses `--label` (singular); `edit` uses `--labels` (plural). CSV bulk column is `label`.
9. **`transition --status` must match an existing workflow status name exactly** (KAN: Idea / In Progress / Done). Batch many keys in one `--key "a,b,c"` call, or target by `--jql`.
11. **`assign` (like create-bulk's siblings) prompts for confirmation — pass `-y`/`--yes`** or it cancels with "assign cancelled". Same for `transition`, `edit`, `delete`.
10. CSV: write with `csv.QUOTE_ALL` (summaries contain commas, `>`, parentheses). Keep descriptions **single-line** (join with ` | `) — avoids any newline-in-CSV-field parser risk.

## Recipe: build a Kanban board from a Google Sheet
Proven flow (used to populate KAN from a Sheet of 57 items across 8 areas):
1. **Read the sheet:** `gws sheets +read --spreadsheet <ID> --range "A1:Z200" --format json` (note: `+read` uses `--spreadsheet`/`--range` flags, NOT `--params`).
2. **Build a CSV** (`build_board_csv.py` in this skill): columns `summary,projectKey,issueType,description,label`. Put a stable source-id prefix in the summary (`A1 — <item>`) so you can match keys later. Map a category column → one label per row (slugified, no spaces). Fold the other columns (owner, phase, status, notes, blockers) into a single-line `description`. Build a sidecar `meta.json` mapping source-id → target status.
3. **Wipe placeholders:** `acli jira workitem delete --key "KAN-1,KAN-2,KAN-3" --yes` (new projects seed 3 sample cards).
4. **Create in batches of ≤50:** `acli jira workitem create-bulk --from-csv batch.csv --yes`.
5. **Recover keys:** `acli jira workitem search --jql "project = KAN ORDER BY created ASC" --limit 100 --json`, match each card to its source-id by the summary prefix.
6. **Set columns:** group keys by target status, then one `transition --key "..." --status "<name>"  --yes` per status (skip the default column).
7. **Apply category labels:** group keys by label, one `edit --key "..." --labels "<slug>" --yes` per group (remember it appends — start from cards with no labels).
8. **Verify:** `search ... --fields status,labels --json`, tally by column and label, confirm total and that no card is unlabelled.

Status mapping used for KAN: sheet `Open → Idea`, `In progress → In Progress`, `Closed → Done`, `Blocked → In Progress` + a `blocked` label (the default board has no Blocked column).
