# Global Claude Code Instructions

## Language preferences

Always use Australian English spelling when:
- Writing comments in code (not the code itself, only comments)
- Communicating with me in chat

Examples: colour, behaviour, organisation, initialise, centre, analyse, favourite, honour.

## Planning workflow

Before implementing any non-trivial task:
1. Plan the approach first — outline what files will be changed and why
2. Present the plan for my review
3. Only proceed with implementation after I approve

Use EnterPlanMode for multi-step tasks. Always think through the full approach before writing code.

## Agent teams

Use agent teams for tasks that benefit from parallel work:
- Research + implementation in parallel
- Frontend + backend changes
- Multi-file refactors
- Testing while implementing

## Auto-commit workflow

Changes are automatically committed and pushed to GitHub by a Stop hook after each response. Do NOT ask about version control — it is handled automatically.

After pushing, relay the Replit pull command from the hook output so I can sync my Replit deployment.
