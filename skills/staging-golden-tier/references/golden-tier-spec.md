# Golden Tier Format Specification

## File naming convention

```
{session_id}_{date}_{type}.md
```

- **session_id**: `s1_ditl`, `s2_feature-val`, `s3_mvp`, `s4_mvp`, `s5_market-val`, `s4s5_hybrid`, `hybrid_ditl-fv`, `optional_support`
- **date**: ISO format `YYYY-MM-DD`
- **type**: `transcript` or `notes`

Examples:
- `s1_ditl_2026-03-12_transcript.md`
- `s4_mvp_2026-04-09_notes.md`
- `s5_market-val_2026-04-13_transcript.md`

## Folder structure

```
Golden_Tier/
  Support_Coordinators/{snake_case_name}/
  Participants/{snake_case_name}/
```

## YAML frontmatter — transcript files

```yaml
---
participant: "Full Name"
role: "Support Coordinator"        # or "Participant"
stage: 4                           # integer 1-5, or descriptive string for hybrids
session_type: "MVP Testing"        # human-readable: "Day in the Life", "Feature Validation", "MVP Testing", "Market Validation"
date: "2026-04-09"                 # ISO date of the session
source: "Gemini embedded transcript"  # or "Read AI"
source_file: "original_filename.docx" # original pre-cleaning filename
content_type: "transcript"
word_count: 12345                  # integer, body only (excludes frontmatter)
has_companion_notes: true          # boolean
---
```

## YAML frontmatter — notes files

```yaml
---
participant: "Full Name"
role: "Support Coordinator"
stage: 4
session_type: "MVP Testing"
date: "2026-04-09"
source: "Google Meet — Notes by Gemini"
source_file: "original_filename.docx"
content_type: "ai_summary_notes"
word_count: 2500
---
```

## Document header (after frontmatter)

```markdown
# {Participant Name} — Stage {N}: {Session Type}
**Date:** {D Month YYYY}

---
```

For Read AI transcripts, use `--` (double hyphen). For Gemini transcripts, use `—` (em dash).

## Speaker turn format

### Read AI-sourced transcripts

Fully standardised format:

```markdown
**Speaker Name** [Role] (H:MM:SS):
Content text here. May span multiple lines.
```

Blank line between each turn. Roles: `Interviewer`, `Support Coordinator`, `Participant`, `Team`, `Observer`, `Unidentified`.

### Gemini-sourced transcripts

Lighter-touch format preserving Gemini structure:

```markdown
00:00:00

Speaker Display Name: Content text here.
Next Speaker: Response text.


00:01:30

Speaker Display Name: More content.
```

Timestamps appear as standalone lines (H:MM:SS or HH:MM:SS). Speaker turns are `Display Name: text`. Blank lines separate timestamp blocks.

## Notes file body format

Preserves Gemini's structured output:
1. Emoji header line
2. Date
3. Meeting title
4. Invited list (cleaned of markdown artifacts)
5. Summary section
6. Theme-based detail sections
7. Suggested next steps

## Cleaning checklist

### Deterministic (script-handled)
- [ ] Strip pandoc artifacts: `{.underline}`, `[~~text~~]`, `{.mark}`, trailing `\`
- [ ] Remove empty `\ ` spacer lines
- [ ] Strip Gemini disclaimer text ("You should review Gemini's notes...")
- [ ] Strip Gemini survey links
- [ ] Clean escaped apostrophes (`\'` to `'`)
- [ ] Normalise Unicode quotes and dashes
- [ ] Strip `[[text]{.underline}](#section-N)` timestamp anchors (replace with plain timestamp)
- [ ] Remove attachment/calendar links from notes header

### AI judgment required
- [ ] Standardise speaker labels using known-speakers.md
- [ ] Assign roles to all speakers
- [ ] Resolve "Unidentified Speaker" from context where possible
- [ ] Correct domain-specific transcription errors
- [ ] Merge consecutive same-speaker turns (only when clearly the same thought)
- [ ] Separate transcript section from notes section (for Gemini exports containing both)
- [ ] Verify session date from content (not just filename)
- [ ] Determine correct session_id and stage from content
