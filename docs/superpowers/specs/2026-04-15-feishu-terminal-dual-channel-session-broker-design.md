# Feishu / Terminal 双通道会话 Broker 设计

## 1. 背景

当前已经具备两类能力：

1. **终端侧**：可以直接发起和观察本地 CLI / Agent 任务
2. **飞书侧**：已经能发送完成通知，并且本地 `lark-cli` 能力表明存在可用的消息接收入口：
   - `lark-cli event +subscribe`
   - `lark-cli im +chat-messages-list`
   - `lark-cli im +messages-reply`
   - `lark-cli im +threads-messages-list`

真正难点不在于“能不能从飞书收到一条消息”，而在于：

> 如何让飞书和终端都参与同一任务，而不让两边**同时污染同一个会话上下文**。

如果直接让飞书监听器和当前终端都去写同一个 live session / TTY / stdin，会立刻出现以下问题：

- 输入交错，agent 无法知道哪句是谁在什么时候插入的
- 正在运行的原子步骤被中途打断，状态不可恢复
- 终端和飞书各自看到的上下文不一致
- 一个端以为自己已经接管，另一个端还在继续推进
- 崩溃后无法判断哪些输入已经处理、哪些仍在队列中

因此，问题的本质不是“多端同时控制一个 shell”，而是：

> 让多端共享**同一个任务状态**，但在任何时刻只允许**一个端真正驱动 agent**。

## 2. 目标

本设计要实现以下目标：

1. 支持终端和飞书同时参与同一任务
2. 任何时刻只允许一个入口真正向 worker / agent 写入
3. 飞书输入在任务运行中可以进入系统，但默认只排队，不抢写
4. 任务状态必须外置，可恢复、可审计、可切换 owner
5. 终端在飞书接管期间依然可观察、可排队、可申请接管
6. 明确 `/takeover`、`/pause`、`/stop` 等控制语义
7. 崩溃、断线、重连后不会把同一条消息重复喂给 agent

## 3. 非目标

本设计**不追求**：

1. 不支持字符级、按键级的双人实时协同控制
2. 不试图让两个入口同时直接写同一个 live TTY
3. 不保证“飞书回复”可以直接接入当前平台内建会话的私有上下文
4. 不把飞书当作完整 IDE 替代品

换句话说，本设计适合**任务级协同**，不适合“两个端同时远程控制同一个 REPL / Vim / shell”。

## 4. 已知能力与假设

### 4.1 本地已确认能力

从当前环境可确认：

1. `lark-cli event +subscribe` 支持通过 WebSocket 订阅事件流
2. `lark-cli im +chat-messages-list` 支持按 chat / P2P 拉取消息
3. `lark-cli im +messages-reply` 支持按消息回复
4. 已存在飞书 bot 发送能力和可复用 profile

### 4.2 设计假设

1. 后续 worker 应由一个外部 broker 托管，而不是直接暴露 live session 给多个输入源
2. broker 可以持有自己的状态存储（SQLite 或文件）
3. 终端输入和飞书输入都必须先进入 broker
4. worker 只接受 broker 转发的输入

## 5. 总体方案

采用 **单写者（single-writer）Broker 架构**。

### 5.1 核心原则

1. **共享任务状态，不共享实时写权限**
2. **双入口入队，单入口出队**
3. **只在安全检查点切换 owner**
4. **所有输入必须带来源、幂等 ID、时间戳**
5. **状态必须外置，不允许只活在某个 live shell 内存里**

### 5.2 组件划分

| 组件 | 职责 | 关键限制 |
| --- | --- | --- |
| **Feishu Listener** | 接收飞书事件/回复消息 | 只接收并入队，不直接写 worker |
| **Terminal Adapter** | 接收终端输入 | 只把输入转交 broker |
| **Broker / Coordinator** | 状态机、队列调度、owner 切换、checkpoint 管理 | 唯一允许驱动 worker 的组件 |
| **State Store** | 持久化 session、锁、待处理事件、checkpoint、发送日志 | 必须是持久层 |
| **Worker Adapter** | 包装实际 CLI / Agent 进程 | 只接受 broker 调度 |
| **Notifier** | 向飞书和终端回显状态变化、完成摘要 | 不拥有驱动权 |

