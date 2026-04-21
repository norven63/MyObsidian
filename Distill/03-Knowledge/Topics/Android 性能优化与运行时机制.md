---
标识: topic-android-performance-runtime
标题: Android 性能优化与运行时机制
标签: [topic, android-performance]
来源:
  - '2026-04-10-资深Android架构师面试核心考点深度复盘与解析'
  - '2026-04-10-Android系统性能优化与底层机制深度解析'
  - '2026-04-10-Android-资深架构面试核心考点深度解析报告'
  - '2026-01-14-性能优化：Perfetto查看app启动时间及冷热启动介绍'
  - '2026-02-07-一个实用的Android-Perfetto分析器'
  - '2026-01-10-Android-一篇理透Binder机制'
  - '2026-02-01-安卓系统框架init.rc启动、Binder原理和binder调用framework层原理解析'
  - '2026-02-22-Android-启动模式详细解析'
关联概念:
  - 'InputManagerService'
  - '硬件层缓存'
  - 'RenderThread'
  - 'Dominator Tree'
  - 'Binder IPC'
  - 'Perfetto'
  - 'Activity 启动模式'
关联主题:
  - '知识图谱总纲'
层级: 专题
状态: stable
更新日期: 2026-04-12
---

# Android 性能优化与运行时机制

## 这篇主题在图谱中的位置
- 上级主题：[[Topics/知识图谱总纲|知识图谱总纲]]
- 本专题职责：把启动、输入、IPC、渲染、内存与 tracing 放回同一条 Android 运行时诊断主线，而不是拆成零散面试点。
- 为什么值得单独学：很多 Android 性能问题不是“某个 API 用错了”，而是用户症状、系统链路与诊断证据分散在不同层；本专题的价值就是把这些层重新缝回一张可执行的问题地图。
- 默认语境 / 术语 / 版本假设：默认讨论 Android 12–14 上的应用层与 framework 交界处诊断；“启动”同时包含冷 / 温 / 热启动与首帧可见，“导航”指 task / back stack / launchMode / Intent Flags，“系统服务 IPC”主要指 app 与 system_server 间 Binder 往返，“输入时延”指事件进入系统到用户看到第一份反馈，“渲染时延”指 UI 线程录制、RenderThread、GPU、SurfaceFlinger 的整段交付，“对象滞留”指对象仍被强引用或被缓存策略长期保活。
- 相邻专题：本专题只讨论 Android 运行时因果链，不展开通用工程治理；它更像一份“先判位、再抓证据、最后定根因”的排障型讲义。
- 建议阅读顺序：先用本专题建立“症状 → 链路 → 第一证据”的总图，再沿 [[Concepts/Perfetto|Perfetto]]、[[Concepts/Binder IPC|Binder IPC]]、[[Concepts/RenderThread|RenderThread]]、[[Concepts/Dominator Tree|Dominator Tree]] 逐个下钻。

## 读完后你应该会回答的问题
1. 当用户说“启动慢、点了没反应、滑动掉帧、返回栈怪、内存一直涨”时，你能先把症状落到哪条运行时链路，而不是直接猜单点原因？
2. [[Concepts/Activity 启动模式|Activity 启动模式]]、[[Concepts/Binder IPC|Binder IPC]]、[[Concepts/InputManagerService|InputManagerService]]、[[Concepts/RenderThread|RenderThread]]、[[Concepts/Perfetto|Perfetto]]、[[Concepts/Dominator Tree|Dominator Tree]] 分别回答哪一段问题，它们为什么必须协同出现？
3. 面对不同症状时，第一份该看的证据分别是什么：task / back stack、Binder 事务、输入分发、Frame Timeline、heap dump，还是统一 trace？
4. 为什么 Android 运行时学习不该停留在“面试八股”，而应该升级为一套可复用的诊断顺序与证据判断框架？

