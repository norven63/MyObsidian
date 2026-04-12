---
标识: concept-windowmanagerservice
标题: WindowManagerService
标签: [concept, android-runtime]
别名: [WMS, 窗口管理服务, Android 窗口总控]
来源:
  - 'WMS（2025面试旧笔记迁移）'
  - 'IMS（2025面试旧笔记迁移）'
  - '渲染绘制（2025面试旧笔记迁移）'
关联概念:
  - 'InputManagerService'
  - 'RenderThread'
  - 'ActivityManagerService'
状态: stable
定义: WindowManagerService 是 Android `system_server` 中负责维护全局窗口结构、层级、焦点和 Layer 属性的总控服务；它真正解决的是“哪个窗口该怎样存在、谁能拿焦点、这些属性怎样交给显示和输入系统”。
---

# WindowManagerService

## WMS 真正决定的，不是像素怎么画，而是窗口怎样存在、排序、拿焦点并接入 Layer 树
### 一眼认知骨架
- **对象**：Android 全局窗口结构与显示属性的控制器，不是绘图引擎。
- **目的**：把 app 端“我想显示一个窗口”翻译成系统级“它该在什么层级、有没有焦点、怎么出现在 Layer 树上”。
- **组成**：`WindowState`、`WindowToken`、`DisplayContent`、`SurfaceControl / Transaction`、`InputWindowHandle`、窗口策略与动画模块。
- **主线**：App 请求加窗 / 启动 Activity → WMS 建立窗口对象 → 计算层级 / 可见性 / 焦点 → 提交 `SurfaceControl.Transaction` → 同步输入窗口信息给 IMS。
- **变体**：Dialog、Overlay、多窗口、旋转、多 Display、`FLAG_NOT_TOUCHABLE`、焦点切换都会改写结果。
- **用法**：最适合解释“看得见却点不到”“层级盖错了”“焦点乱跳”“旋转后窗口关系异常”这类问题。
### 快速判断 / Quick Scan
- 如果只用一句话说清，WMS 管的是“窗口怎么存在和排序”，不是“窗口里面的像素怎么画出来”。
- 你最容易把它和 SurfaceFlinger 或 RenderThread 混为一谈；但后两者负责内容合成与提交，WMS 负责窗口结构、属性和输入目标。
- 一旦你开始追“Dialog 明明显示了为什么点不到”“窗口已经创建了为什么看不见”“哪个窗口才是焦点窗口”，就应该回到 WMS。
### 展开理解
WMS 的真正价值，在于它把 App、`system_server`、输入系统和 SurfaceFlinger 之间的窗口协作规则统一起来。App 可以说“我要显示一个界面”，但它不能自己决定状态栏、Dialog、浮窗、Activity、最近任务缩略图和多 Display 窗口彼此怎样排序，也不能自己定义“现在谁能收输入”。WMS 正是负责把这些全局约束变成一个可持续维护的窗口世界模型。

## 系统宁可用 WMS 统一窗口结构，也不让每个应用自己决定显示秩序和焦点规则
### 它解决的判断 / 工程问题
WMS 要解决的是：**一个窗口什么时候被系统承认、处于什么层级、有没有焦点、该以怎样的几何属性和可见性进入 Layer 树，并把这些信息同步给输入系统。** 如果没有全局窗口总控，App 只能各画各的，系统就很难统一处理状态栏、Dialog、多窗口、旋转和输入焦点。
### 如果忽略它会怎样
如果忽略 WMS，你会把“看不见”“点不到”“盖错层”这类问题统统当成渲染问题，结果一直在 RenderThread 或 View 代码里打转，却看不见真正的问题其实是窗口层级、焦点或输入窗口属性先错了。很多时候，像素本身没问题，是“窗口没被放在正确位置”这件事出了问题。
### 为什么系统宁可这样设计 (Design Rationale / Trade-off)
Android 没有让每个应用独立和 SurfaceFlinger、输入系统直接协商窗口秩序，而是把窗口结构统一交给 WMS。这样换来的好处是：全局 Z-order、焦点、Display、旋转策略、安全窗口属性都能由系统一致治理；代价则是 App 想显示一个窗口时要多穿过一层结构与事务同步，而且显示异常常常要跨 WMS、IMS 和渲染链联合排障。系统宁可增加中枢复杂度，也要换取全局窗口秩序的一致性。

