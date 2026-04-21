# Distill Closeout Guarantee Design

## 背景

当前 Distill 已经具备两类基础能力：

1. `agent-hook-handler.sh on_batch_complete` 能对批次产物做 fail-closed 物理 gate，并在通过后发送飞书完成通知。
2. `send-feishu-task-lifecycle.py` 已支持 `start / progress / wait / complete / fail / cancel / status`，并持久化 lifecycle 状态文件。

但当前仍存在两个闭环缺口：

1. **非 batch 的 Distill 任务** 没有 Distill-owned 的统一收口路径。
2. **模板化终端收口** 与 **飞书终态通知** 没有共享同一份 canonical payload，仍可能分叉或漏调。

## 目标

本轮要把 Distill 的任务结束语义从“Agent 记得做”提升为“Distill runtime 只能这样做”。

要求：

1. 所有非 trivial Distill 任务都能被注册为 open task。
2. 只有写出 closeout receipt 后，任务才算真正 closed。
3. 完成类 closeout 必须先通过飞书终态通知，再允许写 receipt。
4. 批次任务和非 batch 任务都复用同一条 closeout path。
5. Stop / SessionEnd 能对遗失 receipt 的 open task 做 rescue。

## 关键不变量

1. **open debt invariant**：任务 `start` 后，若没有 receipt，就一直视为 open debt。
2. **receipt invariant**：只有 `distill-closeout.py` 能写 closeout receipt。
3. **notify-before-close invariant**：`completed / failed / cancelled` 必须先完成 lifecycle terminal event，再允许写 receipt。
4. **same-payload invariant**：终端模板摘要、receipt 内容、飞书终态摘要必须来自同一份结构化 payload。
5. **rescue invariant**：Stop / SessionEnd 必须扫描 open debt；对 stale open task 或 session-end escaped task 自动补 `cancelled` 终态，并写审计记录。

## 组件

### 1. `scripts/distill-closeout.py`

新增统一 closeout runtime，负责：

1. `start / progress / wait`：代理 lifecycle script，并把任务标记为 closeout-managed。
2. `complete / fail / cancel`：校验模板必填段，调用 lifecycle terminal event，写 canonical summary + receipt。
3. `status`：输出 lifecycle + closeout 的组合状态。
4. `audit-open`：扫描 open managed task，并对超时或 session-end 逃逸任务做 rescue。

### 2. `scripts/distill-stop-hook.sh`

新增 hook wrapper，统一处理：

1. 先跑 `agent-hook-handler.sh`（保留现有 batch gate）
2. 再跑 `distill-closeout.py audit-open`
3. 合并两者退出码，形成 Stop / SessionEnd 的统一 hook 出口

### 3. batch integration

`agent-hook-handler.sh` 在首次写入 current batch manifest 时自动注册 batch lifecycle task，并在 `on_batch_complete` 通过后调用 `distill-closeout.py complete` 完成收口。

## closeout payload

terminal / receipt 的 canonical payload 至少包含：

- `task_id`
- `title`
- `status`
- `source`
- `conclusion`
- `current_complete`
- `previous_step`
- `next_step`
- `plan_position`
- `done_entries`
- `artifact_paths`
- `review_items`
- `manual_checks`
- `help_needed`
- `created_at`

## 保障边界

### 能做到的

1. 对 closeout-managed task，实现 receipt 化的 open/close 账本。
2. 对 terminal lifecycle event 实现 fail-closed。
3. 对 Claude/Kimi 这类可接 Stop / SessionEnd 的宿主，提供 Distill-owned rescue path。
4. 为 Copilot/AGENTS 指令提供统一 closeout 命令，避免继续散调 lifecycle script。

### 不能虚报的

1. 若宿主不能在本地提供 Stop / SessionEnd hook，则无法诚实宣称“终端最终自然语言回复 100% 被机器接管”。
2. 在当前 Copilot CLI 能力边界内，可以把 canonical closeout summary 与 Feishu 终态统一生成，但最终 CLI 自然语言仍需要 Agent 引用该结果。

## 验证目标

1. `start -> complete` 正常写出 summary + receipt
2. 缺少模板必填段时 closeout 失败
3. 飞书 terminal event 失败时不写 completed receipt
4. batch write -> on_batch_complete 走统一 closeout
5. `audit-open --mode session-end` 能 rescue open managed task
