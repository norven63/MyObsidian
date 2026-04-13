
# 🧩 一、ActivityManagerService（AMS） 的定位与作用

|**项目**|**内容**|
|---|---|
|**所在进程**|`system_server`|
|**核心职责**|负责**四大组件调度、进程生命周期管理、系统内存与前后台切换控制**（注：Activity 栈维护已移交 ATMS）|
|**系统地位**|Android Framework 层的中枢控制器，是 SystemServer 最核心的服务之一|
|**Binder 服务名**|`"activity"`、`"gfxinfo"` 等各种系统Binder服务|
|**管理模块**|与 `ActivityTaskManagerService(ATMS)`、`ActiveServices`、`ProcessList`、`BroadcastQueue`、`ContentProviderRecord` 等协作|

AMS 在系统中的地位如下图：

```
┌────────────────────────────────────────┐
│             SystemServer               │
│   ┌────────────────────────────────┐   │
│   │     ActivityManagerService     │◄──┼─── 控制三大组件(Service/Broadcast/Provider)及进程生命周期
│   ├────────────────────────────────┤   │
│   │ ActivityTaskManagerService     │◄──┤─── 管理Activity任务栈与窗口联动 (Android 10+ 拆分)
│   │ ActiveServices                 │◄──┤─── 管理Service
│   │ BroadcastQueue                 │◄──┤─── 管理广播调度
│   │ ContentProviderHelper          │◄──┤─── 管理Provider (注：源码中为Helper类进行管理)
│   │ ProcessList / ProcessRecord    │◄──┤─── 管理进程与线程
│   └────────────────────────────────┘   │
└────────────────────────────────────────┘
```

---

# ⚙️ 二、AMS 创建与注册流程（system_server 阶段）

AMS 在系统启动时由 **SystemServer.java** 初始化。

### 【时序流程】

```
SystemServer.main()
   ↓
startBootstrapServices()
   ↓
ActivityManagerService.Lifecycle.startService() // AOSP标准：通过Lifecycle包装类实例化AMS
   ↓
ActivityManagerService.start() // 启动主循环与核心线程
   ↓
setSystemProcess()
   ↓
ServiceManager.addService("activity", AMS)
   ↓
AMS.installSystemProviders() // 加载 SettingsProvider
   ↓
startOtherServices()
   ↓
AMS.systemReady() // 启动 SystemUI 与 Launcher
```

### 【关键点说明】

|**阶段**|**核心动作**|
|---|---|
|**创建 AMS 实例**|初始化 Runtime、Context、SystemThread 环境，并同步初始化 ATMS|
|**setSystemProcess()**|向 ServiceManager 注册 `"activity"`、`"gfxinfo"` 等各种系统Binder服务|
|**installSystemProviders()**|加载 SettingsProvider 这一特殊的系统级数据库提供者|
|**systemReady()**|通知所有系统服务“系统可运行”，启动 SystemUI、Launcher，发送 BOOT_COMPLETED 广播等|

---

# 🧠 三、AMS 核心职责与子模块拆解

AMS 是“总调度中心”，但它本身并不直接执行具体组件操作，而是通过多个“管理类”进行模块化协作。

|**子模块**|**功能职责**|**运行线程**|
|---|---|---|
|**ActivityTaskManagerService (ATMS)**|管理 Activity 栈、任务、窗口切换（Android 10 从 AMS 剥离，深度与 WMS 绑定）|system_server|
|**ActiveServices**|管理 Service 启动、绑定、生命周期|system_server|
|**BroadcastQueue**|调度广播发送、接收、分发（Android 14 引入了全新的 ModernBroadcastQueue）|system_server|
|**ContentProviderHelper**|管理 Provider 加载、引用计数|system_server|
|**ProcessList / ProcessRecord**|管理应用进程信息与 LMK (Low Memory Killer) 调度策略|system_server|
|**BatteryStatsService**|记录进程运行时间与能耗数据|system_server|
|**AppProfiler**|跟踪 CPU、内存、前后台状态|system_server|

---

# 🔄 四、AMS 在四大组件中的行为流程

