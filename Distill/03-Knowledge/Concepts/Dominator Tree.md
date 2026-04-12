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
  - 'Perfetto'
  - '硬件层缓存'
  - 'RenderThread'
状态: stable
定义: Dominator Tree 是把堆对象引用图压缩成“谁不释放，谁下面这一片对象就都死不了”的支配关系树；它真正回答的是 retained heap 的控制权归属，而不只是对象有多大。
---

# Dominator Tree

## 支配树真正回答的，不是谁最大，而是谁不释放别人就都死不了
### 一眼认知骨架
- **对象**：heap dump 上的对象引用图与它的支配关系树，不是普通排行榜。
- **目的**：找出真正控制对象存活的上游持有者，而不是只看叶子对象谁最大。
- **组成**：GC Root、可达图、immediate dominator、retained heap、被支配子树。
- **主线**：dump heap → 从 GC Root 建图 → 计算支配关系 → 聚合 retained heap → 切断真正的支配节点。
- **变体**：大对象不一定支配整片子树；单条 leak trace 与“所有路径都要经过谁”也不是一回事。
- **用法**：最适合分析 Activity / Bitmap / 缓存泄漏、Listener 残留、单例误持有和“删叶子没用”的内存问题。
### 快速判断 / Quick Scan
- 如果只用一句话说清，支配树不先问“谁最大”，先问“谁不死，别人就都死不了”。
- 你最容易把它和 Histogram、单条 leak trace 混为一谈；但支配关系要求看的不是“存在一条路径”，而是“所有路径都绕不开谁”。
- 一旦你开始追“为什么这个小 Map 下面挂着整片 Activity 与 Bitmap”“为什么删了末端对象内存还是不降”，就该切到 Dominator Tree。
### 展开理解
内存排障最容易陷入一个错觉：看到 Bitmap 大、实例多，就以为根因已经找到。但真正影响回收结果的，常常是一个并不起眼的 owner、singleton、listener 或 cache entry。Dominator Tree 的价值，就是把“对象多不多”升级成“谁控制了回收权”。它迫使你把目光从叶子对象往上游移动，直到定位那个真正让整片 retained set 持续活着的支配者。

## 工具宁可先算支配关系，也不只给你一个大对象排行榜
### 它解决的判断 / 工程问题
Dominator Tree 要解决的是：**当 heap dump 里存在海量对象和复杂引用关系时，如何判断“到底先释放谁，后面这一片对象才有可能一起回收”。** 只看对象数量或浅表大小，通常只能发现症状，不能决定修复落点；而支配关系能把修复动作收敛到真正控制生命周期的那个上游节点。
### 如果忽略它会怎样
如果忽略支配树，你会不停在 Bitmap、Adapter、Fragment、View 这些叶子对象身上打转，删掉一个又来一个，却始终解释不了“为什么它们还活着”。更糟的是，你会把“实例数增加”错当根因，而看不见真正的问题是某个长寿命容器、错误注册关系或缓存策略让这些对象根本没有机会变成垃圾。
### 为什么系统宁可这样设计 (Design Rationale / Trade-off)
分析工具没有停在 Histogram 上，而是继续计算支配关系，是因为堆对象图天然比排行榜更接近真实回收规则。这样换来的好处是：你能把内存问题从“谁多”升级成“谁控制了谁”；代价则是算法更复杂、计算成本更高，而且支配树本身不会告诉你业务语义，只会把“控制回收权”的结构暴露出来。也就是说，工具宁可多做一层图算法，也不愿让定位继续停留在粗粒度猜测上。

## 真正决定 retained heap 归因的是 GC Root 可达图、immediate dominator 和子树聚合
### 机制链 / Mechanism Chain
1. 工具先从 GC Root 出发扫描 heap dump，建立“哪些对象可达、有哪些引用路径”的完整可达图。
2. 然后为每个对象计算 immediate dominator：如果从任意 GC Root 到对象 Y 的所有路径都必须经过 X，那么 X 就支配 Y。
3. 工具把所有被支配对象的内存向上聚合，形成 retained heap，表示“如果 X 消失，这一整片对象理论上都可能被回收”。
4. 排查时，分析重点就从“谁本体最大”转成“谁控制的 retained subtree 最大、它为什么比下游对象活得更久”。
5. 修复时要切断真正的上游持有关系，再重新 dump 验证 retained heap 是否塌下来，而不是只清理被支配的叶子对象。
### 关键条件 / 分支 / 例外 (Critical Conditions / Exceptions)
- **所有路径 vs 单条路径**：看到一条引用链能到达对象，并不等于那个上游就是支配者；只有“所有路径都绕不开它”才成立。
- **浅表大小 vs retained 大小**：一个对象自己可能很小，却支配着一大片 View、Bitmap 和 Adapter；反过来，一个很大的叶子对象也未必是根因。
- **设计持有 vs 误持有**：全局缓存、单例、图片池本来就可能长寿命，是否算问题要看它是不是越过了正确的生命周期边界。
- **时间问题例外**：对象为什么活着和“这一帧为什么慢”不是同一问题；前者看支配树，后者要回到时间线工具。
### 最低决定层 / 关键锚点 (Decisive Layer Anchors)
- `GC Root → all paths → immediate dominator → retained heap` 才是支配树的最低决定层；如果你把“all paths”这一步看丢，就会把任意一条引用链都误判成根因。
- Histogram 只回答“谁多 / 谁大”，leak trace 往往只回答“存在一条路径”；只有 Dominator Tree 才回答“谁控制了这一片对象的生死”。忽略这点，你会一直在错的层修问题。
- retained heap 是一个反事实量：它表达的是“如果这个节点消失，后面能一起释放多少”，不是“这个节点自己占了多少”。把这层看歪，修复优先级也会跟着错。
- 真正的修复落点通常是 owner 的生命周期边界，而不是末端对象本身；只砍叶子不动根，问题往往会复发。
### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- 看到 retained heap 大时，先问“它是自己大，还是它支配的子树大”；这一步能直接把优先级从叶子切到 owner。
- 对比多份 dump：如果同一个上游节点反复成为最大 dominator，说明真正的持有关系还没被切断。
- 如果症状是卡顿、掉帧、启动慢，先别继续在支配树里打转；确认这是对象滞留问题后，再用 heap dump 深挖。

