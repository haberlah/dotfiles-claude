---
name: replit-desktop
description: Operate the native Replit Desktop app through UI automation, including navigating tabs and panes, opening Preview, Database, Git, Shell, Publishing, Agent, Settings, and task board surfaces, using Replit workspace shortcuts, and handling Replit sync or publish UI flows. Use this whenever the user asks to drive Replit Desktop, inspect a Replit workspace UI, open a Replit pane or tab, use the Replit Agent panel, run workspace checks in the Replit shell, sync Git in Replit, or publish from the native app.
---

# Replit Desktop

Use this skill for hands-on work in the native Replit Desktop app. It is for UI navigation and operational control, not for writing Replit PRDs or general app design prompts.

## Tool Choice

- In Codex, use Computer Use for Replit Desktop UI actions. Observe the app state before acting, prefer element-targeted interactions when available, and verify the UI changed after each action.
- In Claude, use the available desktop or UI automation tools. If no UI automation is available, give the user concise step-by-step shortcut instructions instead of pretending to operate the app.
- Do not substitute Chrome for native Replit workspace, Git, Shell, Agent, or Publishing operations unless the user asks for Chrome or Replit Desktop is unavailable. Chrome is fine for checking the live deployed app or authenticated browser-only behavior.

## Navigation Workflow

1. Identify the active Replit window, selected tab, and visible panes.
2. If the target pane is already visible, click its tab directly.
3. If the target pane is not visible, use `Cmd+K` and search for the pane or action.
4. Use `Cmd+Shift+]` and `Cmd+Shift+[` to move across open tabs when direct tab selection is unreliable.
5. After navigation, verify the target pane or action is active before continuing.

Common panes and actions:

- `Preview`
- `Database`
- `Git`
- `Shell`
- `Publishing`
- `Agent`
- `Settings`
- `Task board`
- `Find file`
- `Search file contents`

## Shortcut Reference

These shortcuts were captured from the Replit Desktop keyboard shortcuts modal:

| Action | Shortcut |
| --- | --- |
| Toggle command bar | `Cmd+K` |
| Find file | `Cmd+P` |
| Search file contents | `Cmd+Shift+F` |
| Toggle Agent | `Cmd+Shift+B` |
| Toggle sidebar | `Cmd+Shift+L` |
| Toggle task board | `Cmd+Shift+K` |
| Switch to next tab | `Cmd+Shift+]` |
| Switch to previous tab | `Cmd+Shift+[` |
| Run Repl | `Cmd+Return` |
| Show settings | `Cmd+,` |
| Keyboard shortcuts help | `Shift+/` |

Use `Cmd+K` as the primary recovery path when tabs or panes are not visible.

## Safety

Ask for confirmation immediately before actions that publish, deploy, change Git state, delete data, upload or share files, change permissions, or make externally visible changes.

For Replit release work:

- Treat Publishing, deployment promotion, and production publish buttons as externally visible actions.
- Treat Git pull, commit, merge, checkout, branch delete, and push actions as Git state changes.
- Treat file upload, secret edits, database mutation, and permission changes as sensitive operations.
- Read logs, inspect panes, run safe checks, and gather state before asking for confirmation.

## When Blocked

If the Replit Desktop UI is not accessible, report the blocker and offer the nearest safe fallback:

- Replit workspace shell commands if shell access is already open.
- Local repo or GitHub checks when the issue is source-control state.
- Browser verification for the live app when the task is deployed behavior.
- Step-by-step instructions using the shortcuts above when direct UI automation is unavailable.
