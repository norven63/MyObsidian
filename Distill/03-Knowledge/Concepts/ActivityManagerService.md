---
标识: concept-activitymanagerservice
标题: ActivityManagerService
标签: [concept, android-runtime]
别名: [AMS, Activity 管理服务, 进程与组件调度中枢]
来源:
  - 'AMS（2025面试旧笔记迁移）'
  - '进程启动（2025面试旧笔记迁移）'
关联概念:
  - 'Binder IPC'
  - 'Activity 启动模式'
  - 'WindowManagerService'
状态: stable
定义: ActivityManagerService 是 Android `system_server` 中把四大组件请求、进程启动与进程状态治理收束到统一调度链的核心服务；它真正负责的不是“某个页面怎么开”，而是“系统何时拉起谁、何时回调谁、谁该继续活着”。
---

# ActivityManagerService

## AMS 真正管的，不是某个 Activity，而是组件请求如何被系统接成进程与生命周期调度
### 一眼认知骨架
- **对象**：`system_server` 里的组件与进程总调度器，不是单一的“Activity 栈管理类”。
- **目的**：统一决定组件请求何时拉起进程、何时 attach、何时把生命周期回调送回目标 App。
- **组成**：AMS / ATMS、`ProcessList` / `ProcessRecord`、`ActiveServices`、`BroadcastQueue`、`ApplicationThread` Binder 回路。
- **主线**：组件请求进入系统 → 必要时 `startProcess` → Zygote fork → `ActivityThread.main()` attach → AMS `bindApplication` / `schedule*` 回调。
- **变体**：Activity、Service、Receiver、Provider 各有分支；冷启动、热启动、进程死亡重启也会改写整条链。
- **用法**：最适合解释冷启动、服务起不来、广播迟到、Provider 拉进程、前后台切换和 OOM_adj 异常。
### 快速判断 / Quick Scan
- 如果只用一句话说清，AMS 不是“帮你启动页面”，而是“把系统侧组件意图翻译成进程与生命周期动作”。
- 你最容易把它和 Activity 栈本身混为一谈；但 Android 10 以后 task / stack 更偏 ATMS，AMS 仍然掌控进程、组件与系统状态协同。
- 一旦你开始追“用户还在等但主线程并不重”“服务为什么没调起来”“死进程为什么又被拉起”，就已经进入 AMS 的责任边界。
### 展开理解
AMS 的难点在于：上层看到的是 `startActivity()`、`startService()`、`sendBroadcast()` 这些 API，系统侧真正执行的却是一条长得多的调度链。它既要回答“目标进程存不存在”，也要回答“现在该不该拉起、attach 完没有、该把哪个生命周期投递回去、这个进程之后该以什么优先级活着”。所以 AMS 最重要的不是记住几个类名，而是把**组件请求、进程建立、Binder 回调、存活策略**看成同一条因果链。

## Android 宁可把四大组件和进程命运收束到 AMS，也不让每条组件链各写一套规则
### 它解决的判断 / 工程问题
AMS 要解决的是：**当应用或系统请求启动一个组件时，系统由谁来统一判断是否需要建新进程、何时让目标进程 attach、何时把 Activity / Service / Receiver / Provider 的生命周期真正送进去，以及谁在这之后该继续保活。** 没有这层统一调度，四大组件会各自维护自己的启动协议，前后台切换、权限检查、进程死亡回收也很难保持一致。
### 如果忽略它会怎样
如果忽略 AMS，你会把很多系统等待误看成“App 自己慢”。页面没起来，不一定是 `onCreate()` 重；服务没调到，不一定是业务代码没执行；广播来晚了，也不一定是 receiver 自己阻塞。很多时候，系统还在拉进程、attach、等待 Binder 返回，或者根本没把回调送进目标进程。只盯 App 主线程，等于把真正的前置调度层看丢了。
### 为什么系统宁可这样设计 (Design Rationale / Trade-off)
Android 没有让 Activity、Service、Broadcast、Provider 各写一套独立的系统协议，而是把它们收束到 AMS 这一类中枢服务里。这样换来的好处是：权限检查、进程状态、前后台切换、死进程清理、OOM_adj 调整都能沿一套统一模型推进；代价则是链路更长，排障必须跨 `app → Binder → system_server → Zygote → app` 多层边界，单看一个方法名几乎解释不了完整现象。系统宁可增加中枢复杂度，也要换取全局一致性。

