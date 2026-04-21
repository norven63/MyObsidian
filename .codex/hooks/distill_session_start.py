#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


def main() -> int:
    # Drain stdin so Codex can pass the current hook payload without affecting output.
    sys.stdin.read()

    additional_context = "\n".join(
        [
            "MyObsidian uses Distill closeout as the repository task lifecycle path.",
            "For non-trivial work, call distill-closeout.py start before multi-step execution and complete/fail/cancel before claiming a terminal result.",
            "The repo-local Codex Stop hook audits Distill open closeout debt, batch gate, and review gate, but hooks are experimental and Stop is turn-scoped, not a full SessionEnd guarantee.",
        ]
    )
    print(
        json.dumps(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": additional_context,
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
