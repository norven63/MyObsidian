# Copilot instructions for Distill closeout

When working in this repository on any non-trivial task, GitHub Copilot CLI must use the Distill closeout runtime as the required task lifecycle path.

## Required launch path for repository-enforced rescue

Use:

```bash
bash scripts/copilot-distill-session.sh
```

instead of launching raw `copilot` directly.

Reason: GitHub Copilot CLI documentation currently exposes repository-local instruction files, but not a documented repository-local Stop/SessionEnd hook surface. This wrapper gives the repository a mechanical `SessionEnd` rescue path by calling `distill-stop-hook.sh SessionEnd` after the Copilot process exits.

If `AGENTS.md`, `.github/copilot-instructions.md`, or `.github/instructions/distill-closeout.instructions.md` changes during a running Copilot session, restart Copilot through the wrapper. The wrapper now detects that instruction drift at session end and exits nonzero rather than silently treating the old in-memory instruction set as current.

## Required lifecycle flow

1. Before multi-step execution begins, run:

   ```bash
   python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py start \
     --task-id "<stable-task-id>" \
     --title "<task title>" \
     --repo "/Users/norven/workspace/MyObsidian" \
     --phase "<current phase>" \
     --done "<what is already underway>" \
     --next-step "<next step>"
   ```

2. Reuse the exact same `--task-id` for all later `progress`, `wait`, `complete`, `fail`, or `cancel` calls.

3. `start` and ordinary `progress` are quiet-first by default: they update local lifecycle state without sending Feishu messages. Use `progress --force` only for genuinely useful external visibility. `wait`, `complete`, `fail`, `cancel`, and rescue events remain user-visible.

4. Before any success-shaped final reply, Copilot **must** run:

   ```bash
   python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py complete \
     --task-id "<same-task-id>" \
     --title "<task title>" \
     --repo "/Users/norven/workspace/MyObsidian" \
     --phase "<final phase>" \
     --conclusion "<final conclusion>" \
     --done "<done item 1>" \
     --current-complete "<current complete>" \
     --previous-step "<previous step>" \
     --next-step "<next step or 无>" \
     --plan-position "<plan position>"
   ```

5. If the task is blocked, use `wait`. If it fails, use `fail`. If it must stop, use `cancel`.

## Non-negotiable rules

- Do **not** claim a task is complete before `distill-closeout.py complete` succeeds.
- Do **not** skip Feishu/receipt generation and then “补发” afterwards while still presenting the task as already solved.
- Do **not** call the raw `send-feishu-task-lifecycle.py` terminal commands directly for task closeout.
- Do **not** bypass `scripts/copilot-distill-session.sh` if you need repository-enforced SessionEnd rescue.
- Do **not** continue a long-running Copilot session after these repository instruction files change; restart the wrapper so the new rules actually load.
- If closeout fails, surface that failure explicitly and keep the task open.
- The final user-facing completion message must match the canonical closeout summary, not a simplified freestyle recap that drops the required structure.

## Why this exists

This repository uses Distill closeout as the canonical source for:

- terminal summary shape
- Feishu terminal notification
- closeout receipt persistence

If Copilot bypasses this path, the task is **not** considered properly closed.
