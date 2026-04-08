#!/bin/bash
# verify_backup.sh — Verify a local Drive backup is complete and consistent.
#
# Checks:
# 1. Every .docx has a corresponding .md
# 2. Every .xlsx has a corresponding CSV subdirectory
# 3. No zero-byte files
# 4. Reports file counts by type
#
# Usage: bash verify_backup.sh <backup_directory>

set -euo pipefail

DIR="${1:?Usage: verify_backup.sh <backup_directory>}"

echo "=== GWS Backup Verification ==="
echo "Directory: $DIR"
echo ""

ERRORS=0

# Check every .docx has a .md
echo "--- Checking .docx → .md conversions ---"
find "$DIR" -name "*.docx" -type f | while read -r docx; do
  base="${docx%.docx}"
  if [ ! -f "${base}.md" ]; then
    echo "  MISSING MD: $docx"
    ERRORS=$((ERRORS + 1))
  fi
done
DOCX_COUNT=$(find "$DIR" -name "*.docx" -type f | wc -l | tr -d ' ')
MD_COUNT=$(find "$DIR" -name "*.md" -type f | wc -l | tr -d ' ')
echo "  $DOCX_COUNT .docx files, $MD_COUNT .md files"

# Check every standalone .xlsx has CSVs
echo ""
echo "--- Checking .xlsx → .csv conversions ---"
find "$DIR" -name "*.xlsx" -type f | while read -r xlsx; do
  base=$(basename "$xlsx" .xlsx)
  xlsx_dir=$(dirname "$xlsx")
  csv_dir="$xlsx_dir/$base"
  # Skip if xlsx is inside a sheet subdirectory (it's the export itself)
  parent_base=$(basename "$xlsx_dir")
  if [ "$parent_base" = "$base" ]; then
    continue
  fi
  if [ ! -d "$csv_dir" ] || [ -z "$(find "$csv_dir" -name '*.csv' 2>/dev/null)" ]; then
    echo "  MISSING CSVs: $xlsx"
  fi
done
CSV_COUNT=$(find "$DIR" -name "*.csv" -type f | wc -l | tr -d ' ')
XLSX_COUNT=$(find "$DIR" -name "*.xlsx" -type f | wc -l | tr -d ' ')
echo "  $XLSX_COUNT .xlsx files, $CSV_COUNT .csv files"

# Check for zero-byte files
echo ""
echo "--- Checking for zero-byte files ---"
ZERO=$(find "$DIR" -type f -size 0 -not -name '.DS_Store' | wc -l | tr -d ' ')
if [ "$ZERO" -gt 0 ]; then
  echo "  WARNING: $ZERO zero-byte files found:"
  find "$DIR" -type f -size 0 -not -name '.DS_Store' | head -10
else
  echo "  OK: No zero-byte files"
fi

# Summary
echo ""
echo "--- File counts by type ---"
find "$DIR" -type f -not -name '.DS_Store' | sed 's/.*\.//' | sort | uniq -c | sort -rn

echo ""
TOTAL=$(find "$DIR" -type f -not -name '.DS_Store' | wc -l | tr -d ' ')
SIZE=$(du -sh "$DIR" | awk '{print $1}')
FOLDERS=$(find "$DIR" -type d | wc -l | tr -d ' ')
echo "Total: $TOTAL files, $FOLDERS folders, $SIZE"
# Check metadata completeness
echo ""
echo "--- Metadata completeness ---"
META_FILE="$DIR/drive_metadata.json"
if [ -f "$META_FILE" ]; then
  META_COUNT=$(jq '.files | length' "$META_FILE")
  echo "  Metadata entries: $META_COUNT"
else
  echo "  WARNING: No drive_metadata.json found"
fi

# Check file manifests
echo ""
echo "--- File manifests ---"
MANIFEST_COUNT=$(find "$DIR" -name "file_manifest.json" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$MANIFEST_COUNT" -gt 0 ]; then
  MANIFEST_ENTRIES=$(find "$DIR" -name "file_manifest.json" -exec cat {} + | jq -s '[.[][]] | length')
  echo "  Found $MANIFEST_COUNT manifests with $MANIFEST_ENTRIES entries"
else
  echo "  WARNING: No file_manifest.json found — re-run Phase 1 to generate manifests"
fi

echo ""
echo "=== Verification complete ==="
