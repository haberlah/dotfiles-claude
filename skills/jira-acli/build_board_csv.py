#!/usr/bin/env python3
"""Build acli create-bulk CSV(s) + a status sidecar from a Google-Sheet JSON dump.

Pipeline (see SKILL.md):
  gws sheets +read --spreadsheet <ID> --range "A1:Z200" --format json > raw.json
  python3 build_board_csv.py raw.json --project KAN --outdir ./out
  # -> out/issues_0.csv, issues_1.csv (<=50 rows each), out/meta.json

Then per batch:  acli jira workitem create-bulk --from-csv out/issues_0.csv --yes
Then recover keys via search, transition by meta.json target, apply labels per area.

This is a TEMPLATE: the column indices and the AREA_SLUG / STATUS_MAP dicts below
match the Bella pilot sheet (Area, ID, Item, Owner, Phase, Status, Notes, Blockers?).
Adjust them for a different sheet shape.
"""
import json, csv, sys, os, argparse

# --- sheet-specific config: edit for a new sheet shape ---
COL = dict(area=0, id=1, item=2, owner=3, phase=4, status=5, notes=6, blockers=7)
AREA_SLUG = {  # first letter of the ID (or Area) -> label slug
    'A': 'pilot-enablers', 'B': 'onboarding', 'C': 'consent', 'D': 'security-access',
    'E': 'payment-billing', 'F': 'offboarding-retention', 'G': 'build-engineering', 'H': 'brand-comms'}
STATUS_MAP = {  # lowercased sheet status -> Jira status name (KAN columns)
    'open': 'Idea', 'in progress': 'In Progress', 'closed': 'Done', 'blocked': 'In Progress'}
BLOCKED_LABEL = 'blocked'   # extra label when sheet status is "blocked"
BATCH = 40                  # rows per CSV (acli hard cap is 50)
# ---------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw_json', help='gws sheets +read JSON dump')
    ap.add_argument('--project', default='KAN')
    ap.add_argument('--type', default='Task')
    ap.add_argument('--outdir', default='.')
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rows = json.load(open(a.raw_json))['values'][1:]  # skip header

    issues, meta = [], []
    for r in rows:
        r = r + [''] * (max(COL.values()) + 1 - len(r))
        g = lambda k: r[COL[k]].strip()
        iid, item = g('id'), g('item')
        if not iid and not item:
            continue
        letter = (iid or g('area'))[0]
        norm = g('status').lower()
        parts = [f"{lab}: {g(k)}" for lab, k in
                 [('Owner', 'owner'), ('Phase', 'phase'), ('Sheet status', 'status'),
                  ('Notes', 'notes'), ('Blockers', 'blockers')] if g(k)]
        parts.append(f"Source: sheet {iid}")
        summary = f"{iid} — {item}" if iid else item
        if len(summary) > 250:
            summary = summary[:247] + '...'
        issues.append([summary, a.project, a.type, " | ".join(parts),
                       AREA_SLUG.get(letter, 'misc')])  # label col is IGNORED by acli; kept for reference
        meta.append({"id": iid, "target": STATUS_MAP.get(norm, 'Idea'),
                     "label": AREA_SLUG.get(letter, 'misc'),
                     "blocked": norm == 'blocked'})

    hdr = ['summary', 'projectKey', 'issueType', 'description', 'label']
    for i in range(0, len(issues), BATCH):
        path = os.path.join(a.outdir, f'issues_{i // BATCH}.csv')
        with open(path, 'w', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(hdr); w.writerows(issues[i:i + BATCH])
        print(f'wrote {path} ({len(issues[i:i+BATCH])} rows)')
    json.dump(meta, open(os.path.join(a.outdir, 'meta.json'), 'w'), indent=2)
    print(f'wrote {os.path.join(a.outdir, "meta.json")} ({len(meta)} rows)')
    print('NOTE: the CSV "label" column is ignored by acli create-bulk — '
          'apply labels via `acli jira workitem edit --labels` after creation (it appends).')

if __name__ == '__main__':
    main()