## 6. 状态模型

### 6.1 Session 状态

建议最小状态机如下：

| 状态 | 含义 |
| --- | --- |
| `idle` | 尚未开始执行 |
| `running` | worker 正在执行中 |
| `waiting_human` | worker 到达检查点，等待人类输入 |
| `paused` | 已安全暂停，可恢复 |
| `completed` | 任务已完成 |
| `failed` | 任务失败 |
| `stopped` | 被显式终止 |

### 6.2 Owner 模型

`lock_owner` 仅允许以下值：

- `terminal`
- `feishu`
- `system`

含义：

- `terminal`：当前由终端推进会话
- `feishu`：当前由飞书推进会话
- `system`：当前没有人类主控，系统正在执行或收尾

### 6.3 Event 状态

每条输入事件建议有如下状态：

- `queued`
- `selected`
- `applied`
- `dropped`
- `superseded`

这样可以明确判断“这条飞书回复到底有没有真正喂进 agent”。

## 7. 最小数据模型

建议至少持久化以下实体。

### 7.1 `sessions`

| 字段 | 作用 |
| --- | --- |
| `session_id` | 会话唯一 ID |
| `status` | 当前状态 |
| `lock_owner` | 当前写锁 owner |
| `lock_version` | 锁版本号，防止并发覆盖 |
| `current_checkpoint_id` | 最近检查点 |
| `interrupt_requested` | 是否请求了 stop/pause/takeover |
| `started_at` / `updated_at` | 生命周期时间 |

### 7.2 `events`

| 字段 | 作用 |
| --- | --- |
| `event_id` | 事件唯一 ID |
| `session_id` | 所属会话 |
| `source` | `terminal` / `feishu` / `system` |
| `source_message_id` | 来源侧幂等 ID |
| `kind` | `input` / `takeover` / `pause` / `stop` / `ack` |
| `payload` | 实际内容 |
| `status` | `queued/selected/applied/...` |
| `created_at` | 入队时间 |

### 7.3 `checkpoints`

| 字段 | 作用 |
| --- | --- |
| `checkpoint_id` | 检查点 ID |
| `session_id` | 所属会话 |
| `worker_state_ref` | worker 状态引用 |
| `summary` | 当前阶段摘要 |
| `created_at` | 检查点时间 |

### 7.4 `outbound_messages`

用于记录已经发往飞书或终端的回执、摘要和系统提示，避免重复发送。

## 8. 关键链路详解

这一节是给 redcap / reviewer 的重点：不仅说“系统做什么”，还说“用户会看到什么现象”。

### 8.1 场景 A：终端发起任务

**触发：** 用户在终端输入任务请求。  
**目标：** 创建会话并让终端成为首个 owner。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Terminal Adapter 接收输入并发送给 broker | 终端显示“任务已提交” |
| 2 | Broker 创建 `session_id`、写 `sessions` 记录 | 终端可看到 session 编号 |
| 3 | Broker 获取写锁，`lock_owner=terminal` | 终端成为当前主控 |
| 4 | Broker 启动 worker | 任务开始执行 |
| 5 | 状态切换到 `running` | 飞书可选收到“任务已开始”通知 |

### 8.2 场景 B：任务运行中收到飞书回复

**触发：** worker 仍在跑，飞书用户回复一句新要求。  
**目标：** 不打断当前原子步骤，只入队。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Feishu Listener 收到 `im.message` | 后台接收到新事件 |
| 2 | 事件写入 `events`，状态=`queued` | 没有直接写入 worker |
| 3 | Broker 发送飞书 ACK | 飞书看到“已收到，等待检查点处理” |
| 4 | worker 继续当前任务 | 终端不会被突然插入一段飞书内容 |

**这里的关键现象：**

- 飞书输入不会丢
- 但也不会立刻打断 live 上下文

### 8.3 场景 C：worker 到达检查点

