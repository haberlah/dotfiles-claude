---
name: gws-drive-backup
description: Download and back up Google Drive files locally via the gws CLI with format conversion and AI-readable output. Google Docs to Markdown (with image extraction), Google Sheets to CSV per tab plus XLSX, Google Slides to PPTX. Also converts downloaded .docx to Markdown and .xlsx to CSV per tab for AI readability. Supports personal Drive, shared drives, and folder structures. Use when (1) user asks to back up, download, copy, sync, or mirror Google Drive files locally, (2) user asks to export or convert Google Docs, Sheets, Slides, .docx, or .xlsx to AI-readable formats, (3) user wants offline access to Drive content, (4) user mentions drive backup, download from Drive, export Drive, or copy Drive files.
---

# GWS Drive Backup

## Prerequisites

- `gws` CLI installed and authenticated (`gws auth login`)
- `jq` on PATH
- Python 3 on PATH (standard library only for `extract_images.py`)
- `pandoc` on PATH (for .docx → .md conversion). Install: `brew install pandoc`
- `openpyxl` Python package (for .xlsx → .csv conversion). Install: `pip3 install openpyxl`

Verify: `gws drive files list --params '{"pageSize": 1}'`

## Six-phase workflow

### Phase 0 — Export Drive metadata

Extract metadata for all files before downloading. This provides google_doc_id, modification times, and author info needed for YAML frontmatter.

```bash
gws drive files list --params '{"q": "trashed = false", "includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives", "pageSize": 500, "fields": "files(id,name,mimeType,modifiedTime,createdTime,lastModifyingUser,webViewLink,parents,size)"}'
```

Save output as `drive_metadata.json` in the backup root directory. This file is used by Phase 4 to inject frontmatter.

### Phase 1 — Download from Drive (`gws_backup.sh`)

Downloads files from Google Drive with Google-native format conversion:

```bash
bash <skill_dir>/scripts/gws_backup.sh <output_dir> [--scope personal|shared|all] [--drive-id <id>]
```

| Source type | Downloaded as |
|------------|---------------|
| Google Docs | `.md` (with base64 images extracted to `images/` + `.docx` if images found) |
| Google Sheets | subfolder: `.csv` per tab + `.xlsx` |
| Google Slides | `.pptx` |
| Google Forms | skipped (not exportable) |
| Audio/video | skipped (.mp4, .mp3, .wav, .mov, etc.) |
| Other files | as-is (PDF, DOCX, XLSX, ZIP, etc.) |

### Phase 2 — Convert local files (`convert_local.py`)

Converts downloaded binary files to AI-readable formats:

```bash
python3 <skill_dir>/scripts/convert_local.py <directory>
```

| Source type | Converted to |
|------------|-------------|
| `.docx` | `.md` via pandoc (images extracted to `images/` subfolder) |
| `.xlsx` | subfolder with `.csv` per sheet tab via openpyxl |

The script is idempotent — it skips files that already have conversions (e.g. a `.docx` where a `.md` with the same basename exists).

**Run Phase 2 after Phase 1** to ensure all content is available as plaintext for AI processing.

## Image handling

### Google Docs (Phase 1)

Google's markdown export embeds images as base64 data URIs. The `extract_images.py` script decodes each to a separate file in `images/` and rewrites the markdown with local paths:

```bash
python3 <skill_dir>/scripts/extract_images.py <markdown_file>
```

Before: `[image1]: <data:image/png;base64,iVBOR...>` (huge base64 blob)
After: `[image1]: images/image1.png` (clean local reference)

If images are found, the backup script also exports a `.docx` copy as a backup.

### Uploaded .docx files (Phase 2)

Pandoc extracts embedded images to `images/media/` and references them in the markdown output automatically.

### Phase 3 — Verify backup (`verify_backup.sh`)

Checks the backup is complete and consistent:

```bash
bash <skill_dir>/scripts/verify_backup.sh <directory>
```

Verifies:
- Every `.docx` has a corresponding `.md`
- Every standalone `.xlsx` has a CSV subdirectory
- No zero-byte files (warns if found — may be empty sheets, not errors)
- Reports file counts by type and total size

**Run Phase 3 after Phase 2** to confirm nothing was missed.

### Phase 4 — Build knowledge base (optional)

Creates a filtered, AI-optimised copy containing only token-efficient formats (.md, .csv, .pdf, referenced .png) with YAML frontmatter on every .md and a master `index.json`.

```bash
python3 <skill_dir>/scripts/populate_kb.py <backup_dir> <kb_dir> \
  --mapping <kb_dir>/category_mapping.json \
  --skip <kb_dir>/skip_patterns.json \
  --metadata <backup_dir>/drive_metadata.json
```

**Required flags:**
- `<backup_dir>` — the directory from Phases 1-2 (contains `my_drive/`, `shared_drives/`)
- `<kb_dir>` — output directory for the knowledge base
- `--metadata` — path to `drive_metadata.json` from Phase 0 (provides google_doc_id, author, timestamps)

**Config files you create (project-specific):**

`category_mapping.json` — maps Drive folder patterns to KB topic directories:
```json
[
  {"pattern": "Folder_Name/Subfolder/", "category": "topic-name"},
  {"pattern": ".*Architecture.*", "category": "architecture"},
  {"pattern": ".*Meeting_Minutes/", "category": "operations"}
]
```
Each rule is a regex tested against the file's relative path. First match wins. Files with no match are skipped.

`skip_patterns.json` (optional) — regex patterns for files to exclude:
```json
["Copyrighted_Book_Title", "draft_.*_backup"]
```

**Output:** The KB directory is structured by topic rather than mirroring Drive layout. Each .md file gets YAML frontmatter with:
- `title`, `google_doc_id`, `google_doc_url` (from Drive metadata)
- `last_modified`, `last_modified_by` (from Drive metadata)
- `category`, `tags`, `doc_type` (derived from repo path and filename)
- `word_count`, `has_images` (computed locally)

### Phase 5 — Generate index and sync (`sync_kb.sh`)

Orchestrates all phases end-to-end and creates a GitHub PR:

```bash
bash <skill_dir>/scripts/sync_kb.sh <backup_dir> <kb_dir>
```

Defaults to `~/gws_backup` and `~/gws_backup/kb` if no args provided. Automatically picks up `category_mapping.json` and `skip_patterns.json` from the KB directory if present.

Add `--include-personal` to include personal Drive files (shared drives only by default).

Generates `index.json` via `build_index.py` for programmatic catalogue access.

## Manual export commands

### List files

```bash
# Personal
gws drive files list --params '{"q": "'\''me'\'' in owners and trashed = false", "pageSize": 100, "fields": "files(id,name,mimeType,parents)"}'

# Shared drives
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
gws drive files export --params '{"fileId": "ID", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}'
mv download.xml "sheet.xlsx"

gws sheets spreadsheets get --params '{"spreadsheetId": "ID"}' | jq -r '.sheets[].properties.title'

gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "TAB"}' | jq -r '.values[] | @csv' > "tab.csv"
```

### Google Slides → PPTX

```bash
gws drive files export --params '{"fileId": "ID", "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}'
mv download.xml "slides.pptx"
```

### Binary files

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
