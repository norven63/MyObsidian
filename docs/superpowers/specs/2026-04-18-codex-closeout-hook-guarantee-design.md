# Codex Closeout Hook Guarantee Design

## 背景

Copilot 断联前的主线已经收敛到一个底层问题：任务质量不能只依赖 Agent 记得收口。`distill-closeout.py` 已经能把生命周期通知、终端摘要和 receipt 收敛到同一条 path，但在 Codex App 中还缺少 repo-local 的机械兜底。

OpenAI Codex Hooks 官方文档确认：Codex hooks 仍是 experimental，需要通过 `~/.codex/config.toml` 启用 `features.codex_hooks = true`；Codex 会发现 `~/.codex/hooks.json` 与 `<repo>/.codex/hooks.json`，支持 `SessionStart`、`PreToolUse`、`PostToolUse`、`UserPromptSubmit`、`Stop` 等事件。其中 `Stop` 是 turn-scope hook，可以运行自定义 validator；但文档也明确说明部分 tool interception 仍不完整，所以不能把它宣传成全域不可绕过 final-reply gate。

## 目标

本轮目标不是声称 Codex App 已经拥有 100% final-reply 强保障，而是在当前公开能力面内，把 MyObsidian 的 closeout 保障从“Agent 自觉调用”提升到“每轮停止前有 repo-local 兜底审计”。

成功标准：

1. Codex hooks 在本机配置中显式启用。
2. MyObsidian 提供 repo-local `.codex/hooks.json`。
3. `SessionStart` 向 Codex 注入 Distill closeout 规则提醒。
4. `Stop` 调用 Distill 的 `distill-stop-hook.sh Stop`，统一检查 batch gate、review gate 与 open closeout debt。
5. 若 Stop gate 失败，Codex 不直接结束本轮，而是收到 continuation prompt，要求先处理 closeout 风险。
6. 文档明确实验性边界，不把它虚报成宿主原生 final-reply / SessionEnd 100% 强保障。

## 方案比较

### 方案 A：继续只靠 AGENTS.md + 手工 closeout

优点是简单，不增加 Codex 配置。缺点是强保障能力基本没有变化，仍然依赖当前 Agent 在最终回复前记得调用 `distill-closeout.py complete`。

结论：不够。它解决不了 Copilot 断联前暴露的底层问题。

### 方案 B：启用 Codex hooks + repo-local Stop 兜底（采用）

做法：

1. 在 `~/.codex/config.toml` 启用 `features.codex_hooks = true`。
2. 在仓库新增 `.codex/hooks.json`。
3. `SessionStart` hook 注入 closeout 规则。
4. `Stop` hook 调用 `/Users/norven/.claude/skills/distill/scripts/distill-stop-hook.sh Stop`。
5. Stop hook 失败时返回 Codex 支持的 continuation JSON，要求继续处理未收口事项。

优点是能利用 Codex 原生 hook 面，不再只靠 prompt 记忆。缺点是 hooks 仍为 experimental，且 `Stop` 是 turn-scope，不等价于完整 SessionEnd。

结论：这是当前最务实的第一版强保障。

### 方案 C：外部 supervisor 包住 Codex App / CLI

做法是用外部进程接管启动、输入、退出和 closeout，类似 Copilot wrapper 的更强版本。

优点是理论保障更强。缺点是实现复杂，且对 Codex App 的交互体验侵入更大。当前已有 Codex hooks 可用，先不用把问题升级到重写宿主入口。

结论：保留为第二阶段。

## 设计

### 配置层

`~/.codex/config.toml` 增加：

```toml
[features]
codex_hooks = true
```

这是用户级配置，不提交到 MyObsidian 仓库，但必须在验收报告中说明。

### Repo Hook 层

新增 `.codex/hooks.json`：

- `SessionStart`：执行 `.codex/hooks/distill_session_start.py`，向 Codex 注入当前仓库 closeout 规则。
- `Stop`：执行 `.codex/hooks/distill_stop_hook.py`，调用 Distill stop hook。

### Stop Wrapper 行为

`distill_stop_hook.py` 只输出 Codex Stop hook 支持的 JSON，避免普通 stdout 污染 Stop 事件。

执行逻辑：

1. 从 hook stdin 读取 `cwd`、`session_id`、`turn_id`、`stop_hook_active`。
2. 解析 git root 作为 repo scope。
3. 设置：
   - `DISTILL_CLOSEOUT_REPO_SCOPE=<repo>`
   - `VAULT_PATH=<repo>`
   - `DISTILL_PATH=<repo>/Distill`
4. 调用 `distill-stop-hook.sh Stop`。
5. 成功时返回 `{"continue": true}`。
6. 失败且本轮尚未因 Stop hook continuation 过时，返回 `decision=block`，让 Codex 自动继续一轮。
7. 若已经是 continuation 后仍失败，返回 `continue=false` 和 `systemMessage`，避免无限循环，并要求最终回复显式披露失败。

## 边界

能做到：

1. Codex 每轮 Stop 时自动检查 Distill closeout debt。
2. 对 open closeout、batch gate、review gate 增加机械兜底。
3. 让 Agent 更难在未收口时直接结束。

不能虚报：

1. `Stop` 不是完整 SessionEnd。
2. hooks 当前仍为 experimental。
3. Codex 文档说明部分 tool interception 仍不完整。
4. 这不是 server-side gate，也不是 GitHub branch protection。

## 验证

首轮验证应覆盖：

1. `codex features list` 显示 `codex_hooks` effective state 为 `true`。
2. 手工向 `.codex/hooks/distill_session_start.py` 输入最小 hook JSON，输出合法 SessionStart JSON。
3. 手工向 `.codex/hooks/distill_stop_hook.py` 输入最小 Stop JSON，在当前无 open debt 时返回合法成功 JSON。
4. `python3 /Users/norven/.claude/skills/distill/scripts/validate-distill.py --distill-path /Users/norven/workspace/MyObsidian/Distill` 仍为 `ok`。

## 后续

如果 Codex hooks 后续从 experimental 进入 stable，或提供更强的 SessionEnd / final-response hook，应把当前 Stop 兜底升级为正式 closeout boundary，并重新评估是否还需要外部 supervisor。
