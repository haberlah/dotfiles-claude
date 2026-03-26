#!/bin/bash
# gws_backup.sh — Download and convert Google Drive files via gws CLI
# Usage: bash gws_backup.sh <output_dir> [--scope personal|shared|all] [--drive-id <id>]
#
# Conversion rules:
#   Google Docs  → .md (+ .docx if doc contains images)
#   Google Sheets → subdirectory with .csv per tab + .xlsx
#   Google Slides → .pptx
#   Other files   → downloaded as-is
#
# Requires: gws CLI authenticated, jq

set -euo pipefail

OUTPUT_DIR="${1:?Usage: gws_backup.sh <output_dir> [--scope personal|shared|all] [--drive-id <id>]}"
SCOPE="personal"
DRIVE_ID=""

shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    --drive-id) DRIVE_ID="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

# Build query based on scope
case "$SCOPE" in
  personal)
    QUERY="'me' in owners and trashed = false"
    EXTRA_PARAMS=""
    ;;
  shared)
    if [ -z "$DRIVE_ID" ]; then
      echo "Error: --drive-id required for shared scope"; exit 1
    fi
    QUERY="'${DRIVE_ID}' in parents and trashed = false"
    EXTRA_PARAMS=', "includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives"'
    ;;
  all)
    QUERY="trashed = false"
    EXTRA_PARAMS=', "includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives"'
    ;;
  *) echo "Invalid scope: $SCOPE"; exit 1 ;;
esac

echo "=== GWS Drive Backup ==="
echo "Output: $OUTPUT_DIR"
echo "Scope:  $SCOPE"
[ -n "$DRIVE_ID" ] && echo "Drive:  $DRIVE_ID"
echo ""

# List all files
FILES_JSON=$(gws drive files list --params "{\"q\": \"${QUERY}\", \"pageSize\": 1000, \"fields\": \"files(id,name,mimeType,parents)\"${EXTRA_PARAMS}}" 2>/dev/null)
TOTAL=$(echo "$FILES_JSON" | jq '.files | length')
echo "Found $TOTAL files"
echo ""

# Sanitise a filename for local filesystem
sanitise() {
  echo "$1" | sed 's/[/:*?"<>|]/_/g; s/ /_/g; s/—/-/g'
}

# Process each file
echo "$FILES_JSON" | jq -c '.files[]' | while IFS= read -r file; do
  ID=$(echo "$file" | jq -r '.id')
  NAME=$(echo "$file" | jq -r '.name')
  MIME=$(echo "$file" | jq -r '.mimeType')
  SAFE_NAME=$(sanitise "$NAME")

  case "$MIME" in

    # ── Google Docs → Markdown (+ docx if images present) ──
    application/vnd.google-apps.document)
      echo "DOC: $NAME"

      # Export as markdown
      cd "$OUTPUT_DIR"
      gws drive files export --params "{\"fileId\": \"$ID\", \"mimeType\": \"text/markdown\"}" >/dev/null 2>&1
      [ -f download.bin ] && mv download.bin "${SAFE_NAME}.md"
      echo "  → ${SAFE_NAME}.md"

      # Check for inline images via Docs API
      IMG_COUNT=$(gws docs documents get --params "{\"documentId\": \"$ID\"}" 2>/dev/null \
        | jq '.inlineObjects | length // 0' 2>/dev/null || echo 0)

      if [ "$IMG_COUNT" -gt 0 ]; then
        echo "  ⚠ $IMG_COUNT image(s) detected — also exporting as .docx (images are embedded)"
        gws drive files export --params "{\"fileId\": \"$ID\", \"mimeType\": \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\"}" >/dev/null 2>&1
        local_file=$(ls -t download.* 2>/dev/null | head -1)
        [ -n "$local_file" ] && mv "$local_file" "${SAFE_NAME}.docx"
        echo "  → ${SAFE_NAME}.docx"
      fi
      ;;

    # ── Google Sheets → CSV per tab + XLSX ──
    application/vnd.google-apps.spreadsheet)
      echo "SHEET: $NAME"
      SHEET_DIR="$OUTPUT_DIR/${SAFE_NAME}"
      mkdir -p "$SHEET_DIR"

      # Full workbook as xlsx
      cd "$OUTPUT_DIR"
      gws drive files export --params "{\"fileId\": \"$ID\", \"mimeType\": \"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\"}" >/dev/null 2>&1
      local_file=$(ls -t download.* 2>/dev/null | head -1)
      [ -n "$local_file" ] && mv "$local_file" "${SHEET_DIR}/${SAFE_NAME}.xlsx"
      echo "  → ${SAFE_NAME}/${SAFE_NAME}.xlsx"

      # Each tab as CSV
      TABS=$(gws sheets spreadsheets get --params "{\"spreadsheetId\": \"$ID\"}" 2>/dev/null \
        | jq -r '.sheets[].properties.title' 2>/dev/null || true)
      if [ -n "$TABS" ]; then
        echo "$TABS" | while IFS= read -r tab; do
          SAFE_TAB=$(sanitise "$tab")
          gws sheets spreadsheets values get --params "{\"spreadsheetId\": \"$ID\", \"range\": \"${tab}\"}" 2>/dev/null \
            | jq -r '.values[] | @csv' > "${SHEET_DIR}/${SAFE_TAB}.csv" 2>/dev/null
          echo "  → ${SAFE_NAME}/${SAFE_TAB}.csv"
        done
      fi
      ;;

    # ── Google Slides → PPTX ──
    application/vnd.google-apps.presentation)
      echo "SLIDES: $NAME"
      cd "$OUTPUT_DIR"
      gws drive files export --params "{\"fileId\": \"$ID\", \"mimeType\": \"application/vnd.openxmlformats-officedocument.presentationml.presentation\"}" >/dev/null 2>&1
      local_file=$(ls -t download.* 2>/dev/null | head -1)
      [ -n "$local_file" ] && mv "$local_file" "${SAFE_NAME}.pptx"
      echo "  → ${SAFE_NAME}.pptx"
      ;;

    # ── Skip non-exportable types ──
    application/vnd.google-apps.folder)
      echo "FOLDER: $NAME (skipped)"
      ;;
    application/vnd.google-apps.form)
      echo "FORM: $NAME (skipped — not exportable)"
      ;;

    # ── All other files → download as-is ──
    *)
      echo "FILE: $NAME"
      cd "$OUTPUT_DIR"
      gws drive files get --params "{\"fileId\": \"$ID\", \"alt\": \"media\"}" >/dev/null 2>&1
      local_file=$(ls -t download.* 2>/dev/null | head -1)
      if [ -n "$local_file" ]; then
        if echo "$NAME" | grep -q '\.'; then
          mv "$local_file" "${SAFE_NAME}"
        else
          EXT="${local_file##*.}"
          mv "$local_file" "${SAFE_NAME}.${EXT}"
        fi
        echo "  → ${SAFE_NAME}"
      fi
      ;;
  esac
done

echo ""
echo "=== Backup complete ==="
echo "Output: $OUTPUT_DIR"
ITEM_COUNT=$(find "$OUTPUT_DIR" -type f -not -name '.DS_Store' | wc -l | tr -d ' ')
echo "Total files: $ITEM_COUNT"