**触发：** worker 完成一轮阶段性动作，或主动询问人类输入。  
**目标：** 只在这里考虑切 owner / 处理队列。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Broker 写 checkpoint | 会话进入可恢复状态 |
| 2 | `status=waiting_human` | 两端都可以看到“等待输入” |
| 3 | Broker 检查 `events` 队列 | 系统准备选择下一条输入 |
| 4 | 按策略选择一个事件 | 只有被选中的那条会推进 worker |
| 5 | 选中的事件状态变 `selected -> applied` | 被处理的一侧看到“已接管/已应用” |

### 8.4 场景 D：飞书接管主控

**触发：** 队列中存在飞书消息，且 broker 决定下一轮由飞书推进。  
**目标：** 切 owner，但不并发双写。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Broker 将 `lock_owner` 改为 `feishu` | 会话所有权发生切换 |
| 2 | 终端被切到观察/排队模式 | 终端提示“当前由 Feishu 驱动” |
| 3 | 飞书那条输入被真正写给 worker | 任务从飞书输入继续推进 |
| 4 | worker 恢复 `running` | 飞书侧可感知自己成为当前主控 |

### 8.5 场景 E：飞书主控期间，终端又输入一条命令

**触发：** `lock_owner=feishu` 时，终端用户继续输入。  
**目标：** 终端不失效，但不允许抢写。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Terminal Adapter 把输入发给 broker | 输入不会报错 |
| 2 | Broker 发现 owner 不是 terminal | 不直接写给 worker |
| 3 | 输入以 `queued` 状态写入 `events` | 终端提示“你的输入已排队” |
| 4 | 等待下一个 checkpoint 再考虑处理 | 任务上下文保持稳定 |

**这一步是“CLI 不会失效”的核心原因。**

终端依然能输入，只是它的输入不再具备即时写入权。

### 8.6 场景 F：紧急停止

**触发：** 终端或飞书发出 `/stop`。  
**目标：** 快速但有序地终止。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | 事件入队，优先级标为最高 | 不会与普通输入混排 |
| 2 | Broker 设置 `interrupt_requested=stop` | worker 被标记为待中断 |
| 3 | 在安全点执行 stop | 避免中途破坏原子写入 |
| 4 | `status=stopped` 或 `paused` | 两端同步看到任务已停止 |

### 8.7 场景 G：申请接管

**触发：** 非 owner 端发送 `/takeover`。  
**目标：** 有序切换 owner，而不是抢写。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | broker 记录 takeover 请求 | 请求已被系统接受 |
| 2 | 如果 worker 正在 `running`，不立刻切换 | 任务继续到下一个 checkpoint |
| 3 | checkpoint 到达后切 owner | 两端都能看到 owner 变化 |
| 4 | 新 owner 获得下一轮驱动权 | 切换稳定，不串上下文 |

### 8.8 场景 H：完成与收尾

**触发：** worker 成功完成任务。  
**目标：** 统一收尾，统一广播。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Broker 写最终状态=`completed` | 状态冻结 |
| 2 | 持久化最终 summary / artifacts | 可追溯 |
| 3 | 终端打印完成摘要 | 终端知道已收口 |
| 4 | 飞书收到完成摘要 | 飞书知道任务结束 |
| 5 | 释放 owner 锁 | session 正式关闭 |

### 8.9 场景 I：崩溃、断线、重连

**触发：** Feishu listener 断线、worker 崩溃、broker 重启。  
**目标：** 恢复，不重复投喂。

| 步骤 | 系统动作 | 用户可见现象 |
| --- | --- | --- |
| 1 | Broker 从 SQLite 读出 `session` 和 `checkpoint` | 会话状态不丢 |
| 2 | 未 `applied` 的事件继续保留在队列 | 飞书消息不会丢失 |
| 3 | 已 `applied` 的事件按 `message_id` 去重 | 不会重复喂给 worker |
| 4 | 恢复到最近 checkpoint | 任务可以继续推进 |

## 9. 为什么 CLI 不会“无法回复消息”

结论是：**只要采用 broker 架构，CLI 不会因为飞书接入而失去回复能力。**

