# Security Policy

## Reporting a vulnerability

This is a small, single-purpose tool maintained by an individual. If you find a
security issue, please report it privately using GitHub's "Report a
vulnerability" button (the Security tab on this repository) rather than opening a
public issue. I aim to respond within about a week.

## What this tool does with your data

- It runs entirely on your machine using only the Python standard library. It
  makes no network calls and transmits nothing anywhere.
- It reads and rewrites Codex session rollout files under `~/.codex/sessions`.
  Before modifying a file it copies the original to `<file>.orig` (or to your
  `--backup-dir`), so every change is reversible.
- It never uploads or commits session contents. The bundled `.gitignore`
  excludes `*.jsonl` and `*.orig` so session data cannot be committed by
  accident.

## Scope and safety

The scripts modify local files you point them at, which is inherently
destructive. Two safeguards are built in and should not be removed: the original
is always archived before a write, and `verify_rollout.py` checks the result is
valid before you rely on it. Keep the archived original until you have confirmed
the repaired session loads and resumes.
