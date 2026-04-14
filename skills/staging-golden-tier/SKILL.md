---
name: staging-golden-tier
description: "Process raw Co-Design Program transcripts from the Google Drive Staging_Transcripts folder into Golden Tier format. Use when asked to clean transcripts, promote staging files, or update the Golden Tier collection."
summary: "Raw transcript → Golden Tier pipeline: download, clean, format, verify."
metadata:
  version: 1.0.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
        - python3
        - pandoc
---

# staging-golden-tier

Process raw Co-Design Program interview transcripts from `Staging_Transcripts` on Google Drive into the curated Golden Tier collection.

## Prerequisites

- `gws` CLI authenticated as `david@bellamed.ai` with Drive scope
- `python3` available
- `pandoc` available (for .docx conversion)
- Golden Tier location: `~/Documents/bella_assist/gws_copy/shared_drives/BellaAssist_-_Product/Co-Design_Program/Golden_Tier/`
- Staging Drive folder ID: `1W169BsPkexomhf6Qeyz-6dFOkTn-Z2UW`

## Reference files

- `references/golden-tier-spec.md` — format spec (frontmatter schema, speaker format, naming convention, cleaning checklist)
- `references/known-speakers.md` — speaker name-to-role mapping, Gemini display names, common transcription errors

Read both references before starting any processing.

## Workflow

### Phase 1 — Inventory

List the staging folder and cross-reference against the manifest.

```bash
# List staging files
gws drive files list --params '{"q": "\"1W169BsPkexomhf6Qeyz-6dFOkTn-Z2UW\" in parents and trashed=false", "includeItemsFromAllDrives": true, "supportsAllDrives": true, "fields": "files(id,name,modifiedTime,mimeType,size)", "pageSize": 100}'
```

For each file:
1. Parse the filename to extract person, session type, and stage
2. Check `manifest.yaml` for an existing entry matching that person + stage
3. Flag duplicates for comparison, mark new sessions for processing

Present the inventory table to the user for approval before proceeding.

### Phase 2 — Download & Convert

For each approved file:

```bash
# Download .docx files
gws drive files get --params '{"fileId": "<ID>", "alt": "media", "supportsAllDrives": true}' --output "/tmp/staging/<filename>"

# Convert .docx to .md
pandoc -f docx -t markdown --wrap=none "/tmp/staging/<filename>.docx" -o "/tmp/staging/<filename>.md"
```

For files already in `.md` format, download directly — no conversion needed.

### Phase 3 — Parse & Extract

Identify the source type and extract the transcript content.

**Gemini Notes exports** (most common in staging):
- The `.docx` contains both AI summary notes AND an embedded transcript
- The transcript section starts after a line containing `Transcript` (often preceded by a clipboard emoji)
- Everything before that line is the notes section (Summary, Details, Suggested next steps)
- Extract both sections: transcript → `_transcript.md`, notes → `_notes.md`

**Read AI exports** (`.txt` files):
- Pure transcript, no notes section
- Format: `TIMESTAMP - Speaker Name` followed by dialogue on next lines

**Pre-cleaned files** (already `.md` with some processing done):
- Validate existing structure against the spec
- Apply remaining cleaning steps as needed

### Phase 4 — Clean

Run the deterministic cleanup script first:

```bash
python3 scripts/clean_transcript.py "/tmp/staging/<file>.md" -o "/tmp/staging/<file>_cleaned.md"
```

This handles: pandoc artifacts, Unicode normalisation, empty spacer lines, Gemini disclaimer removal, timestamp anchor cleanup.

Then apply AI judgment (Claude does this directly):

1. **Read `references/known-speakers.md`** to map display names to canonical names and roles
2. **Standardise speaker labels**: map Gemini display names (e.g., `Bails18 Wills` → keep as-is for Gemini format; resolve `Unidentified Speaker` where possible from context)
3. **For Read AI sources**: convert to `**Speaker Name** [Role] (H:MM:SS):` format
4. **For Gemini sources**: preserve `Speaker Name: text` format with standalone timestamp blocks
5. **Merge consecutive same-speaker turns** only when clearly a single thought interrupted by the transcription
6. **Correct transcription errors** using the known errors table in known-speakers.md
7. **Verify session metadata**: confirm the date, participant name, and session type from transcript content (not just filename)

### Phase 5 — Format & Place

Generate the YAML frontmatter:

```bash
python3 scripts/generate_frontmatter.py \
  --participant "Name" \
  --role "Support Coordinator" \
  --stage 4 \
  --session-type "MVP Testing" \
  --date "2026-04-09" \
  --source "Gemini embedded transcript" \
  --source-file "original.docx" \
  --content-type transcript \
  --has-companion-notes true \
  "/tmp/staging/<file>_cleaned.md"
```

This prepends the frontmatter and document header, calculates word count, and writes the final file.

Place the output file:
- Transcript: `Golden_Tier/{SC_or_Participants}/{name}/{session_id}_{date}_transcript.md`
- Notes: `Golden_Tier/{SC_or_Participants}/{name}/{session_id}_{date}_notes.md`

### Phase 6 — Lock & Update Index

```bash
# Lock processed files
chmod 444 "Golden_Tier/{path}_transcript.md"
chmod 444 "Golden_Tier/{path}_notes.md"

# Update manifest
python3 scripts/update_manifest.py \
  --manifest "Golden_Tier/manifest.yaml" \
  --transcript "Golden_Tier/{path}_transcript.md" \
  --notes "Golden_Tier/{path}_notes.md"
```

Also update `Golden_Tier/README.md`:
- Update the folder structure section if new people added
- Update session counts in person entries
- Update gap register (remove filled gaps, note remaining ones)
- Update totals in the "What is this?" section

**IMPORTANT**: Every file write to the Golden Tier is a curated corpus modification. Present the diff for user review.

### Phase 7 — Final Verification

Re-read each produced Golden Tier file and validate:

| Check | Method | Pass criteria |
|-------|--------|---------------|
| YAML frontmatter | Parse YAML block | All required fields present and correctly typed |
| Word count | Count body words, compare to frontmatter | Within +/- 5 of `word_count` field |
| Speaker format (Read AI) | Regex: `^\*\*[^*]+\*\* \[[^\]]+\] \(\d+:\d{2}:\d{2}\):` | Every speaker turn matches |
| Speaker format (Gemini) | Regex: `^[A-Z][^:]+:` after a timestamp block | Consistent speaker labels |
| No pandoc artifacts | Search for `{.underline}`, `[~~`, trailing `\` | Zero matches |
| No Gemini noise | Search for "You should review", "Suggested next steps" | Zero matches in transcript files |
| No unmerged turns | Check for consecutive identical speaker labels | None found (or justified) |
| File permissions | `stat -f %Lp` or `ls -la` | `444` (read-only) |
| File location | Path check | Correct subfolder and naming convention |
| Manifest consistency | Parse manifest, check for duplicates, verify totals | Clean |

Present a verification summary table. Any failures get flagged for manual review.

## Safety

- All Google Drive operations follow the GWS write guard: read operations run freely, write operations require explicit user approval
- Golden Tier files are set read-only after processing — to modify, the user must explicitly unlock
- The skill is idempotent: re-running on an already-processed file detects it via the manifest and skips
- Original staging files are NOT deleted from Drive — that requires a separate approval
