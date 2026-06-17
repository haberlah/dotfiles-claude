#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  gws_auth_preset.sh <preset[,preset...]> [--print] [--login] [--allow-large]

Examples:
  gws_auth_preset.sh workspace-core --print
  gws_auth_preset.sh workspace-core
  gws_auth_preset.sh gmail,chat-user --print

Presets:
  workspace-core
  drive-backup
  readonly
  gmail
  chat-user
  chat-admin
  meet
  script
  admin-directory
  classroom
  cloud-identity-admin
  cloud-platform

Default mode is --login. Use --print to emit the comma-separated scope list.
USAGE
}

mode="login"
allow_large=0
presets=()
scopes=()

add_scope() {
  local scope="$1"
  local existing
  if [[ ${#scopes[@]} -gt 0 ]]; then
    for existing in "${scopes[@]}"; do
      [[ "$existing" == "$scope" ]] && return 0
    done
  fi
  scopes+=("$scope")
}

add_identity() {
  add_scope "openid"
  add_scope "https://www.googleapis.com/auth/userinfo.email"
  add_scope "https://www.googleapis.com/auth/userinfo.profile"
}

add_preset() {
  local preset="$1"
  case "$preset" in
    workspace-core)
      add_identity
      add_scope "https://www.googleapis.com/auth/drive"
      add_scope "https://www.googleapis.com/auth/gmail.modify"
      add_scope "https://www.googleapis.com/auth/gmail.send"
      add_scope "https://www.googleapis.com/auth/gmail.compose"
      add_scope "https://www.googleapis.com/auth/calendar"
      add_scope "https://www.googleapis.com/auth/documents"
      add_scope "https://www.googleapis.com/auth/spreadsheets"
      add_scope "https://www.googleapis.com/auth/presentations"
      add_scope "https://www.googleapis.com/auth/tasks"
      add_scope "https://www.googleapis.com/auth/contacts"
      add_scope "https://www.googleapis.com/auth/chat.messages"
      add_scope "https://www.googleapis.com/auth/chat.spaces"
      add_scope "https://www.googleapis.com/auth/chat.memberships"
      add_scope "https://www.googleapis.com/auth/chat.delete"
      add_scope "https://www.googleapis.com/auth/forms"
      add_scope "https://www.googleapis.com/auth/meetings.space.created"
      add_scope "https://www.googleapis.com/auth/meetings.space.readonly"
      add_scope "https://www.googleapis.com/auth/script.projects"
      ;;
    drive-backup)
      add_identity
      add_scope "https://www.googleapis.com/auth/drive"
      ;;
    readonly)
      add_identity
      add_scope "https://www.googleapis.com/auth/drive.readonly"
      add_scope "https://www.googleapis.com/auth/gmail.readonly"
      add_scope "https://www.googleapis.com/auth/calendar.readonly"
      add_scope "https://www.googleapis.com/auth/documents.readonly"
      add_scope "https://www.googleapis.com/auth/spreadsheets.readonly"
      add_scope "https://www.googleapis.com/auth/presentations.readonly"
      add_scope "https://www.googleapis.com/auth/tasks.readonly"
      add_scope "https://www.googleapis.com/auth/contacts.readonly"
      ;;
    gmail)
      add_identity
      add_scope "https://www.googleapis.com/auth/gmail.modify"
      add_scope "https://www.googleapis.com/auth/gmail.send"
      add_scope "https://www.googleapis.com/auth/gmail.compose"
      add_scope "https://www.googleapis.com/auth/gmail.labels"
      add_scope "https://www.googleapis.com/auth/gmail.settings.basic"
      ;;
    chat-user)
      add_identity
      add_scope "https://www.googleapis.com/auth/chat.messages"
      add_scope "https://www.googleapis.com/auth/chat.spaces"
      add_scope "https://www.googleapis.com/auth/chat.memberships"
      add_scope "https://www.googleapis.com/auth/chat.delete"
      add_scope "https://www.googleapis.com/auth/chat.customemojis"
      add_scope "https://www.googleapis.com/auth/chat.users.readstate"
      add_scope "https://www.googleapis.com/auth/chat.users.spacesettings"
      add_scope "https://www.googleapis.com/auth/chat.users.sections"
      ;;
    chat-admin)
      add_identity
      add_scope "https://www.googleapis.com/auth/chat.admin.delete"
      add_scope "https://www.googleapis.com/auth/chat.admin.memberships"
      add_scope "https://www.googleapis.com/auth/chat.admin.spaces"
      add_scope "https://www.googleapis.com/auth/chat.messages"
      add_scope "https://www.googleapis.com/auth/chat.spaces"
      add_scope "https://www.googleapis.com/auth/chat.memberships"
      ;;
    meet)
      add_identity
      add_scope "https://www.googleapis.com/auth/meetings.space.created"
      add_scope "https://www.googleapis.com/auth/meetings.space.readonly"
      add_scope "https://www.googleapis.com/auth/meetings.space.settings"
      ;;
    script)
      add_identity
      add_scope "https://www.googleapis.com/auth/script.projects"
      add_scope "https://www.googleapis.com/auth/script.deployments"
      add_scope "https://www.googleapis.com/auth/script.processes"
      add_scope "https://www.googleapis.com/auth/script.metrics"
      ;;
    admin-directory)
      add_identity
      add_scope "https://www.googleapis.com/auth/admin.directory.customer"
      add_scope "https://www.googleapis.com/auth/admin.directory.device.chromeos"
      add_scope "https://www.googleapis.com/auth/admin.directory.device.mobile"
      add_scope "https://www.googleapis.com/auth/admin.directory.domain"
      add_scope "https://www.googleapis.com/auth/admin.directory.group"
      add_scope "https://www.googleapis.com/auth/admin.directory.orgunit"
      add_scope "https://www.googleapis.com/auth/admin.directory.resource.calendar"
      add_scope "https://www.googleapis.com/auth/admin.directory.rolemanagement"
      add_scope "https://www.googleapis.com/auth/admin.directory.user"
      add_scope "https://www.googleapis.com/auth/admin.directory.userschema"
      add_scope "https://www.googleapis.com/auth/directory.readonly"
      add_scope "https://www.googleapis.com/auth/groups"
      ;;
    classroom)
      add_identity
      add_scope "https://www.googleapis.com/auth/classroom.addons.student"
      add_scope "https://www.googleapis.com/auth/classroom.addons.teacher"
      add_scope "https://www.googleapis.com/auth/classroom.announcements"
      add_scope "https://www.googleapis.com/auth/classroom.courses"
      add_scope "https://www.googleapis.com/auth/classroom.coursework.me"
      add_scope "https://www.googleapis.com/auth/classroom.coursework.students"
      add_scope "https://www.googleapis.com/auth/classroom.courseworkmaterials"
      add_scope "https://www.googleapis.com/auth/classroom.guardianlinks.me.readonly"
      add_scope "https://www.googleapis.com/auth/classroom.guardianlinks.students"
      add_scope "https://www.googleapis.com/auth/classroom.profile.emails"
      add_scope "https://www.googleapis.com/auth/classroom.profile.photos"
      add_scope "https://www.googleapis.com/auth/classroom.push-notifications"
      add_scope "https://www.googleapis.com/auth/classroom.rosters"
      add_scope "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly"
      add_scope "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly"
      add_scope "https://www.googleapis.com/auth/classroom.topics"
      ;;
    cloud-identity-admin)
      add_identity
      add_scope "https://www.googleapis.com/auth/cloud-identity.devices.lookup"
      add_scope "https://www.googleapis.com/auth/cloud-identity.groups"
      add_scope "https://www.googleapis.com/auth/cloud-identity.groups.readonly"
      add_scope "https://www.googleapis.com/auth/cloud-identity.inboundsso"
      add_scope "https://www.googleapis.com/auth/cloud-identity.inboundsso.readonly"
      add_scope "https://www.googleapis.com/auth/cloud-identity.policies"
      add_scope "https://www.googleapis.com/auth/cloud-identity.policies.readonly"
      ;;
    cloud-platform)
      add_identity
      add_scope "https://www.googleapis.com/auth/cloud-platform"
      ;;
    cloud-identity-devices|devices|full|all)
      echo "Refusing preset '$preset': do not request full cloud-identity.devices or all scopes through interactive OAuth." >&2
      echo "Use Cloud Identity Devices API with service account domain-wide delegation instead." >&2
      exit 2
      ;;
    "")
      ;;
    *)
      echo "Unknown preset: $preset" >&2
      usage >&2
      exit 2
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --print)
      mode="print"
      shift
      ;;
    --login)
      mode="login"
      shift
      ;;
    --allow-large)
      allow_large=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      IFS=',' read -r -a parts <<< "$1"
      for part in "${parts[@]}"; do
        presets+=("$part")
      done
      shift
      ;;
  esac
