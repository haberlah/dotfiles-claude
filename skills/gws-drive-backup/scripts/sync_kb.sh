#!/bin/bash
# sync_kb.sh — End-to-end sync: Google Drive → local backup → knowledge base → GitHub PR
#
# Usage: bash sync_kb.sh <backup_dir> <kb_dir> [--full] [--include-personal] [--allow-dirty]
#        bash sync_kb.sh (uses defaults)
#
# Defaults:
#   backup_dir: ~/gws_backup  (or specify your own)
#   kb_dir:     ~/gws_backup/kb  (or specify your own)
#
# Phases:
#   0. Export Drive metadata
#   1. Download changed files from Drive (incremental by default, --full for all)
#   2. Convert local files (.docx→.md, .xlsx→.csv)
#   3. Populate KB (filter, categorise, frontmatter)
#   4. Regenerate index.json
#   5. Create sync PR on GitHub
#
# Requires: gws CLI authenticated, jq, pandoc, openpyxl, pyyaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$HOME/gws_backup"
KB_DIR=""
FULL_SYNC=false
SHARED_ONLY=true
ALLOW_DIRTY=false
POSITIONAL=()

for arg in "$@"; do
  case "$arg" in
    --full) FULL_SYNC=true ;;
    --include-personal) SHARED_ONLY=false ;;
    --allow-dirty) ALLOW_DIRTY=true ;;
    *) POSITIONAL+=("$arg") ;;
  esac
done

[ "${#POSITIONAL[@]}" -ge 1 ] && BACKUP_DIR="${POSITIONAL[0]}"
[ "${#POSITIONAL[@]}" -ge 2 ] && KB_DIR="${POSITIONAL[1]}"
[ -z "$KB_DIR" ] && KB_DIR="$BACKUP_DIR/kb"

mkdir -p "$BACKUP_DIR" "$KB_DIR"

if [ -d "$KB_DIR/.git" ] && [ "$ALLOW_DIRTY" = false ]; then
  if [ -n "$(git -C "$KB_DIR" status --porcelain)" ]; then
    echo "ERROR: KB repo has existing uncommitted changes."
    echo "Review, commit, or stash them first, then rerun."
    echo "Use --allow-dirty only when you intentionally want this sync to include the whole worktree."
    git -C "$KB_DIR" status --short
    exit 1
  fi
fi

echo "=== KB Sync ==="
echo "Backup: $BACKUP_DIR"
echo "KB:     $KB_DIR"
echo "Mode:   $([ "$FULL_SYNC" = true ] && echo 'full' || echo 'incremental')"
echo "Scope:  $([ "$SHARED_ONLY" = true ] && echo 'shared drives only' || echo 'shared + personal')"
echo ""

# --- Phase 0: Export Drive metadata ---
echo "--- Phase 0: Export Drive metadata ---"
gws drive files list --params '{"q": "trashed = false", "includeItemsFromAllDrives": true, "supportsAllDrives": true, "corpora": "allDrives", "pageSize": 500, "fields": "files(id,name,mimeType,modifiedTime,createdTime,lastModifyingUser,webViewLink,parents,size),nextPageToken"}' \
  --page-all --page-limit 50 --page-delay 200 2>/dev/null \
  | jq -s '{files: [.[].files[]]}' > "$BACKUP_DIR/drive_metadata.json"
META_COUNT=$(jq '.files | length' "$BACKUP_DIR/drive_metadata.json")
echo "Exported metadata for $META_COUNT files (paginated)"
echo ""

# --- Phase 1: Download from Drive ---
echo "--- Phase 1: Download from Drive ---"

# Detect shared drives
DRIVES=$(gws drive drives list --params '{"pageSize": 50}' 2>/dev/null | jq -r '.drives[] | "\(.id)\t\(.name)"' 2>/dev/null || true)

# Personal drive (only if --include-personal flag is set)
if [ "$SHARED_ONLY" = false ]; then
  echo "Including personal drive..."
  bash "$SCRIPT_DIR/gws_backup.sh" "$BACKUP_DIR/my_drive" </dev/null 2>/dev/null || true
