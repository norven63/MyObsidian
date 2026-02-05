# 🧭 WindowManagerService 全景解析

---

## 一、WMS 在 Android 图形系统中的角色定位

|模块|所在进程|核心职责|
|---|---|---|
|**App进程（ViewRootImpl + RenderThread）**|应用进程|负责应用界面的绘制、合成前的数据生产|
|**WindowManagerService（WMS）**|`system_server`|负责系统全局窗口的管理、层级排序、布局策略、焦点分配、窗口动画|
|**SurfaceFlinger**|独立进程（native 层）|负责将所有窗口（Layer）的内容进行最终合成并提交给显示硬件|
|**Choreographer**|App主线程（UI Thread）|负责帧同步调度（基于 VSync），驱动应用绘制与动画的时序协调|

---

## 二、WMS 的核心职责与结构分层

|模块|职责描述|关键类/组件|
|---|---|---|
|**窗口管理**|负责创建、销毁、更新所有窗口的属性与层级|`WindowManagerService`, `WindowState`, `WindowToken`|
|**输入焦点与事件分发**|管理输入焦点窗口，与 InputManagerService 协同|`InputMonitor`, `InputWindowHandle`|
|**Surface 管理**|通过 SurfaceControl 操作 SurfaceFlinger 的 Layer|`SurfaceControl`, `SurfaceSession`|
|**动画与过渡**|负责系统窗口与应用窗口的过渡动画|`WindowAnimator`, `SurfaceAnimationRunner`|
|**显示输出管理**|管理多显示屏（DisplayContent），协调不同 Display 的窗口|`DisplayContent`, `DisplayPolicy`|

---

## 三、WMS 的工作主线流程

整个 WMS 的工作大致分为三大主线：

|主线|流程描述|关键方法|
|---|---|---|
|**1️⃣ 窗口创建/添加流程**|App 请求添加窗口 → WMS 创建对应 WindowState 与 SurfaceControl → 通知 SurfaceFlinger 创建 Layer|`addWindow()`, `relayoutWindow()`|
|**2️⃣ 窗口布局与更新流程**|系统状态（旋转、焦点、可见性）变更 → 重新计算布局 → 更新 Layer 属性|`performLayoutAndPlaceSurfacesLocked()`|
|**3️⃣ 窗口显示合成流程**|每次窗口状态或内容变化 → WMS 通过 Transaction 更新 Layer → SurfaceFlinger 执行合成|`SurfaceControl.Transaction.apply()`|

---

## 四、WMS 与 SurfaceFlinger 的协作机制

> 🧠 二者通过 **SurfaceControl / Layer 树结构** 进行通信  
> WMS 不直接绘制像素，而是控制每个窗口在 SurfaceFlinger Layer 树中的位置与属性。

### 1️⃣ Layer 创建与绑定

1. 当 App 创建窗口（例如 `ViewRootImpl.setView() / WindowManager.addView()` → `WMS.addWindow()` ）时：    
    - WMS 为该窗口创建 `WindowState`        
    - 通过 `SurfaceSession` 调用 native 层 `SurfaceFlinger` 创建一个 Layer        
    - 生成对应的 `SurfaceControl`（Java 对 Layer 的控制封装）
        
2. App 端拿到 `Surface`，其底层其实是 `BufferQueue` 的生产端；    
    - SurfaceFlinger 持有 BufferQueue 的消费端。
        
> 结果：  
> 每个 Window = 1 个 Layer（由 SurfaceFlinger 合成时使用）

---

### 2️⃣ Layer 属性同步（WMS → SurfaceFlinger）

当窗口位置、大小、可见性、Z序变化时：
```java
SurfaceControl.Transaction t = new SurfaceControl.Transaction(); 
t.setPosition(surfaceControl, x, y); 
t.setLayer(surfaceControl, zOrder); 
t.setAlpha(surfaceControl, alpha); 
t.show(surfaceControl); 
t.apply();
```
此时：
- 调用 `.apply()` 会通过 Binder 向 SurfaceFlinger 发送 Transaction；    
- SurfaceFlinger 在下一帧（VSync）时更新 Layer 树；    
- 并在合成时使用新的属性。
    
