#!/usr/bin/env python3
"""Deterministic cleanup for raw transcript markdown files.

Handles pandoc artifacts, Unicode normalisation, Gemini noise removal,
and timestamp anchor cleanup. Does NOT handle speaker attribution or
content-level decisions (those require AI judgment).

Usage:
    python3 clean_transcript.py INPUT_FILE [-o OUTPUT_FILE]

If no output file is specified, prints to stdout.
"""

import argparse
import re
import sys
from pathlib import Path


def strip_pandoc_artifacts(text: str) -> str:
    """Remove pandoc conversion artifacts."""
    # {.underline} markers
    text = re.sub(r'\{\.underline\}', '', text)
    # {.mark} markers
    text = re.sub(r'\{\.mark\}', '', text)
    # Strikethrough markers [~~text~~]
    text = re.sub(r'\[~~(.*?)~~\]', r'\1', text)
    # Trailing backslash line breaks
    text = re.sub(r'\\\s*$', '', text, flags=re.MULTILINE)
    # Empty spacer lines (just a backslash and space)
    text = re.sub(r'^\\ \s*$', '', text, flags=re.MULTILINE)
    # Escaped apostrophes
    text = text.replace("\\'", "'")
    return text


def normalise_unicode(text: str) -> str:
    """Normalise Unicode quotes and dashes to consistent forms."""
    # Curly quotes to straight
    text = text.replace('\u2018', "'")  # left single
    text = text.replace('\u2019', "'")  # right single
    text = text.replace('\u201c', '"')  # left double
    text = text.replace('\u201d', '"')  # right double
    # Normalise dashes (keep em-dashes, convert en-dashes in non-name contexts)
    # Don't touch em-dashes as they're used in Gemini transcript headers
    return text


def strip_gemini_noise(text: str) -> str:
    """Remove Gemini-specific noise from notes/transcript files."""
    # Gemini disclaimer
    text = re.sub(
        r'You should review Gemini[^\n]*notes[^\n]*\n?',
        '', text, flags=re.IGNORECASE
    )
    # Gemini survey/feedback links
    text = re.sub(
        r'\[?How helpful were these notes\??\]?[^\n]*\n?',
        '', text, flags=re.IGNORECASE
    )
    # Thumbs up/down feedback links
    text = re.sub(r'\[?[\U0001F44D\U0001F44E][^\n]*\]?\n?', '', text)
    return text


def clean_timestamp_anchors(text: str) -> str:
    """Convert Gemini timestamp anchor links to plain timestamps.

    Converts: [[00:01:14]{.underline}](#section-1)
    To:       00:01:14
    """
    text = re.sub(
        r'\[\[?(\d{1,2}:\d{2}:\d{2})\]?\{?\.?underline\}?\]\(#[^)]*\)',
        r'\1', text
    )
    # Also handle simpler link format: [00:01:14](#section-1)
    text = re.sub(
        r'\[(\d{1,2}:\d{2}:\d{2})\]\(#[^)]*\)',
        r'\1', text
    )
    return text


def strip_attachment_links(text: str) -> str:
    """Remove attachment/calendar event links from Gemini notes header."""
    # Google Calendar event links
    text = re.sub(r'\[.*?calendar\.google\.com[^\]]*\]\([^)]*\)\n?', '', text)
    # Google Docs self-links
    text = re.sub(r'\[.*?docs\.google\.com[^\]]*\]\([^)]*\)\n?', '', text)
    return text


def collapse_excess_blank_lines(text: str) -> str:
    """Collapse runs of 3+ blank lines to 2."""
    return re.sub(r'\n{4,}', '\n\n\n', text)


def clean_transcript(text: str) -> str:
    """Apply all deterministic cleaning steps in order."""
    text = strip_pandoc_artifacts(text)
    text = clean_timestamp_anchors(text)
    text = normalise_unicode(text)
    text = strip_gemini_noise(text)
    text = strip_attachment_links(text)
    text = collapse_excess_blank_lines(text)
    # Strip trailing whitespace on each line
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    # Ensure file ends with single newline
    text = text.rstrip('\n') + '\n'
    return text


def main():
    parser = argparse.ArgumentParser(
        description='Clean raw transcript markdown files'
    )
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)'
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8')
    cleaned = clean_transcript(text)

    if args.output:
        Path(args.output).write_text(cleaned, encoding='utf-8')
        print(f"Cleaned output written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(cleaned)


if __name__ == '__main__':
    main()
