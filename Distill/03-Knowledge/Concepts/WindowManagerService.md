---
标识: concept-windowmanagerservice
标题: WindowManagerService
标签: [concept, android-runtime]
别名: [WMS, 窗口管理服务, Android 窗口总控]
来源:
  - 'WMS（2025面试旧笔记迁移）'
  - '渲染绘制（2025面试旧笔记迁移）'
  - 'IMS（2025面试旧笔记迁移）'
关联概念:
  - 'InputManagerService'
  - 'RenderThread'
  - 'ActivityManagerService'
状态: stable
定义: WindowManagerService 是 Android system_server 中负责维护全局窗口对象、焦点与可见性、布局策略以及 Layer 属性同步的窗口总控服务，它把 app 端“想显示一个界面”转成系统级“这个窗口该以什么结构和属性出现在屏幕上”。
---

# WindowManagerService

## 1. 它是什么 (What It Is)
### 快速判断 / Quick Scan
| 维度 | 内容 |
| --- | --- |
| 一句话定义 | WindowManagerService 负责管理 Android 所有窗口的结构、层级、焦点、布局和对 SurfaceFlinger 的 Layer 控制。 |
| 不要和什么混为一谈 | 它不负责真正绘制像素；WMS 决定“哪个窗口如何出现”，但具体画面内容由 app 的 UI / RenderThread 生产，最终由 SurfaceFlinger 合成。 |
| 什么时候想到它 | 弹窗层级错乱、点击落到错误窗口、焦点不对、窗口明明创建了却看不见、旋转和布局更新异常时。 |

### 展开理解
- WMS 的核心价值不是“维护几个 WindowState”，而是把 app、system_server 和 SurfaceFlinger 之间的窗口协作规则统一起来。
- 一旦把 WMS 理解成“窗口结构与显示属性的控制器”，你就会自然区分：谁负责窗口存在与顺序，谁负责输入归属，谁负责真正把像素合成上屏。

## 2. 为什么它重要 (Why It Matters)
### 它解决的判断 / 工程问题
- 它解决的是：**一个窗口什么时候能被系统承认、处于什么层级、是否拥有焦点、要以怎样的几何属性和可见性进入 Layer 树。**
- 没有 WMS，app 只能各画各的，系统很难统一处理状态栏、对话框、Activity 切换、多显示屏和输入焦点。

### 如果忽略它会怎样
- 你会把“窗口看不见”“触摸没到”“层级盖错了”错当成纯渲染问题，实际上很多时候是窗口结构或焦点判断先错了。
- 你也会误以为画面一旦掉帧就只能去查 RenderThread，忽略了窗口属性、输入窗口列表、SurfaceControl 事务本身也可能是前因。

## 3. 它是怎么工作的 (How It Works)
### 机制链 / Mechanism Chain
1. App 通过 `addView()` / `setView()` / 启动 Activity 等路径请求显示窗口后，WMS 为它创建 `WindowState`、`WindowToken` 等系统级窗口对象。
2. WMS 根据窗口类型、Display、Z-order、可见性和策略规则，决定这个窗口在全局窗口树里应该处于什么位置、由谁覆盖、是否允许获得焦点。
3. 需要实际显示时，WMS 通过 `SurfaceControl` / `SurfaceSession` 向 SurfaceFlinger 创建或更新 Layer，把位置、大小、透明度、层级等属性同步出去。
4. 与此同时，WMS 还会维护输入窗口信息并同步给 [[Concepts/InputManagerService|InputManagerService]]，让输入系统知道“当前哪些窗口可触摸、谁是焦点窗口、触摸区域是什么”。
5. 当旋转、可见性、焦点或动画状态变化时，WMS 会重新布局并再次提交事务；SurfaceFlinger 再在下一帧合成时使用这些最新属性。

### 排查 / 应用抓手 (Diagnostic / Application Hooks)
- **先分清“没画出来”还是“没被当作目标窗口”**：窗口看不见、触摸不响应、层级不对，先问是像素没生产出来，还是 WMS 根本没把它放到正确的位置和焦点上。
- **看窗口相关证据**：焦点窗口、InputWindowHandle、SurfaceControl 事务、Layer 层级和可见性，比单看 app 线程栈更能解释“为什么用户点了却像没点”。
- **WMS 是交接层**：如果你发现语义已经从 AMS 切到了“窗口出现与否”，或者从输入链切到了“目标窗口判定”，那就是 WMS 该优先上场的时刻。

