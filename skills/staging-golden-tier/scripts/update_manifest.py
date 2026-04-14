#!/usr/bin/env python3
"""Update the Golden Tier manifest.yaml with new session entries.

Reads a transcript file's YAML frontmatter and adds it to the appropriate
person's session list in the manifest. Also updates totals and can verify
manifest consistency.

Usage:
    # Add a new session
    python3 update_manifest.py \
        --manifest Golden_Tier/manifest.yaml \
        --transcript Golden_Tier/Support_Coordinators/jane/s4_mvp_2026-04-09_transcript.md \
        [--notes Golden_Tier/Support_Coordinators/jane/s4_mvp_2026-04-09_notes.md]

    # Verify manifest consistency
    python3 update_manifest.py \
        --manifest Golden_Tier/manifest.yaml \
        --verify
"""

import argparse
import re
import sys
from pathlib import Path

import yaml


def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    text = filepath.read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {filepath}")
    return yaml.safe_load(match.group(1))


def find_person_entry(manifest: dict, participant: str, role: str):
    """Find or create a person entry in the manifest."""
    key = 'support_coordinators' if role == 'Support Coordinator' else 'participants'
    people = manifest['golden_tier'].get(key, [])

    for person in people:
        if person['name'] == participant:
            return person, key

    return None, key


def make_session_entry(
    transcript_path: Path,
    transcript_meta: dict,
    notes_path: Path = None,
    notes_meta: dict = None,
    golden_tier_root: Path = None,
) -> dict:
    """Build a session entry dict for the manifest."""
    # Make path relative to Golden_Tier root
    rel_transcript = str(transcript_path.relative_to(golden_tier_root))

    entry = {
        'id': extract_session_id(transcript_path.name),
        'stage': transcript_meta['stage'],
        'type': transcript_meta['session_type'],
        'date': transcript_meta['date'],
        'transcript': rel_transcript,
        'transcript_words': transcript_meta['word_count'],
        'transcript_source': transcript_meta['source'],
    }

    if notes_path and notes_path.exists():
        rel_notes = str(notes_path.relative_to(golden_tier_root))
        entry['notes'] = rel_notes
        entry['notes_words'] = notes_meta['word_count'] if notes_meta else 0
    else:
        entry['notes'] = None
        entry['notes_words'] = 0

    return entry


def extract_session_id(filename: str) -> str:
    """Extract session ID from filename like s4_mvp_2026-04-09_transcript.md."""
    # Remove date and type suffix
    match = re.match(r'(.+?)_\d{4}-\d{2}-\d{2}_(transcript|notes)\.md$', filename)
    if match:
        return match.group(1)
    return filename.rsplit('_', 2)[0]


def update_totals(person: dict):
    """Recalculate total word counts for a person."""
    t_words = sum(s.get('transcript_words', 0) for s in person['sessions'])
    n_words = sum(s.get('notes_words', 0) for s in person['sessions'])
    person['total_transcript_words'] = t_words
    person['total_notes_words'] = n_words


def update_grand_totals(manifest: dict):
    """Recalculate grand totals across all people."""
    total_t = 0
    total_n = 0
    total_sessions = 0
    total_people = 0

    for key in ['support_coordinators', 'participants']:
        people = manifest['golden_tier'].get(key, [])
        total_people += len(people)
        for person in people:
            total_sessions += len(person.get('sessions', []))
            total_t += person.get('total_transcript_words', 0)
            total_n += person.get('total_notes_words', 0)

    manifest['golden_tier']['totals']['people'] = total_people
    manifest['golden_tier']['totals']['sessions'] = total_sessions
    manifest['golden_tier']['totals']['transcript_words'] = total_t
    manifest['golden_tier']['totals']['notes_words'] = total_n


def verify_manifest(manifest: dict, golden_tier_root: Path) -> list:
    """Verify manifest consistency. Returns list of issues."""
    issues = []

    for key in ['support_coordinators', 'participants']:
        for person in manifest['golden_tier'].get(key, []):
            seen_ids = set()
            for session in person.get('sessions', []):
                # Check for duplicate session IDs
                sid = session.get('id', 'unknown')
                if sid in seen_ids:
                    issues.append(
                        f"Duplicate session ID '{sid}' for {person['name']}"
                    )
                seen_ids.add(sid)

                # Check transcript file exists
                t_path = session.get('transcript')
                if t_path and not (golden_tier_root / t_path).exists():
                    issues.append(
                        f"Missing transcript: {t_path}"
                    )

                # Check notes file exists
                n_path = session.get('notes')
                if n_path and not (golden_tier_root / n_path).exists():
                    issues.append(
                        f"Missing notes file: {n_path}"
                    )

            # Verify totals
            expected_t = sum(
                s.get('transcript_words', 0)
                for s in person.get('sessions', [])
            )
            if person.get('total_transcript_words', 0) != expected_t:
                issues.append(
                    f"Word count mismatch for {person['name']}: "
                    f"total says {person.get('total_transcript_words', 0)}, "
                    f"sum is {expected_t}"
                )

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Update Golden Tier manifest.yaml'
    )
    parser.add_argument('--manifest', required=True, help='Path to manifest.yaml')
    parser.add_argument('--transcript', help='Path to new transcript file')
    parser.add_argument('--notes', help='Path to companion notes file')
    parser.add_argument(
        '--verify', action='store_true',
        help='Verify manifest consistency only'
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    golden_tier_root = manifest_path.parent

    with open(manifest_path, encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    if args.verify:
        issues = verify_manifest(manifest, golden_tier_root)
        if issues:
            print("Manifest verification FAILED:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Manifest verification PASSED", file=sys.stderr)
            sys.exit(0)

    if not args.transcript:
        print("Error: --transcript required when not using --verify", file=sys.stderr)
        sys.exit(1)

    transcript_path = Path(args.transcript)
    transcript_meta = parse_frontmatter(transcript_path)

    notes_path = Path(args.notes) if args.notes else None
    notes_meta = parse_frontmatter(notes_path) if notes_path and notes_path.exists() else None

    person, key = find_person_entry(
        manifest,
        transcript_meta['participant'],
        transcript_meta['role'],
    )

    session = make_session_entry(
        transcript_path=transcript_path,
        transcript_meta=transcript_meta,
        notes_path=notes_path,
        notes_meta=notes_meta,
        golden_tier_root=golden_tier_root,
    )

    if person is None:
        print(
            f"Warning: {transcript_meta['participant']} not found in manifest "
            f"under {key}. Add them manually.",
            file=sys.stderr
        )
        sys.exit(1)

    # Check for existing session with same ID
    existing = [s for s in person['sessions'] if s['id'] == session['id']]
    if existing:
        print(
            f"Warning: Session {session['id']} already exists for "
            f"{person['name']}. Skipping.",
            file=sys.stderr
        )
        sys.exit(0)

    person['sessions'].append(session)
    update_totals(person)
    update_grand_totals(manifest)

    with open(manifest_path, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(
        f"Added {session['id']} for {person['name']} "
        f"({session['transcript_words']} words)",
        file=sys.stderr
    )


if __name__ == '__main__':
    main()