> ⚠️ **源码级修正：** 自 Android 9 (Pie) 起，AMS 向 App 进程下发组件生命周期指令，已全面废弃 `scheduleXXX` 等零散方法，统一重构为 **`ClientTransaction` (客户端事务)** 机制。

|**组件**|**调用入口**|**AMS/ATMS 主要行为**|**IPC 下发方式 (Android 9+)**|
|---|---|---|---|
|**Activity**|`startActivity()`|调度到 ATMS → 检查目标进程 → 若无则由AMS启动进程 → ATMS组装事务下发|构建 `LaunchActivityItem` 包装入 `ClientTransaction`|
|**Service**|`startService()` / `bindService()`|调用 `startServiceLocked()` → 检查目标进程 → 启动进程 → 组装事务下发|构建 `CreateServiceItem` 等包装入 `ClientTransaction`|
|**BroadcastReceiver**|`sendBroadcast()`|调用 `broadcastIntentLocked()` → 分发到队列 → 依次调度执行|静态注册的构建 `ReceiverItem` 包装入 `ClientTransaction`|
|**ContentProvider**|`ContentResolver.query()`|调用 `getContentProviderImpl()` → 检查进程 → 若无则启动 → 调用 `installProvider()`|（特殊）主要由 `ActivityThread.installProvider` 直接处理|

> 📌 统一规律：**AMS/ATMS 统一接收 Binder 调用 → 检查/创建目标进程(ProcessRecord) → 组装 ClientTransaction 事务 → 通过 Binder 投递给 ActivityThread 执行**

---

# 🔋 五、AMS 与进程管理机制

AMS 的另一个核心职能是 **进程生命周期与内存回收控制**。

这部分逻辑主要集中在 `ProcessList` 与 `ProcessRecord` 中。

### 进程管理生命周期

|**阶段**|**行为**|**触发模块**|
|---|---|---|
|创建进程|通过 Zygote fork 子进程|AMS.startProcessLocked()|
|注册应用|App attach → ApplicationThread.attach()|AMS.attachApplicationLocked()|
|启动组件|由 ClientTransaction 触发组件真正实例化|system_server 下发事务|
|进程死亡|BinderDied 死亡回调 / low memory killer 查杀|AMS.handleAppDiedLocked()|
|进程回收|根据 OOM_adj 阈值、优先级回收|lmkd 守护进程 + AMS ProcessList|

### AMS 的进程优先级模型（OOM_adj 现代量级）

> ⚠️ **源码级修正：** 早期 Android 的 OOM_adj 是 -16 到 15。但现代 Android（7.0之后）为了更精细的控制，`ProcessList.java` 中的 adj 值已扩展为 **0 ~ 1000** 的级别。

|**优先级等级 (常量)**|**OOM_adj 值**|**说明 / 举例**|
|---|---|---|
|**FOREGROUND_APP_ADJ**|0|前台进程（当前正在交互的 Activity 或前台 Service）|
|**VISIBLE_APP_ADJ**|100|可见进程（被弹窗遮挡的 Activity，可见但不可交互）|
|**PERCEPTIBLE_APP_ADJ**|200|可感知进程（如正在播放音乐、显示悬浮窗）|
|**SERVICE_ADJ**|500|服务进程（后台运行的普通 Service）|
|**CACHED_APP_MIN/MAX_ADJ**|900 ~ 999|缓存进程（随时可被 LMK 回收的后台驻留进程，如按 Home 键退出的 App）|

---

# 🧭 六、AMS 在系统Ready阶段的协作

AMS 的 `systemReady()` 是系统正式可运行的标志，它会：

|**调用目标**|**行为**|
|---|---|
|**PackageManagerService**|触发应用扫描、dex 优化|
|**WindowManagerService**|准备窗口显示环境|
|**BatteryStatsService**|启动能耗监控|
|**SystemUIService**|启动状态栏、导航栏|
|**Launcher**|发送 `ACTION_MAIN` 的 Intent 启动桌面|

这一阶段也会启动系统级广播：

```
ACTION_BOOT_COMPLETED
```

触发用户级应用自启动（前提是 App 未被系统级限制）。

---

# 🧩 七、AMS 与 Binder 通信架构

AMS 既是一个 **Binder 服务端**（被调用）， 也是一个 **Binder 客户端**（调用其他系统服务）。

