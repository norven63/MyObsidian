---
标识: concept-activity-launch-mode
标题: Activity 启动模式
标签: [concept, android-app-runtime]
别名: [LaunchMode, Activity Launch Mode]
来源:
  - '2026-02-22-Android-启动模式详细解析'
关联概念:
  - 'ActivityManagerService'
  - 'Binder IPC'
  - 'Perfetto'
状态: stable
定义: Activity 启动模式是 Android 在处理 `startActivity()` 请求时，用来决定实例复用、Task 归属和返回栈重排规则的运行时契约；真正结果由 `launchMode`、`Intent Flags`、`taskAffinity` 与当前栈状态共同决定。
---

# Activity 启动模式

## 启动模式真正管理的，不是页面能不能打开，而是任务栈会被怎么改写
### 一眼认知骨架
- **对象**：一次 `startActivity()` 发生时，系统如何决定新建实例、复用实例、放进哪个 Task。
- **目的**：让多入口导航、返回路径和最近任务列表保持可预期，而不是越跳越乱。
- **组成**：`launchMode`、`Intent Flags`、`taskAffinity`、现有 `Task` / `ActivityRecord`、`onNewIntent()` 回调。
- **主线**：发起跳转 → 查找可复用实例 / Task → 决定新建还是复用 → 必要时清理栈顶 → 回到 `onCreate()` 或 `onNewIntent()`。
- **变体**：`standard`、`singleTop`、`singleTask`、`singleInstance` / `singleInstancePerTask`，以及 `NEW_TASK`、`CLEAR_TOP`、`MULTIPLE_TASK` 等 flag 组合都会改写结果。
- **用法**：最适合解释通知 / 深链二次进入、首页多入口、返回键错乱、重复详情页和任务切换异常。
### 快速判断 / Quick Scan
- 如果只用一句话说清，启动模式不是“怎么把页面打开”，而是“这次打开要不要改写已有历史”。
- 你最容易把它和 Nav API、页面路由表混为一谈；但它真正约束的是系统级 Task 与实例复用，而不是代码里写了哪个 destination。
- 一旦你开始追“为什么返回顺序和打开顺序不一致”“为什么通知点进来没新建页面”“为什么最近任务里多了一份副本”，就已经进入启动模式的判定范围。
### 展开理解
启动模式的学习难点，不在四个名词本身，而在**入口语义怎样落成运行时栈结果**。同一个详情页，从列表进入时通常希望自然入栈；从通知或深链再次进入时，可能更希望复用旧实例并把那个 Task 拉回前台。系统之所以要把这件事做成显式规则，是因为导航问题一旦跨进程、跨任务、跨最近任务列表，就不能再交给页面自己“猜一下应该怎么回退”。

## 系统宁可把导航语义写进 launchMode 和 Intent Flags，也不愿让每次跳转都靠页面自己猜
### 它解决的判断 / 工程问题
启动模式要解决的是：**当同一个 Activity 可能被多个入口、多次调用、多种任务上下文命中时，系统怎样稳定决定“复用谁、清掉谁、回退到哪”。** 如果没有这层统一规则，通知、桌面图标、应用内跳转、分享面板和深链接都会各自制造一套历史，用户看到的返回行为会越来越不可预测。
### 如果忽略它会怎样
如果忽略这一层，你很容易把“返回栈乱了”“页面又开了一个”“回退直接回桌面”误判成 UI Bug 或者 Nav 库问题。实际上，很多异常是系统在 `launchMode + flags + taskAffinity` 这层做了与你预期不同的实例复用与 Task 选择；你若只盯页面代码，等于把真正决定行为的那一层看丢了。
### 为什么系统宁可这样设计 (Design Rationale / Trade-off)
系统没有把“是否复用旧实例”做成某个 Activity 自己随手决定的局部策略，而是让 `launchMode` 与 `Intent Flags` 进入统一启动链。这样换来的好处是：最近任务、跨应用入口、进程重建后的恢复语义都能遵守同一套规则；代价则是规则组合变多，`onCreate()` 与 `onNewIntent()` 的分叉、`singleTask` 与 `NEW_TASK` 的联动、以及 `CLEAR_TOP` 的清栈副作用都必须显式理解。也就是说，系统宁可让模型更严格，也不愿让导航语义在不同入口下各说各话。

