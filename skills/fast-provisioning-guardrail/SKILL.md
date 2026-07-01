---
name: fast-provisioning-guardrail
description: This skill should be used whenever a task involves creating, changing, or granting access to any GCP resource — creating a project, adding or modifying an IAM binding or role grant, provisioning a secret, KMS key, or CMEK, enabling an API, changing an org policy, or touching networking, folders, or service accounts. It enforces that every such write happens through FAST (Fabric Automation and Scalability Toolkit / Cloud Foundation Fabric) YAML plus Terraform plus a reviewed PR against the foundations repo, never via ad-hoc `gcloud` commands or GCP Console clicks — including when the request is phrased as "quickly," "just for now," "as a one-off," or "to unblock." Also use this skill when asked to bring an already-existing (brownfield) GCP resource under Terraform management, or when reviewing whether a proposed GCP change is safe to apply directly. Read-only/diagnostic GCP requests (describing a project, listing IAM bindings, checking quota, viewing Console screens) do not need this skill.
---

# FAST Provisioning Guardrail

## Before You Use This Skill

This skill is a generic template. Before it is usable for a specific client or project, fill in the configuration values it depends on — never leave the placeholder tokens in place when applying this skill live. The concrete values belong in a companion `references/organisation-config.md` file, completed per engagement from `references/organisation-config.TEMPLATE.md`, and this skill must be read alongside that file.

At minimum, a new client/project needs to supply:

- **Foundations repo path** — the `<FOUNDATIONS_REPO>` token below, e.g. `my-org/gcp-foundations`. This is the single repo where all FAST stage YAML and `.tf` files live and where every provisioning PR lands.
- **Org/project-prefix convention** — the `<ORG_PREFIX>` token, e.g. how application, security, and automation projects are named (`acme-`, `acme-prod-`, etc.).
- **Security-project naming convention** — the `<APP>-sec-core` / `<ENV>-sec-core` pattern this client actually uses for isolating secrets, KMS keys, and CMEKs.
- **Whether this client uses CMEK/KMS** — some clients are fine with Google-managed encryption everywhere; others mandate CMEK for some or all environments. This changes which services get enabled on the sec-core project.
- **Where this client's own historical remediation examples live** — once a client has been through a brownfield-import or incident-remediation exercise of their own, link the real write-up from a `references/<client>-config.md` file (internal-only, never shipped to other clients) rather than inventing one. Until such an example exists, use the generic illustrative walkthrough in `references/illustrative-walkthrough.md` as-is.

Everything below this point uses placeholder tokens (`<FOUNDATIONS_REPO>`, `<APP_NAME>`, `<ORG_PREFIX>`, `<SEC_CORE_SA>`, etc.) — substitute the client's real values only in the client-specific config file, never by editing this shared skill file per client.

## Core Principles & Execution Rules

> [!CRITICAL]
> **Read is free, write is not.** `gcloud` and the GCP Console may be used freely for reading and diagnosing state (`gcloud projects describe`, `gcloud iam ...list`, Console viewing screens). Every GCP **write** — project creation, IAM binding, secret/KMS/CMEK creation, org policy change, API enablement, folder/network change, or any application-delivery resource (Cloud Run, Cloud Deploy, Artifact Registry, load balancers, Cloud Build triggers) — MUST be made as a Terraform resource, planned and applied, landed via a reviewed PR. There is no "just this once" exception. This rule binds an autonomous coding agent exactly as it binds a human operator, regardless of which coding tool or CLI is issuing the command.
>
> This does NOT mean every write lives in one single repo. Foundation-level resources (the project itself, org/project-level IAM for automation identities, shared secret containers, the security project, networking backbone, org policies, API enablement) belong in `<FOUNDATIONS_REPO>`'s FAST YAML. Application-delivery resources (CI/CD pipelines, Artifact Registry, Cloud Run/Cloud Deploy, an app-specific encryption key for that app's own data) commonly live in the app's own Terraform repo instead — see "Which Repo Owns This Resource?" below. Either way, the invariant is the same: declarative Terraform through a reviewed PR, never ad hoc `gcloud`/Console — the repo is a detail, the mechanism is not.

