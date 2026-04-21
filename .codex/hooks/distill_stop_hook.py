#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


DISTILL_STOP_HOOK = Path("/Users/norven/.claude/skills/distill/scripts/distill-stop-hook.sh")


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def load_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw_stdin": raw}


def resolve_repo_root(cwd: str | None) -> str:
    candidate = Path(cwd or os.getcwd()).expanduser()
    try:
        completed = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        root = completed.stdout.strip()
        if root:
            return str(Path(root).resolve())
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return str(candidate.resolve())


def compact_output(stdout: str, stderr: str) -> str:
    parts = []
    if stdout.strip():
        parts.append("stdout:\n" + stdout.strip())
    if stderr.strip():
        parts.append("stderr:\n" + stderr.strip())
    return "\n\n".join(parts).strip()


def main() -> int:
    event = load_event()
    repo_root = resolve_repo_root(event.get("cwd"))
    env = os.environ.copy()
    env["DISTILL_CLOSEOUT_REPO_SCOPE"] = repo_root
    env["VAULT_PATH"] = repo_root
    env["DISTILL_PATH"] = str(Path(repo_root) / "Distill")

    try:
        completed = subprocess.run(
            ["bash", str(DISTILL_STOP_HOOK), "Stop"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=115,
        )
    except subprocess.TimeoutExpired as exc:
        reason = "Distill Stop hook timed out before closeout verification finished."
        if exc.stdout:
            reason += "\nstdout:\n" + exc.stdout.strip()
        if exc.stderr:
            reason += "\nstderr:\n" + exc.stderr.strip()
        emit(
            {
                "decision": "block",
                "reason": reason[:4000],
                "systemMessage": "Distill closeout gate timed out; continue and surface the failure.",
            }
        )
        return 0

    if completed.returncode == 0:
        emit({"continue": True})
        return 0

    details = compact_output(completed.stdout, completed.stderr)
    reason = "\n".join(
        [
            "Distill closeout gate failed before Codex stopped.",
            f"repo: {repo_root}",
            "Action: inspect open closeout debt, review gate, or batch gate, then run the appropriate distill-closeout.py terminal command before finalizing.",
            details,
        ]
    ).strip()

    if event.get("stop_hook_active"):
        emit(
            {
                "continue": False,
                "systemMessage": reason[:4000],
            }
        )
        return 0

    emit(
        {
            "decision": "block",
            "reason": reason[:4000],
            "systemMessage": "Distill closeout gate requested one continuation pass before final response.",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