## 真正决定结果的是复用判定、Task 选择与 Flag 合成，而不是单看 singleTop 这几个名词
### 机制链 / Mechanism Chain
1. 调用方发起 `startActivity()` 后，请求会穿过 instrumentation / Binder 进入系统启动链；系统先拿到目标 `ActivityInfo`、调用方上下文以及本次 `Intent Flags`。
2. 系统把 `launchMode`、`taskAffinity`、当前所在 `Task`、现有 `ActivityRecord` 一起纳入判断：它不是只看目标页面配置了什么，而是同时看“现在栈里已经有什么”。
3. 如果命中可复用实例，系统会决定是直接把 `Intent` 送给旧实例，还是把它所在 `Task` 搬到前台，并在必要时清理它上面的历史；如果没命中，就新建 `ActivityRecord` 与实例。
4. 这个分支会直接改写生命周期：新建通常走 `onCreate()`；复用通常走 `onNewIntent()`，并且可能伴随栈顶清理、Task 切换或最近任务重排。
5. 用户最终感知到的不是“系统用了哪种模式名字”，而是“我现在回到哪里、最近任务里是哪一份、这次进入是新上下文还是旧上下文”。
### 关键条件 / 分支 / 例外 (Critical Conditions / Exceptions)
- `singleTop` 只在**目标实例已经位于当前栈顶**时才避免新建；同一个页面如果已经在栈里但不在顶部，仍然可能再创建一个。
- `singleTask` / `singleInstance` 关注的是 Task 级别的唯一性；一旦命中旧实例，常见结果不是“原地刷新一下”，而是把那个 Task 搬回来，并处理它上面的历史。
- `FLAG_ACTIVITY_CLEAR_TOP` 不是单纯“找到旧页就复用”，而是可能先把目标页之上的 Activity 全部清掉，再把新的 `Intent` 交给目标实例。
- `FLAG_ACTIVITY_NEW_TASK` 与 `taskAffinity` 会共同影响 Task 归属；这也是为什么有些页面会出现在新的最近任务里，而有些只是在原任务中重排。
- Android 新版本里的 `singleInstancePerTask` 进一步说明：系统关心的从来不只是“有没有实例”，而是**实例与 Task 边界是否仍然一致**。
### 最低决定层 / 关键锚点 (Decisive Layer Anchors)
- 真正决定结果的，不是某一个 `singleTop` / `singleTask` 名词，而是 `ActivityInfo.launchMode + Intent flags + taskAffinity + 当前 ActivityRecord / Task` 这组组合。少看任何一个，你都会把结果看歪。
- `onCreate()` 和 `onNewIntent()` 是最直接的分流证据：前者更接近新建实例，后者更接近旧实例接收新语义；如果你只看页面长得像不像新页面，很容易误判。
- `CLEAR_TOP`、`NEW_TASK`、`MULTIPLE_TASK` 这类 flag 会把 Manifest 里的静态配置改写成运行时分支；忽略 flag，你几乎一定会把“清栈”误读成“系统随机抽风”。
- 启动模式只解决“实例与 Task 语义”，不直接回答“为什么这次启动很慢”；如果把时间问题也塞给它，就会看丢真正的系统等待层。
### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- 先定义业务预期：这次进入到底是“自然入栈”还是“回到旧任务并刷新内容”。没有语义预期，任何模式都可能被误用。
- 同时记录 `taskId`、生命周期回调和 `Intent Flags`；只看页面现象，不看 `onNewIntent()` / `onCreate()` 与 Task 变化，定位会一直漂。
- 如果既有“回退错乱”又有“这次特别慢”，先拆成两件事：前者看 Task / 实例复用，后者交给 [[Concepts/Perfetto|Perfetto]] 或系统启动链，不要混成一个结论。

