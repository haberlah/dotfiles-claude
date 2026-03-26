---
name: gws-drive-backup
description: Download and back up Google Drive files locally via the gws CLI with format conversion. Google Docs to Markdown (plus DOCX if images detected), Google Sheets to CSV per tab plus XLSX, Google Slides to PPTX, all other files as-is. Supports personal Drive, shared drives, and folder structures. Use when (1) user asks to back up, download, copy, sync, or mirror Google Drive files locally, (2) user asks to export Google Docs, Sheets, or Slides to local formats, (3) user wants offline access to Drive content, (4) user mentions drive backup, download from Drive, export Drive, or copy Drive files.
---

# GWS Drive Backup

## Prerequisites

- `gws` CLI installed and authenticated (`gws auth login`)
- `jq` on PATH

Verify: `gws drive files list --params '{"pageSize": 1}'`

## Automated backup

Run `scripts/gws_backup.sh`:

```bash
bash <skill_dir>/scripts/gws_backup.sh <output_dir> [--scope personal|shared|all] [--drive-id <id>]
```

```bash
bash <skill_dir>/scripts/gws_backup.sh ./my_drive                                          # personal
bash <skill_dir>/scripts/gws_backup.sh ./shared --scope shared --drive-id 0ANNP52NXM_4zUk9PVA  # one shared drive
bash <skill_dir>/scripts/gws_backup.sh ./everything --scope all                             # all drives
```

## Conversion rules

| Source | Output | Notes |
|--------|--------|-------|
| Google Docs | `.md` | If images detected, also exports `.docx` (images embedded) |
| Google Sheets | subfolder: `.csv` per tab + `.xlsx` | Tab names become CSV filenames |
| Google Slides | `.pptx` | |
| Google Forms | skipped | Not exportable via API |
| Other (PDF, DOCX, ZIP, etc.) | as-is | Original filename preserved |

## Image handling in Google Docs

Google's markdown export **silently drops all images** — no placeholders, no broken links. Content appears complete but images are simply absent.

Detection: query the Docs API for `inlineObjects`:

```bash
gws docs documents get --params '{"documentId": "DOC_ID"}' | jq '.inlineObjects | length'
```

If count > 0, also export as `.docx` which preserves embedded images:

```bash
gws drive files export --params '{"fileId": "DOC_ID", "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}'
```

The backup script does this automatically.

## Manual export commands

### List files

```bash
# Personal
gws drive files list --params '{"q": "'\''me'\'' in owners and trashed = false", "pageSize": 100, "fields": "files(id,name,mimeType,parents)"}'

# Shared drives (requires all three extra params)
gws drive files list --params '{"q": "trashed = false", "includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives", "pageSize": 100}'

# List shared drives
gws drive drives list --params '{"pageSize": 50}'
```

### Google Docs → Markdown

```bash
gws drive files export --params '{"fileId": "ID", "mimeType": "text/markdown"}'
mv download.bin "filename.md"
```

### Google Sheets → CSV + XLSX

```bash
# Full workbook
gws drive files export --params '{"fileId": "ID", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}'
mv download.xml "sheet.xlsx"

# Tab names
gws sheets spreadsheets get --params '{"spreadsheetId": "ID"}' | jq -r '.sheets[].properties.title'

# Single tab as CSV
gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "TAB"}' | jq -r '.values[] | @csv' > "tab.csv"
```

### Google Slides → PPTX

```bash
gws drive files export --params '{"fileId": "ID", "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}'
mv download.xml "slides.pptx"
```

### Binary files (PDF, DOCX, ZIP, etc.)

```bash
gws drive files get --params '{"fileId": "ID", "alt": "media"}'
mv download.bin "filename.ext"
```

## gws export behaviour

- `export` saves to `download.bin` (text) or `download.xml` (office formats) in CWD
- Each export **overwrites** the previous — rename immediately
- Shared drives require: `includeItemsFromAllDrives`, `supportsAllDrives`, `corpora: "allDrives"`
- Paginate via `nextPageToken` / `pageToken`
- All operations are **read-only** — no Drive data is modified
