# Common FAST/CFF Pitfalls

Specific technical gotchas found across real FAST deployments. Each one has tempted a "quick gcloud/Console fix" in practice — read the relevant section before assuming an error means the FAST path is broken.

## WIF / OIDC

- **Org-policy overrides for WIF providers sometimes belong on the parent folder, not the project.** If a new WIF pool/provider needs `iam.workloadIdentityPoolProviders` (or a similar constraint) allowed, and the project-factory stage's service account lacks `orgpolicy.policies.create` on projects, set the override on the parent folder in the org-setup stage instead. Setting it at the project level recreates a create-ordering deadlock between the org-policy apply and the WIF provider's own API precondition check. This is a placement decision, not a shortcut to skip.
- **WIF bindings need the project NUMBER, not the project ID.** When writing `iam.workloadIdentityUser` bindings or `principalSet://iam.googleapis.com/...` URIs for a WIF pool, resolve to the numeric project number — the API rejects the project ID with a misleading "Identity Pool does not exist" error. Treat that error as a resolution mistake in the YAML, not a signal to fix it via `gcloud`/Console.
- **A misleading "API not enabled" error under WIF may be a provider config gap, not a real missing API.** If Terraform running under a WIF-federated identity reports an API not enabled in a project that clearly has it enabled, check two things before touching any API-enablement YAML: `user_project_override = true` on the provider block, and `roles/serviceusage.serviceUsageConsumer` granted to the calling identity on the resource's actual project. The error otherwise points at the WIF pool's own project number, not the real target — don't `gcloud services enable` your way around it.
- **Two-layer WIF defense worth checking is intact:** an org-level `attribute_condition` restricting the pool to the exact GitHub org (`attribute.repository_owner=="<org>"`), plus per-identity scoping where apply-capable identities are branch-scoped (`attribute.sub` matched to `repo:<repo>:ref:refs/heads/<protected-branch>`) while plan/read-only identities can be broader (any ref, since they can't mutate state). Reviewing a proposed WIF change should check both layers, not just the provider's attribute condition.

## Certificates vs. Secrets/KMS

- **Certificate Manager does not follow the sec-core centralisation pattern.** Unlike Secret Manager and KMS (which support cross-project IAM and are correctly centralised in a shared security project), a Certificate Manager certificate, certificate map, and certificate map entry must all live in the *same* project as the target HTTPS proxy referencing them — this is a GCP API constraint, not a design choice. Don't assume "put sensitive shared infra in sec-core" extends to certs; keep them with the load balancer.

## Cross-Project Load Balancers

- **A cross-project load balancer has an org-policy prerequisite.** A serverless NEG/backend service must live in the same project as the Cloud Run service it targets, but the LB itself (IP, URL map, proxy) can live in a different project (e.g. the network host project) only under the non-Classic `EXTERNAL_MANAGED` scheme. That scheme requires `compute.restrictLoadBalancerCreationForTypes` to allow `GLOBAL_EXTERNAL_MANAGED_HTTP_HTTPS`, which must be added via the org-setup stage — never a per-project override, and never a Console org-policy edit to unblock a stuck LB creation.

## Cloud SQL Private Connectivity

- **Confirm PSA vs. PSC before adding Cloud SQL private connectivity — they are mutually exclusive per VPC and declared in different files.** Standalone-VPC apps typically use Private Service Access (a reserved range declared in the VPC's own config file). Shared-VPC hub-and-spoke apps typically use Private Service Connect (a per-instance service-attachment declared in that VPC's addresses file). Determine which pattern the target VPC already uses before editing either — adding a PSC address to a PSA-based VPC (or vice versa) is a common mismatch.

## Secret Manager

- **`gcloud secrets list` without a location silently omits regional secrets — do not conclude "container missing" from the global list alone.** Regional secrets (`location:` set in the secrets-factory YAML) live under `projects/P/locations/L/secrets/S` and are only visible via the location-specific API (`gcloud secrets list --location=L` on a current CLI, or the regional REST endpoint `https://secretmanager.<location>.rep.googleapis.com/v1/...` on older CLIs). A "declared 9, live shows 5" comparison built on the global list can manufacture phantom drift and trigger unnecessary remediation work — always check both surfaces before declaring declared-vs-applied drift for secrets.

## "Is This Resource Idle?" Before Decommission

- **Raw `request_count` conflates control-plane with data-plane — break it down by caller before declaring a resource idle OR in-use.** A service's API request metric counts management/list/describe calls (control-plane) alongside real data operations (data-plane). An auditor or agent verifying "is this idle?" generates control-plane traffic themselves, so a nonzero count can be entirely self-inflicted. Conversely, a coarse "zero traffic" claim can miss a real consumer. Break the metric down by `credential_id` (or method): traffic authenticating as `oauth2:32555940559.apps.googleusercontent.com` is the gcloud CLI (a human/agent verifying), not an app; a live consumer authenticates as a service account calling a data-plane method (e.g. `Process`/`BatchProcess`, not `List`/`Get`). Only the latter should block a decommission. State the caller breakdown as the evidence, never the bare count.

## Brownfield Imports

- **Two specific things to check on every brownfield import plan before applying:** (1) the target resource plans as an in-place update, not a REPLACE (common causes: attributes like `auto_create_network`/`deletion_policy` drifting from the live resource's actual state) — never apply a replace on a live brownfield resource without explicit human sign-off; (2) the `for_each` key in the import's `to =` address actually matches the module's naming convention — cross-check against `terraform state list` of an already-imported sibling resource if unsure.

## Reviewing Terraform PRs for This Kind of Repo

- **Red flags checklist before approving a landing-zone Terraform PR:** (1) a tfvars value contradicting its own README/variable-documented gate or sequencing; (2) a known module/provider lifecycle bug around update-in-place (e.g. an attribute silently ignored on update); (3) a resource that can come up before a dependency it needs is actually ready (e.g. a minimum-instance count racing secret version creation); (4) IAM incomplete for an API the config calls; (5) an output whose actual shape doesn't match its documented contract; (6) a failing or absent CI plan check. Any one of these is grounds to close the PR and restart from a clean branch rather than merge and patch forward.
- **Flag topology departures explicitly, don't bury them.** When a per-app Terraform root makes a deliberate blast-radius/isolation tradeoff that diverges from how sibling apps are structured (e.g. no VPC because the app has no private backend, or one project instead of one-per-environment), call it out as a named, reversible decision block in the PR description or README — state the tradeoff and how to reverse it — rather than letting a reviewer discover the divergence by diffing against a different app.

## Auditing Whether the FAST Boundary Is Actually Enforced

- **A clean Terraform history doesn't mean the boundary is enforced at the IAM layer.** Before trusting that "everything goes through Terraform+PR" for a given client, check whether any human group or individual user holds `roles/owner`, `roles/resourcemanager.organizationAdmin`, `roles/resourcemanager.projectCreator`, `roles/resourcemanager.projectDeleter`, or `roles/orgpolicy.policyAdmin` directly at the organization level (`gcloud organizations get-iam-policy <org-id>`). If any human principal holds these, standing bypass capability exists regardless of how disciplined the Terraform has been so far — flag this ahead of, not instead of, remediating any individual drifted resource found. This is the single highest-leverage thing to check on a new engagement.
