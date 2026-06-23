---
name: aws-access
description: How to authenticate and operate the AWS CLI for David's Bella Slainte AWS account (571573791861), and how to manage AWS API keys / IAM / IAM Identity Center. Use whenever the task involves running AWS CLI commands, logging in to AWS or refreshing AWS credentials, creating or rotating API keys / IAM access keys / Bedrock API keys, adding or auditing IAM Identity Center (SSO) users and permission sets, or any AWS console/CLI administration. Covers the SSO login gotchas (portal username is "David" not his email; the `aws configure sso` region prompt loops).
---

# AWS access — Bella Slainte (account 571573791861)

## Account & access model
- **Account:** `571573791861` (account name "Bella Slainte"), AWS Org `o-6vofitqx49`, root/master email `david@bellamed.ai`. Root has MFA + no access keys — never create root access keys.
- **Identity model = IAM Identity Center (SSO).** Instance `ssoins-8259f73bbff538d7`, primary region `ap-southeast-2`, identity source = Identity Center directory (not Okta).
- **AWS access portal (start URL):** `https://d-97679b00f6.awsapps.com/start`
- **David's SSO username is `David`** — NOT `david@bellamed.ai`. Signing in with the email drops into a broken forgot-password/CAPTCHA loop.
- Default region for everything: **`ap-southeast-2`** (Sydney) — keeps data AU-resident.

## CLI profiles (AWS CLI v2, installed via Homebrew)
| Profile | Identity | Scope | When to use |
|---|---|---|---|
| `admin` | SSO → `AdministratorAccess` permission set | **Full admin**, short-lived auto-rotating creds | All AWS management / build-out |
| `default` | IAM access key on user `BedrockAPIKey-yx0m` | **Bedrock-only** (control-plane read + `bedrock-runtime:Converse`); zero IAM/other perms | Bedrock model calls |
| `bsadmin` | legacy SSO fallback, no token | unused | ignore |

Use a profile with `--profile admin` (or `export AWS_PROFILE=admin`). Bedrock-specific work can use `default` or `admin`.

## Logging in / refreshing credentials
- The `admin` SSO session expires (a few hours). When a command returns an auth/token error, **David must re-auth himself** (browser login — don't run it via the Bash tool):
  - Give him: `! aws sso login --profile admin`
  - Browser opens (already authorised → quick) → "credentials shared successfully" → close tab.
- Verify after: `aws sts get-caller-identity --profile admin` (expect an `assumed-role/AWSReservedSSO_AdministratorAccess_.../David` ARN).

## Bedrock notes
- AU-resident model invocation goes through `au.*` inference profiles via the **Converse** API. See the `reference_bedrock_au_inference_profiles` memory for the live model list and invocation mechanics.
- Quick test: `aws bedrock-runtime converse --region ap-southeast-2 --model-id "au.anthropic.claude-haiku-4-5-20251001-v1:0" --messages '[{"role":"user","content":[{"text":"hi"}]}]' --inference-config '{"maxTokens":20}' --profile admin`

## Managing API keys & identities (runbooks)
All of the below are **console** actions David performs as account owner/admin (the Bedrock `default` key has no IAM perms; it cannot self-grant). The `admin` SSO profile CAN do these via CLI if preferred.

- **New Bedrock API key (least-privilege):** Bedrock console → Discover → *API keys* → generate. This creates a purpose-built IAM user `BedrockAPIKey-xxxx` scoped to Bedrock only — preferred over a broad key for service access.
- **New IAM access key for an existing user:** IAM → Users → <user> → Security credentials → Create access key → "Command Line Interface (CLI)". Secret shown once. Then `aws configure` (static) — only when SSO isn't viable.
- **New human user with admin:** IAM Identity Center → Users → Add user (username = first name, e.g. `David`; email; "send email to set password") → then Permission sets → ensure `AdministratorAccess` exists → AWS accounts → tick the account → Assign users or groups → pick user + permission set → Submit. They set password + MFA via the invite email (or admin Reset password → one-time password).
- **MFA enforcement:** Identity Center → Settings → Authentication → Multi-factor authentication → Configure. **Standing policy (David, 2026-06-23): always-on, instance-wide** — "Prompt users for MFA = Every time they sign in (always-on)", "Require them to register an MFA device at sign-in", authenticator apps + passkeys enabled, users self-manage devices. This is the GitHub-org-2FA equivalent: because all human access is via SSO, login-MFA = MFA on every action incl. Bedrock changes. AWS has no per-service MFA toggle — MFA is enforced at the identity layer. Known bypass = the static `BedrockAPIKey-yx0m` key (invoke/read only, can't make config changes); acceptable. An Organizations SCP denying `aws:MultiFactorAuthPresent=false` is the stronger option but David has deferred it (lockout risk).
- **Audit who holds which keys:** as `admin` — `aws iam list-users`, `aws iam list-access-keys --user-name <u>`, `aws iam get-access-key-last-used --access-key-id <id>`, `aws iam list-attached-user-policies --user-name <u>`. Feeds the ISO 27001 access-control review (Mountwinter).

## Setup gotchas (learned 2026-06-23)
- `aws configure set` only writes `profile.*` keys — it **cannot** create a `[sso-session]` section. To get a working SSO profile either (a) complete a real `aws configure sso` run, or (b) use the legacy self-contained format (`sso_start_url` + `sso_region` inside the profile) then `aws sso login`.
- The interactive `aws configure sso` "Default client Region" prompt can **loop** if Enter isn't registering as accept; worse, a still-running stuck `configure sso` will silently swallow the next thing pasted into the terminal as its prompt answer. If setup goes sideways, have David `Ctrl-C`, then build the profile with `aws configure set` and finish with `aws sso login`.

## Safety (mirror David's gws discipline)
- **Read-only** AWS CLI (`describe*`, `list*`, `get*`) runs freely.
- **Any write / destructive / cost-incurring action** (create, update, put, delete, terminate, rotate, detach, scale, anything that provisions billable resources) requires **explicit approval BEFORE execution** — present as `ACTION: <DESCRIPTION IN CAPS>` with the target, profile, and region. One approval per action; never batch destructive ops; never run them from background agents.
- Browser logins (`aws sso login`, `aws configure sso`) are David's to run via `! <cmd>` — don't invoke them through the Bash tool.