## 真正决定“看得见 / 点得到 / 盖得住”的，是 WindowState、SurfaceControl 事务和输入窗口同步这条链
### 机制链 / Mechanism Chain
1. App 通过 `addView()`、`setView()`、启动 Activity 等路径请求显示窗口后，WMS 会为它创建或更新 `WindowState`、`WindowToken` 等系统级窗口对象，并把它们挂到对应 `DisplayContent` 下。
2. WMS 根据窗口类型、Z-order、可见性、策略标志和当前焦点状态，决定这个窗口在全局窗口树里该处于什么位置、能不能拿焦点、会不会被别的窗口盖住。
3. 当需要真正显示或更新时，WMS 通过 `SurfaceControl.Transaction` 把位置、大小、alpha、layer、show / hide 等属性同步到 SurfaceFlinger 的 Layer 树。
4. 同时，WMS 还会把 `InputWindowHandle`、焦点窗口和可触区域同步给 [[Concepts/InputManagerService|InputManagerService]]，让输入系统知道“事件现在该发给谁”。
5. SurfaceFlinger 在后续合成周期里使用这些最新属性去合成显示；用户看到的“窗口是否可见 / 可点 / 在最上层”，其实取决于这条结构链而不只是一块 Buffer 有没有内容。
### 关键条件 / 分支 / 例外 (Critical Conditions / Exceptions)
- **焦点 / 可触摸分支**：窗口可以看得见，但若 `FLAG_NOT_TOUCHABLE`、`NOT_FOCUSABLE` 或可触区域配置不对，输入仍会被系统跳过或发给别的窗口。
- **旋转 / Display 分支**：旋转、多窗口和多 Display 会触发布局重算；同一个窗口能不能继续显示在你预期的位置，取决于 WMS 如何重新安放它。
- **有 Surface 不等于能看见**：窗口内容已经画出来，不代表它一定在正确 Layer、alpha、Display 或焦点关系上；结构先错，像素再对也没用。
- **输入与显示分支**：WMS 决定窗口结构和属性，IMS 决定按这些信息路由输入；看得见却点不到时，常常就是这两个分支的协同问题。
### 最低决定层 / 关键锚点 (Decisive Layer Anchors)
- `WindowState / WindowToken / DisplayContent → SurfaceControl.Transaction → InputWindowHandle` 才是 WMS 的最低决定层。只看 App 代码，你会把结构错误误读成渲染错误。
- WMS 不画像素，它决定的是“这些像素有没有正确的位置、层级和焦点”；忽略这条边界，你会一直盯错优化对象。
- `FLAG_NOT_TOUCHABLE` 等窗口属性最终会落成输入系统看到的 `NOT_TOUCHABLE` / 可触区域判断；如果把这层看丢，就解释不了“Dialog 看得见却点不到”。
- SurfaceFlinger 只会按收到的 layer / alpha / visible 事务去合成；WMS 一旦把这些属性交错，App 即便画对了内容，用户也仍会看到错位结果。
### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- 先分清“像素没画出来”还是“窗口根本没被放到正确位置 / 焦点上”；这一步能决定你该看 RenderThread 还是 WMS / IMS。
- 重点看焦点窗口、`InputWindowHandle`、layer 顺序、alpha / visible 事务和窗口标志；这些证据往往比单看 App 线程栈更直接。
- 遇到“看得见但点不到”“点穿到底层”“旋转后层级乱了”时，优先回到窗口结构与输入目标，不要先怀疑业务逻辑。

## 一个 Dialog 看得见却点不到的场景，最能暴露 WMS 的关键作用
### 最小例子
- **场景**：一个 Activity 成为前台后立即弹出 Dialog，用户能看到弹窗，但点击却像是穿透到了底层页面。
- **为什么这里会想到它**：这往往不是“Dialog 没画出来”，而是 WMS 在层级、焦点、可触摸属性或输入窗口同步上没有形成正确状态。
- **结果**：如果 WMS 正确建立了窗口结构并同步了输入窗口信息，用户会得到正常的悬浮对话框；如果这些属性错了，就会出现“看得见却点不到”或“点穿到底层”的典型问题。
### 对比
- **SurfaceFlinger**：负责读取各 Layer 的 Buffer 并做最终合成；它不决定业务层级、焦点或窗口策略。
- **RenderThread**：负责把窗口内容画成 Buffer；WMS 决定的是“这个 Buffer 对应的窗口怎么存在”。
- **[[Concepts/InputManagerService|InputManagerService]]**：IMS 负责把事件送给目标窗口，但目标窗口名单、焦点和可触区域本身来自 WMS。

## 把所有显示异常都当成渲染问题，会直接错过窗口和焦点这一层
### 常见误解
- “WMS 就是窗口版的绘图引擎。” 错。它管结构和属性，不亲自画像素。
- “触摸不准一定是 IMS 的事。” 现实里很多输入异常是因为 WMS 给出去的焦点窗口、可触区域或窗口标志先错了。
### 失效 / 反噬信号
- 弹窗显示层级怪、焦点总落在错误窗口、`FLAG_NOT_TOUCHABLE` 一类属性让触摸被跳过，都是典型的 WMS / 输入窗口协同问题。
- 旋转或多窗口切换后布局和可见性异常、窗口已经创建却没出现在正确 Display / Layer 上，也说明该回到 WMS 看结构与事务链。
### 不适用场景
- 如果问题已经明确是 GPU 太慢、着色开销高或 Frame Timeline miss deadline，WMS 不是主要抓手。
- 如果你要解释的是 View 树内部某个控件的事件冒泡和拦截，WMS 只负责更上游的“目标窗口是谁”，不负责控件级分发细节。

## WindowManagerService 总要和这些概念一起看
- [[Concepts/InputManagerService|InputManagerService]] `(routing[强])`：WMS 给出窗口和焦点，IMS 再据此把事件路由到正确目标；两者一起才能解释“为什么这个点击落到了这里”。
- [[Concepts/RenderThread|RenderThread]] `(handoff[中])`：WMS 决定窗口怎样出现在系统里，RenderThread 决定窗口内容怎样被画出来并交给合成链。
- [[Concepts/ActivityManagerService|ActivityManagerService]] `(context[中])`：AMS 把组件和进程拉起，WMS 接着处理窗口可见性、层级与焦点协同；它们是同一条用户体验链的上下游。

## 先记住“WMS 管结构，渲染线程画像素”，再用三个问题自测
### 记忆锚点 / Memory Anchor
- **一句话记住**：WMS = 决定窗口怎么存在、怎么排序、谁拿焦点、怎么把属性交给显示与输入系统的总控层。
- **看到这个信号就想到它**：窗口层级不对、焦点乱跳、看得见却点不到、旋转后显示关系异常。
### 自测问题
1. 为什么说 WMS 负责“决定窗口怎么出现”，而不是“亲自把像素画出来”？
2. 输入事件为什么必须依赖 WMS 提供的窗口与焦点信息？
3. 当一个 Dialog 看得见却点不到时，你为什么应该先回到 WMS / IMS 的协同链，而不是先怪 RenderThread？
