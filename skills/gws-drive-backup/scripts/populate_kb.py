#!/usr/bin/env python3
"""Populate a knowledge base from a gws CLI backup with AI-readable files only.

Copies .md, .csv, .pdf, .txt (→.md), and referenced .png files.
Injects YAML frontmatter into .md files using Drive metadata.
Reorganises into topic-based directory structure.

Usage: python3 populate_kb.py <backup_dir> <kb_dir> [--metadata <file>] [--mapping <file>]

The --mapping flag accepts a JSON file with category path rules. If not provided,
the script uses a built-in default mapping. To create a mapping file for your
own project, export the PATH_RULES list to JSON:
  [{"pattern": "regex_pattern", "category": "target/category"}, ...]
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Parse arguments or use defaults
if len(sys.argv) >= 3:
    SRC = Path(sys.argv[1]).resolve()
    DST = Path(sys.argv[2]).resolve()
else:
    print("Usage: python3 populate_kb.py <backup_dir> <kb_dir> [--metadata <file>]")
    sys.exit(1)

# Find metadata file
META_FILE = SRC / "drive_metadata.json"
if "--metadata" in sys.argv:
    idx = sys.argv.index("--metadata")
    META_FILE = Path(sys.argv[idx + 1]).resolve()

# Find mapping file (optional — external JSON overrides built-in PATH_RULES)
MAPPING_FILE = None
if "--mapping" in sys.argv:
    idx = sys.argv.index("--mapping")
    MAPPING_FILE = Path(sys.argv[idx + 1]).resolve()

# Load Drive metadata
with open(META_FILE) as f:
    drive_meta = json.load(f)["files"]

# Build name → metadata lookup (fuzzy: strip extensions, normalise)
def normalise(name):
    return re.sub(r'[^a-z0-9]', '', name.lower().split('.')[0])

meta_lookup = {}
for m in drive_meta:
    key = normalise(m["name"])
    meta_lookup[key] = m

def find_meta(filename):
    """Find Drive metadata for a local filename."""
    key = normalise(filename)
    if key in meta_lookup:
        return meta_lookup[key]
    # Try partial match
    for k, v in meta_lookup.items():
        if key[:20] in k or k[:20] in key:
            return v
    return None

def sanitise(name):
    """Sanitise a filename."""
    name = re.sub(r'^\(Make_a_Copy\)_', '', name)
    name = re.sub(r'^\(Make a Copy\) ', '', name)
    name = re.sub(r'[/:*?"<>|]', '_', name)
    name = name.replace(' ', '_')
    name = name.replace('—', '-')
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name

# Path mapping rules: source path pattern → destination category
# NOTE: These rules are project-specific defaults. For a different project,
# pass --mapping <file.json> with your own rules as:
# [{"pattern": "regex", "category": "target/path"}, ...]
#
# Load external mapping if provided
if MAPPING_FILE and MAPPING_FILE.exists():
    with open(MAPPING_FILE) as f:
        _rules = json.load(f)
    PATH_RULES = [(r["pattern"], r["category"]) for r in _rules]
    print(f"Loaded {len(PATH_RULES)} mapping rules from {MAPPING_FILE}")
else:
    # No mapping provided — all files go to a flat 'documents' category
    print("WARNING: No --mapping file provided. All files will be categorised as 'documents'.")
    print("  Create a mapping file: [{\"pattern\": \"regex\", \"category\": \"target/path\"}, ...]")
    PATH_RULES = [(r'.*', 'documents')]

def get_category(rel_path):
    """Determine the KB category from a source relative path."""
    path_str = str(rel_path)
    for pattern, cat in PATH_RULES:
        if re.search(pattern, path_str):
            return cat
    return None  # Skip if no match

# File inclusion rules
INCLUDE_EXT = {'.md', '.csv', '.pdf', '.txt'}
SKIP_NAMES = {'.DS_Store'}
# Load skip patterns from --skip flag (JSON array of regex patterns to exclude)
SKIP_PATTERNS = []
if "--skip" in sys.argv:
    _idx = sys.argv.index("--skip")
    with open(sys.argv[_idx + 1]) as _f:
        SKIP_PATTERNS = json.load(_f)
    print(f"Loaded {len(SKIP_PATTERNS)} skip patterns")

def should_include(path, name):
    """Check if a file should be included."""
    ext = Path(name).suffix.lower()
    if name in SKIP_NAMES:
        return False
    for pat in SKIP_PATTERNS:
        if re.search(pat, name):
            return False
    if ext in INCLUDE_EXT:
        return True
    if ext == '.png':
        return False  # Handle separately via image references
    return False

def get_sensitivity(category, filename):
    """Auto-assign sensitivity from path/category."""
    if category and category.startswith('contacts'):
        return 'confidential'
    if category and category.startswith('legal'):
        return 'confidential'
    if 'transcript' in filename.lower():
        return 'confidential'
    if 'website' in filename.lower() and category and 'comms' in category:
        return 'public'
    return 'internal'

def get_doc_type(category, filename):
    """Infer document type."""
    if category and 'template' in category:
        return 'template'
    if 'transcript' in filename.lower():
        return 'transcript'
    if 'summary' in filename.lower() or 'analysis' in filename.lower():
        return 'analysis'
    if category and 'architecture' in category:
        return 'specification'
    if category and 'legal' in category:
        return 'legal'
    if category and 'external' in category:
        return 'external'
    if category and 'strategy' in category:
        return 'analysis'
    if category and 'ontolog' in category:
        return 'data'
    return 'document'

def get_source_drive(rel_path):
    """Derive source drive name from the top-level directory under shared_drives/ or my_drive/."""
    parts = Path(rel_path).parts
    if parts[0] == 'my_drive':
        return 'personal'
    if parts[0] == 'shared_drives' and len(parts) >= 2:
        # Derive a short label from the shared drive directory name:
        # e.g. "OrgName_-_Product" -> "product", "Acme_GTM" -> "acme-gtm"
        raw = parts[1]
        # Strip common org-name prefixes separated by " - " or "_-_"
        raw = re.sub(r'^.*?[_\s]*-[_\s]+', '', raw)
        return raw.lower().replace('_', '-').strip('-')
    # Fallback: use the first path component as-is
    return parts[0].lower().replace('_', '-')

def get_tags(filename, category):
    """Generate cross-cutting tags from filename and category using universal patterns."""
    tags = set()
    fn = filename.lower()
    cat = (category or '').lower()

    # Research methodology
    if 'interview' in fn: tags.add('interview')
    if 'transcript' in fn: tags.add('transcript')
    if 'summary' in fn: tags.add('summary')
    if 'analysis' in fn: tags.add('analysis')

    # Content structure
    if 'briefing' in fn or 'brief' in fn: tags.add('briefing')
    if 'specification' in fn or 'spec' in fn: tags.add('specification')
    if 'canvas' in fn: tags.add('canvas')
    if 'report' in fn: tags.add('report')
    if any(x in fn for x in ['template', 'make_a_copy']): tags.add('template')

    # Status
    if 'draft' in fn: tags.add('draft')

    return sorted(tags) if tags else ['general']

def inject_frontmatter(filepath, meta, category, source_drive):
    """Read an .md file, prepend YAML frontmatter."""
    with open(filepath, 'r', errors='replace') as f:
        content = f.read()

    # Skip if already has frontmatter
    if content.startswith('---\n'):
        return

    # Extract title: prefer H1 heading, fall back to filename
    filename_title = Path(filepath).stem.replace('_', ' ')
    title = filename_title
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('---'):
            continue
        if line.startswith('# '):
            candidate = line[2:].strip().strip('*')
            if len(candidate) > 3 and len(candidate) <= 100:
                title = candidate
            break
        # Skip template instructions, markdown artefacts, tables
        if line.startswith('*[') or line.startswith('|') or line.startswith('>'):
            break
        if line.startswith('**'):
            candidate = line.strip('*').strip().rstrip('♡').strip().rstrip('|').strip()
            if len(candidate) > 3 and len(candidate) <= 80:
                title = candidate
            break
        # Generic first line — only use if it looks like a real title
        if len(line) <= 100 and not line.startswith('[') and not line.startswith('!'):
            title = line
        break

    word_count = len(content.split())
    has_images = bool(re.search(r'!\[', content))
    filename = os.path.basename(filepath)
    sensitivity = get_sensitivity(category, filename)
    doc_type = get_doc_type(category, filename)
    tags = get_tags(filename, category)

    # Drive metadata
    doc_id = meta.get('id', '') if meta else ''
    doc_url = meta.get('webViewLink', '') if meta else ''
    modified = meta.get('modifiedTime', '') if meta else ''
    modified_by = ''
    if meta and meta.get('lastModifyingUser'):
        lmu = meta['lastModifyingUser']
        modified_by = lmu.get('displayName', '') if isinstance(lmu, dict) else str(lmu)

    fm = f"""---