## 真正决定启动结果的是 startProcess、attachApplication 和 schedule 这条系统链
### 机制链 / Mechanism Chain
1. App 或系统组件通过 Binder 把 `startActivity()`、`startService()`、`sendBroadcast()`、`getContentProvider()` 等请求送进 `system_server`，AMS / ATMS 先解析目标组件、调用方身份与当前系统状态。
2. 如果目标进程不存在，AMS 会走 `startProcessLocked()` / `Process.start()`，准备 `uid`、`gid`、`nice-name` 等参数，再通过 Zygote socket 请求 `forkAndSpecialize()`；热进程则直接跳过这段。
3. 新进程被 fork 后进入 `ActivityThread.main()`：先 `Looper.prepareMainLooper()`，再创建 `ActivityThread`，随后通过 `attach()` 把 `ApplicationThread` 这个 Binder“遥控器”回传给 AMS。
4. AMS 在 `attachApplicationLocked()` 中拿到这个遥控器后，先发 `bindApplication`，再根据组件分支发 `scheduleLaunchActivity()`、`scheduleCreateService()`、`scheduleReceiver()` 或 Provider 安装等回调，让真正执行动作落回目标进程主线程。
5. 组件跑起来以后，AMS 还会继续维护 `ProcessRecord`、前后台状态与 `OOM_adj`，并在进程死亡、低内存或绑定关系变化时决定谁该重启、谁该回收、谁该继续保活。
### 关键条件 / 分支 / 例外 (Critical Conditions / Exceptions)
- **热进程分支**：如果进程已经存在，AMS 会直接走 attach 之后的 schedule 路径，不再重复 fork；这也是为什么“同一个页面第二次进来”常常比第一次短很多。
- **组件分工分支**：Activity 的任务栈语义更多落在 ATMS；Service、Broadcast、Provider 则分别走 `ActiveServices`、`BroadcastQueue`、Provider helper 的专用分支。
- **Provider 提前拉进程**：有些场景下用户甚至还没看到页面，只因为先访问了 ContentProvider，AMS 就已经把目标进程拉起来了。
- **死亡 / 超时分支**：attach 失败、Binder death、低内存回收都会让链路换轨，表现为进程反复重建或组件回调迟迟进不去。
### 最低决定层 / 关键锚点 (Decisive Layer Anchors)
- `startProcessLocked()` / `Process.start()` → `ZygoteConnection.runOnce()` → `forkAndSpecialize()` → `ActivityThread.main()` → `attachApplicationLocked()` 是 AMS 最低决定层的主链。只看 App 端 `onCreate()`，你会把大量启动空洞误判成业务代码慢。
- `ApplicationThread` 是 AMS 控制目标进程的 Binder 遥控器；AMS 并不直接在 app 进程里跑代码，而是靠这条回路把生命周期投递回去。忽略这一点，就会把“谁在执行”看歪。
- `ProcessRecord` / `OOM_adj` 不是附属信息，而是组件启动后“它能活多久”的关键约束。若把它看丢，就解释不了为什么同一 App 总在后台被杀、前台又被拉起。
- Activity 栈不对、页面复用异常不一定是 AMS 本体的问题，那更像 [[Concepts/Activity 启动模式|Activity 启动模式]] / ATMS 分支；AMS 负责的是更上游的系统调度骨架。
### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- 把“启动慢”拆成 `process start`、`attach`、`bindApplication`、`activity launch`、`first frame` 五段；只有先分层，后面的证据才不会混在一起。
- 如果 Service / Receiver / Provider 没有真正跑到 App 里，先确认目标进程是否存在、`attachApplication` 是否完成、AMS 是否已经发出了对应 `schedule*` 回调。
- 反复重启或偶发白屏时，不要只盯 Activity 生命周期；同时看进程是否被 LMK 杀过、Binder 是否断过、`OOM_adj` 是否异常抖动。

