这是AMS的笔记，请严格按照Android源码进行评估和优化，要求铁律依然是：不要破坏原是结构，但允许因为“需要更好的表达要点“而微调结构；不要贸然删除原文，除非是100%确认错误的、冗余的描述；修改动作仅限于发现有必要执行”补充和润色“的情况下。



请直接调用 Tailored Report / 定制报告能力，基于我当前 NotebookLM 中的全部资料，一次性生成一份完整、独立、可直接复习的 **Android 资深架构师面试讲义**。不要反问、不要让我补充、不要分阶段输出、不要先给大纲；若术语有误，请自行纠正并在开头统一说明假设。

## 术语统一
- IMS = InputManagerService
- ViewPage 按 ViewPager / ViewPager2 理解
- RanderNode 按 RenderNode 理解
- “disable 源码”按 requestDisallowInterceptTouchEvent / FLAG_DISALLOW_INTERCEPT 理解
- hprf = hprof
- 默认以 Android 10~14 / 现代 AOSP 为主，必要时注明版本差异

## 资料原则
严格基于当前资料生成。若资料冲突，优先官方文档 / AOSP / Android Developers / Perfetto / Google 技术分享，并说明冲突点、适用版本、采用依据。若证据不足，请明确写“基于当前资料，可得结论到这里”，并指出还需补充哪类资料；不要编造。

## 任务目标
这不是摘要，而是知识重构：让我能把每个题目讲清 **是什么、为什么、底层机制、线程/队列/锁/状态机、关键调用链、关键源码位置、线上定位手段、性能/稳定性代价、优化抓手、面试追问答法**。

## 必须覆盖的 16 个主题
1. IMS：核心机制、队列、输入卡顿区分系统调度 vs 业务逻辑  
2. ~~Android 事件分发；子控件拦截后父控件是否还能收到；结合 requestDisallowInterceptTouchEvent / FLAG_DISALLOW_INTERCEPT~~  
3. ViewPager / ViewPager2 滑动高效处理；结合 RenderNode  
4. View 异步渲染方案与线上不稳定因素  
5. 内存泄漏分析与 hprof 分析  
6. ~~Systrace / Perfetto / Android Studio Profiler 的统计口径、实现思路 / 算法、性能耗损~~  
7. 冷启动优化：ART 角度方案（除基准文件促进 AOT 外）  
8. 从 so 远程化扩展到 so 热修复：核心原理与工程边界  
9. Android 进程启动机制  
10. Handler / Looper / MessageQueue 底层原理  
11. Android 渲染绘制原理与关键底层机制  
12. AMS 核心机制与原理  
13. Binder 核心机制与原理  
14. WMS 核心机制与原理  
15. ANR 机制、判定链路与排查  
16. App 冷启动优化方法论

## 报告结构
### 一、总览
输出：能力模型、知识依赖图、复习路线、易混概念对比、为什么这些题能区分资深度。

### 二、正文
可按“输入与调度 / 渲染与性能 / 内存与诊断 / 启动与运行时 / 系统服务与 IPC / Native 动态化与修复”分章，但 16 题必须全部覆盖。

每个主题统一写：
- 面试官真正想考什么
- 一句话结论
- 30 秒回答
- 3~5 分钟展开回答
- 系统架构与核心对象
- 关键线程 / 队列 / 缓冲区 / 数据结构 / 锁 / 状态机
- 关键流程 / 时序 / 调用链
- 关键源码类 / 方法 / 源码路径
- 线上排查方法；Trace / Perfetto / log / metric 看什么
- 性能耗损点、稳定性风险、边界条件、优化抓手
- 常见误区
- 3~5 个高频追问
- 记忆锚点 / 对比表 / 口诀

### 三、跨主题串联
解释以下关系：
- IMS / InputDispatcher / ViewRootImpl / Looper / MessageQueue / Choreographer / RenderThread / SurfaceFlinger
- AMS / WMS / IMS / Binder
- 进程启动 / 冷启动 / ART / dex / so / 类加载 / Application / 首屏
- ANR / 输入卡顿 / 主线程阻塞 / 消息积压 / 掉帧
- Trace / Profiler / hprof / 内存泄漏 / 卡顿分析

### 四、附录
输出：
- 16 题速答表
- 每题至少 3 个深挖追问
- 最易失分薄弱点
- 推荐复习顺序
- 资料缺口提醒

## 风格要求
写成正式、细致、饱满、体系化的完整讲义，不要聊天口吻，不要只停留在概念层；优先保证 **机制完整、调用链完整、诊断方法可落地、面试可复述**。

请现在直接生成最终的 Tailored Report，并作为一份独立文档输出。
