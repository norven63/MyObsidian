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