done

if [[ ${#presets[@]} -eq 0 ]]; then
  presets=("workspace-core")
fi

for preset in "${presets[@]}"; do
  add_preset "$preset"
done

for scope in "${scopes[@]}"; do
  if [[ "$scope" == "https://www.googleapis.com/auth/cloud-identity.devices" ]]; then
    echo "Refusing full Cloud Identity Devices scope in interactive OAuth." >&2
    exit 2
  fi
done

scope_count=${#scopes[@]}
if [[ "$allow_large" -ne 1 && "$scope_count" -gt 24 ]]; then
  echo "Preset combination resolves to $scope_count scopes." >&2
  echo "Unverified/testing OAuth apps commonly fail around 25 scopes; use a narrower preset or pass --allow-large to try anyway." >&2
  exit 2
fi

joined=""
for scope in "${scopes[@]}"; do
  if [[ -z "$joined" ]]; then
    joined="$scope"
  else
    joined="$joined,$scope"
  fi
done

if [[ "$mode" == "print" ]]; then
  echo "$joined"
  exit 0
fi

if ! command -v gws >/dev/null 2>&1; then
  echo "gws is not on PATH." >&2
  exit 127
fi

echo "Starting gws auth login with $scope_count scopes from preset(s): ${presets[*]}" >&2
exec gws auth login --scopes "$joined"
