#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DISTILL_STOP_HOOK="/Users/norven/.claude/skills/distill/scripts/distill-stop-hook.sh"
INSTRUCTION_FILES=(
    "$REPO_ROOT/AGENTS.md"
    "$REPO_ROOT/.github/copilot-instructions.md"
    "$REPO_ROOT/.github/instructions/distill-closeout.instructions.md"
)

if ! command -v copilot >/dev/null 2>&1; then
    echo "copilot command not found in PATH" >&2
    exit 127
fi

if [ -z "${VAULT_PATH:-}" ] && [ -z "${DISTILL_PATH:-}" ]; then
    export VAULT_PATH="$REPO_ROOT"
fi
export DISTILL_CLOSEOUT_REPO_SCOPE="$REPO_ROOT"

hook_status=0
instruction_drift_status=0

instruction_digest() {
    python3 - "$@" <<'PY'
import hashlib
import pathlib
import sys

hasher = hashlib.sha256()
for raw_path in sys.argv[1:]:
    path = pathlib.Path(raw_path)
    hasher.update(str(path).encode("utf-8"))
    hasher.update(b"\0")
    if path.exists():
        hasher.update(b"1\0")
        hasher.update(path.read_bytes())
    else:
        hasher.update(b"0\0")
print(hasher.hexdigest())
PY
}

SESSION_INSTRUCTION_DIGEST="$(instruction_digest "${INSTRUCTION_FILES[@]}")"

run_session_end_hook() {
    local prior_status=$1
    local current_instruction_digest

    current_instruction_digest="$(instruction_digest "${INSTRUCTION_FILES[@]}")"
    if [ "$current_instruction_digest" != "$SESSION_INSTRUCTION_DIGEST" ]; then
        instruction_drift_status=1
        echo "Repository Copilot instruction files changed during this session. Restart with bash scripts/copilot-distill-session.sh so the latest Distill closeout rules take effect." >&2
    fi

    set +e
    bash "$DISTILL_STOP_HOOK" SessionEnd
    hook_status=$?
    set -e

    if [ "$hook_status" -ne 0 ]; then
        echo "Distill SessionEnd hook reported open closeout debt or batch validation failure." >&2
    fi

    if [ "$prior_status" -ne 0 ]; then
        return "$prior_status"
    fi

    if [ "$instruction_drift_status" -ne 0 ]; then
        return "$instruction_drift_status"
    fi

    return "$hook_status"
}

trap 'status=$?; trap - EXIT; run_session_end_hook "$status"; exit $?' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

copilot "$@"
