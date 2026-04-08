#!/usr/bin/env python3
"""Extract base64-encoded images from Google Docs markdown export.

Google's text/markdown export embeds images as reference-style base64 data URIs:
  [image1]: <data:image/png;base64,iVBOR...>

This script extracts each image to a separate file in an images/ subdirectory
and rewrites the markdown to reference local file paths instead:
  [image1]: images/image1.png

Usage: python3 extract_images.py <markdown_file>

The original file is overwritten with the rewritten version.
Images are saved to images/ relative to the markdown file's directory.
"""
import re
import base64
import sys
import os

md_path = sys.argv[1]
output_dir = os.path.dirname(os.path.abspath(md_path))
images_dir = os.path.join(output_dir, "images")

with open(md_path, "r") as f:
    content = f.read()

pattern = r'^\[(image\d+)\]: <data:image/(\w+);base64,([^>]+)>$'
matches = list(re.finditer(pattern, content, re.MULTILINE))

if not matches:
    print(f"No embedded images found in {md_path}")
    sys.exit(0)

os.makedirs(images_dir, exist_ok=True)
print(f"Extracting {len(matches)} images from {os.path.basename(md_path)}")

for match in matches:
    label = match.group(1)
    fmt = match.group(2)
    b64_data = match.group(3)

    fname = f"{label}.{fmt}"
    fpath = os.path.join(images_dir, fname)

    img_bytes = base64.b64decode(b64_data)
    with open(fpath, "wb") as f:
        f.write(img_bytes)

    print(f"  {fname}: {len(img_bytes):,} bytes")
    content = content.replace(match.group(0), f"[{label}]: images/{fname}")

with open(md_path, "w") as f:
    f.write(content)

print(f"Rewrote {md_path} with local image paths")
