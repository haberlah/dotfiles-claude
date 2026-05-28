---
description: Report dotfiles-claude repo sync state and ~/.claude symlink health. Use to check whether the Claude Code config is clean, in sync with origin, and correctly linked.
allowed-tools: Bash(git -C ~/dotfiles-claude status:*), Bash(git -C ~/dotfiles-claude log:*), Bash(ls:*)
---

# Dotfiles status

Report the health of the Claude Code config managed in `~/dotfiles-claude`. The `!` lines
below run at expansion time and their output is inlined for you to interpret.

## Repo sync state

!`git -C ~/dotfiles-claude status -sb`
!`git -C ~/dotfiles-claude log -1 --format='last commit: %h %ci %s'`

## Symlinks in ~/.claude

!`ls -la ~/.claude`

From the output above:
1. State whether the working tree is clean and whether the branch is ahead of or behind
   `origin/main` (the `## main...origin/main` line shows this).
2. List the `~/.claude` entries that are symlinks into `dotfiles-claude` and flag any whose
   target looks wrong or missing.
3. Give a one-line verdict: config is clean and in sync, or here is what needs attention.