## 先把全局图装进脑子
### 2.1 一屏总图
| 步骤 | 你先回答什么 | 常见选择 | 这一轮的目标 |
| --- | --- | --- | --- |
| **1. 先按症状分型** | 用户抱怨的是启动、点击没反应、滑动掉帧、回退异常，还是越用越重？ | 启动 / 导航、IPC、输入、渲染、内存 | 先确定主链路，不要把所有问题都混成“卡” |
| **2. 先抓第一证据** | 这类症状最值得先看的证据是什么？ | Perfetto、task / back stack、Binder、Frame Timeline、heap dump | 先拿到第一份能分流的证据，而不是直接猜根因 |
| **3. 再看 dominant wait / dominant owner** | 时间主要耗在哪段，或对象到底被谁保活？ | 等 system_server、晚在输入、晚在渲染、滞留在引用链 | 把“感觉慢”变成可定位的因果链 |
| **4. 最后决定往哪个概念下钻** | 下一步该补哪块专用知识？ | [[Concepts/Perfetto]]、[[Concepts/Binder IPC]]、[[Concepts/RenderThread]]、[[Concepts/Dominator Tree]] 等 | 让 Topic 先完成分流，再用 Concept 做深挖 |

### 2.2 问题地图
| 症状簇 | 先落到哪条链 | 第一份证据先看什么 | 最容易犯的误判 |
|---|---|---|---|
| 冷 / 温 / 热启动慢、通知跳转后回退异常 | 启动 / 导航链 | Perfetto 启动时间线、task / back stack、launchMode / Intent Flags | 只因为“慢”就先盯主线程函数耗时，忽略实例复用与系统服务准备 |
| 调系统服务时卡住、偶发 ANR、页面明明逻辑不重却迟迟不动 | 系统服务 IPC 链 | Binder transaction slice、线程状态、system_server 相关服务轨迹 | 把等待 system_server 误判成纯 App 代码慢 |
| 点击后半秒才有反应、滑动不跟手 | 输入链 | Input dispatch latency、焦点窗口、Choreographer 前后的线程切换 | 只看渲染，不看事件到底何时进到目标窗口 |
| 动画掉帧、首帧晚、主线程不忙但仍不流畅 | 渲染链 | Frame Timeline、RenderThread、SurfaceFlinger、GPU deadline | 以为主线程空闲就说明渲染一定没问题 |
| 内存越用越高、页面退出后对象还活着、GC 频繁 | 内存 / 对象滞留链 | heap dump、Dominator Tree、allocation / GC 节律 | 只看内存总量，不去证明“谁让对象活着” |
| 症状模糊、复现不稳、跨多层链路 | tracing / diagnostics 链 | 统一 Perfetto trace、复现脚本、关键时点 marker | 还没统一时间线就开始到处打日志和猜根因 |

### 2.3 主线全景
Android 运行时排障最重要的不是“知道更多名词”，而是先建立一个稳定的分流顺序：**先按用户症状分型，再把症状映射到链路，再挑第一份证据，再决定是否继续下钻。** 启动 / 导航链回答“为什么这次要新建实例、为什么回栈顺序和预期不一样、为什么从点击到首帧这么久”；Binder 和系统服务链回答“为什么线程明明没在干重活却还在等”；输入链和渲染链一起回答“为什么用户手已经滑了，但画面没及时跟上”；内存链回答“为什么对象应该死却还活着”；tracing / diagnostics 则负责把这些局部证据装进一条统一时间线。

把这条主线记清后，很多看似分散的 Android 题会自动归位。比如“点击没反应”不一定是渲染卡，也可能是输入分发晚、Binder 同步调用堵住，或者页面虽然启动了但任务栈复用错误导致用户其实没到目标页；“首帧正常但越用越卡”也不一定是 Frame 问题，可能是对象滞留、Bitmap / layer 缓存膨胀、GC 节律恶化。也就是说，Android 运行时学习的主线不是 API 清单，而是一张**症状 → 链路 → 证据 → 根因**的决策地图。

### 2.4 这条线先不展开什么
- 不展开业务接口本身的慢查询、服务端延迟与产品策略错误；这些会影响体验，但不属于本专题要讲清的 Android 运行时主线。
- 不深入 GPU driver、厂商内核、音视频编解码、NDK 锁竞争等更底层专题；本专题只把它们当作“需要继续转交的下一层证据入口”。
- 不把 Activity 启动模式、硬件层缓存、Perfetto 当成孤立“背诵点”；这里关心的是它们如何组成同一条诊断链，而不是名词定义本身。

