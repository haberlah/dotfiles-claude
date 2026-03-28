#!/usr/bin/env python3
"""Populate a knowledge base from a gws CLI backup with AI-readable files only.

Copies .md, .csv, .pdf, .txt (→.md), and referenced .png files.
Injects YAML frontmatter into .md files using Drive metadata.
Reorganises into topic-based directory structure.

Usage: python3 populate_kb.py <backup_dir> <kb_dir> [--metadata <drive_metadata.json>]
       python3 populate_kb.py (uses defaults if no args)
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
elif len(sys.argv) == 1:
    # Default paths for BellaAssist (backwards compatible)
    SRC = Path.home() / "Documents" / "bella_assist" / "gws_copy"
    DST = SRC / "bella_kb"
else:
    print("Usage: python3 populate_kb.py <backup_dir> <kb_dir> [--metadata <file>]")
    sys.exit(1)

# Find metadata file
META_FILE = SRC / "drive_metadata.json"
if "--metadata" in sys.argv:
    idx = sys.argv.index("--metadata")
    META_FILE = Path(sys.argv[idx + 1]).resolve()

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
    name = name.replace('Baliey', 'Bailey')
    name = re.sub(r'[/:*?"<>|]', '_', name)
    name = name.replace(' ', '_')
    name = name.replace('—', '-')
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name

# Path mapping rules: source path pattern → destination category
PATH_RULES = [
    # architecture
    (r'my_drive/.*Architecture.*', 'architecture'),
    (r'my_drive/.*Production_Architecture.*', 'architecture'),
    (r'my_drive/.*MVP_Architecture.*', 'architecture'),
    (r'my_drive/.*Replit_PRD.*', 'architecture'),
    (r'my_drive/.*Testing_Guide', 'architecture'),
    (r'my_drive/.*Document_Processing_Gaps', 'architecture'),
    (r'Tool___Tech/David_Notes/.*Pipeline.*', 'architecture'),
    (r'Tool___Tech/David_Notes/.*Redaction.*', 'architecture'),
    # strategy
    (r'my_drive/.*Blue_Ocean.*', 'strategy'),
    (r'my_drive/.*CBIM.*', 'strategy'),
    (r'my_drive/.*Lean_Canvas.*', 'strategy'),
    (r'my_drive/.*market_research.*', 'strategy'),
    (r'my_drive/.*CRCP.*', 'strategy'),
    (r'my_drive/.*Aviato.*', 'strategy'),
    (r'GTM___Strategy/Key_Assumptions.*', 'strategy'),
    (r'GTM___Strategy/\(V2\)_BellaAssist_Project_Plan/.*\.csv', 'strategy/project-plan'),
    (r'GTM___Strategy/BellaAssist.*GTM.*', 'strategy'),
    # co-design
    (r'Co-Design_Program/\(Make_a_Copy\).*', 'co-design/templates'),
    (r'Co-Design_Program/Make_a_Copy.*', 'co-design/templates'),
    (r'Co-Design_Program/Analyses/', 'co-design/analyses'),
    (r'Co-Design_Program/.*Briefing.*', 'co-design/briefings'),
    (r'Co-Design_Program/MVP_Test_Files/Mike_Smith/', 'co-design/mvp-testing/mike_smith'),
    (r'Co-Design_Program/MVP_Test_Files/Sarah_Mitchell/', 'co-design/mvp-testing/sarah_mitchell'),
    (r'Co-Design_Program/MVP_Test_Files/Craig.*', 'co-design/mvp-testing'),
    (r'Co-Design_Program/David_Methodology_Docs/', 'co-design/methodology'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Amanda/', 'co-design/participants/amanda'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Bailey/', 'co-design/participants/bailey'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Casey/', 'co-design/participants/casey'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Craig/', 'co-design/participants/craig'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Dionne/', 'co-design/participants/dionne'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Jane/', 'co-design/participants/jane'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Kim/', 'co-design/participants/kim'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Peter.*Kathy.*Rachel/', 'co-design/participants/peter_kathy_rachel'),
    (r'Co-Design_Program/SC_Co-Design_Docs/Teresa/', 'co-design/participants/teresa'),
    (r'Co-Design_Program/SC_Co-Design_Docs/13_Mar.*', 'co-design/analyses'),
    (r'Co-Design_Program/SC_Co-Design_Docs/\(Mike.*Claude.*', 'co-design/templates'),
    (r'Co-Design_Program/Participant_Docs/.*Tom.*', 'co-design/participants/tom'),
    (r'Co-Design_Program/Participant_Docs/.*Kylie.*', 'co-design/participants/kylie'),
    (r'Co-Design_Program/.*Stage_2.*Feature_Validation\.(md|docx)', 'co-design/participants'),
    (r'Co-Design_Program/.*Stage_1.*Day_In_The_Life\.(md|docx)', 'co-design/participants'),
    (r'Co-Design_Program/.*Feature_Validation\.(md|docx|pptx)', 'co-design/participants'),
    (r'Co-Design_Program/', 'co-design'),
    # comms
    (r'General___Comms/', 'comms'),
    (r'General___Comms/Brand_Guide/', 'comms/brand-guide'),
    # investors
    (r'Investors/', 'investors'),
    # marketing
    (r'Marketing_Comms_Asset_Directory/', 'marketing'),
    # legal
    (r'Participant_Consent_Forms/', 'legal'),
    # ontologies
    (r'my_drive/NDIS_data_ontology', 'ontologies/ndis_v2.1'),
    (r'my_drive/iso_27001', 'ontologies/iso_27001'),
    # test documents
    (r'Test_Documents_for_Redaction/', 'test-documents'),
    # external references
    (r'Helpful_External_Documents/', 'external-references'),
    # operations
    (r'General___Meeting_Minutes/', 'operations'),
    (r'Tool___Tech/Testing_Files/', 'operations/product-testing'),
    (r'Tool___Tech/BellaAssist_Document.*', 'operations'),
    # customer
    (r'Customer/Research_Verbatim', 'customer'),
    (r'Customer/Consultations', 'customer'),
    (r'Customer/SC_Contacts', 'contacts'),
    # contacts (sensitive)
    (r'SC_and_PM_contact_details/', 'contacts'),
]

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
    """Generate tags from filename and category."""
    tags = []
    if category:
        tags.append(category.split('/')[0])
    fn = filename.lower()
    tag_patterns = {
        'ndis': 'ndis', 'mvp': 'mvp', 'architecture': 'architecture',
        'co-design': 'co-design', 'empathy': 'empathy-map',
        'stage1': 'stage1-discovery', 'stage2': 'stage2-validation',
        'ontology': 'ontology', 'iso': 'iso-27001', 'consent': 'consent',
        'testing': 'testing', 'gtm': 'gtm', 'strategy': 'strategy',
    }
    for pat, tag in tag_patterns.items():
        if pat in fn and tag not in tags:
            tags.append(tag)
    return tags

def inject_frontmatter(filepath, meta, category, source_drive):
    """Read an .md file, prepend YAML frontmatter."""
    with open(filepath, 'r', errors='replace') as f:
        content = f.read()

    # Skip if already has frontmatter
    if content.startswith('---\n'):
        return

    # Extract title from first H1 or first non-empty line
    title = Path(filepath).stem.replace('_', ' ')
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip().strip('*')
            break
        elif line.startswith('**') and line.endswith('**'):
            title = line.strip('*').strip()
            break
        elif line and not line.startswith('---'):
            title = line[:100]
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
title: "{title.replace('"', "'")}"
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

            # Avoid overwriting (handle name collisions)
            if dst_path.exists():
                base, extension = os.path.splitext(safe_name)
                dst_path = DST / category / f"{base}_2{extension}"

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
