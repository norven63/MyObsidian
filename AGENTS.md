# Repository agent instructions

## Task lifecycle notifications

For GitHub Copilot CLI specifically, the supported launch path in this repository is `bash scripts/copilot-distill-session.sh`. Raw Copilot CLI currently documents repository-local instruction files, but not repository-local Stop/SessionEnd hooks, so direct `copilot` launch is not the repository-enforced path.

For Codex App / Codex CLI, this repository uses experimental Codex hooks as an additional local safety net:

1. The user-level Codex config must enable hooks with `features.codex_hooks = true` in `~/.codex/config.toml`.
2. The repository-local hook config is `.codex/hooks.json`.
3. `SessionStart` injects the Distill closeout reminder into Codex context.
4. `Stop` runs `.codex/hooks/distill_stop_hook.py`, which delegates to `bash /Users/norven/.claude/skills/distill/scripts/distill-stop-hook.sh Stop`.
5. This hook can catch open closeout debt, batch gate issues, and review gate issues before a turn stops, but it is still an experimental turn-scoped guardrail. Do not describe it as a stable host-native final-reply or full SessionEnd 100% guarantee.

For non-trivial tasks in this repository:

1. Before a task enters multi-step execution, initialize lifecycle tracking with `python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py start`.
2. Reuse the same `--task-id` for later `progress`, `wait`, `complete`, `fail`, or `cancel` events.
3. `start` and `progress` are quiet-first by default: they update local lifecycle state without sending Feishu messages. Use `progress --force` only when external visibility is genuinely useful; `DISTILL_FEISHU_NOTIFY_POLICY=normal|verbose` restores noisier progress delivery for special sessions.
4. When the task is blocked on user input or external confirmation, send `wait` and fill `--help-needed`.
5. **Do not call the raw lifecycle script directly for terminal closeout.** Use `python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py` so Distill can write a canonical summary and closeout receipt.
6. Before claiming success, run `distill-closeout.py complete`; before claiming failure or stopping, run `distill-closeout.py fail` or `distill-closeout.py cancel`.
7. Terminal closeout must provide all required summary fields: `--current-complete` / `--previous-step` / `--next-step` / `--plan-position`.
8. Completion-style events still require `--title`, `--conclusion`, 1-3 `--done` items, and `--path` for key files/artifacts when relevant.
9. The Distill sender automatically prepends `发送者：Distill`, so no manual sender label is needed.
10. If a critical lifecycle notification or closeout step fails, surface the failure instead of silently claiming completion.
11. If `AGENTS.md` or the Copilot instruction files change during a running Copilot session, restart via `bash scripts/copilot-distill-session.sh`; the wrapper now treats that instruction drift as a failed closeout boundary instead of silently continuing under stale rules.

Example:

```bash
TASK_ID="feishu-lifecycle-example"

python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py start \
  --task-id "$TASK_ID" \
  --title "Distill task" \
  --phase "分析" \
  --done "已进入多阶段执行" \
  --next-step "继续分析并准备落地修改"

python3 /Users/norven/.claude/skills/distill/scripts/distill-closeout.py complete \
  --task-id "$TASK_ID" \
  --title "Distill task" \
  --conclusion "已完成修复并通过验证" \
  --done "升级飞书通知模板" \
  --done "补充任务结果与协助项说明" \
  --path "AGENTS.md" \
  --current-complete "任务已完成收口，已生成模板化摘要并写出 closeout receipt。" \
  --previous-step "已完成修改、验证和最终审查。" \
  --next-step "无" \
  --plan-position "分析 -> 修改 -> 验证 -> 收口（当前已到收口完成）"
```