## 把主线真正讲透
### 3.1 启动与导航：从一次点击到首帧可交互
- **30 秒答案**：启动问题本质上是“实例与任务栈决策 + 进程 / Activity 拉起 + 首帧准备”这三段链路的组合题；导航异常先问实例复用是否正确，时间异常先问首帧前卡在哪一段，二者都不该只靠 launchMode 背诵解决。
- **展开解释**：用户点图标、通知或 deeplink 之后，系统先决定是否复用现有 task / Activity，再决定是否要拉起进程、attach application、创建目标 Activity、完成布局与首帧。这里“跳转怪”和“启动慢”经常混在一起：前者更偏语义正确性，常由 [[Concepts/Activity 启动模式|Activity 启动模式]]、Intent Flags、task 组织导致；后者更偏时间分布，常由进程冷启动、ContentProvider / Application 初始化、Binder 请求系统服务、首屏布局或图片准备导致。把这两类问题分开，才能避免一边修改 launchMode 一边误以为自己在做性能优化。
- **关键机制 / 决策链**：
  1. 用户动作进入 ActivityTaskManager，系统先决定复用哪个 task、要不要新建实例，以及返回栈将如何组织。
  2. 如果需要真正拉起页面，进程初始化、Application / provider 准备、Activity 生命周期推进与首屏资源准备会依次发生。
  3. 用户真正感知到“启动完成”，不是 onCreate 结束，而是首帧可见且页面已可交互，因此需要把语义路径和时间路径放在同一张图里看。
- **诊断 / 应用抓手**：
  - 启动慢先看 Perfetto 的 process start、bindApplication、activity launch、first frame、binder wait；导航怪先看 taskId、back stack、launchMode / flags 与实际实例复用情况。
  - 如果“通知打开后返回错页”，优先回到导航语义；如果“每次冷启动都慢”，优先看初始化和首帧前的时间分布，而不是先调 launchMode。

### 3.2 系统服务 IPC：为什么线程看起来不忙，用户却还在等
- **30 秒答案**：很多 Android 运行时卡顿不是 App 自己在做重活，而是同步 Binder 调用把等待时间折叠回了发起线程；看见线程 blocked，不代表根因在本进程。
- **展开解释**：应用层大量关键动作都要穿过系统服务：启动 Activity 要找 ActivityTaskManager，窗口与焦点要找 WindowManager，包信息、内容提供者、输入、传感器、通知等也都依赖 Binder。只要调用链是同步的，system_server 或其他服务侧的排队、锁竞争、线程池饱和、慢服务逻辑，都会让发起线程表现为“没做多少事但一直没返回”。这也是为什么 Android 性能问题不能只盯 Java 栈：你看到的主线程空闲、短函数、偶发 stalled，背后可能是一段跨进程等待。
- **关键机制 / 决策链**：
  1. App 线程通过代理对象发起 transact，请求进入 Binder driver 并被路由到目标进程 / 线程池。
  2. 目标服务线程真正处理请求，期间可能再受锁、调度、队列深度或下游调用影响。
  3. 只有当服务端完成并返回，发起线程才继续执行，因此“等待谁”比“当前线程做了什么”更关键。
- **诊断 / 应用抓手**：
  - 先在 Perfetto 对齐 Binder transaction slice、blocked state、system_server 相关线程，再回到具体服务日志 / dumpsys 解释语义原因。
  - 如果点击后 UI 线程栈不重却仍卡顿，优先怀疑同步 Binder、锁竞争或服务端拥塞，而不是立刻重写页面逻辑。

### 3.3 输入链与渲染链：为什么“手到了，画面还没到”
- **30 秒答案**：流畅度不是单看主线程，而是从输入事件进入系统，到目标窗口拿到事件，再到 UI 线程录制、RenderThread 提交、SurfaceFlinger 呈现的整条交付链；任何一段错过 deadline，用户都会感觉“不跟手”。
- **展开解释**：触摸事件先进系统侧的输入读取与分发路径，经 [[Concepts/InputManagerService|InputManagerService]] 找到当前焦点窗口，再进入应用进程的 Looper、ViewRootImpl、Choreographer。随后主线程根据事件更新状态并录制 DisplayList，[[Concepts/RenderThread|RenderThread]] 再把绘制命令与 GPU / 合成链衔接起来。如果主线程太忙，输入会来不及消费；如果 RenderThread、SurfaceFlinger 或 GPU 侧错过 VSync，事件虽然已经处理，画面仍会晚到。[[Concepts/硬件层缓存|硬件层缓存]] 只能优化重复变换和重绘成本，不能替你修复错误的布局失效、频繁 invalidate 或输入分发排队。
- **关键机制 / 决策链**：
  1. 设备事件被系统读取并分发到目标窗口，决定“事件何时真正进到 App”。
  2. App 主线程完成业务处理、measure / layout / draw 相关录制，决定“这帧内容何时准备好”。
  3. RenderThread、GPU 与 SurfaceFlinger 完成提交和呈现，决定“用户何时真正看见反馈”。