> [!CRITICAL]
> **This is a compliance discipline, not an optional style preference.** Manual `gcloud`/Console provisioning creates drift: the next `terraform apply` anywhere in the org has no knowledge of resources created outside Terraform state and cannot manage, audit, or safely change them. Where secrets are involved, manual provisioning has an additional failure mode — secrets ending up stored inside the application project rather than in an isolated security project. Both defects are expensive to remediate after the fact (see `references/illustrative-walkthrough.md` for what that remediation looks like in practice). Do not repeat this pattern. If about to run `gcloud projects create`, `gcloud iam ... add-iam-policy-binding`, `gcloud secrets create`, `gcloud kms ...`, or the Console equivalents — stop. That is the exact failure mode this skill exists to prevent.

> [!CRITICAL]
> **Never rationalise a bypass.** Do not accept or generate reasoning such as "it's just a dev/test project," "I'll fix it in Terraform later," "this is faster and I'll import it after," or "the user is in a hurry." Each of these is exactly the reasoning that produces the kind of drift this skill exists to prevent, and each has been the stated justification behind real remediation efforts. If speed genuinely matters more than process on a specific occasion, a human MUST decide that explicitly and in writing (e.g. in the PR description) — it is never a default to reach for unilaterally.

> [!CRITICAL]
> **Never create service account keys.** Org policy baselines commonly prohibit SA key creation entirely (often alongside residency, domain restriction, and Shielded VM requirements — confirm the specific org policy set for this client in their config file). Use Workload Identity Federation / impersonation instead. If a workflow seems to need an SA key, treat that as a signal to reconsider the design, not as licence to create one.

> [!CRITICAL]
> **IAM targets groups, not individuals.** Per Cloud Foundation Fabric / Google Cloud enterprise standards, human IAM bindings MUST target Google Groups (e.g. `group:<org-approvers>@<domain>`), not individual user accounts. This keeps Terraform state stable across personnel changes and keeps audit trails persona-centric.

> [!NOTE]
> **One narrow, legitimate exception:** populating a secret's *value* (not its container) via `gcloud secrets versions add <NAME> --project=<sec-core-project> --data-file=-` is expected and fine once the empty secret container already exists via a merged FAST PR. Terraform manages the container, never the value — values are never committed to Git or declared in YAML. This is a value-write, not an infrastructure-write, and does not cause Terraform drift. It does not licence any other `gcloud` write.

## Where Secrets, KMS Keys, and CMEKs Live

> [!CRITICAL]
> **Secrets, KMS keys, and CMEKs must never live inside an application project.** They live exclusively in that environment's dedicated security project, following the `<ENV>-sec-core` (or `<APP_NAME>-sec-core`) naming pattern. This is a rule about *which GCP project the resource is provisioned into*, not about *which Terraform repo declares it* — see "Which Repo Owns This Resource?" below for that distinction. Secrets/keys stored inside an app project rather than an isolated security project is one of the most common — and most consequential — provisioning defects this skill exists to prevent; if this pattern is already in place, treat it as a remediation task (see "Bringing an Existing Resource Under FAST Management" below), not something to leave as-is.

