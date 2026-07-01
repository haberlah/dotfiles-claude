# Bella Sláinte — Organisation Configuration (INTERNAL ONLY — do not ship to Aviato or other clients)

> This file contains real Bella Sláinte project names, service account names, PR numbers, and incident dates. It is the filled-in instance of `references/organisation-config.TEMPLATE.md` for internal/local use with the `fast-provisioning-guardrail` skill. Do not copy this file's contents into the shareable Aviato skill package or into any other client's config.

## 1. Foundations Repository

- **Foundations repo path:** `Bella-Slainte/bella-gcp-foundations`
- **FAST version / layout in use:** Cloud Foundation Fabric FAST, standard stage numbering (`0-org-setup`, `1-resman`, `2-project-factory`, `2-security`, `2-networking`, etc.)
- **Stage directory layout confirmed?** Yes — standard layout, no deviations noted in the source material reviewed.
- **PR review requirements:** Not specified in source material — confirm with David/Aviato before relying on this.

## 2. Naming Conventions

- **Org/project-prefix convention:** `bellamed-` for application projects (e.g. `bellamed-glassbox`, `bellamed-mountwinter-isms-2`, `bellamed-bella-assist-dev`).
- **Application naming pattern:** `bellamed-<app-name>`, or `bellamed-bella-assist-<env>` for the main app's per-environment projects.
- **Folder structure keys (verified directly against `fast/stages/2-project-factory/datasets/classic/projects/*.yaml`, 2026-07-01):**
  - Root product folder: `bellamed-product1`
  - Dev: `bellamed-product1/dev` (project `bella-assist-dev`)
  - Stage: `bellamed-product1/test` — note the environment is called "stage" but the folder key is `test`, not `stage`; don't assume they match
  - Vibe: `bellamed-product1/vibe` (project `bella-assist-vibe`)
  - Prod: `bellamed-product1/prod` (project `bella-assist-prod`)
  - Incident-remediated projects (glassbox, mountwinter-isms-2) are parented directly at the `bellamed-product1` root, not under an env sub-folder — they sit outside the dev/test/vibe/prod pipeline.
  - CI/CD project (`bella-assist-cicd`): `fldr-common/fldr-ops`
  - Security/sec-core projects: `fldr-common/fldr-security`
