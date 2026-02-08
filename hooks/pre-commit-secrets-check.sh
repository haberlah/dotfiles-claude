#!/bin/bash
# Pre-commit hook for dotfiles-claude repo.
# Scans staged files for secrets, credentials, and sensitive data
# before allowing a commit to the (potentially public) repository.

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BLOCKED=0

# Patterns that indicate secrets or credentials
SECRET_PATTERNS=(
  # Google session cookies
  'APISID'
  'SAPISID'
  'SSID'
  '__Secure-[0-9]P'
  # Anthropic
  'sk-ant-[a-zA-Z0-9]'
  # Generic secret keys
  'sk-[a-zA-Z0-9]{20,}'
  # GitHub tokens
  'ghp_[a-zA-Z0-9]{36}'
  'gho_[a-zA-Z0-9]{36}'
  # Slack tokens
  'xox[bpors]-[a-zA-Z0-9]'
  # AWS
  'AKIA[0-9A-Z]{16}'
  # JWTs
  'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*'
  # Stripe
  'sk_live_[a-zA-Z0-9]{24,}'
  'pk_live_[a-zA-Z0-9]{24,}'
  # npm / PyPI / Vercel tokens
  'npm_[a-zA-Z0-9]{36}'
  'pypi-[a-zA-Z0-9]{50,}'
  'vercel_[a-zA-Z0-9]{24}'
  # SendGrid
  'SG\.[a-zA-Z0-9]{22}\.'
  # Google Cloud service accounts
  '"type":\s*"service_account"'
  # Browser cookies and sessions
  '"cookie"'
  '"cookies"'
  'httpOnly.*true'
  # Passwords and auth
  'password.*=.*[^$]'
  'bearer [a-zA-Z0-9_-]'
  'token":\s*"[a-zA-Z0-9_-]{20,}'
  'secret":\s*"[a-zA-Z0-9_-]{10,}'
  'api_key":\s*"[a-zA-Z0-9_-]{10,}'
  # Private keys
  'private_key'
  'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY'
)

# File patterns that should never be committed
DANGEROUS_FILES=(
  'state.json'
  'auth_info.json'
  '.env'
  '.env.*'
  'credentials.json'
  'token.json'
  'keyfile.json'
  '*.pem'
  '*.key'
  '*.p12'
  '*.pfx'
  '*.jks'
  'id_rsa'
  'id_ed25519'
  '.npmrc'
  '.pypirc'
)

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

# Check for dangerous file names
for pattern in "${DANGEROUS_FILES[@]}"; do
  matches=$(echo "$STAGED_FILES" | grep -E "(^|/)${pattern}$" 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo -e "${RED}BLOCKED:${NC} Potentially sensitive file staged for commit:"
    echo "  $matches"
    BLOCKED=1
  fi
done

# Check staged content for secret patterns (exclude this hook script itself and README)
for pattern in "${SECRET_PATTERNS[@]}"; do
  matches=$(git diff --cached -U0 --no-color -- . ':!hooks/pre-commit-secrets-check.sh' ':!README.md' 2>/dev/null | grep -iE "^\+" | grep -iE "$pattern" 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo -e "${RED}BLOCKED:${NC} Potential secret detected (pattern: ${pattern}):"
    echo "$matches" | head -3 | while read -r line; do
      # Truncate long lines to avoid dumping full secrets
      echo "  ${line:0:100}..."
    done
    BLOCKED=1
  fi
done

if [ "$BLOCKED" -eq 1 ]; then
  echo ""
  echo -e "${YELLOW}Commit blocked to protect against leaking secrets to a public repo.${NC}"
  echo "If this is a false positive, commit with: git commit --no-verify"
  exit 1
fi

exit 0