The reference pattern (step by step, tokens to be filled from the client's own foundations repo layout):

1. **Define the sec-core project** at `fast/stages/2-security/datasets/classic/projects/<APP_NAME>-sec-core.yaml` (path may vary by FAST version/layout — confirm against this client's actual repo structure), parented at `$folder_ids:<security-folder-key>`. Enable only the services actually needed — for a typical app this might be just `secretmanager.googleapis.com`, `logging.googleapis.com`, `monitoring.googleapis.com`. Omit KMS/CA services entirely unless CMEK is actually required for this client/environment. Do not add KMS "just in case."
2. **Grant cross-project read access to secrets** at the project level (not per secret) via a `roles/secretmanager.secretAccessor` binding listing the runtime service account emails from the app project.
3. **Grant the app's own CI/CD service account admin rights** within sec-core additively (e.g. `roles/secretmanager.admin` to `<APP_NAME>-cicd-sa`) — additive so it does not clobber other bindings already on the project.
4. **Declare empty secret containers** (no values) in a separate dataset file at `fast/stages/2-security/datasets/classic/secrets/<APP_NAME>-secrets.yaml`, with `project_id: $project_ids:<sec-core-project-key>` and a map of `<SECRET_NAME>: {}` entries.
5. **Apply the 2-security stage before any consumer is created.** This cuts two ways: (a) apply before app-level Terraform writes secret *versions* (e.g. a generated `DATABASE_URL`) — the version-write step needs the container to exist first; (b) apply before the Cloud Run/Cloud Deploy service that *reads* the secret is created — Cloud Run reads `version: latest` at service-create time and fails outright if the container does not exist yet. This ordering gotcha is easy to hit in practice and worth calling out explicitly whenever a new secret consumer is being added.
6. **Never commit secret values to Git.** Values are populated out of band — either manually at bootstrap, or via `gcloud secrets versions add` per the exception noted above, or by app-level Terraform writing a version afterward.
7. **Consume from the app repo** by referencing the full resource path `projects/<sec-core-project-id>/secrets/<SECRET_NAME>` directly — there is no special shorthand context variable for this; it is the standard GCP secret resource path plus the project-level `secretAccessor` binding already granted in step 2.

If a detail for a specific case is not covered above (e.g. a new API needed on sec-core, or a KMS keyring requirement), do not invent a path or shortcut it via `gcloud` — follow the general FAST principle (edit the relevant stage's YAML, plan, apply, PR) and ask a human to confirm the exact file/service list if uncertain.

## Which Repo Owns This Resource?

Do not assume every GCP write belongs in `<FOUNDATIONS_REPO>`. It is normal, sanctioned practice for an app's own Terraform repo to declare real resources directly inside a foundation-owned project — including the sec-core project — provided two things both hold: the resource is genuinely scoped to that one app (not shared infrastructure), and the app's automation identity already has the necessary cross-project role, itself granted through `<FOUNDATIONS_REPO>`.

A concrete, verified pattern: an app-specific CMEK key for that app's own storage bucket can be declared as a `google_kms_key_ring` / `google_kms_crypto_key` resource inside the *app's* Terraform repo, with an explicit `project = <sec-core-project-id>` attribute pointing it at the security project — cross-project resource declaration is ordinary Terraform, not a violation. This works only because `<FOUNDATIONS_REPO>` separately granted that app's IaC-apply service account `roles/cloudkms.admin` (or equivalent) on the sec-core project. The FAST-granted role is the actual control point, not which repo's `.tf` file happens to contain the resource block.

Rule of thumb for classifying a new write:

- **Foundation-owned (→ `<FOUNDATIONS_REPO>` FAST YAML):** the project itself, org/project-level IAM grants for automation identities, shared or reserved secret containers consumed by more than one thing, the security project itself, networking backbone (shared VPC, subnets, firewall policy), org policies, API enablement on a project.
- **App-owned (→ the app's own Terraform repo, commonly using its own reusable modules):** CI/CD delivery pipelines (Cloud Build triggers, Cloud Deploy, Artifact Registry), the app's runtime services (Cloud Run, load balancers, Cloud Armor), an app-specific encryption key or bucket that is genuinely single-app-scoped, cross-project IAM member grants that consume a role already established by FAST (e.g. `secretAccessor` for a specific secret) rather than establishing the role itself.
- **When a new client/project doesn't yet have this split documented**, check `references/organisation-config.md` for their specific app-repo boundary notes, or look at how an existing resource of the same type is already handled in their repos. If there's no precedent either way, ask a human rather than guessing which repo it belongs in — guessing wrong in either direction either creates the exact drift this skill exists to prevent, or blocks a legitimate app-level change behind an unnecessary foundations PR.

> [!NOTE]
> **Default to reusing existing networking, not creating new networking.** Many FAST deployments use a hub-and-spoke shared-VPC topology (one hub VPC, one spoke VPC per environment, peered to the hub). When a new app needs network connectivity, check for this topology first — the default move is adding a subnet to the relevant environment's existing spoke, not creating a dedicated VPC for the new app. A new VPC means re-establishing peering, NAT, and PSA ranges from scratch, and drifts away from however this client's existing apps are networked. This is still a FAST YAML change either way — the point is which resource to create, not whether to go through FAST.

## Bringing an Existing (Brownfield) Resource Under FAST Management

If a GCP project, service account, IAM binding, or API enablement already exists in real GCP outside Terraform state — whether from a past incident or a legitimate one-off — it MUST be brought under Terraform management. It must never be left as unmanaged drift, and it must never be "fixed" by deleting and recreating live resources. There are two valid patterns, depending on whether the live resource's identity (project ID) can genuinely be kept.

### Pattern A — Import in place (use when the project ID itself is reusable)

1. **Write the project-factory YAML first**, as if the project were new — `fast/stages/2-project-factory/datasets/classic/projects/<name>.yaml`, starting with the schema comment `# yaml-language-server: $schema=../../../schemas/project.schema.json`, declaring `name:`, `parent: $folder_ids:<folder-key>`, `services:`, and `service_accounts:` matching the live config as closely as possible.
2. **Verify live placement before the follow-up PR.** Check which folder the project actually lives in in real GCP (`gcloud projects describe <id>` / Console — read-only, fine to use). The `parent:` in the YAML must point at where it *actually* is. Pointing at the wrong folder makes `terraform plan` show a folder **move** on apply, a real disruptive action, not a no-op. Catch and fix this in the same PR that adds the imports, before applying.
3. **Add a plain `.tf` file** alongside the project-factory stage (e.g. `<name>-imports.tf`) using Terraform's declarative `import {}` block syntax:
   ```
   import {
     to = module.factory.module.projects["<name>"].google_project.project[0]
     id = "<live-project-id>"
   }
   ```
   Add one `import` block per resource that already exists live: the project itself, each `google_project_service` (per enabled API), each `google_service_account`, each `google_project_iam_member`. Comment the file clearly as a **one-time** import, with the intended workflow (`plan` → review → `apply` → delete the file) spelled out inline.
4. **Plan with the complete FAST input set.** A partial-input plan produces spurious shared-VPC replacement diffs that look like real changes but are not — never apply from a partial-input plan.
5. **Verify the plan updates in place.** The `google_project` resource must show as updated, not destroyed/recreated. Attribute drift (e.g. `auto_create_network`, `deletion_policy`) can force a replace, which would be destructive for a brownfield adoption — if a replace shows up, stop and get human confirmation before applying.
6. **Apply, then delete the imports `.tf` file** once state is reconciled and a subsequent clean plan shows no further import/replace actions.

### Pattern B — Parallel replacement (use only when the ID cannot be reused)

Project IDs are immutable and globally unique. If the desired/live project ID is unusable for import — for example because the exact ID is already taken, or the live config diverged too far from the desired state to reconcile — the fallback is:

1. Create a **new** project under a placeholder/alternate ID via the normal project-factory YAML, replicating the old project's APIs, service accounts, and roles as closely as needed.
2. Explicitly and visibly flag the original unmanaged project for decommission in the PR description. Decommissioning is a separate, deliberate action — never assume it happens implicitly.
3. **Track the decommission to completion.** An orphaned resource with no tracked decommission step is exactly the kind of silent drift this skill exists to prevent — do not let a Pattern-B replacement quietly become a second piece of untracked drift. Log the decommission as an explicit open item (ticket, tracked TODO in the PR, whatever this client's process uses) and do not consider the remediation done until it closes.

Prefer Pattern A whenever the live project's ID and configuration are reusable. Reach for Pattern B only when they genuinely are not, and never as a shortcut to avoid the more careful import workflow.

> [!NOTE]
> **Don't assume one environment-isolation convention applies org-wide.** It's common for different apps within the same foundations repo to isolate environments differently — some split each environment into its own project with a single runtime SA, others keep one project with environment-suffixed SAs. Check how the specific app being worked on actually does it (read its existing project-factory YAML) rather than copying whatever pattern happened to be used for a different app.

For a full worked example of both patterns plus the secrets-apply-order and two-automation-identities gotchas playing out across a real PR sequence, read `references/illustrative-walkthrough.md`.

## When to Stop and Ask a Human

Per the FAST operations guide, stop and get explicit human confirmation before proceeding in these situations — do not resolve them independently, and do not treat "the plan looked mostly fine" as sufficient:

1. `terraform plan` shows destruction of any resource not explicitly asked to be removed.
2. Asked to run `terraform destroy` on any stage.
3. An error surfaces that is not covered by the relevant stage's troubleshooting notes.
4. A change would affect the org-setup stage's core automation resources (the equivalents of `iac-0`, `log-0`, `billing-0` projects or their service accounts — confirm the exact names for this client).
5. It is unclear whether a resource is foundation-owned (belongs in `<FOUNDATIONS_REPO>`) or app-owned (belongs in the app's own Terraform repo) — see "Which Repo Owns This Resource?" above. Some resource types are legitimately created directly by app-level Terraform, including inside a foundation-owned project like sec-core; others must go through `<FOUNDATIONS_REPO>`. Follow this client's existing pattern for the specific resource type; if there's no precedent, ask rather than guess.
6. Choosing between Pattern A (import) and Pattern B (parallel replacement) for a brownfield resource — this is a judgement call with real consequences (Pattern B leaves an orphaned resource that must be tracked to decommission) and must be confirmed with a human, not decided unilaterally.

If none of the above apply but there still is not a clear FAST path for a specific write (a stage, file, or field with no precedent), say so explicitly and ask, rather than falling back to `gcloud`/Console "just to unblock" the task.