---

### 3️⃣ Buffer 数据流动（App → SurfaceFlinger）

当应用完成一帧绘制（RenderThread 渲染完成）：

`Surface::queueBuffer(buffer)`
- RenderThread 将新的图像 Buffer 放入 BufferQueue；    
- SurfaceFlinger 收到 Buffer（消费端）；    
- 在下一帧 Composition 阶段读取所有 Layer 的最新 Buffer；    
- 完成合成（Composition）后交由 Display HAL 输出。    

---

### 4️⃣ WMS + SF + Choreographer 协同的完整时序
```css

┌────────────────────────────────────────────────────────────┐ 
│                  [App进程]                               
│ UI线程(ViewRootImpl)   RenderThread                        
│     │ invalidate()        │                                 
│     │ requestDraw()       │                                 
│     ├──> Choreographer <--┘ (等待VSync信号)                 
│     │   │ draw()          │                                 
│     │   └→ OpenGL绘制 → queueBuffer()                       
│     │                           │                          
└─────┼───────────────────────────┼──────────────────────────┘
      │                           │
      ▼                           ▼ 
[system_server进程]        [SurfaceFlinger进程] 
WMS控制层级、窗口属性      消费所有Layer的Buffer并合成帧 
│                             │ 
│ SurfaceControl.Transaction  │ Layer树更新 
│ setLayer()/apply() ───────► │ 合成(Composition) 
│                             │ 输出到显示设备 
└─────────────────────────────┘

```

---

## 五、线程与进程分布关系表

| 角色                    | 所属进程             | 关键线程               | 主要职责                         |
| --------------------- | ---------------- | ------------------ | ---------------------------- |
| **WMS**               | `system_server`  | Binder线程池          | 控制所有窗口层级与属性                  |
| **App端 ViewRootImpl** | App进程            | UI主线程              | 发起绘制请求、处理输入事件                |
| **RenderThread**      | App进程            | RenderThread       | 实际执行 GPU 渲染并调用 queueBuffer() |
| **SurfaceFlinger**    | `surfaceflinger` | 主线程 / HWComposer线程 | 合成所有 Layer 并输出至屏幕            |
| **Choreographer**     | App进程            | UI线程（VSync回调）      | 驱动每帧绘制节奏                     |

---

## 七、总结：WMS的全景认知框架

| 模块                 | 职责             | 关键交互对象                          |
| ------------------ | -------------- | ------------------------------- |
| **WMS**            | 控制窗口结构与层级      | 与 SurfaceFlinger 交互             |
| **SurfaceFlinger** | 合成所有图像并输出      | 与 GPU、Display HAL 交互            |
| **RenderThread**   | 绘制像素并上交 Buffer | 与 SurfaceFlinger（BufferQueue）交互 |
| **Choreographer**  | 驱动时序（VSync）    | 控制 UI 主线程绘制节奏                   |
| **IMS**            | 输入系统协调         | 与 WMS 窗口焦点协调输入                  |

---

## 🧩 八、总结一句话核心逻辑

> 🔹 **WMS 决定“显示什么、怎么显示”**
> 🔹 **RenderThread 负责“画出内容”**
> 🔹 **SurfaceFlinger 负责“把所有画面拼成一张”**
> 🔹 **Choreographer 控制整个系统的“节奏心跳”**


## 关于findTouchedWindowTargetsLocked实现
在Android系统中，触摸事件从发生到传递至合适的窗口，其中关键的一环便是`InputDispatcher::findTouchedWindowTargetsLocked`函数。这个函数会根据触摸点的位置等信息，找到应该接收该事件的窗口。在这个过程中，系统会仔细检查候选窗口的`LayoutParams`中的标志位，`FLAG_NOT_TOUCHABLE`正是其中之一，它会导致窗口被跳过。

下面，我们通过一个表格来梳理触摸事件目标窗口查找与标志位检查过程中的关键函数：