## 4. 一个最小例子 / 对比 (Minimal Example / Contrast)
### 最小例子
- **场景**：一个 Activity 成为前台后立即弹出 Dialog。
- **为什么这里会想到它**：不是 app 自己决定“Dialog 一定压在页面上”；WMS 需要为新窗口建结构、分配层级、处理焦点，再把 Layer 属性提交给 SurfaceFlinger。
- **结果**：如果层级和焦点都正确，用户会看到对话框浮在页面上并且输入落到它；如果窗口标志或焦点关系不对，就会出现“Dialog 看见了但点不到”或“点穿到底层”的问题。

### 对比
| 易混概念 / 做法 | 真正差异 | 这里为什么不是它 |
| --- | --- | --- |
| SurfaceFlinger | 负责读取 Buffer 并做最终合成 | SurfaceFlinger 不替你决定 app 窗口的业务层级、焦点和策略 |
| RenderThread | 负责把绘制命令变成 Buffer | RenderThread 生产画面内容，但不决定窗口结构和输入目标 |
| InputManagerService | 负责事件读取与分发 | IMS 会根据 WMS 提供的窗口信息决定把输入发给谁，但窗口列表和焦点来源仍由 WMS 维护 |

## 5. 常见误解与边界 (Mistakes & Boundaries)
### 常见误解
- “WMS 就是窗口版的绘图引擎。” 错，WMS 管结构和属性，不画像素。
- “触摸不准肯定是 InputManagerService 的事。” 实际上很多输入异常是因为 WMS 提供的焦点窗口、可触摸区域或窗口属性先错了。

### 失效 / 反噬信号
- 弹窗显示层级怪、焦点总在错误窗口、`FLAG_NOT_TOUCHABLE` 之类的窗口属性让触摸被跳过，都是典型的 WMS / 输入窗口协同问题。
- 旋转或多窗口切换后布局和可见性异常、窗口已经创建却没有出现在正确 Display / Layer 上，也说明该回到 WMS 看结构与事务链。

### 不适用场景
- 如果问题已经确认是 GPU 过慢、着色开销高或 Frame Timeline miss deadline，WMS 不是主抓手。
- 如果你要解释的是 View 树内部某个控件的事件冒泡和拦截，WMS 只负责更上游的“目标窗口是谁”，不负责控件级分发细节。

## 6. 与哪些概念容易一起出现 (Nearby Concepts)
- [[Concepts/InputManagerService|InputManagerService]] `(routing[强])`：WMS 决定窗口与焦点，IMS 负责把事件路由到这些窗口；两者一起才能解释“为什么这个点击落到了这里”。
- [[Concepts/RenderThread|RenderThread]] `(handoff[中])`：WMS 决定窗口怎么出现，RenderThread 决定窗口内容怎么被画出来并送去合成。
- [[Concepts/ActivityManagerService|ActivityManagerService]] `(context[中])`：AMS 把组件和进程拉起，WMS 接着处理窗口可见性、焦点和显示协作。

## 7. 来源对照 (Source Cross-check)
- **来源 1（WMS 旧笔记）**：补足了窗口创建、布局更新、SurfaceControl / Layer 属性同步，以及 WMS 与 SurfaceFlinger 的交接边界。
- **来源 2（IMS 旧笔记）**：明确了输入路由不是凭空发生，而是依赖 WMS 提供的 InputWindowHandle、焦点窗口和触摸区域信息。
- **来源 3（渲染旧笔记）**：把 WMS 放进 Choreographer、RenderThread、SurfaceFlinger 的整条交付链里，避免把它误学成孤立的 system_server 服务。
- **我的整合结论**：WMS 最值得记住的不是 API 名称，而是它在“窗口结构、输入归属、Layer 属性、显示协同”这四件事上的枢纽作用。

## 8. 自测问题 (Self-Test)
### 记忆锚点 / Memory Anchor
- **一句话记住**：WMS = 决定窗口怎么存在、怎么排序、谁拿焦点、怎么把属性交给合成系统的总控层。
- **看到这个信号就想到它**：窗口层级不对、焦点乱跳、看得见但点不到、旋转后显示关系异常。

### 自测问题
1. 为什么说 WMS 负责“决定窗口怎么出现”，而不是“亲自把像素画出来”？
2. 输入事件为什么必须依赖 WMS 提供的窗口与焦点信息？
3. 当一个 Dialog 看得见却点不到时，你为什么应该先回到 WMS / IMS 的协同链，而不是先怪 RenderThread？