else
  echo "Skipping personal drive (shared drives only by default)"
  echo "  Use --include-personal to include personal Drive files"
fi

# Shared drives (always included — all members have access)
echo "$DRIVES" | while IFS=$'\t' read -r drive_id drive_name; do
  [ -z "$drive_id" ] && continue
  safe_name=$(echo "$drive_name" | sed 's/[/:*?"<>|]/_/g; s/ /_/g')
  echo "Shared drive: $drive_name"
  bash "$SCRIPT_DIR/gws_backup.sh" "$BACKUP_DIR/shared_drives/$safe_name" --scope shared --drive-id "$drive_id" </dev/null 2>/dev/null || true
done
echo ""

# --- Phase 2: Convert local files ---
echo "--- Phase 2: Convert local files ---"
python3 "$SCRIPT_DIR/convert_local.py" "$BACKUP_DIR/shared_drives" 2>/dev/null || true
python3 "$SCRIPT_DIR/convert_local.py" "$BACKUP_DIR/my_drive" 2>/dev/null || true
echo ""

# --- Phase 3: Populate KB ---
echo "--- Phase 3: Populate KB ---"
POPULATE_ARGS=("$BACKUP_DIR" "$KB_DIR")
[ -f "$KB_DIR/category_mapping.json" ] && POPULATE_ARGS+=(--mapping "$KB_DIR/category_mapping.json")
[ -f "$KB_DIR/skip_patterns.json" ] && POPULATE_ARGS+=(--skip "$KB_DIR/skip_patterns.json")
POPULATE_ARGS+=(--metadata "$BACKUP_DIR/drive_metadata.json")
python3 "$SCRIPT_DIR/populate_kb.py" "${POPULATE_ARGS[@]}"
echo ""

# --- Phase 4: Regenerate index ---
echo "--- Phase 4: Regenerate index ---"
cd "$KB_DIR"
python3 "$SCRIPT_DIR/build_index.py" . 2>/dev/null || echo "WARN: build_index.py not found or failed"
echo ""

# --- Phase 5: Create sync PR ---
echo "--- Phase 5: Create sync PR ---"
cd "$KB_DIR"

# Check if there are actual changes
if git diff --quiet HEAD 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "No changes detected. KB is up to date."
  exit 0
fi

BASE_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=$(git branch --show-current)
BRANCH="sync/$(date +%Y-%m-%d)"
CHANGES_ADDED=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')
CHANGES_MODIFIED=$(git diff --name-only | wc -l | tr -d ' ')
CHANGES_DELETED=$(git diff --name-only --diff-filter=D | wc -l | tr -d ' ')

echo "Changes: $CHANGES_ADDED added, $CHANGES_MODIFIED modified, $CHANGES_DELETED deleted"

if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  BRANCH="$BRANCH-$(date +%H%M%S)"
fi
git switch -c "$BRANCH"
git add --all .

git commit -m "$(cat <<EOF
sync: update KB from Drive $(date +%Y-%m-%d)

Added: $CHANGES_ADDED files
Modified: $CHANGES_MODIFIED files
Deleted: $CHANGES_DELETED files
EOF
)"

git push -u origin "$BRANCH" 2>/dev/null

# Create PR
PR_BODY_FILE=$(mktemp)
cat > "$PR_BODY_FILE" <<EOF
## Drive Sync — $(date +%Y-%m-%d)

**$CHANGES_ADDED** files added, **$CHANGES_MODIFIED** modified, **$CHANGES_DELETED** deleted.

Automated sync from Google Drive via \`sync_kb.sh\`.
EOF

gh pr create --draft --base "$BASE_BRANCH" --head "$BRANCH" \
  --title "Sync: Drive changes $(date +%Y-%m-%d)" \
  --body-file "$PR_BODY_FILE" 2>/dev/null || echo "PR creation failed (may need gh auth)"
rm -f "$PR_BODY_FILE"

echo ""
echo "=== Sync complete ==="
