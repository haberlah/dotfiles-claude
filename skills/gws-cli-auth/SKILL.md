---
name: gws-cli-auth
description: Authenticate or repair Google Workspace CLI (`gws`) OAuth with reusable scope presets instead of manually toggling scopes. Use when setting up GWS CLI, running `gws auth login`, fixing invalid_scope errors, avoiding `cloud-identity.devices`, refreshing invalid tokens such as invalid_rapt, or preparing a broad Google Workspace CLI OAuth login for engineering workflows.
---

# GWS CLI Auth

Use this skill to authenticate `gws` repeatably with named scope presets. For Haberlah/startup engineering use, default to `workspace-core`; it is intentionally broad so agents and engineering tools can use Google Workspace through one CLI without manual consent-screen scope picking.

## First Check

Check local auth state without exposing secrets:

```bash
gws auth status
```

If status reports `token_valid: false`, `invalid_rapt`, expired refresh behavior, missing credentials, or a scope-related failure, reauthenticate with a preset. Do not print, cat, export, or paste token files unless the user explicitly asks and understands the secret exposure.

## Agent Recovery Flow

When a `gws` command fails because auth is missing, expired, invalid, or under-scoped:

1. Run `gws auth status` to confirm the auth state without exposing secrets.
2. If the token is invalid or missing, run the `workspace-core` login command below.
3. Let the user complete the browser consent flow. If `gws` prints a URL instead of opening the browser, show that URL to the user and wait for them to finish authentication.
4. After the browser callback completes, run `gws auth status` again.
5. Run a harmless smoke test such as `gws drive files list --params '{"pageSize": 1}'`.

Do not use `gws auth logout` unless the user explicitly asks to clear credentials.

## Default Login

Use `workspace-core` for the broad startup engineering workflow:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh workspace-core
```

Preview the exact scopes without launching browser auth:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh workspace-core --print
```

The helper calls:

```bash
gws auth login --scopes "<comma-separated scopes>"
```

This avoids the interactive scope picker and keeps the login deterministic.

## Never Use Full Auth

Do not use:

```bash
gws auth login --full
```

`--full` can request scopes that cannot be shown in normal installed-app OAuth, especially:

```text
https://www.googleapis.com/auth/cloud-identity.devices
```

The helper refuses `full`, `all`, `devices`, and `cloud-identity-devices`. For Cloud Identity full device management, use a service account with Google Workspace domain-wide delegation impersonating an admin user. For interactive user OAuth, use `cloud-identity.devices.lookup` only when user-facing device lookup is enough.

## Presets

Use one preset unless there is a clear reason to combine a small number. The helper refuses combinations over 24 scopes unless `--allow-large` is passed.

- `workspace-core`: default broad engineering preset for Drive, Gmail modify/send/compose, Calendar, Docs, Sheets, Slides, Tasks, Contacts, Chat user actions, Forms, Meet create/read, and Apps Script projects.
- `drive-backup`: Drive access for local Drive exports and mirrors.
- `readonly`: read-oriented Workspace access across Drive, Gmail, Calendar, Docs, Sheets, Slides, Tasks, and Contacts.
- `gmail`: Gmail modify/send/compose, labels, and basic settings.
- `chat-user`: Chat messages, spaces, memberships, deletion, custom emoji, read state, space settings, and sections.
- `chat-admin`: Chat admin scopes. Use only with a Workspace admin account and admin-approved OAuth client.
- `meet`: Google Meet space create/read/settings.
- `script`: Apps Script project/deployment/process/metrics scopes.
- `admin-directory`: Admin SDK Directory scopes. Use only with a Workspace admin account and admin-approved OAuth client.
- `classroom`: Classroom scopes.
- `cloud-identity-admin`: Cloud Identity groups, inbound SSO, policies, and device lookup. It intentionally excludes full `cloud-identity.devices`.
- `cloud-platform`: Google Cloud `cloud-platform` only. Keep separate unless the workflow genuinely needs GCP APIs.

Examples:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh gmail
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh chat-user
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh gmail,chat-user --print
bash ${CLAUDE_SKILL_DIR}/scripts/gws_auth_preset.sh admin-directory --print
```

If a large combination is intentional, pass `--allow-large` only after explaining that Google may reject it in testing or unverified OAuth mode.

## Google Cloud Settings

For normal installed-app OAuth:

1. Use an OAuth client of type `Desktop app`.
2. In Google Auth Platform / OAuth consent, add the user as a test user when the app is external/testing.
3. Enable APIs needed by the preset: Drive, Gmail, Calendar, Docs, Sheets, Slides, Tasks, Chat, Forms, Meet, Apps Script, Admin SDK, Classroom, Cloud Identity, and any Cloud APIs used.
4. For external apps, expect sensitive or restricted scopes to require verification before broad use.
5. For internal Workspace apps, still keep unsupported scopes out of interactive OAuth; internal status does not make `cloud-identity.devices` valid in this flow.

## After Login

Verify auth and run one harmless smoke test:

```bash
gws auth status
gws drive files list --params '{"pageSize": 1}'
```

For non-Drive-only work, choose a read-only smoke test from the relevant service. Do not run destructive API methods as auth checks.