### Binder 通信方向

|**方向**|**发送方**|**接收方**|**调用示例**|
|---|---|---|---|
|App → AMS/ATMS|应用进程|system_server|startActivity(), startService()|
|AMS/ATMS → App|system_server|应用进程|ClientLifecycleManager.scheduleTransaction()|
|ATMS → WMS|system_server|system_server|控制窗口显示、焦点、动画切换|
|AMS → PMS|system_server|system_server|查询 Activity/Service 的 Manifest 声明信息|

---

# 🧩 八、AMS 的线程模型

AMS 实例本身驻留在 **system_server 主线程（SystemServerThread）**，但在运行中它的业务逻辑主要分布在以下线程：

|**线程名称**|**作用**|
|---|---|
|`Binder 线程池`|接收 App 进程跨进程调用的第一入口（并发执行）|
|`ActivityManager` 线程|AMS 的核心工作线程（对应的 Handler 绑定在此，处理大多数同步锁操作）|
|`BroadcastQueue` 线程|异步广播分发|
|`CpuTracker`|跟踪进程 CPU 占用|

---

# 📦 九、AMS 核心源码位置

|**模块**|**源码路径**|
|---|---|
|AMS 主类|`frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java`|
|ATMS (Android 10+)|`frameworks/base/services/core/java/com/android/server/wm/ActivityTaskManagerService.java`|
|ActiveServices|`frameworks/base/services/core/java/com/android/server/am/ActiveServices.java`|
|ProcessList|`frameworks/base/services/core/java/com/android/server/am/ProcessList.java`|
|ClientTransaction|`frameworks/base/core/java/android/app/servertransaction/ClientTransaction.java`|
|ActivityThread|`frameworks/base/core/java/android/app/ActivityThread.java`|

---

# ✅ 十、总结：AMS 的“操作系统级角色”

|**领域**|**AMS 的作用**|
|---|---|
|**进程管家**|启动、绑定、销毁进程，维持进程缓存池|
|**内存调度**|根据 OOM_adj 动态调整进程查杀优先级|
|**组件驱动**|统筹 Service / Receiver / Provider 启停（Activity归ATMS）|
|**广播枢纽**|控制广播队列、前后台分发与超时 ANR 触发|
|**系统协同**|与 WMS、PMS、BatteryStats 协同维持 Android 运转|
|**安全壁垒**|检查调用方 UID/PID 权限、防止非法跨进程调用|

---

### Activity 启动流程（现代化简化版）

|**阶段**|**所在线程**|**切换方式**|
|---|---|---|
|Launcher 进程|主线程 → Binder|调用 `startActivity()` 时通过 Binder 陷入内核切换到 ATMS|
|system_server 进程|Binder 线程 → `ActivityManager`线程|ATMS 内部完成 Task/Stack 管理，并通过 `ClientLifecycleManager` 下发事务|
|目标 App 进程|Binder 线程 → 主线程|`ApplicationThread` 接收事务，通过 `ActivityThread.H` 投递到主线程执行|

> ⚠️ **源码级修正：** Android 11 之后，`ActivityStack` 概念被淡化，统一合并为 `Task` 层级管理；IPC 统一使用 `ClientTransaction`。

CSS

```
[Launcher进程]
  Activity.startActivity()
    ↓
  Instrumentation.execStartActivity()
    ↓ Binder IPC
[system_server进程]
  ATMS.startActivity()
    ↓
  ActivityStarter → RootWindowContainer → Task (旧称ActivityStack)
    ↓
  若进程不存在 → AMS.startProcessLocked() → Zygote fork()
    ↓
  RootWindowContainer.resumeFocusedTasksTopActivities()
    ↓ Binder IPC (ClientTransaction)
[目标 App 进程]
  ApplicationThread.scheduleTransaction()
	↓ 
  ClientTransactionHandler (ActivityThread)
    ↓ Handler (H)
  TransactionExecutor.execute() → handleLaunchActivity()
    ↓
  Instrumentation.callActivityOnCreate()
    ↓
  Activity.onCreate() → onStart() → onResume()
```

![[Pasted image 20251019174251.png]]