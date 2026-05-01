#!/usr/bin/env python3
"""Build index.json from YAML frontmatter in all .md files and catalogue CSVs/PDFs.

Usage: python3 build_index.py [kb_root]
       Defaults to current directory if kb_root not specified.

Outputs index.json at the KB root with category summaries and per-document records.
Requires: pyyaml (pip3 install pyyaml)
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install with: pip3 install pyyaml")
    sys.exit(1)

KB_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
KB_ROOT = KB_ROOT.resolve()

SKIP_DIRS = {".git", ".claude", "scripts", "__pycache__", "node_modules"}
SKIP_FILES = {"CLAUDE.md", "README.md", "CONTRIBUTING.md", "index.json", ".gitignore", ".gitattributes", ".DS_Store"}

docs = []
categories = {}

for root, dirs, files in os.walk(KB_ROOT):
    # Skip hidden and infrastructure dirs
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

    for fname in sorted(files):
        if fname in SKIP_FILES or fname.startswith("."):
            continue

        fpath = Path(root) / fname
        rel = str(fpath.relative_to(KB_ROOT))
        ext = fpath.suffix.lower()

        if ext not in {".md", ".csv", ".pdf", ".png"}:
            continue

        entry = {
            "path": rel,
            "filename": fname,
            "file_type": ext.lstrip("."),
            "file_size_bytes": fpath.stat().st_size,
        }

        if ext == ".md":
            try:
                with open(fpath, "r", errors="replace") as fh:
                    content = fh.read()
                if content.startswith("---\n"):
                    end = content.find("\n---\n", 4)
                    if end > 0:
                        fm = yaml.safe_load(content[4:end])
                        if isinstance(fm, dict):
                            fm.pop("sensitivity", None)
                            entry.update(fm)
                            if not fm.get('google_doc_id'):
                                print(f"  WARN: Empty provenance in {rel}")
            except Exception as e:
                print(f"  WARN: Failed to parse frontmatter in {rel}: {e}")

        # Derive category from path
        parts = rel.split("/")
        cat = parts[0] if parts else "uncategorised"
        if cat not in entry:
            entry.setdefault("category", cat)

        # Track categories
        if cat not in categories:
            categories[cat] = {"count": 0, "description": ""}
        categories[cat]["count"] += 1

        docs.append(entry)

# Auto-generate category descriptions from directory names
for cat in categories:
    categories[cat]["description"] = cat.replace("-", " ").replace("/", " — ").title()

# Build index
index = {
    "version": "1.1.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total_documents": len(docs),
    "categories": {k: v for k, v in sorted(categories.items())},
    "documents": sorted(docs, key=lambda d: d["path"]),
}

out_path = KB_ROOT / "index.json"
with open(out_path, "w") as f:
    json.dump(index, f, indent=2, default=str)

print(f"index.json: {len(docs)} documents across {len(categories)} categories")
for cat, info in sorted(categories.items()):
    print(f"  {cat}: {info['count']}")
print(f"\nWritten to: {out_path}")