## 一个通知二次进入详情页的场景，最能看清“新建”和“复用”的差别
### 最小例子
- **场景**：用户先从商品列表进入详情页 A，随后又从通知点击进入同一商品详情页 A。
- **为什么这里会想到它**：列表入口通常希望“顺着当前任务继续走”，而通知入口往往更像“把那份已有任务找回来，或者按新的任务语义重新组织历史”。
- **结果**：如果模式与 flags 配对正确，用户会觉得“回到了原来的详情上下文”；如果设计错误，就会出现两份详情页并存、回退路径断裂，甚至最近任务里多出一个不该存在的副本。
### 对比
- **Nav API / 路由表**：它们负责表达“我要去哪个页面”，但不单独决定旧实例是否复用、Task 是否重排。
- **[[Concepts/ActivityManagerService|ActivityManagerService]]**：AMS / ATMS 负责把启动请求接进系统并执行；启动模式负责其中“实例 / Task 语义”这一层，不等于整条系统启动链。
- **[[Concepts/Perfetto|Perfetto]]**：Perfetto 更适合回答“为什么这次启动慢”，而不是“为什么这次回退路径变了”。

## 把启动模式学歪之后，最常出现的是回退错乱和历史被意外清空
### 常见误解
- “返回栈不对就统一改成 `singleTask`。” 这是最典型的看歪：它可能消掉重复实例，却把用户原本需要保留的历史也一起抹掉。
- “页面没重复就说明模式配对了。” 错。你还要看最近任务、回退路径、二次进入语义是否仍然符合业务预期。
### 失效 / 反噬信号
- 同一详情页被通知、列表、分享入口反复打开后，出现多份实例或回退直接跳桌面。
- 日志里 `onNewIntent()` 和 `onCreate()` 的实际分支与预期完全不符，或者最近任务列表出现不该出现的新任务。
- 某个页面明明只想刷新内容，却总是把上层历史一起清掉，说明 `CLEAR_TOP`、`NEW_TASK` 或 `taskAffinity` 的组合已经反噬。
### 不适用场景
- 如果返回栈完全正确，只是首帧出来得慢，优先看启动耗时、Binder 等待、进程初始化，而不是先调 launchMode。
- 如果问题发生在同一 Activity 内部的 Fragment / Compose 导航，启动模式只提供更外层的 Task / Activity 语义，不是主要抓手。

## Activity 启动模式总要和这些概念一起看
- [[Concepts/ActivityManagerService|ActivityManagerService]] `(decision[强])`：启动模式的语义最终要落进系统启动链，由 AMS / ATMS 把“复用谁、把哪个 Task 搬回来”真正执行出去。
- [[Concepts/Binder IPC|Binder IPC]] `(handoff[中])`：一次 `startActivity()` 并不是本地方法直接生效，而是要先穿过 Binder 边界进入系统服务，再做复用与清栈判定。
- [[Concepts/Perfetto|Perfetto]] `(observes[中])`：当“语义不对”和“启动很慢”同时出现时，Perfetto 帮你把时间问题先切开，避免把所有异常都甩给 launchMode。

## 先记住“这次进入会怎样改写历史”，再用三个问题检查自己
### 记忆锚点 / Memory Anchor
- **一句话记住**：启动模式不是“能不能打开页面”，而是“这次打开会怎样改写实例与 Task 历史”。
- **看到这个信号就想到它**：多入口进入同一页、返回路径不稳定、最近任务多副本、`onNewIntent()` 与预期不一致。
### 自测问题
1. 为什么说启动模式真正管理的是“Task 语义”，而不只是“页面实例个数”？
2. 列表入口和通知入口都指向同一详情页时，你会先定义哪类复用 / 回栈预期，再去选模式与 flags？
3. 如果页面打开得慢但回退语义完全正确，为什么不该先把问题归到启动模式上？