- **诊断 / 应用抓手**：
  - 先看输入分发延迟、Frame Timeline、RenderThread 与 SurfaceFlinger；把“事件晚到”与“画面晚呈现”拆开判断。
  - 如果主线程不忙但仍掉帧，优先看 RenderThread、GPU、合成链或 layer cache 是否频繁失效，而不是只看 Java 方法耗时。

### 3.4 内存与对象滞留：为什么页面退出了，对象却还活着
- **30 秒答案**：内存问题要区分“短时间分配过猛”与“生命周期结束后仍被保活”；前者看 allocation / GC 节律，后者看 heap dump 与 [[Concepts/Dominator Tree|Dominator Tree]]，不要只看一个总内存数字。
- **展开解释**：Android 应用常见问题不是“有内存就一定坏”，而是对象本该随着页面、任务或动画结束而死亡，却被 listener、Handler、协程、Adapter、单例、Bitmap 缓存、View 树、硬件层或 Context 链条继续强引用。另一类问题则是对象并没有永久泄漏，但因为频繁创建大对象、图片解码或列表抖动，导致 allocation burst 和 GC pause 让体验持续恶化。前者回答“为什么活着”，后者回答“为什么分配得这么猛”。这也是 [[Concepts/Dominator Tree|Dominator Tree]] 与 Perfetto 不能互相替代的原因。
- **关键机制 / 决策链**：
  1. 对象因页面进入、图片加载、动画或缓存策略被创建，本该随生命周期结束而失效。
  2. 如果仍存在强引用链或缓存淘汰策略错误，GC 就无法回收，对象会继续支配更多子对象存活。
  3. 当 retained set 或 allocation / GC 节律持续恶化时，问题会从“内存高”进一步扩散成卡顿、频繁 GC 甚至 OOM。
- **诊断 / 应用抓手**：
  - 怀疑泄漏先抓 heap dump，看 Dominator Tree、retained size、引用链；怀疑抖动先看 allocation、bitmap 峰值与 GC 频率。
  - 如果“首帧正常但越用越重”，不要只盯 Frame trace；先确认页面退出后相关 Activity、View、Bitmap、layer 是否真的消失。

### 3.5 用 tracing 组织全局诊断：先统一时间线，再下钻专用证据
- **30 秒答案**：[[Concepts/Perfetto|Perfetto]] 不是万能工具，但它是最好的总装配台：当你还不能确定问题属于启动、IPC、输入、渲染还是内存时，先用 trace 把用户动作与系统时间线对齐，再决定下一步该去 heap、back stack 还是服务日志。
- **展开解释**：实践里最浪费时间的事情，是一开始就在单层证据上打转：只看日志、不对时间；只看 Java profiler、不知道 system_server 在等什么；只看 heap、不知道症状发生在哪个操作之后。更可靠的顺序是：先固定复现场景，给用户动作加 marker 或明确时间点，采集能覆盖 app / system / frame 的 trace，再看 dominant wait 在哪一段。如果 dominant wait 已经很清楚，沿那条链继续深挖；如果时间线正常但对象持续滞留，就转 heap dump；如果时间问题不大但返回栈异常，就转 task / navigation 证据。也就是说，Perfetto 的价值不是“替代所有工具”，而是让你知道哪一个工具现在最值得用。
- **关键机制 / 决策链**：
  1. 先把场景复现做稳定：同一入口、同一操作、同一设备状态，否则任何 trace 都很难比较。
  2. 再把用户动作、线程状态、Binder、Frame Timeline、进程生命周期对齐，确认 dominant wait / dominant stall 在哪条链上。
  3. 最后把统一 trace 转成专用证据分流：启动 / 导航去 task 与初始化，IPC 去服务端，渲染去 RenderThread / SurfaceFlinger，内存去 heap dump。
