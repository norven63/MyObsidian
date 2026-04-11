---
标识: concept-dominator-tree
标题: Dominator Tree
标签: [concept, android-memory]
别名: [支配树]
来源:
  - '2026-04-10-Android-资深架构面试核心考点深度解析报告'
  - '2026-04-10-Android系统性能优化与底层机制深度解析'
  - '2026-04-10-资深Android架构师面试核心考点深度复盘与解析'
关联概念:
  - 'InputManagerService'
  - 'RenderThread'
状态: stable
定义: Dominator Tree 是把对象引用图压缩成支配关系树的分析模型，用来判断“哪个对象必须先释放，后面的对象才可能被回收”。
---

# Dominator Tree

## 1. 它是什么 (What It Is)
### 快速判断 / Quick Scan
| 维度 | 内容 |
| --- | --- |
| 一句话定义 | Dominator Tree 是把堆对象引用图折叠成“谁支配谁存活”的树形视图，用来回答“先释放谁，才能让后面一大片对象跟着回收”。 |
| 不要和什么混为一谈 | 它不是单纯的大对象排行榜，也不是看到某条引用链就结束；真正关心的是所有到达路径是否都要先经过同一个上游持有者。 |
| 什么时候想到它 | Heap dump 里 Retained Heap 异常、Histogram 只能看到“谁多”却解释不了“为什么活着”、怀疑 Activity / Bitmap / 缓存泄漏时，就该想到它。 |

### 展开理解
- 支配树把复杂对象图转成“控制回收权”的结构。它逼你从“哪个对象最大”转向“哪个对象卡住了整片子树的释放”。
- 对泄漏排查来说，它最有价值的地方不是展示数据，而是提供归因逻辑：如果不先切断支配节点，清理叶子对象往往只是表面工作。

## 2. 为什么它重要 (Why It Matters)
### 它解决的判断 / 工程问题
- 它解决“到底是谁让这些对象一直活着”的判断问题。内存问题最怕看到一堆大对象，却不知道该从哪个生命周期持有者下刀。
- 它解决“修末端还是修上游”的工程问题。通过 retained heap 与支配关系，你能优先处理那个真正控制回收结果的上游容器、单例、回调链或缓存入口。

### 如果忽略它会怎样
- 你会不停盯着 Bitmap、Adapter、Fragment 这些肉眼看起来大的对象，却忽略真正把它们绑住的小 Map、小 List 或错误注册的 listener。
- 你也容易把“实例数变多”误当根因；但实例只是症状，支配树才解释谁让这些实例无法变成垃圾。

## 3. 它是怎么工作的 (How It Works)
### 机制链 / Mechanism Chain
1. 分析器先对 heap dump 从 GC Root 出发构建可达图，记录对象之间的全部引用路径。
2. 然后计算 immediate dominator：如果从任意 GC Root 到对象 Y 的所有路径都必须经过 X，那么 X 支配 Y。
3. 工具把被支配子树的大小向上聚合，形成 Retained Heap——表示“如果 X 消失，这一大片内存理论上就可能一起释放”。
4. 于是排查重点从“谁本体最大”转成“谁控制了最多子孙对象的存活”；很多真正的根因是一个看起来不大的 owner、singleton 或 cache entry。
5. 修复时要切断支配关系：解绑 listener、清空错误缓存、缩短 lifecycle 持有，而不是只清理被支配的叶子对象。

### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- **排查时先问**：这个节点 retained heap 大，是因为它自己大，还是因为它支配了一大片对象子树？如果只看 shallow size，容易看错方向。
- **设计时先问**：这个对象到底拥有谁的生命周期？它是否把 Activity / View / Bitmap / 回调塞进了一个比它们更长寿的容器里？
- **常见观察信号**：小容器支配巨大 retained heap、同类 Activity/Fragment 挂在同一上游单例下、清掉叶子对象后内存仍不降，都是典型的支配关系问题。