原因不是“它永远是主控”，而是：

1. CLI 只是一个输入端
2. CLI 始终可以把输入交给 broker
3. 只是当它不是 owner 时，输入会变成**排队输入**，不是**即时写入**

因此，CLI 的能力会从“随时直接写 session”变成：

- **owner 时**：即时推进任务
- **非 owner 时**：观察 + 排队 + 申请接管

这并不是“CLI 不能回复”，而是“CLI 回复不再绕过调度层”。

## 10. 方案真正解决了什么

它解决的是这几个核心问题：

1. **双端同时写入同一上下文**
2. **谁在驱动当前任务不清楚**
3. **飞书消息到底有没有被处理无法证明**
4. **一旦崩溃就不知道处理到了哪里**
5. **终端和飞书各自以为自己是主控**

它没有解决的，是字符级并发协作；那类问题不该在这个方案里支持。

## 11. 失败模式与防护

### 11.1 不允许的设计

以下设计应明确拒绝：

1. 飞书监听器直接写 worker stdin
2. 终端和飞书共用同一个 live TTY
3. 不持久化队列和锁，只靠内存状态切 owner
4. 不做 `message_id` 去重

### 11.2 必须有的防护

1. **单写锁**：任意时刻只有一个 owner
2. **幂等 ID**：防止飞书重投 / listener 重连后重复消费
3. **checkpoint**：只在检查点切换 owner
4. **事件优先级**：`/stop`、`/pause` 高于普通输入
5. **显式状态广播**：两端都应看到 owner / status 变化

## 12. 推荐的实现顺序

建议按下面顺序落地，而不是一步做到全自动双向会话。

### Phase 1：只做飞书入队，不做接管

先实现：

1. Feishu Listener 收消息
2. 入 SQLite 队列
3. 飞书收到 ACK
4. 终端侧可以看到待处理飞书消息

这一阶段先证明“消息能收、不会打断 live 会话”。

### Phase 2：支持 checkpoint 消费飞书消息

再实现：

1. worker 到达等待输入点
2. broker 可以选择飞书队列中的消息推进任务
3. owner 可以在 checkpoint 间切换

这一阶段证明“飞书不只是收得到，还能有序参与任务”。

### Phase 3：支持 `/takeover`、`/pause`、`/stop`

把控制指令做成显式协议，而不是普通文本猜测。

### Phase 4：补恢复、审计与摘要

补：

1. 崩溃恢复
2. 幂等去重
3. 完成摘要双端广播
4. 审计日志

## 13. 需要 redcap 团队重点评审的问题

这份方案建议 reviewer 重点盯以下问题，而不是只看“概念上是否可行”。

### 13.1 状态边界

1. `waiting_human` 的定义是否足够明确？
2. 哪些 worker 状态算“安全检查点”？
3. `paused` 与 `stopped` 的边界是否清楚？

### 13.2 并发语义

1. `takeover` 是立即生效还是只在 checkpoint 生效？
2. 同一时刻两个端都发 `/takeover` 时谁优先？
3. 普通输入和控制指令是否进入同一队列？

### 13.3 数据持久化

1. SQLite 是否足够，还是需要更稳定的 event log？
2. checkpoint 记录的是抽象状态，还是完整 worker 快照？
3. 去重的主键应该是飞书 message id、事件 hash，还是二者结合？

### 13.4 UX

1. 非 owner 端收到的“已排队”提示是否够清晰？
2. 两端是否都应看到 owner 切换通知？
3. 飞书上是否需要显式命令语法（如 `/takeover`）？

## 14. 推荐结论

推荐采用本方案，原因如下：

1. 它正面解决了“飞书和终端同时污染同一上下文”的根因
2. 它把问题从“多端同时控制一个 shell”降维成“多端协作一个任务状态”
3. 它允许分阶段落地，不需要一步做成全自动复杂系统
4. 它保留了终端主体验，同时给飞书提供稳定、可控的介入面

一句话总结：

> **双通道协同不是让两个端同时写同一个 session，而是让两个端共享同一任务状态，并由 broker 保证任一时刻只有一个写者。**