## 一个小单例拖住整片 Activity 与 Bitmap 的场景，最能看出支配树的价值
### 最小例子
- **场景**：一个全局单例缓存管理器里错误保存了 Activity 的 listener，而这条链下面还挂着 View、Bitmap 和 Adapter。
- **为什么这里会想到它**：Histogram 最先告诉你“Bitmap 很大”，但支配树会继续告诉你：真正让这片内存活着的，是那个长寿命单例，而不是 Bitmap 本身。
- **结果**：只要解绑 listener 或修正 owner 生命周期，整片 retained heap 就会一起下降；如果你只清 Bitmap，很快还会被同一条错误持有链重新拖住。
### 对比
- **Histogram**：更擅长告诉你“谁多 / 谁大”，但不证明“谁控制这些对象继续活着”。
- **单条 leak trace**：能证明“存在一条路径能到达它”，却不保证那条路径对应的对象就是 immediate dominator。
- **[[Concepts/Perfetto|Perfetto]]**：Perfetto 解释时间与等待关系；支配树解释对象保活关系，二者不能互相替代。

## 只盯 Histogram 和 leak trace，最容易把真正的上游控制者看丢
### 常见误解
- “最大的对象就是根因。” 很多时候，真正的问题是一个看起来不起眼的小容器、错误 owner 或回调注册关系在支配整棵子树。
- “看到 Activity 泄漏，就只修 Activity。” 如果不处理上游单例、缓存或 listener，Activity 只是最先暴露出来的受害者。
### 失效 / 反噬信号
- 你不断清理末端对象却不见内存下降，或者每次 dump 都是同一个上游节点挂着大 retained heap，说明真正的 dominator 还没有动到。
- OOM 前总是一类对象堆积，但修完表面对象后问题很快复发，也常意味着你修的是症状，不是支配者。
### 不适用场景
- Dominator Tree 解释的是对象为什么还活着，不解释线程调度、输入时延或渲染 deadline；时间问题要交给 [[Concepts/Perfetto|Perfetto]] 一类工具。
- 如果只是字段算错、业务规则写反，支配树同样不是第一抓手。

## Dominator Tree 总要和这些概念连起来看
- [[Concepts/Perfetto|Perfetto]] `(contrasts[强])`：Perfetto 负责回答“慢发生在什么时候、谁在等谁”，支配树负责回答“对象为什么没死、谁控制了 retained set”。
- [[Concepts/硬件层缓存|硬件层缓存]] `(context[中])`：Layer、Bitmap 与缓存对象也会进入 heap dump；只有支配树才能说明这些资源为什么超出预期地长期滞留。
- [[Concepts/RenderThread|RenderThread]] `(boundary[弱])`：RenderThread 解释渲染提交成本，支配树解释对象保活根因；两者一起才能把“卡”和“涨”分开判断。

## 先记住“谁不死，别人就都死不了”，再回答三个问题
### 记忆锚点 / Memory Anchor
- **一句话记住**：Dominator Tree 不先问“谁最大”，先问“谁不释放，后面这一大片对象就都死不了”。
- **看到这个信号就想到它**：小 owner 挂着巨大 retained heap、删末端没用、同一上游节点在多份 dump 中反复出现。
### 自测问题
1. 为什么 Histogram 发现异常后，通常还要切到 Dominator Tree 才能真正定位根因？
2. “X 支配 Y” 与 “X 只是引用到 Y” 在排障意义上有什么本质区别？
3. 如果一个小 Map 支配了一整片 Activity 与 Bitmap，你的修复动作应该优先落在哪一层？