- **诊断 / 应用抓手**：
  - 一句话记法：时间问题先 trace，语义问题看导航，保活问题看 heap，跨层模糊问题先统一证据口径。
  - 每次排障都问自己两个问题：第一份证据是否已经能证明“谁在等谁 / 谁让谁活着”？如果不能，就别急着下结论。

### 3.6 完整案例推演
- **场景**：用户反馈“从通知点进详情页后，页面首屏有时很慢，点按钮第一下也没反应，返回时还偶尔回到奇怪的页面”。这是典型的启动 / 导航、Binder、输入、渲染多条链纠缠在一起的症状。
- **先看什么 / 第一证据**：先把一次稳定复现的 Perfetto trace 和当次 task / back stack 快照放在一起看；不要先盯某个 Java 方法或某个 launchMode 配置。
- **推演链 / Decision Path**：
  1. 先用 task / back stack + launchMode / flags 判断“回退异常”是不是语义问题；如果语义已经错了，先修导航链，不要把它误当成纯性能问题。
  2. 如果语义正确但首帧明显偏晚，沿 Perfetto 看 process start、bindApplication、binder wait、activity launch、first frame，确认时间主要耗在初始化、系统服务还是首帧准备。
  3. 如果首帧出来后“第一下点击没反应”，继续看输入分发是否晚到目标窗口，还是事件已经到达但 RenderThread / SurfaceFlinger 让反馈晚呈现。
  4. 如果问题只在多次进入退出后越来越明显，再补 heap dump 与 Dominator Tree，检查是否存在页面对象、Bitmap 或 layer 长期滞留。
- **结论 / 迁移**：Android 性能排障最怕一上来就猜单点原因。先按“语义是否正确 → 第一份时间证据 → 输入与渲染谁更慢 → 是否存在对象滞留”分流，才能把跨层症状拆回可执行判断。

## 把关键概念重新串成一张图
### 4.1 为什么这组概念必须一起看
这组概念之所以必须一起看，是因为 Android 运行时症状天然跨层。[[Concepts/Activity 启动模式|Activity 启动模式]] 只解释实例与任务栈，不解释时间分布；[[Concepts/Binder IPC|Binder IPC]] 解释跨进程等待，不解释输入事件何时到达；[[Concepts/InputManagerService|InputManagerService]] 解释事件入场，不解释帧何时呈现；[[Concepts/RenderThread|RenderThread]] 解释渲染提交，不解释对象为什么一直活着；[[Concepts/Perfetto|Perfetto]] 给出统一时间线，但不证明引用链；[[Concepts/Dominator Tree|Dominator Tree]] 证明保活关系，但不解释用户那一秒为什么觉得慢。只有把它们放在同一条主线上，你才能既回答“症状属于哪段链”，又回答“第一份证据该看什么”。

### 4.2 概念分工表
| 概念 | 在这条主线里负责什么 | 如果缺它会漏掉什么 |
|------|----------------------|--------------------|
| [[Concepts/Activity 启动模式]] | 解释页面实例复用、task 组织、返回栈语义 | 会把导航异常错当成纯性能问题，或把时间问题误改成 launchMode 配置 |
| [[Concepts/Binder IPC]] | 解释 app 与系统服务之间的同步等待、排队与返回 | 会把 system_server 的延迟误判成 App 本地代码慢 |
| [[Concepts/InputManagerService]] | 解释输入事件何时被读取、路由、分发到目标窗口 | 会看见“滑动不跟手”却不知道事件到底晚在进入系统还是晚在应用消费 |
| [[Concepts/RenderThread]] | 解释渲染命令提交、与 GPU / 合成链的协作 | 会错误地把所有掉帧都归咎于主线程 |
| [[Concepts/硬件层缓存]] | 解释某些动画为什么能更快，以及缓存失效为什么会反噬内存与重绘 | 会把 layer 当万能开关，忽略缓存成本与失效时机 |
| [[Concepts/Perfetto]] | 负责把启动、Binder、输入、渲染、调度放到同一时间线上 | 会失去跨层因果链，只剩零散日志和局部 profiler |
| [[Concepts/Dominator Tree]] | 负责证明对象为什么仍然存活、谁支配了 retained set | 会知道“内存高”，却无法证明“哪条引用链让它高” |

