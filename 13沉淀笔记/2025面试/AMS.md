# 🧩 一、AMS 的定位与作用

|项目|内容|
|---|---|
|**英文全称**|ActivityManagerService|
|**所在进程**|`system_server`|
|**核心职责**|负责**四大组件调度、进程管理、任务栈维护、系统内存与前后台切换控制**|
|**系统地位**|Android Framework 层的中枢控制器，是 SystemServer 最核心的服务之一|
|**Binder 服务名**|`"activity"`|
|**管理模块**|与 `ActivityTaskManagerService(ATMS)`、`ActiveServices`、`ProcessList`、`BroadcastQueue`、`ContentProviderRecord` 等协作|

AMS 在系统中的地位如下图：

```
┌────────────────────────────────────────┐
│             SystemServer               │
│   ┌────────────────────────────────┐   │
│   │     ActivityManagerService     │◄──┼─── 控制四大组件生命周期
│   ├────────────────────────────────┤   │
│   │ ActivityTaskManagerService     │◄──┤─── 管理Activity任务栈
│   │ ActiveServices                 │◄──┤─── 管理Service
│   │ BroadcastQueue                 │◄──┤─── 管理广播调度
│   │ ContentProviderRecord          │◄──┤─── 管理Provider
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
ActivityManagerService.self()  // 创建单例
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

| 阶段                           | 核心动作                                                        |
| ---------------------------- | ----------------------------------------------------------- |
| **创建 AMS 实例**                | 初始化 Runtime、ActivityThread、Context、SystemThread 环境          |
| **setSystemProcess()**       | 向 ServiceManager 注册 `"activity"`、`"gfxinfo" ` 等各种系统Binder服务 |
| **installSystemProviders()** | 加载 SettingsProvider、系统数据库                                   |
| **systemReady()**            | 通知所有系统服务“系统可运行”，启动 SystemUI、Launcher、PMS 触发广播等              |

---

# 🧠 三、AMS 核心职责与子模块拆解

AMS 是“总调度中心”，但它本身并不直接执行具体组件操作，而是通过多个“管理类”进行模块化协作。

|子模块|功能职责|运行线程|
|---|---|---|
|**ActivityTaskManagerService (ATMS)**|管理 Activity 栈、任务、窗口切换|system_server|
|**ActiveServices**|管理 Service 启动、绑定、生命周期|system_server|
|**BroadcastQueue**|调度广播发送、接收、分发|system_server|
|**ContentProviderHelper**|管理 Provider 加载、引用计数|system_server|
|**ProcessList / ProcessRecord**|管理应用进程信息与调度策略|system_server|
|**BatteryStatsService**|记录进程运行时间与能耗数据|system_server|
|**AppProfiler**|跟踪 CPU、内存、前后台状态|system_server|

---

# 🔄 四、AMS 在四大组件中的行为流程

| 组件                    | 调用入口                               | AMS 主要行为                                                                       | 调用下层类                                           |
| --------------------- | ---------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------- |
| **Activity**          | `startActivity()`                  | 调用 `startActivityAsUser()` → 调度到 ATMS → 启动目标进程 → 调用 `scheduleLaunchActivity()` | ATMS / ActivityStackSupervisor / ActivityRecord |
| **Service**           | `startService()` / `bindService()` | 调用 `startServiceLocked()` → 检查目标进程 → 启动进程 → 调用 `scheduleCreateService()`       | ActiveServices / ServiceRecord                  |
| **BroadcastReceiver** | `sendBroadcast()`                  | 调用 `broadcastIntentLocked()` → 分发到队列 → 依次调度执行 `scheduleReceiver()`             | BroadcastQueue / BroadcastRecord                |
| **ContentProvider**   | `ContentResolver.query()`          | 调用 `getContentProviderImpl()` → 检查进程 → 若不存在则启动 → 调用 `installProvider()`        | ContentProviderRecord                           |

> 📌 统一规律：**AMS 统一接收 Binder 调用 → 检查/创建目标进程 → 通知 ActivityThread 执行组件生命周期**

---

# 🔋 五、AMS 与进程管理机制

AMS 的另一个核心职能是 **进程生命周期与内存回收控制**。  
这部分逻辑主要集中在 `ProcessList` 与 `ProcessRecord` 中。

### 进程管理生命周期

|阶段|行为|触发模块|
|---|---|---|
|创建进程|通过 Zygote fork|AMS.startProcessLocked()|
|注册应用|App attach → ApplicationThread.attach()|AMS.attachApplicationLocked()|
|启动组件|AMS.realStartActivityLocked() / ActiveServices.realStartServiceLocked()|system_server|
|进程死亡|BinderDied / low memory killer|AMS.handleAppDiedLocked()|
|进程回收|根据 OOM_adj、优先级回收|LMK + AMS|

### AMS 的进程优先级模型（OOM_adj 层级）

|优先级等级|说明|举例|
|---|---|---|
|Foreground (0)|当前前台Activity进程|当前Activity|
|Visible (1~2)|可见但非前台|弹窗Activity|
|Service (4~6)|正在运行的Service|播放音乐的进程|
|Background (7~8)|已暂停Activity|最近任务|
|Cached (9~15)|被缓存等待重启|最近使用过但已销毁|

---

# 🧭 六、AMS 在系统Ready阶段的协作

AMS 的 `systemReady()` 是系统正式可运行的标志，它会：

|调用目标|行为|
|---|---|
|**PackageManagerService**|触发应用扫描、dex 优化|
|**WindowManagerService**|准备窗口显示环境|
|**BatteryStatsService**|启动能耗监控|
|**SystemUIService**|启动状态栏、导航栏|
|**Launcher**|发送 `ACTION_MAIN` 启动桌面|

这一阶段也会启动广播：

```
ACTION_BOOT_COMPLETED
```

触发用户级应用自启动。

---

# 🧩 七、AMS 与 Binder 通信架构

AMS 既是一个 **Binder 服务端**（被调用）， 也是一个 **Binder 客户端**（调用其他系统服务）。

### Binder 通信方向

|方向|发送方|接收方|调用示例|
|---|---|---|---|
|App → AMS|应用进程|system_server|startActivity(), startService()|
|AMS → App|system_server|应用进程|scheduleLaunchActivity(), scheduleReceiver()|
|AMS → WMS|system_server|system_server|控制窗口显示、焦点|
|AMS → PMS|system_server|system_server|查询 Activity/Service 信息|

---

# 🧩 八、AMS 的线程模型

AMS 属于 **system_server 主线程（SystemServerThread）**，但在运行中会创建多个辅助线程：

|线程名称|作用|
|---|---|
|`ActivityManager` 主线程|处理大多数同步操作（消息队列）|
|`BroadcastHandler`|异步广播发送|
|`CpuTracker`|跟踪进程 CPU 占用|
|`BatteryStatsWorker`|异步记录功耗数据|

---

# 📦 九、AMS 核心源码位置

|模块|源码路径|
|---|---|
|AMS 主类|`frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java`|
|ATMS|`frameworks/base/services/core/java/com/android/server/wm/ActivityTaskManagerService.java`|
|ActiveServices|`frameworks/base/services/core/java/com/android/server/am/ActiveServices.java`|
|ProcessList / Record|`frameworks/base/services/core/java/com/android/server/am/ProcessList.java`|
|BroadcastQueue|`frameworks/base/services/core/java/com/android/server/am/BroadcastQueue.java`|
|ApplicationThread|`frameworks/base/core/java/android/app/ActivityThread.java`|

---

# ✅ 十、总结：AMS 的“操作系统级角色”

|领域|AMS 的作用|
|---|---|
|**组件生命周期**|管理 Activity / Service / Receiver / Provider 启停|
|**进程生命周期**|启动、绑定、销毁进程|
|**任务与栈调度**|维护 ActivityStack 与前后台切换|
|**广播分发**|控制广播队列与延迟策略|
|**系统事件协调**|与 WMS、PMS、BatteryStats、InputManager 协同工作|
|**安全与权限**|检查调用权限、防止非法启动|
|**内存控制**|根据 OOM_adj 管理进程优先级与回收|

---

### Activity启动流程
|阶段|所在线程|切换方式|
|---|---|---|
|Launcher 主线程|→ Binder|调用 `startActivity()` 时通过 Binder 切换到 AMS|
|system_server Binder 线程|→ 主线程|AMS 内部使用 `Handler` 切换到主线程执行 Stack 管理|
|目标进程 Binder 线程|→ 主线程|ApplicationThread 收到消息后，通过 `Handler` 投递到主线程执行|

```css

[Launcher进程]
  Activity.startActivity()
    ↓
  Instrumentation.execStartActivity()
    ↓ Binder IPC
[system_server进程]
  AMS.startActivity()
    ↓
  ActivityStarter → ActivityStackSupervisor → ActivityStack
    ↓
  若进程不存在 → AMS.startProcessLocked() → Zygote fork()
    ↓
  ActivityStackSupervisor.realStartActivityLocked()
    ↓ Binder IPC
[目标进程]
  ApplicationThreadProxy.scheduleLaunchActivity()
	↓ 
  ApplicationThread
    ↓ Handler
  ActivityThread.handleLaunchActivity()
    ↓
  Instrumentation.callActivityOnCreate()
    ↓
  Activity.onCreate() → onStart() → onResume()


```

![[Pasted image 20251019174251.png]]