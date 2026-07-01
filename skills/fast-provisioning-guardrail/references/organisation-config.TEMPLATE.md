# Organisation Configuration — TEMPLATE

Fill in every field below before using the `fast-provisioning-guardrail` skill with a specific client/project. Copy this file to `references/organisation-config.md` (or `references/<client-name>-config.md`) inside the shareable skill package and complete it per engagement. Leave no `<...>` placeholder unresolved before treating the skill as ready for a client.

## 1. Foundations Repository

- **Foundations repo path:** `<org>/<repo-name>` (e.g. `my-org/gcp-foundations`)
- **FAST version / layout in use:** (e.g. Cloud Foundation Fabric FAST, specific tag/commit if pinned)
- **Stage directory layout confirmed?** (yes/no — note any deviation from the standard `fast/stages/0-org-setup`, `1-resman`, `2-project-factory`, `2-security`, `2-networking`, etc. numbering)
- **PR review requirements:** (required reviewers, required checks, branch protection notes)

## 2. Naming Conventions

- **Org/project-prefix convention (`<ORG_PREFIX>`):** e.g. `acme-`, `acme-prod-`
- **Application naming pattern:** e.g. `<ORG_PREFIX><app-name>`
- **Folder structure keys:** list the actual `$folder_ids:` keys in use, e.g.:
  - Common/security folder key: `___`
  - Production folder key: `___`
  - Non-production folder key: `___`
  - Sandbox/dev folder key: `___`

## 3. Security / Secrets Isolation

- **Sec-core naming pattern:** e.g. `<APP_NAME>-sec-core` or `<ENV>-sec-core`
- **Default services enabled on sec-core:** e.g. `secretmanager.googleapis.com`, `logging.googleapis.com`, `monitoring.googleapis.com`
- **Does this client use CMEK/KMS?** (yes/no — if yes, which environments/apps, and which additional services/keyrings are standard)
- **Secret-container dataset path pattern:** e.g. `fast/stages/2-security/datasets/classic/secrets/<app>-secrets.yaml`
- **Cross-project secret access pattern:** confirm whether access is granted project level (`secretAccessor` on the whole project) or per secret, and to which SA groupings

## 4. Automation Identities

- **IaC-apply service account naming pattern:** e.g. `<org-prefix>-iac-tf-sa`
- **Release/deploy service account naming pattern:** e.g. `<app-name>-cicd-sa`
- **Confirmed: both identities' roles are declared in FAST, never granted ad hoc?** (yes/no)

## 5. Org Policy Baseline

- **SA key creation prohibited?** (yes/no)
- **Domain-restricted sharing enforced?** (yes/no — note the tag-binding pattern used for public/invoker exceptions, if any)
- **Data residency requirement?** (region/multi-region, if applicable)
- **Shielded VM / other compute baseline requirements?**

## 6. Core Automation Resources (Do-Not-Touch List)

- **Org-setup stage core projects/SAs** that require human confirmation before any change (equivalents of `iac-0`, `log-0`, `billing-0`): list actual names here.

## 7. App-Repo Boundary

- **App-owned Terraform repo(s):** list per app, e.g. `<app-name>-terraform`
- **Confirmed convention:** foundation-owned resources are referenced from app repos (string/data-source), never redeclared as resources there.

## 8. Historical Remediation Examples (Internal Reference Only)

- **Does this client have a real brownfield-import or incident-remediation history?** (yes/no)
- If yes, link the **internal-only** write-up here (e.g. `references/<client>-config.md`), including real PR numbers/dates. **Do not paste real incident details into this template file or into any file shared outside the client engagement** — keep that content in the client-specific internal file only.
- If no such history exists yet, note "none yet — using the generic illustrative walkthrough in `references/illustrative-walkthrough.md`."