### 4.3 关键连接
- [[Concepts/Activity 启动模式|Activity 启动模式]] ↔ [[Concepts/Binder IPC|Binder IPC]]：一次页面拉起既有 task / instance 语义，也常伴随对 ActivityTaskManager、PackageManager、WindowManager 的跨进程请求；“能不能复用”和“为什么还在等”往往同时出现。
- [[Concepts/InputManagerService|InputManagerService]] ↔ [[Concepts/RenderThread|RenderThread]]：输入链决定事件何时进入 App，渲染链决定反馈何时出现在屏幕上；用户感知的流畅度是两段串起来后的总时延。
- [[Concepts/RenderThread|RenderThread]] ↔ [[Concepts/硬件层缓存|硬件层缓存]]：layer cache 的收益只在渲染路径里成立，一旦频繁失效或生命周期失控，就会把优化项变成额外内存与重绘成本。
- [[Concepts/Perfetto|Perfetto]] ↔ [[Concepts/Binder IPC|Binder IPC]] / [[Concepts/InputManagerService|InputManagerService]] / [[Concepts/RenderThread|RenderThread]]：前者提供统一时间坐标，后者提供具体语义解释；没有统一时间线，单点概念很难串成因果链。
- [[Concepts/Perfetto|Perfetto]] ↔ [[Concepts/Dominator Tree|Dominator Tree]]：Perfetto 解释“慢发生在什么时候、谁在等待谁”，Dominator Tree 解释“对象为什么没死”；时间证据与对象证据必须互补使用。

## 容易混淆的地方与边界
### 5.1 常见误解
- “所有卡顿都先看主线程”——错误。同步 Binder、输入分发、RenderThread、SurfaceFlinger、GPU deadline 都可能是主因。
- “launchMode 调好了就算做了启动优化”——错误。launchMode 主要解决导航与实例复用语义，不直接替代初始化、渲染和系统服务耗时分析。
- “开硬件层就一定更流畅”——错误。缓存只有在重绘模式与失效时机合适时才有收益，滥用会转成额外内存与更新成本。
- “抓一次 Perfetto 就能解释所有问题”——错误。Perfetto 擅长回答时间和等待关系，不负责证明对象保活根因。

### 5.2 适用边界
- 适用于启动慢、导航异常、系统服务调用卡顿、输入不跟手、动画掉帧、内存滞留与跨层 tracing 等 Android 运行时问题。
- 适用于希望把“八股知识点”升级成“第一份证据怎么选、后续怎么分流”的系统学习者与实际排障场景。
- 适用于以现代 Android 诊断工具链为主的分析路径：Perfetto、Frame Timeline、heap dump、task / dumpsys、服务日志。

### 5.3 不适用边界
- 不适用于把网络接口慢、后端排队、业务策略错误直接包装成 Android 运行时问题；那类问题需要回到服务端或产品流程。
- 不适用于需要深入厂商定制内核、GPU driver、ART 内部实现、音视频 pipeline 的专题；本专题只负责把你送到正确入口。
- 不适用于没有稳定复现场景的“玄学问题”；如果复现条件不固定，先收敛场景，比继续讨论概念更重要。

### 5.4 高频追问
- 启动慢时先看 [[Concepts/Activity 启动模式|Activity 启动模式]] 还是 [[Concepts/Perfetto|Perfetto]]？——如果是“回退错乱 / 复用异常”，先看导航语义；如果是“就是慢”，先看 Perfetto 把首帧前时间切开，再决定要不要回到 launchMode。
- 点击后没反应，但主线程函数耗时并不高，下一步看什么？——先查输入分发是否晚到、是否卡在同步 Binder、Frame Timeline 是否错过 deadline，再决定是输入链还是渲染链问题。
- 为什么明明首帧正常，App 用久了还是越来越卡？——常见原因是 retained object、图片 / layer 缓存膨胀或 allocation / GC 节律恶化；这时应把 heap dump 与运行时 trace 联合看。
- 为什么 trace 里已经看见 Binder wait，还要继续看 system_server 或具体服务？——因为 trace 证明了“等待发生在哪”，但真正的语义根因仍可能在服务端锁、队列深度、策略或下游调用上。