title: "{title.replace(chr(92), '').replace('"', "'")}"
source_drive: {source_drive}
google_doc_id: "{doc_id}"
google_doc_url: "{doc_url}"
last_modified: "{modified}"
last_modified_by: "{modified_by}"
category: {category or 'uncategorised'}
tags: [{', '.join(tags)}]
doc_type: {doc_type}
word_count: {word_count}
has_images: {str(has_images).lower()}
sensitivity: {sensitivity}
---

"""
    with open(filepath, 'w') as f:
        f.write(fm + content)

# Track referenced images
referenced_images = set()

def find_referenced_images(src_dir):
    """Scan all .md files for image references and collect paths."""
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.md'):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', errors='replace') as fh:
                        content = fh.read()
                    # Find image references: ![...](images/...) or [imageN]: images/...
                    for match in re.finditer(r'(?:!\[.*?\]\(|^\[image\d+\]: )(images/[^\s)]+)', content, re.MULTILINE):
                        img_rel = match.group(1)
                        img_abs = os.path.normpath(os.path.join(root, img_rel))
                        if os.path.exists(img_abs):
                            referenced_images.add(img_abs)
                except:
                    pass

# Main
print("=== Scanning for referenced images ===")
for d in SRC.iterdir():
    if d.is_dir() and d != DST and not d.name.startswith('.'):
        find_referenced_images(d)
print(f"Found {len(referenced_images)} referenced images")

print(f"\n=== Populating KB at {DST.name}/ ===")
DST.mkdir(parents=True, exist_ok=True)

copied = 0
skipped = 0
errors = []

# Scan all top-level subdirectories in the backup (e.g. my_drive/, shared_drives/)
src_bases = [d for d in SRC.iterdir() if d.is_dir() and d != DST and not d.name.startswith('.')]
for src_base in src_bases:
    for root, dirs, files in os.walk(src_base):
        # Skip the KB output directory
        if str(DST) in root:
            continue
        for fname in sorted(files):
            src_path = Path(root) / fname
            rel_path = src_path.relative_to(SRC)
            ext = src_path.suffix.lower()

            # Handle .png separately
            if ext == '.png':
                if str(src_path) in referenced_images:
                    # Find which .md references it and copy to same relative location
                    category = get_category(rel_path)
                    if category:
                        # Preserve images/ subpath
                        parts = str(rel_path).split('images/')
                        if len(parts) > 1:
                            dst_path = DST / category / "images" / sanitise(parts[-1])
                        else:
                            dst_path = DST / category / "images" / sanitise(fname)
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        copied += 1
                else:
                    skipped += 1
                continue

            if not should_include(str(rel_path), fname):
                if ext not in {'.docx', '.xlsx', '.pptx', '.zip', '.tsv'}:
                    pass  # Don't log expected skips
                skipped += 1
                continue

            category = get_category(rel_path)
            if not category:
                skipped += 1
                continue

            # Sanitise filename
            safe_name = sanitise(fname)
            if ext == '.txt':
                safe_name = safe_name.rsplit('.', 1)[0] + '.md'

            # Build destination path
            dst_path = DST / category / safe_name
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # On re-sync, overwrite existing files with fresh copy from Drive

            shutil.copy2(src_path, dst_path)
            source_drive = get_source_drive(rel_path)

            # Inject frontmatter for .md files (and converted .txt)
            if dst_path.suffix == '.md':
                meta = find_meta(fname)
                inject_frontmatter(str(dst_path), meta, category, source_drive)

            copied += 1

print(f"\n=== Complete ===")
print(f"Copied: {copied}")
print(f"Skipped: {skipped}")

# Count by type
from collections import Counter
types = Counter()
for root, _, files in os.walk(DST):
    for f in files:
        ext = Path(f).suffix.lower()
        types[ext] += 1

print(f"\nBy type:")
for ext, count in types.most_common():
    print(f"  {ext}: {count}")

total_size = sum(f.stat().st_size for f in DST.rglob('*') if f.is_file())
print(f"\nTotal: {sum(types.values())} files, {total_size / 1048576:.1f} MB")
