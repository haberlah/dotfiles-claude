#!/usr/bin/env python3
"""Populate a knowledge base from a gws CLI backup with AI-readable files only.

Copies .md, .csv, .pdf, .txt (→.md), and referenced .png files.
Injects YAML frontmatter into .md files using Drive metadata.
Reorganises into topic-based directory structure.

Usage: python3 populate_kb.py <backup_dir> <kb_dir> [--metadata <file>] [--mapping <file>]
       python3 populate_kb.py (uses defaults if no args)

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
SKIP_NAMES = {
    'blog_draft_gws_drive_backup.md',
    '00_file_manifest.md',
    '.DS_Store',
}
SKIP_PATTERNS = [
    r'Testing_Business_Ideas',
    r'Value_Proposition_Design.*How_to_Create',
]

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
    """Determine source drive."""
    p = str(rel_path)
    if p.startswith('my_drive'):
        return 'personal'
    if 'GTM' in p or 'Marketing' in p or 'Comms' in p:
        return 'gtm'
    return 'product'

def get_tags(filename, category):
    """Generate cross-cutting research tags from filename and category."""
    tags = set()
    fn = filename.lower()
    cat = (category or '').lower()

    # Research methodology
    if 'empathy' in fn: tags.add('empathy-map')
    if 'persona' in fn or 'comparison' in fn: tags.add('persona')
    if 'transcript' in fn: tags.add('transcript')
    if 'summary' in fn or 'executive_summary' in fn: tags.add('summary')
    if 'interview' in fn: tags.add('interview')
    if 'golden_metrics' in fn or 'quote' in fn: tags.add('quotes')
    if 'kano' in fn: tags.add('kano-analysis')
    if 'think_aloud' in fn or 'think-aloud' in fn: tags.add('think-aloud')
    if 'day_in_the_life' in fn or 'ditl' in fn: tags.add('day-in-life')
    if 'feature_validation' in fn or 'stage_2' in fn or 'stage2' in fn: tags.add('feature-validation')
    if 'pain' in fn or 'frequency' in fn: tags.add('pain-analysis')

    # Content type
    if 'canvas' in fn or 'lean_canvas' in fn: tags.add('canvas')
    if 'briefing' in fn or 'brief' in fn: tags.add('briefing')
    if any(x in fn for x in ['template', 'make_a_copy', 'protocol']): tags.add('template')
    if 'analysis' in fn or 'interim' in fn: tags.add('analysis')
    if 'prd' in fn or 'specification' in fn: tags.add('specification')
    if 'pipeline' in fn or 'redaction' in fn: tags.add('redaction')

    # Domain
    if 'ndis' in fn or 'ndis' in cat: tags.add('ndis')
    if 'mvp' in fn: tags.add('mvp')
    if 'iso' in fn or 'iso_27001' in cat: tags.add('compliance')
    if 'ontology' in fn or 'ontolog' in cat: tags.add('ontology')
    if 'consent' in fn or 'nda' in fn: tags.add('legal')
    if 'contact' in fn or 'tracker' in fn: tags.add('contacts')

    # Stakeholder facing
    if 'investor' in cat: tags.add('investor-facing')
    if 'website' in fn or 'faq' in fn or 'objection' in fn: tags.add('external-facing')
    if 'testing_guide' in fn or 'test_doc' in cat: tags.add('synthetic-data')

    # Participant vs SC (support coordinator)
    if 'participants/' in cat and 'participant' not in fn:
        tags.add('support-coordinator')
    elif 'participant' in fn.lower():
        tags.add('participant')

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
find_referenced_images(SRC / "my_drive")
find_referenced_images(SRC / "shared_drives")
print(f"Found {len(referenced_images)} referenced images")

print("\n=== Populating bella_kb/ ===")
DST.mkdir(parents=True, exist_ok=True)

copied = 0
skipped = 0
errors = []

for src_base in [SRC / "my_drive", SRC / "shared_drives"]:
    for root, dirs, files in os.walk(src_base):
        # Skip bella_kb itself
        if 'bella_kb' in root:
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
                # Try to assign based on broader patterns
                if 'Co-Design' in str(rel_path):
                    category = 'co-design'
                elif 'GTM' in str(rel_path):
                    category = 'strategy'
                elif 'Product' in str(rel_path):
                    category = 'operations'
                else:
                    print(f"  SKIP (no category): {rel_path}")
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