- **Two different per-environment SA strategies coexist:** the main `bella-assist-*` app splits environments across separate *projects*, each with a single `app-sa` (e.g. "Bella Assist app runtime (prod)"). Mountwinter-isms-2 instead keeps all environments in *one* project with env-suffixed SAs (`mountwinter-app-dev/stage/prod`, per PR #56's description) alongside `mountwinter-cicd-sa`. Don't assume one pattern applies to a new app without checking which style it's following.
- **Per-project Terraform state buckets:** each `bella-assist-*` env project declares its own `buckets: tf-state<env>bucket: {}` (e.g. `tf-stateprodbucket`) — this is the app's own Terraform state storage, declared in the foundations repo's project YAML but used by `bella-assist-terraform`, not by FAST itself.
- **`defaults.yaml` location:** `fast/stages/0-org-setup/datasets/classic/defaults.yaml`, not under `2-project-factory` — don't look for it in the project-factory dataset folder.

## 3. Security / Secrets Isolation

- **Sec-core naming pattern:** `<app>-sec-core`, e.g. `mountwinter-sec-core`. Bella-assist sec-core projects follow the same pattern.
- **Default services enabled on sec-core:** `secretmanager.googleapis.com`, `logging.googleapis.com`, `monitoring.googleapis.com`. Mountwinter's sec-core deliberately omits KMS/CA services (Google-managed encryption only). Note: the bella-assist sec-core projects carry KMS/CA services and key-delegation bindings — CMEK usage differs by app within Bella Sláinte, not uniformly on or off.
- **Does this client use CMEK/KMS?** Mixed — Mountwinter: no (Google-managed encryption). Bella-assist family: yes (KMS/CA services and key-delegation bindings present). Confirm per app before assuming either default.
- **Secret-container dataset path pattern:** `fast/stages/2-security/datasets/classic/secrets/<app>-secrets.yaml`, e.g. `mountwinter-secrets.yaml` containing `DATABASE_URL-*`, `CLOUDSQL_SERVER_CA-*`, `AUTH_*`, and later `ANTHROPIC_API_KEY`.
- **Cross-project secret access pattern:** project-level `roles/secretmanager.secretAccessor` binding listing runtime SA emails (not per-secret bindings). Additive `roles/secretmanager.admin` granted to the app's CI/CD SA (e.g. `mountwinter-cicd-sa`).

## 4. Automation Identities

- **IaC-apply service account naming pattern:** `bellamed-iac-tf-sa` — the Terraform-apply automation SA used by the `bella-assist-terraform` CI/CD pipeline.
- **Release/deploy service account naming pattern:** `<app>-cicd-sa`, e.g. `mountwinter-cicd-sa` — the app's release/deploy pipeline SA, distinct from the IaC-apply SA above.
- **Confirmed: both identities' roles are declared in FAST, never granted ad hoc?** Yes, per the Mountwinter remediation (PR #59 fixed the IaC-apply SA's missing roles; PR #62 fixed the release SA's missing `actAs` roles) — this was the explicit lesson the original incident produced.

## 5. Org Policy Baseline

- **SA key creation prohibited?** Yes.
- **Domain-restricted sharing enforced?** Yes — public/invoker (`allUsers`) access is granted via a `tag_bindings:` entry binding a pre-existing conditional tag (PR #64), never by editing the org policy directly.
- **Data residency requirement?** AU residency (stated as part of the org policy baseline alongside SA-key prohibition, domain restriction, and Shielded VM requirements). Specific region not detailed in source material.
- **Shielded VM / other compute baseline requirements?** Shielded VM required, per the org policy baseline statement in source material. No further detail given.

## 6. Core Automation Resources (Do-Not-Touch List)

- Org-setup stage core projects/SAs requiring human confirmation before any change: `iac-0`, `log-0`, `billing-0` projects and their service accounts (0-org-setup stage).

## 6a. Networking (Hub-and-Spoke, Verified 2026-07-01)

- **Topology:** hub-and-spoke shared VPC, declared at `fast/stages/2-networking/datasets/hub-and-spokes-peerings/vpcs/`. Hub project `net-core-0` hosts `bellamed-assist-vpc-hub-0`. Spoke projects: `net-dev-0`, `net-test-0` (the "stage" env's networking spoke — again note env name ≠ folder/project key), `net-vibe-0`, `net-prod-0`, each hosting its own `bellamed-assist-vpc-<env>-0` peered back to the hub.
- **Mountwinter reused the existing prod spoke, not a new VPC.** `mountwinter-default` (10.30.1.0/24, `australia-southeast2`) is declared as a subnet file at `fast/stages/2-networking/datasets/hub-and-spokes-peerings/vpcs/prod/subnets/mountwinter-default.yaml`, alongside the pre-existing `prod-default` (10.30.0.0/24) subnet — PR #55. This is the correct pattern verified directly in both the live GCP console and the repo: a new app joining an existing environment gets a new subnet in that environment's spoke, not a dedicated VPC.
- **PSA (Private Service Access) range for prod:** `10.72.224.0/24`, declared in the prod spoke's `.config.yaml` (`psa_configs.ranges`), with `peered_domains: ["test."]`. This range is what allows Cloud SQL private-IP instances in prod-adjacent projects to be provisioned — a prerequisite for any new Cloud SQL instance, analogous to the secrets apply-order gotcha: the PSA range must exist before a private-IP Cloud SQL instance can be created against it.
- **Reserved proxy-only subnet for the regional external LB:** `prod-proxy`, `10.72.240.0/24`, role `ACTIVE`, purpose `REGIONAL_MANAGED_PROXY` — required for the external Application Load Balancer fronting Cloud Run services in prod.
- **DNS zones per environment** live at `fast/stages/2-networking/datasets/hub-and-spokes-peerings/dns/zones/{net-core-0,net-dev-0,net-prod-0,net-test-0,net-vibe-0}/` — per-spoke private zones, maintained by Aviato (Brett).

## 7. App-Repo Boundary

- **App-owned Terraform repo(s):** `bella-assist-terraform` (covers bella-assist and Mountwinter). Ships its own reusable modules under `modules/`: `artifact-registry`, `cloud-deploy`, `cloudbuild-trigger`, `cloud-run-v2`, `cloudsql-instance`, `cloud-armor`, `net-lb-app-ext`, `net-address`, `certificate-manager`, `monitoring-alerts`.
- **Verified app-owned resource types (created directly by `bella-assist-terraform`, not by FAST YAML):** Artifact Registry repos (with cross-project `artifactregistry.reader` grants to each env's `serverless-robot-prod` service agent for image pulls), Cloud Deploy pipelines/targets, Cloud Run services, Cloud Build triggers, load balancers + Cloud Armor policies, certificate management, monitoring alerts, and — notably — **per-app CMEK key rings/crypto keys for that app's own GCS bucket**, declared as `google_kms_key_ring`/`google_kms_crypto_key` resources with an explicit `project = <sec_core_project>` attribute pointing into the environment's sec-core project (`terraform/main.tf`, `object_storage` resources, keyed by env via a `cloud_run_services` map that carries `sec_core_project` per entry). This works only because PR #49 (`bella-gcp-foundations`) granted `bellamed-iac-tf-sa` `secretmanager.admin`/KMS-equivalent roles on the sec-core projects — the app repo can create resources there, but only within the role FAST already granted.
- **What still goes through `bella-gcp-foundations` FAST YAML regardless:** the app projects themselves (`bella-assist-{dev,stage,vibe,prod}`, `bellamed-glassbox`, `bellamed-mountwinter-isms-2`), the sec-core projects themselves, project-level IAM grants for the automation identities (`bellamed-iac-tf-sa` in `cicd.yaml`, per-app `*-cicd-sa` `iam_self_roles`), shared/reserved secret containers (`DATABASE_URL-*`, `AUTH_*`, `ANTHROPIC_API_KEY`), networking backbone (shared VPC host projects, subnets), and org policy tag bindings (`allow-allusers-iam`).
- **Folder note:** `bella-assist-terraform`'s own repo also contains per-app subdirectories (`terraform/mountwinter/`, `terraform/glassbox/`) with their own `main.tf`/`backend.tf` — confirm which one is authoritative for a given app before editing; don't assume the root `terraform/main.tf` covers everything.

## 8. Historical Remediation Example — Full Real Worked Example (2026-06-29 Incident)

**Before (the violation):** both `bella-assist-glassbox` and `mountwinter-isms-compliance` (project `bellamed-mountwinter-isms-2`) were provisioned by running `gcloud` commands / Console clicks directly against the org — creating the projects, enabling APIs, and binding IAM by hand. No YAML existed in `bella-gcp-foundations`; Terraform had never heard of either project. This is drift by definition: the next `terraform apply` anywhere in the org had no knowledge of these projects' existence and could not manage, audit, or safely change them. Aviato detected this independently and issued a hard halt on all deployments (2026-06-29) until it was resolved. Secrets for `bellamed-glassbox` were also found stored inside the app project itself rather than a security project — the second declared compliance gap from the same incident.

**After (the remediation, PRs #54–#64):**

- **PR #54** — added the `bellamed-glassbox` project-factory YAML as a starting point.
- **PR #56** — two different fixes landed together: **glassbox** got a genuine `terraform import` (Pattern A, `glassbox-imports.tf`, with the `parent:` folder corrected — first-pass YAML pointed at a `prod` sub-folder, but the live project was actually parented at the root folder); **mountwinter** got a **parallel replacement** project, `mountwinter-isms-2` (Pattern B), because the original project ID (`bellamed-mountwinter-isms`) was already in use and not cleanly reusable — the original project was left unmanaged, with decommissioning still outstanding as of the source material's writing.
- **PR #57** — created `mountwinter-sec-core` under `fldr-common/fldr-security` (Google-managed encryption, no KMS), granting cross-project `secretAccessor` to the runtime SAs and additive `secretmanager.admin` to `mountwinter-cicd-sa`.
- **PR #58** — declared the empty secret containers (`DATABASE_URL-*`, `CLOUDSQL_SERVER_CA-*`, `AUTH_*`) in `mountwinter-secrets.yaml` inside the new sec-core project, applied *before* the app-level Terraform in `bella-assist-terraform` wrote any secret versions.
- **PR #59** — granted `bellamed-iac-tf-sa` (the Terraform-apply automation SA used by the `bella-assist-terraform` CI/CD pipeline — distinct from the app's own release SA below) an `iam_project_roles` entry on the new project in `cicd.yaml`, because that automation account had zero permissions there and its `terraform apply` was failing outright trying to create the Artifact Registry repo, Cloud SQL instance, and monitoring resources. This produced the "two automation identities" lesson: the account that runs `terraform apply` for an app's own IaC and the account that runs the app's release/deploy pipeline are two different service accounts, and both need their roles declared in FAST — never granted ad hoc to unblock a failing apply.
- **PR #60** — added `servicenetworking.googleapis.com` / `sqladmin.googleapis.com` to the project's `services:` list (for Cloud SQL PSA) instead of `gcloud services enable`.
- **PR #61** — granted `compute.networkUser` on the specific subnet to the literal Cloud Run serverless-robot service-agent identity, declared in the 2-networking stage YAML.
- **PR #62** — granted the app's *release* SA, `mountwinter-cicd-sa`, `roles/iam.serviceAccountUser` (`actAs`) on the runtime SAs and on itself, needed for the Cloud Deploy pipeline to deploy revisions as those SAs — the release-pipeline counterpart to the IaC-pipeline fix in PR #59.
- **PR #63** — declared the `ANTHROPIC_API_KEY` secret container in the same sec-core secrets dataset, after a Cloud Run service failed to start because it referenced a secret whose container had not been declared yet — reinforcing the apply-order rule in section 3 above.
- **PR #64** — added a `tag_bindings:` entry to allow `allUsers` invoker access under the org's Domain Restricted Sharing policy, by binding the pre-existing conditional tag rather than editing the org policy directly.

**Outstanding as of source material:** the original `bellamed-mountwinter-isms` project (superseded by `mountwinter-isms-2` under Pattern B) has not yet been decommissioned. This is flagged in the skill as an example of Pattern-B risk — track this to closure; do not let it become permanent silent drift.

Every one of these PRs was a YAML edit plus `terraform plan`/`apply` plus PR. None was a `gcloud` write or a Console click.