| 函数名                                      | 关键作用                                                                 |
| :------------------------------------------ | :----------------------------------------------------------------------- |
| `InputDispatcher::findTouchedWindowTargetsLocked` | 触摸事件目标查找的**入口**和**核心协调者**。                               |
| `InputDispatcher::findTouchedWindowAtLocked`     | **按Z序从前往后**遍历窗口，寻找第一个“接受触摸”的窗口。                   |
| `windowAcceptsTouchAt`                      | **关键判断**：检查窗口是否可见、可触摸且触摸点在其区域内。                 |

### 🔍 关键函数流程与标志位检查

#### **1. `InputDispatcher::findTouchedWindowTargetsLocked`**

这是触摸事件目标查找的**入口**和**核心协调者**。它会调用 `findTouchedWindowAtLocked` 来获取当前被触摸的窗口。

#### **2. `InputDispatcher::findTouchedWindowAtLocked`**

此函数负责**按Z序从前往后**遍历指定屏幕上的所有窗口，寻找第一个“接受触摸”的窗口。其核心逻辑如下：
```cpp
sp<WindowInfoHandle> InputDispatcher::findTouchedWindowAtLocked(int32_t displayId, int32_t x, int32_t y, ...) {
    // 获取当前屏幕上的所有窗口句柄
    const auto& windowHandles = getWindowHandlesLocked(displayId);
    for (const sp<WindowInfoHandle>& windowHandle : windowHandles) { // 从顶层到底层遍历
        ...
        const WindowInfo& info = *windowHandle->getInfo();
        // 关键判断：该窗口是否接受此次触摸？
        if (!info.isSpy() && windowAcceptsTouchAt(info, displayId, x, y, isStylus)) {
            ... // 找到目标窗口，返回其句柄
            return windowHandle;
        }
        ...
    }
    return nullptr; // 未找到符合条件的窗口
}
```

#### **3. `windowAcceptsTouchAt`**

这是**判断窗口是否接受触摸的核心函数**，窗口的多种属性（包括标志位）都在此检查。其简化代码如下：
```cpp
bool windowAcceptsTouchAt(const WindowInfo& windowInfo, int32_t displayId, int32_t x, int32_t y, bool isStylus) {
    const auto inputConfig = windowInfo.inputConfig;
    
    // 检查1：显示ID是否匹配，窗口是否可见
    if (windowInfo.displayId != displayId || inputConfig.test(WindowInfo::InputConfig::NOT_VISIBLE)) {
        return false;
    }
    
    // 检查2（关键）：窗口是否可触摸
    const bool windowCanInterceptTouch = isStylus && windowInfo.interceptsStylus();
    if (inputConfig.test(WindowInfo::InputConfig::NOT_TOUCHABLE) && !windowCanInterceptTouch) {
        return false; // 设置FLAG_NOT_TOUCHABLE会导致NOT_TOUCHABLE为true，此处返回false
    }
    
    // 检查3：触摸点是否在窗口的可触摸区域内
    if (!windowInfo.touchableRegionContainsPoint(x, y)) {
        return false;
    }
    
    ...
    
    return true;
}
```

这里，`WindowInfo::InputConfig::NOT_TOUCHABLE` 这个内部状态就来源于窗口 `LayoutParams` 中的 `FLAG_NOT_TOUCHABLE` 标志。当此标志被设置，`NOT_TOUCHABLE` 为真，并且没有手写笔拦截等特殊情况时，函数返回 `false`，表示该窗口不接受触摸事件。

### 💎 总结

在`InputDispatcher::findTouchedWindowTargetsLocked`等相关函数中，系统通过遍历窗口并调用`windowAcceptsTouchAt`等函数，检查窗口的`LayoutParams`标志位。如果`FLAG_NOT_TOUCHABLE`被设置，检查会失败，导致该窗口被跳过，触摸事件也就不会传递到该窗口的`ViewRootImpl`及后续的`Activity.onTouchEvent()`。

希望这些具体的源码逻辑能帮助你彻底理解`FLAG_NOT_TOUCHABLE`的作用机制。如果你对`WindowInfo`的构成或者触摸区域判断等细节还有兴趣，我们可以继续探讨。