## 4. 一个最小例子 / 对比 (Minimal Example / Contrast)
### 最小例子
- **场景**：一个全局单例的缓存管理器里留着 Activity 的 listener，同时这条链下面还挂着 View、Bitmap 和 Adapter。
- **为什么这里会想到它**：Histogram 最先告诉你“Bitmap 很大”，但 Dominator Tree 会进一步告诉你：真正控制这片内存存活的，是那个长寿命单例，而不是末端的 Bitmap 本身。
- **结果**：只要解绑 listener 或修正单例持有策略，整片 retained heap 会一起下降；如果只清 Bitmap，很快还会被同一条错误持有链重新拖住。

### 对比
| 易混概念 / 做法 | 真正差异 | 这里为什么不是它 |
| --- | --- | --- |
| Histogram | 告诉你“谁多 / 谁大” | 这里真正要回答的是“谁控制这些对象继续活着”，不是只看数量和体积 |
| 单条引用链 / Leak Trace | 只能证明“存在一条路径能到达它” | 支配关系要求看“所有路径都绕不开谁”，否则未必是真正的上游控制者 |
| Perfetto 时间线 | 解释时间消耗和线程阻塞 | 这里的问题是对象为什么被保活，而不是哪段执行更慢 |

## 5. 常见误解与边界 (Mistakes & Boundaries)
### 常见误解
- “最大的对象就是根因。”很多时候，真正的泄漏口是支配整棵子树的小容器或错误 owner，而不是最重的叶子节点。
- “看到 Activity leak trace，就只修 Activity。”如果不处理上游单例、缓存或注册关系，Activity 只是最先暴露出来的受害者。

### 失效 / 反噬信号
- 你不断清理末端对象却不见内存下降，或每次 dump 都是同一个上游节点挂着大 retained heap，说明真正的支配节点还没有被处理。
- OOM 前总能看到一类对象堆积，但修完表面对象后问题很快复发，也常常意味着上游持有关系没动到。

### 不适用场景
- Dominator Tree 解释的是对象存活关系，不解释线程调度、首帧时序或输入延迟；时间问题仍应交给 Perfetto 一类工具。
- 如果你只是在判断“这一帧为什么掉了”或“某次 Binder 为什么慢”，支配树不是首选抓手。

## 6. 与哪些概念容易一起出现 (Nearby Concepts)
- [[Concepts/InputManagerService|InputManagerService]] `(context[弱])`：IMS 不是内存工具，但排障时常要把“事件慢”与“对象没释放”分开；支配树负责回答后者。
- [[Concepts/RenderThread|RenderThread]] `(complements[弱])`：Bitmap、纹理和渲染资源最终也可能通过某个错误 owner 被长期持有，Dominator Tree 能补上“为什么资源没掉”的那半张图。
- [[Concepts/Perfetto|Perfetto]] `(contrasts[中])`：Perfetto 解释时间消耗，支配树解释对象图；一个看关键路径，一个看关键持有者。

## 7. 来源对照 (Source Cross-check)
- **来源 1** ([[2026-04-10-资深Android架构师面试核心考点深度复盘与解析]])：把 Retained Heap 直接和支配关系挂钩，提醒不要只看实例数。
- **来源 2** ([[2026-04-10-Android-资深架构面试核心考点深度解析报告]])：强调真正根因往往是上游持有者，不一定是末端大对象本身。
- **来源 3** ([[2026-04-10-Android系统性能优化与底层机制深度解析]])：把 Dominator Tree 放进内存优化流程，说明它是从“看到异常”走向“证明泄漏”的关键步骤。
- **我的整合结论**：支配树最大的教学价值，是把泄漏排查从“经验猜谁没释放”升级成“图结构证明谁控制了回收权”。先找支配者，再谈清理细节。

## 8. 自测问题 (Self-Test)
### 记忆锚点 / Memory Anchor
- **一句话记住**：Dominator Tree 不先问“谁最大”，先问“谁不死，别人就都死不了”。
- **看到这个信号就想到它**：Histogram 里看见一堆大对象，但删末端没用；retained heap 一直挂在某个小 owner 下面。

### 自测问题
1. 为什么 Histogram 发现异常后，通常还要切到 Dominator Tree 才能真正定位根因？
2. “X 支配 Y” 与 “X 只是引用到 Y” 有什么本质区别？
3. 如果一个小 Map 支配了一整片 Activity 与 Bitmap，你的修复动作应该落在哪一层？