## 复盘框架与自测
### 6.1 记忆框架
- **先分症状**：先把问题分到启动 / 导航、IPC、输入、渲染、内存、诊断六类，而不是先猜 API。
- **再找链路**：问自己用户动作是怎样进系统、进进程、进渲染、进对象生命周期的。
- **再抓第一证据**：时间问题优先 trace，语义问题优先 task / navigation，保活问题优先 heap dump。
- **最后定根因**：把结论写成“谁在等谁、谁让谁活着、哪一层先失真”，而不是写成模糊的“感觉这里有点卡”。

### 6.2 自测问题
1. 如果用户抱怨“点击通知进详情页后，返回键经常回到奇怪页面，而且偶尔还很慢”，你会怎样拆成导航语义问题和时间问题两条线？
2. 为什么“主线程并不忙”不能推出“不是 Android 性能问题”，反而可能提示你去看 Binder、RenderThread 或输入分发？
3. 当你在 Perfetto 里看到首帧并不慢，但页面退出后内存长期不降，你为什么应该把主要精力切到 heap dump 与 Dominator Tree？
4. 请说出一个“表面像渲染卡，实际更可能卡在系统服务或输入链”的场景，并说明第一份证据是什么。
5. 如果你只能给新人留一句诊断口诀，这句口诀应该如何同时覆盖启动、渲染与内存问题？
- **一句话复盘**：Android 性能与运行时学习的核心，不是多背几个名词，而是先把症状映射到正确链路，再用正确证据证明谁在等待、谁在保活、哪一段真正失真。

## 证据锚点与下一步
### 7.1 证据锚点
- **先读哪篇 Source**：[[Sources/2026-04-10-Android系统性能优化与底层机制深度解析]] —— 用它先建立启动、输入、渲染、缓存与 tracing 的总图，因为它最接近本专题的全链路视角。
- **再补哪个概念**：[[Concepts/Perfetto|Perfetto]] —— 当你能先看时间线再下钻，后续学习 Binder、RenderThread 和启动细节才不会散掉。
- **继续交叉验证**：[[2026-01-10-Android-一篇理透Binder机制]] / [[Concepts/Binder IPC|Binder IPC]] —— 把“线程为什么在等”从抽象说法落到真实跨进程调用语义。
- **再把启动问题补完整**：[[2026-01-14-性能优化：Perfetto查看app启动时间及冷热启动介绍]] / [[Concepts/Activity 启动模式|Activity 启动模式]] —— 前者统一冷 / 温 / 热启动与首帧口径，后者补齐实例复用和返回栈语义。
- **再补运行时综述 Source**：[[Sources/2026-04-10-资深Android架构师面试核心考点深度复盘与解析]] —— 用它把输入、渲染、内存与 tracing 的跨层可观测性装回同一张图。
- **最后补对象证据**：[[Sources/2026-04-10-Android-资深架构面试核心考点深度解析报告]] / [[Concepts/Dominator Tree|Dominator Tree]] —— 把“内存高”升级成“能证明谁支配了对象存活”的能力。
- **需要行动顺序时**：[[Guides/Android 运行时性能分诊与证据顺序手册]] —— 当你已经知道主题主线，但需要“现在第一份证据看什么”的执行顺序时，直接走这份手册。

### 7.2 推荐学习顺序
1. 先吃透本专题第 2 节的问题地图，并用 [[Concepts/Perfetto|Perfetto]] 学会把症状统一成一条时间线。
2. 再把启动 / 导航与 [[Concepts/Binder IPC|Binder IPC]] 放在一起学，建立“页面为什么没来 / 为什么来的慢”这条因果链。
3. 接着联学 [[Concepts/InputManagerService|InputManagerService]]、[[Concepts/RenderThread|RenderThread]]、[[Concepts/硬件层缓存|硬件层缓存]]，把“手到了、画面没到”的链条串起来。
4. 最后补 [[Concepts/Dominator Tree|Dominator Tree]] 与 heap dump，把“越用越重”纳入同一套证据判断方法。

### 7.3 缺口提醒
- 如果你还不能对每类症状说出“第一份证据先看什么”，说明你现在记住的还是概念清单，不是诊断地图。
- 如果你能看 trace，却说不清 task / back stack、Binder wait、Frame Timeline、retained object 之间的分工，说明你还没有真正把跨层因果链串起来。
- 下一步最值得补的，不是再背更多术语，而是拿一个真实启动慢 / 掉帧 / 内存涨案例，按“症状 → 链路 → 证据 → 根因”完整走一遍。
