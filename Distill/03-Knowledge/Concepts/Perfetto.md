---
标识: concept-perfetto
标题: Perfetto
标签: [concept, android-observability]
别名: [Perfetto Trace, 系统时序追踪]
来源:
  - '2026-01-14-性能优化：Perfetto查看app启动时间及冷热启动介绍'
  - '2026-02-07-一个实用的Android-Perfetto分析器'
关联概念:
  - 'RenderThread'
  - 'Binder IPC'
  - 'Dominator Tree'
状态: stable
定义: Perfetto 是 Android / Linux 的统一时序追踪框架；它把 app、framework、内核和渲染轨道放到同一条时间线上，让团队能沿着“第一处变宽或变空的时间段”追到真实瓶颈。
---

# Perfetto

## Perfetto 真正给你的，不是彩色轨道，而是一条跨线程跨进程的因果时间线
### 一眼认知骨架
- **对象**：Android / Linux 的统一 tracing 与时间线分析框架，而不是一张好看的轨道截图。
- **目的**：把 app、Binder、调度、渲染、Frame Timeline 和自定义 marker 放到同一时钟上对齐。
- **组成**：trace config、数据源（sched / binder / gfx / app marker 等）、track / slice / counter、Frame Timeline、分析器与查询视图。
- **主线**：定义里程碑 → 采集 trace → 对齐关键轨道 → 找第一处变宽 / 变空的时间段 → 决定下一步下钻工具。
- **变体**：启动慢、Binder 等待、掉帧、调度饥饿、复现不稳、marker 缺失都会改写分析路径。
- **用法**：最适合处理跨线程、跨进程、跨系统层的性能问题，把“感觉卡”变成“知道卡在哪一段”。
### 快速判断 / Quick Scan
- 如果只用一句话说清，Perfetto 不是“抓 trace”，而是“用统一时间轴证明谁先拖慢了谁”。
- 你最容易把它和 Method Profiler、普通日志混为一谈；但前两者通常只给你局部视角，Perfetto 的价值在于跨层对齐。
- 一旦你开始追“首帧到底晚在 Binder 还是 RenderThread”“线程不忙为什么还在等”“团队为什么对同一问题讲出三个故事”，就该打开 Perfetto。
### 展开理解
性能排障最浪费时间的事，不是没有工具，而是没有共同时间轴。应用日志、自定义埋点、服务日志、渲染轨道、调度事件如果不能落在同一时钟上，每个人都能讲一个“听起来合理”的故事，却很难真正证明因果。Perfetto 之所以重要，不是因为它能显示很多彩条，而是因为它第一次把这些分散证据拉到同一个坐标系里，让“第一处变慢的是哪段”成为可以复核的问题。

## 团队宁可先统一时间线，也不愿继续靠零散日志和各自的“感觉”排障
### 它解决的判断 / 工程问题
Perfetto 要解决的是：**当问题跨越 app、system_server、调度、渲染和 Binder 边界时，团队怎样还能回答“时间到底花在哪、谁在等谁、第一处变宽发生在哪”。** 单点日志和局部 profiler 往往只看到一截链路，无法证明真正的上游瓶颈。
### 如果忽略它会怎样
如果忽略 Perfetto，你会不停优化看起来最忙的那段代码，却可能错过真正把用户体验拖慢的等待段、调度空洞或 Binder reply gap。更严重的是，团队讨论会退化成“有人怪主线程、有人怪系统服务、有人怪 GPU”，但没有一条能被统一验证的时间线。
### 为什么系统宁可这样设计 (Design Rationale / Trade-off)
Perfetto 没有停留在某一种 profiler 视角，而是把调度、Binder、图形、Frame Timeline 和 app marker 都接进同一个 trace 体系。它换来的好处是：跨层问题终于有了共同语言；代价则是 capture 成本、数据量和分析复杂度都更高，而且如果 marker / 里程碑不清晰，trace 很快会退化成噪声。也就是说，系统宁可让 tracing 框架更通用，也不愿让每类问题永远困在各自孤立的小工具里。