## 一次冷启动首页的过程，最能看出 AMS 如何把“点一下”变成“首屏出现”
### 最小例子
- **场景**：用户从 Launcher 点击一个此前未运行的应用首页 Activity。
- **为什么这里会想到它**：用户只做了一次点击，但系统要先确认目标进程是否存在、是否要 fork、何时 attach、何时 `bindApplication`、何时把 Activity 真正 launch 进主线程。
- **结果**：如果这条链一路顺畅，用户感知到的是“点一下就开”；如果某段卡在 process start、attach、Binder 等待或首帧前准备，表面看起来像“App 没干活”，实际上系统调度链还没走完。
### 对比
- **ActivityTaskManagerService**：更聚焦 Task / Stack 与 Activity 组织；AMS 仍要负责进程建立、其他组件调度和系统级进程状态治理。
- **ActivityThread**：它是目标 App 进程里的执行入口，负责在应用主线程真正跑生命周期；AMS 则是 `system_server` 里的总调度者。
- **[[Concepts/WindowManagerService|WindowManagerService]]**：WMS 负责窗口可见与焦点；AMS 负责把组件与进程先推到“可以显示”的状态，两者是上下游关系。

## 把 AMS 看成“只管 Activity 栈”之后，排障几乎一定会盯错层
### 常见误解
- “AMS 只要懂 `startActivity()` 就够了。” 错。AMS 真正难的是四大组件共享同一条进程与生命周期调度骨架，Activity 只是最常被拿来讲的一支。
- “页面没起来，一定是 App 自己 `onCreate()` 慢。” 很多时候，进程都还没 attach 完、`bindApplication` 还没走到、或者系统正在等跨进程返回。
### 失效 / 反噬信号
- 冷启动 trace 里 `process start`、`attach`、`bindApplication`、`activity launch` 之间存在明显空洞，但 App 主线程看起来并不重。
- system_server 没崩，但 Service / Receiver / Provider 的创建时序反复异常，死进程被频繁重拉，说明该回到 AMS 的进程状态与调度分支看问题。
- 明明优化了首页代码，体验却只改善一点点，往往说明真正拖慢的是 AMS 之前或 AMS 驱动的系统前置阶段。
### 不适用场景
- 如果问题已经明确发生在 View 树的布局、绘制或 GPU 提交阶段，AMS 不是主要抓手。
- 如果现象是“回退路径不对、实例复用错了”，优先回到 [[Concepts/Activity 启动模式|Activity 启动模式]] 与 Task 语义，而不是继续深挖 AMS。

## AMS 通常要和这些概念连着看
- [[Concepts/Binder IPC|Binder IPC]] `(mechanism[强])`：AMS 的关键调度几乎都要穿过 Binder 往返；不理解远程调用等待，就很难解释“主线程不忙但用户还在等”。
- [[Concepts/Activity 启动模式|Activity 启动模式]] `(context[中])`：启动模式负责实例与 Task 语义，AMS 负责把组件真正拉起来；两者经常在“启动不对劲”问题里同时出现。
- [[Concepts/WindowManagerService|WindowManagerService]] `(handoff[中])`：AMS 把组件和进程推到可运行状态后，窗口何时可见、谁拿焦点、Layer 怎样交给显示系统，就转交给 WMS。

## 先记住这条系统调度线，再用三个问题自测
### 记忆锚点 / Memory Anchor
- **一句话记住**：AMS = `system_server` 里的组件与进程总调度器，负责把“有人要启动它”翻译成“进程被拉起、生命周期被送达、状态被继续管理”。
- **看到这个信号就想到它**：冷启动要拉进程、服务 / 广播 / Provider 迟迟不进目标进程、后台进程总被反复拉起。
### 自测问题
1. 为什么说 AMS 的关键不只是“管理 Activity”，而是“统一组件请求、进程建立和生命周期投递”？
2. 冷启动时，`Process.start()`、Zygote、`ActivityThread.main()`、`attachApplicationLocked()` 各自负责哪一段动作？
3. 如果用户看到“页面还没出来但主线程看起来不忙”，你为什么应该先怀疑 AMS 主导的系统调度链？
