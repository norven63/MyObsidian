# Distill closeout requirement

For GitHub Copilot CLI sessions in this repository:

- Required launch path for repository-enforced SessionEnd rescue: `bash scripts/copilot-distill-session.sh`
- Do not present a task as complete before `python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py complete` succeeds.
- Do not skip terminal template / Feishu / receipt generation and then backfill later while still claiming the task was already solved.
- If terminal closeout fails, surface that failure and keep the task open.
- If `AGENTS.md` or the Copilot instruction files change during a running session, restart via the wrapper; the wrapper now flags that instruction drift instead of silently continuing under stale rules.

`scripts/copilot-distill-session.sh` exists because raw Copilot CLI does not provide a documented repo-local Stop/SessionEnd hook surface. The wrapper gives this repository a mechanical SessionEnd rescue path via `distill-stop-hook.sh`.