## 真正决定分析质量的是里程碑、关键轨道和第一处变宽的等待段
### 机制链 / Mechanism Chain
1. 在复现场景前先定义里程碑与 trace config：例如首帧、某个 Binder reply、某个 dropped frame，并决定是否打开 sched、binder、gfx、frame timeline 与 app marker 等数据源。
2. 采集开始后，内核、framework 和应用会把这些事件按同一时间戳体系写进 trace；Perfetto 的价值首先来自“同一时钟”，不是“数据很多”。
3. Perfetto 把数据整理成 process / thread / track 视图，让 UI 线程、RenderThread、Binder、`system_server`、CPU runnable 状态和 Frame Timeline 能放在同一条时间线上对齐。
4. 分析时先锚定一个症状里程碑，再沿时间线回看第一处明显变宽、变空或开始等待的片段，确认它是计算、调度、锁、Binder 还是渲染提交。
5. 一旦 primary wait 被找出来，就把问题分流：Binder 问题回服务端与事务链，渲染问题回 [[Concepts/RenderThread|RenderThread]]，对象滞留问题回 [[Concepts/Dominator Tree|Dominator Tree]]，而不是继续在同一张 trace 上胡乱猜。
### 关键条件 / 分支 / 例外 (Critical Conditions / Exceptions)
- **marker 缺失分支**：没有关键业务 marker，trace 再大也难把系统轨道和业务阶段对齐。
- **问题假设缺失分支**：没有里程碑与问题假设的海量 trace，只会增加阅读噪声，不会自动产生结论。
- **时间线正常例外**：如果时间线本身很健康，但对象长期不释放，Perfetto 并不能替代 heap dump 与支配树。
- **语义补充例外**：Perfetto 能告诉你“哪里在等”，但不总能告诉你“为什么服务端要这样等”；真正的语义解释还得回到对应概念或日志。
### 最低决定层 / 关键锚点 (Decisive Layer Anchors)
- Perfetto 最低决定层不是某一条线程截图，而是“app / system / kernel 落在同一时钟上”这件事。少了统一时间轴，谁先拖慢谁就无法被证明。
- 真正该先看的，往往不是最忙的那块，而是**第一处变宽或变空的时间段**；如果你只盯最显眼的宽 slice，很容易把下游等待误读成上游根因。
- `binder transaction`、runnable 却不被调度、RenderThread 宽 slice、Frame Timeline miss deadline，这些都是 Perfetto 擅长揭示而普通日志很难对齐的证据层。
- Perfetto 回答的是“时间如何分布”，不是“对象为什么没死”或“任务栈语义为什么不对”；如果把工具边界看丢，就会一直在错误的问题上加更多 trace。
### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- 先定义问题里程碑，再抓 trace；“我到底在找首帧晚、Binder reply 晚，还是 dropped frame”这一步比 capture 命令本身更重要。
- 尽量同时保留一份“好 trace”和“一份坏 trace”做对照；很多时候瓶颈不是看一份 trace 看出来的，而是比较出来的。
- 当时间线已经指向某个链路时，立刻分流到更专用的工具或概念，不要继续把所有问题都压在 Perfetto 一张图上。

## 一次冷启动为什么会从“总耗时高”变成“知道该先改哪段”
### 最小例子
- **场景**：一次冷启动总耗时 1200ms，但日志只告诉你“总耗时高”，无法回答慢在 Application 初始化、Binder 调系统服务、首帧同步还是 RenderThread 提交。
- **为什么这里会想到它**：这类问题天然跨越应用、framework 与渲染阶段，单点日志只会把链路切碎，无法说明第一处瓶颈是谁。
- **结果**：Perfetto 会把 process start、bindApplication、activity launch、Binder wait、RenderThread 与 first frame 放到同一时间轴上，让你先知道“该改哪段”，而不是先改看起来最显眼的代码块。
### 对比
- **普通日志**：更像一串事件点，只告诉你“发生过什么”，不擅长回答谁先拖慢了谁。
- **CPU / Method Profiler**：更适合看单进程内部谁在执行耗时方法；跨 Binder、调度和渲染的链路仍然会断掉。
- **[[Concepts/Dominator Tree|Dominator Tree]]**：Dominator Tree 解释对象为什么被保活，不解释某段时间为什么被耗掉。

## 只会抓 trace 不会定锚，Perfetto 很快就会退化成高级截图
### 常见误解
- “抓到 trace 就等于分析完成。” 如果没有里程碑、marker 和问题假设，Perfetto 很容易沦为只会看彩色轨道的截图工具。
- “trace 越大越全越好。” 没有问题边界的海量数据，只会增加噪声和阅读成本，不会自动产生洞见。
### 失效 / 反噬信号
- 不同人对同一份 trace 能讲出完全不同的结论、每次都临场猜该先看哪条轨道，说明团队还没有把 Perfetto 变成统一分析语言。
- 你总能看见“某线程很忙”，却说不清它是不是关键路径上的第一处瓶颈，也说明分析还停留在表面热闹，而不是因果定位。
### 不适用场景
- 如果核心问题是对象为什么泄漏、谁支配了 retained heap，Perfetto 不是主要工具，应转向 [[Concepts/Dominator Tree|Dominator Tree]] 和 heap dump。
- 如果只是业务规则写反、字段算错或 UI 文案异常，Perfetto 也不是第一选择。

## Perfetto 最值得和这些概念一起看
- [[Concepts/Binder IPC|Binder IPC]] `(observes[中])`：Binder 事务何时排队、谁在等 reply、`system_server` 哪条线程成了等待源，往往要靠 Perfetto 才能被完整还原。
- [[Concepts/RenderThread|RenderThread]] `(observes[中])`：Perfetto 能把 UI 线程、RenderThread、Frame Timeline 和合成相关轨道放到同一时间线上，是掉帧分析的重要入口。
- [[Concepts/Dominator Tree|Dominator Tree]] `(contrasts[中])`：Perfetto 解释“时间花在哪”，Dominator Tree 解释“对象为什么活着”；二者共同构成运行时排障地图。

## 记住“先找第一处变宽或变空”，再用三个问题复盘
### 记忆锚点 / Memory Anchor
- **一句话记住**：Perfetto 不是看彩条，而是沿着统一时间线找“第一处变宽或变空的时间段”。
- **看到这个信号就想到它**：知道用户觉得慢，却说不清慢在主线程、Binder、RenderThread 还是调度等待上。
### 自测问题
1. 为什么 Perfetto 不是“抓 trace 就结束”的工具？
2. 启动慢、Binder 阻塞、RenderThread 掉帧，为什么都能被 Perfetto 放到同一条时间线上分析？
3. 什么问题应该转向 Dominator Tree，而不是继续在 Perfetto 里找答案？
