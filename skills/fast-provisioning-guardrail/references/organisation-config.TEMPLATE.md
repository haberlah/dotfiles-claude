# Organisation Configuration — TEMPLATE

Fill in every field below before using the `fast-provisioning-guardrail` skill with a specific client/project. Copy this file to `references/organisation-config.md` (or `references/<client-name>-config.md`) inside the shareable skill package and complete it per engagement. Leave no `<...>` placeholder unresolved before treating the skill as ready for a client.

## 1. Foundations Repository

- **Foundations repo path:** `<org>/<repo-name>` (e.g. `my-org/gcp-foundations`)
- **FAST version / layout in use:** (e.g. Cloud Foundation Fabric FAST, specific tag/commit if pinned)
- **Stage directory layout confirmed?** (yes/no — note any deviation from the standard `fast/stages/0-org-setup`, `1-resman`, `2-project-factory`, `2-security`, `2-networking`, etc. numbering)
- **PR review requirements:** (required reviewers, required checks, branch protection notes)
- **Real project ID derivation rule:** live project IDs are usually `<projects.defaults.prefix><logical-name>` from `defaults.yaml` (e.g. prefix `acme` + logical name `prod-iac-core-0` → `acme-prod-iac-core-0`). Record the prefix here rather than a point-in-time list of resolved names, so real names can always be derived from the YAML instead of going stale: `___`
- **Search path reminder:** when checking whether something is already declared in Terraform, search `2-project-factory` (app/foundation projects), `2-security` (sec-core projects and secrets — NOT project-factory), and `2-networking` (VPCs/subnets/firewall) — plus the app's own Terraform repo. Concluding something is "undeclared" after checking only one of these is a common false positive.

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

- **Org-setup stage core projects/SAs** that require human confirmation before any change: list this client's actual project names and automation SA naming pattern here — do not assume any specific naming convention (e.g. `iac-0`/`log-0`/`billing-0`) without confirming against this client's actual `0-org-setup` output: `___`
- **Org-level IAM audit (do this before trusting the boundary is enforced at all):** confirm no human group or individual user holds `roles/owner`, `roles/resourcemanager.organizationAdmin`, `roles/resourcemanager.projectCreator`, `roles/resourcemanager.projectDeleter`, or `roles/orgpolicy.policyAdmin` directly at the organization level (`gcloud organizations get-iam-policy <org-id>`). If any human principal holds these, the entire "everything goes through Terraform+PR" guarantee is only a convention, not an enforced control — flag this to the client regardless of how clean their Terraform looks. Result: `___`

## 7. App-Repo Boundary

- **App-owned Terraform repo(s):** list per app, e.g. `<app-name>-terraform`
- **What the app repo is actually allowed to create directly** (not just reference) — check the app repo's own modules/resources rather than assuming; common app-owned resource types include CI/CD delivery pipelines (Cloud Build triggers, Cloud Deploy, Artifact Registry), runtime services (Cloud Run, load balancers, Cloud Armor), and app-specific encryption keys/buckets declared with a cross-project `project = <sec-core-project-id>` attribute once FAST has granted the automation identity the matching role. List the confirmed resource types here: `___`
- **What must stay in `<FOUNDATIONS_REPO>` regardless:** the project itself, org/project-level IAM grants for automation identities, shared/reserved secret containers, the security project itself, networking backbone, org policies, API enablement.
- **Confirmed:** cross-project resources declared from the app repo only exist because `<FOUNDATIONS_REPO>` granted the specific IAM role first — never because the app repo's Terraform identity happened to have broad enough access to just work.

## 8. Historical Remediation Examples (Internal Reference Only)

- **Does this client have a real brownfield-import or incident-remediation history?** (yes/no)
- If yes, link the **internal-only** write-up here (e.g. `references/<client>-config.md`), including real PR numbers/dates. **Do not paste real incident details into this template file or into any file shared outside the client engagement** — keep that content in the client-specific internal file only.
- If no such history exists yet, note "none yet — using the generic illustrative walkthrough in `references/illustrative-walkthrough.md`."

## 9. Known Open Items (Live, Unresolved — Internal Reference Only)

Distinct from section 8: this tracks compliance/drift gaps that are confirmed but NOT yet resolved, so a future agent working on this client's infrastructure doesn't act on stale assumptions (e.g. assuming a remediated project is receiving production traffic when DNS/cutover hasn't happened yet, or missing that an unmanaged resource still exists and needs careful handling rather than casual deletion).

- List each open item as: what's confirmed live, how it was verified (exact command/evidence, not assumption), and what decision is still pending. **Do not paste this section's content into the shareable Aviato package or any other client's config** — internal-only, like section 8.
