#!/usr/bin/env bash
set -u

repo="${1:-.}"
if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is not installed or not on PATH" >&2
  exit 2
fi

if ! git -C "$repo" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "ERROR: not a git repository: $repo" >&2
  exit 2
fi

root="$(git -C "$repo" rev-parse --show-toplevel)"
cd "$root" || exit 2

echo "== Repository =="
echo "path: $root"
echo "branch: $(git branch --show-current 2>/dev/null || echo detached)"
echo "head: $(git rev-parse HEAD)"
echo "remote.origin.url: $(git remote get-url origin 2>/dev/null || echo missing)"

echo
echo "== GitHub =="
if command -v gh >/dev/null 2>&1; then
  gh_repo="$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || true)"
  default_branch="$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null || true)"
  viewer_permission="$(gh repo view --json viewerPermission --jq '.viewerPermission' 2>/dev/null || true)"
  echo "repo: ${gh_repo:-unknown}"
  echo "viewer_permission: ${viewer_permission:-unknown}"
  echo "default_branch: ${default_branch:-unknown}"
else
  gh_repo=""
  default_branch=""
  echo "gh: missing"
fi

if [ -z "${default_branch:-}" ]; then
  default_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's#^refs/remotes/origin/##')"
fi
if [ -z "${default_branch:-}" ]; then
  default_branch="main"
fi

echo
echo "== Remote sync =="
git fetch --prune origin >/dev/null 2>&1 || echo "fetch: failed"
if git rev-parse --verify "origin/$default_branch" >/dev/null 2>&1; then
  echo "origin/$default_branch: $(git rev-parse "origin/$default_branch")"
  ahead_behind="$(git rev-list --left-right --count "HEAD...origin/$default_branch" 2>/dev/null || echo "unknown unknown")"
  echo "HEAD_vs_origin_$default_branch: $ahead_behind (left=ahead, right=behind)"
else
  echo "origin/$default_branch: missing"
fi

echo
echo "== Working tree =="
status="$(git status --short)"
if [ -n "$status" ]; then
  echo "$status"
else
  echo "clean"
fi

echo
echo "== Pull request =="
if command -v gh >/dev/null 2>&1; then
  current_branch="$(git branch --show-current 2>/dev/null || true)"
  if [ -n "$current_branch" ]; then
    gh pr list --head "$current_branch" --state open --json number,title,url,headRefName,baseRefName,statusCheckRollup \
      --jq '.[] | {number, title, url, headRefName, baseRefName, checks: [.statusCheckRollup[]?.conclusion]}' 2>/dev/null || true
  else
    echo "detached HEAD; no branch PR lookup"
  fi
else
  echo "gh: missing"
fi

echo
echo "== Project hints =="
if [ -f package.json ]; then
  echo "package_manager_lockfiles: $(ls package-lock.json pnpm-lock.yaml yarn.lock bun.lockb 2>/dev/null | tr '\n' ' ')"
  if command -v node >/dev/null 2>&1; then
    node -e 'const p=require("./package.json"); for (const [k,v] of Object.entries(p.scripts||{})) console.log(`script.${k}: ${v}`)' 2>/dev/null || true
  else
    echo "node: missing"
  fi
fi

if [ -f .replit ]; then
  echo ".replit: present"
  grep -nE 'deploymentTarget|run =|build =|ISMS_AUTH_MODE|modules =|GITHUB_ALLOWED|ALLOWED_' .replit 2>/dev/null || true
else
  echo ".replit: missing"
fi

if command -v replit >/dev/null 2>&1; then
  echo "replit_cli: $(replit --version 2>/dev/null || echo present)"
else
  echo "replit_cli: missing"
fi

echo
echo "== Other local clones with same origin =="
origin_url="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$origin_url" ] || [ ! -d "$HOME/Documents" ]; then
  echo "not checked"
else
  found_clone=0
  while IFS= read -r gitdir; do
    clone="${gitdir%/.git}"
    [ "$clone" = "$root" ] && continue
    clone_origin="$(git -C "$clone" remote get-url origin 2>/dev/null || true)"
    if [ "$clone_origin" = "$origin_url" ]; then
      found_clone=1
      echo "$clone"
      echo "  branch: $(git -C "$clone" branch --show-current 2>/dev/null || echo detached)"
      echo "  head: $(git -C "$clone" rev-parse HEAD 2>/dev/null || echo unknown)"
      if git -C "$clone" rev-parse --verify "origin/$default_branch" >/dev/null 2>&1; then
        echo "  origin/$default_branch: $(git -C "$clone" rev-parse "origin/$default_branch" 2>/dev/null || echo unknown)"
        echo "  status: $(git -C "$clone" status --short --branch 2>/dev/null | head -n 1)"
      fi
    fi
  done < <(find "$HOME/Documents" -maxdepth 7 -type d -name .git -prune 2>/dev/null)
  if [ "$found_clone" -eq 0 ]; then
    echo "none found under $HOME/Documents"
  fi
fi
