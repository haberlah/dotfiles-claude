---
name: vercel-bellaslainte-site
description: >
  Deploy and verify the Bella Sláinte marketing site (BellaSlainteSite) on Vercel.
  Use when deploying bellaslainte.com, shipping site HTML changes, checking if the
  site is live, fixing blocked Vercel deploys, linking GitHub to Vercel for
  haberlah/david-6804, or running vercel CLI against project-iw363. Triggers:
  "deploy the website", "ship BellaSlainteSite", "push site to prod", "is
  bellaslainte.com live", "Vercel blocked", "redeploy marketing site",
  /vercel-bellaslainte-site.
---

# Vercel — Bella Sláinte marketing site

Runbook for agents (Claude Code, Codex, Grok) shipping `BellaSlainteSite` to production.

## Constants

| Item | Value |
|------|--------|
| Local repo | `~/Documents/GitHub/BellaSlainteSite` |
| GitHub | `Bella-Slainte/BellaSlainteSite` |
| Production domain | https://bellaslainte.com |
| Vercel team slug | `bella-slainte` (display name: **bellamedai's projects**) |
| Vercel project | `project-iw363` |
| Vercel project URL | https://vercel.com/bella-slainte/project-iw363 |
| CLI user (David) | `david-6804` (`david@bellamed.ai`) — **Owner** on the team |
| GitHub author | `haberlah` — must be linked to the Vercel account above |
| Required GitHub check on `main` | `site-validate` (branch is protected) |
| Contact email domain (public) | `@bellaassist.au` |
| Site / brand domain | `bellaslainte.com` (do not change site URLs when editing emails) |

## Preferred production path (CLI)

Use this when content is already on `main` (or in the working tree you intend to ship) and you need a reliable prod deploy.

```bash
# 1. Auth + team
vercel whoami
# Expect: david-6804
vercel switch bella-slainte   # active team must be bella-slainte, NOT david-6804s-projects

# 2. Repo
cd ~/Documents/GitHub/BellaSlainteSite
git status
git pull origin main          # or work from the branch you mean to ship

# 3. Link once per machine (creates .vercel/ — gitignored)
# Only if not already linked:
#   vercel link --yes --scope bella-slainte
# Pick existing project-iw363 / linked by git

# 4. Production deploy
vercel deploy --prod --yes --scope bella-slainte
# Expect: ✓ Ready in a few seconds
# Expect: ▲ Aliased https://bellaslainte.com
```

### Verify live

```bash
curl -sI https://bellaslainte.com/ | grep -iE 'last-modified|x-vercel|age:'
# Emails (after contact-domain change):
curl -sL https://bellaslainte.com/ | grep -oE '[a-z.]+@bellaassist\.au' | sort -u
# Should list hello, jessica, david, michael, laura, georgia, mike, jem, peter
# Must NOT show @bellaslainte.com for contact mailto addresses
```

## GitHub → Vercel path (auto deploy)

Works only when GitHub identity is linked (see below).

1. Do **not** `git push origin main` for routine ship — `main` is protected.
2. Open a PR → wait for `site-validate` → merge (squash + `--admin` only if user asks to bypass review).
3. Vercel should create a Production deployment for the merge commit.
4. If status is **Blocked**, use the CLI path or fix identity then push a **fresh** commit via PR (blocked deploys often cannot be “Redeploy”ed).

Empty commits to trigger redeploy must go through a **branch + PR**, not direct push to `main`:

```bash
git checkout -b auto/trigger-redeploy
git commit --allow-empty -m "chore: trigger production redeploy"
git push -u origin auto/trigger-redeploy
gh pr create --base main --title "chore: trigger production redeploy" --body "Redeploy only."
# after site-validate: merge (with user approval / admin if requested)
```

## Identity: GitHub ↔ Vercel (the usual blocker)

**Symptom:** Deployment **Blocked** —

> *haberlah does not have a Vercel account linked to their GitHub account*

**Or:** GitHub integration fails; CLI deploys stuck `UNKNOWN` / not Ready; alias fails with *deployment is not ready*.

**Fix (David):**

1. Open https://vercel.com/account/settings/authentication  
2. Under **Sign-in Methods → GitHub**, ensure **`haberlah`** is connected (Last used recent).  
3. Confirm team membership: https://vercel.com/bella-slainte/~/settings/members — `david-6804` should be **Owner**.  
4. **Do not** “invite yourself” again if already Owner — that does not link GitHub.  
5. After linking, create a **new** deployment (CLI `--prod` or fresh commit). Dashboard **Redeploy** on an old blocked deployment often fails with: *This deployment can not be redeployed. Please try again from a fresh commit.*

Team members who already ship Ready prod builds: `michael-2254`, `bellamedai` — can redeploy from the dashboard if David’s identity is still broken.

## Install / auth (one-time machine setup)

```bash
brew install vercel-cli    # or: npm i -g vercel  (avoid both fighting over /opt/homebrew/bin/vercel)
vercel login              # browser device flow
vercel whoami
vercel teams ls           # must list bella-slainte
vercel switch bella-slainte
```

If CLI upgrade via npm fails with `EEXIST` on Homebrew’s binary, ignore or upgrade with `brew upgrade vercel-cli` only.

## Common traps

| Trap | What to do |
|------|------------|
| Active team is `david-6804s-projects` | `vercel switch bella-slainte` before link/deploy |
| `git push origin main` → GH006 / site-validate | Use PR or CLI deploy; never force-push around protection without explicit user ask |
| `git reset --hard origin/main # comment` | Trailing `# comment` is parsed as paths → *Cannot do hard reset with paths*. Put comments on their own line |
| Blocked deploy “Redeploy” greyed / errors | Fresh commit (PR) or `vercel deploy --prod` |
| Alias error *not ready* | Deploy never left Blocked/UNKNOWN — fix identity first |
| Changing emails | Only replace `@bellaslainte.com` in **mailto / displayed emails**; keep `https://bellaslainte.com` site URLs |
| Email signatures script | `EMAIL_DOMAIN=bellaassist.au`, `SITE_DOMAIN=bellaslainte.com` (see `scripts/make-signatures.mjs`) |
| Inspecting wrong team | Pass `--scope bella-slainte` on `vercel ls`, `inspect`, `alias`, `deploy` |

## Useful URLs

- Project: https://vercel.com/bella-slainte/project-iw363  
- Deployments: https://vercel.com/bella-slainte/project-iw363/deployments  
- Auth (link GitHub): https://vercel.com/account/settings/authentication  
- Team members: https://vercel.com/bella-slainte/~/settings/members  
- Domain: https://bellaslainte.com  

## Agent checklist before declaring “live”

1. Deploy status **Ready** (not Blocked / UNKNOWN).  
2. Output shows alias to `https://bellaslainte.com` **or** `vercel alias` / domain points at that deployment.  
3. Live curl shows expected content (emails `@bellaassist.au`, or whatever change was shipped).  
4. Report: deployment URL, inspect URL, and live verification snippet.

## Related

- Generic Vercel CLI help: Vercel plugin `vercel-cli` skill (not Bella-specific).  
- Site code reviews / PRs: `claude-pr-review` + `github-pr-review-policy` (Codex review default on PR create).
