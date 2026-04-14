#!/usr/bin/env python3
"""Generate YAML frontmatter and document header for Golden Tier files.

Prepends frontmatter to a cleaned transcript/notes markdown file,
calculates word count, and writes the final output.

Usage:
    python3 generate_frontmatter.py \
        --participant "Name" \
        --role "Support Coordinator" \
        --stage 4 \
        --session-type "MVP Testing" \
        --date "2026-04-09" \
        --source "Gemini embedded transcript" \
        --source-file "original.docx" \
        --content-type transcript \
        [--has-companion-notes] \
        INPUT_FILE \
        [-o OUTPUT_FILE]
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


def count_words(text: str) -> int:
    """Count words in the body text (excludes frontmatter)."""
    # Remove YAML frontmatter if present
    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    # Remove markdown header lines
    body = re.sub(r'^#.*$', '', body, flags=re.MULTILINE)
    body = re.sub(r'^\*\*Date:\*\*.*$', '', body, flags=re.MULTILINE)
    body = re.sub(r'^---\s*$', '', body, flags=re.MULTILINE)
    # Count words
    words = body.split()
    return len(words)


def format_date_human(iso_date: str) -> str:
    """Convert ISO date to human-readable format: D Month YYYY."""
    dt = datetime.strptime(iso_date, '%Y-%m-%d')
    return dt.strftime('%-d %B %Y')


def generate_frontmatter(
    participant: str,
    role: str,
    stage,
    session_type: str,
    date: str,
    source: str,
    source_file: str,
    content_type: str,
    word_count: int,
    has_companion_notes: bool = False,
) -> str:
    """Generate YAML frontmatter block."""
    lines = [
        '---',
        f'participant: "{participant}"',
        f'role: "{role}"',
        f'stage: {stage}',
        f'session_type: "{session_type}"',
        f'date: "{date}"',
        f'source: "{source}"',
        f'source_file: "{source_file}"',
        f'content_type: "{content_type}"',
        f'word_count: {word_count}',
    ]
    if content_type == 'transcript':
        lines.append(
            f'has_companion_notes: {"true" if has_companion_notes else "false"}'
        )
    lines.append('---')
    return '\n'.join(lines)


def generate_header(
    participant: str,
    stage,
    session_type: str,
    date: str,
    source: str,
) -> str:
    """Generate the document header after frontmatter."""
    human_date = format_date_human(date)
    # Read AI uses -- (double hyphen), Gemini uses em-dash
    separator = '--' if source == 'Read AI' else '\u2014'
    return f'\n# {participant} {separator} Stage {stage}: {session_type}\n**Date:** {human_date}\n\n---\n'


def main():
    parser = argparse.ArgumentParser(
        description='Generate YAML frontmatter for Golden Tier files'
    )
    parser.add_argument('input', help='Input cleaned markdown file')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--participant', required=True)
    parser.add_argument('--role', required=True)
    parser.add_argument('--stage', required=True)
    parser.add_argument('--session-type', required=True)
    parser.add_argument('--date', required=True, help='ISO date YYYY-MM-DD')
    parser.add_argument('--source', required=True)
    parser.add_argument('--source-file', required=True)
    parser.add_argument(
        '--content-type', required=True,
        choices=['transcript', 'ai_summary_notes']
    )
    parser.add_argument(
        '--has-companion-notes', action='store_true', default=False
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    body = input_path.read_text(encoding='utf-8')
    word_count = count_words(body)

    # Try to parse stage as int, fall back to string
    try:
        stage = int(args.stage)
    except ValueError:
        stage = f'"{args.stage}"'

    frontmatter = generate_frontmatter(
        participant=args.participant,
        role=args.role,
        stage=stage,
        session_type=args.session_type,
        date=args.date,
        source=args.source,
        source_file=args.source_file,
        content_type=args.content_type,
        word_count=word_count,
        has_companion_notes=args.has_companion_notes,
    )

    header = generate_header(
        participant=args.participant,
        stage=args.stage,
        session_type=args.session_type,
        date=args.date,
        source=args.source,
    )

    output = frontmatter + header + '\n' + body

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(
            f"Generated {args.output} ({word_count} words)",
            file=sys.stderr
        )
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
