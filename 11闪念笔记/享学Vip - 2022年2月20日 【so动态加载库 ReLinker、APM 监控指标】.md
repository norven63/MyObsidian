日期： 2022-03-06

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - 
https://ke.qq.com/webcourse/347420/103755197#taid=12286797627608348&vid=387702296383669027 （上）
https://ke.qq.com/webcourse/347420/103755197#taid=13385596290813212&vid=387702296478569180 （下）

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8811%EF%BC%892022.2.20-%E7%BA%BF%E4%B8%8A%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96---%E8%B7%AF%E5%93%A5


---
<br>


- 性能优化目的：知识点的沉淀、总结
- 比如Mem（2种方案 手动GC[Matrix]、阈值的处理[Koom]）
- FPS(Handler机制、Printer)、idleHandler（闲时延迟操作）

- 闲时延迟操作：
```java
Looper.myQueue().addIdelHandler(new Message.IdelHandler(){
	//queueIdle return true/false
})
```

## 一、so动态加载库：ReLinker
- [ReLinker 库github](https://github.com/KeepSafe/ReLinker )：
- 通过动态加载so的技术，解决UnsatisfiedLinkError问题。
	- UnsatisfiedLinkError : 主要的原因是兼容性的问题。包so的裁剪由于国内的厂商魔改ROM，改的是so加载的路径（3种）。
- Tinker的so的加载流程（电量那节课讲的[[享学Vip - 2022年2月15日 【网络优化（HttpDNS） & 电量】delay]]）
- 核心类 [`ReLinkerInstance`](https://github.com/KeepSafe/ReLinker/blob/master/relinker/src/main/java/com/getkeepsafe/relinker/ReLinkerInstance.java)
- ReLinker**最牛逼的地方就是解析SO的2进制文件，获取so的依赖属性。** 参见ELF文件解析类 [`ElfParser`](https://github.com/KeepSafe/ReLinker/blob/master/relinker/src/main/java/com/getkeepsafe/relinker/elf/ElfParser.java) 中的 `parseNeededDependencies()` 方法
- System类
	- `System.mapLibraryName("abc");` 自带拼接返回 `"libabc.so"` 字符串
	- `loadLibrary()`、`load()` 价值so
	- `getenv()`

<br><br>


## 二、性能优化
- 性能优化框架：做什么？怎么做？如何设计方案与架构？

#### 1、主流开源项目的调研、用法：
- [rabbit 库github](https://github.com/SusionSuc/rabbit-client)
- [**Matrix 库github**](https://github.com/Tencent/matrix/wiki/Matrix-Android-TraceCanary) ：功能全，但很重，不适合公司的业务迭代，稳定性低
- 听云SDK（>8.0 CPU 指标的问题）
- 网易 腾讯GT （时间非常老）16年
- 360的[ArgusAPM](https://github.com/Qihoo360/ArgusAPM) gradle 集成的时候会有很多的问题
- [BlockCanary](https://github.com/markzhai/AndroidPerformanceMonitor)

#### 2、APM有哪些指标
##### 2.1、不要去碰和讲的指标
1. 稳定性的问题（崩溃的问题）
	- 主流方案：breakpad+bugly+Firebase(海外)

2. 流量/网络 （Http协议的可达率、流量的大小）
	- 使用OKHTTP的拦截器（可以获取请求的链接、byte大小，但是能够覆盖的面太小）
	- 全链路的网络监控APM：网络一体化的问题、协议本身（例如Socket，但各家公司不一样，所以SDK本身很难统一的处理）

##### 2.2、重点关注的APM指标
1. **==电量==**（battery、historian、广播）

2. **==流量消耗==**： 
	- `TrafficStats / getUidRxBytes(int uid) / getTotalbytes()`
	- 后台偷跑：后台定时任务，获取时间间隔（2、5分钟）流量，计算平均值

3. **==内存指标的统计 / 内存的泄漏==**
 - rabbit库的 [RabbitMemoryMonitor](https://github.com/SusionSuc/rabbit-client/blob/master/rabbit-monitor/src/main/java/com/susion/rabbit/monitor/instance/RabbitMemoryMonitor.kt)
```java
/**
 * 只能用在debug model,
 **/
private fun getMemoryInfoInDebug(): RabbitMemoryInfo {
	val info = Debug.MemoryInfo()
	Debug.getMemoryInfo(info)
	
	val memInfo = RabbitMemoryInfo()
	memInfo.totalSize = (info.totalPss) * 1024 // 这个值比profiler中的total大一些
	memInfo.vmSize = (info.dalvikPss) * 1024   // 这个值比profiler中的 java 内存值小一些, Doesn't include other Dalvik overhead
	memInfo.nativeSize = info.nativePss * 1024
	memInfo.othersSize = info.otherPss * 1024 + info.totalSwappablePss * 1024
	memInfo.time = System.currentTimeMillis()
	memInfo.pageName = RabbitMonitor.getCurrentPage()
	
	return memInfo
}

// 统计进程的内存信息 total Pss
fun getMemoryByActivityManager(): Long {
	... 
    mActivityManager?.getProcessMemoryInfo(intArrayOf(Process.myPid())) ?: return 0
    ...
}
    

//内存的泄漏  利用ActivityLifeCycleCallback机制
weakreference
activity，activity.class.simplename
activity onStop的时候 手动GC2次 sleep间隔500ms，影响性能
```

4. **==FPS 帧率、卡顿==**
- Vsync 16ms
- 卡顿：偶尔丢1、2帧不会造成卡顿，但如果在某个时间点丢了较多帧，就会卡顿。[Matrix wiki-什么是卡顿](https://github.com/Tencent/matrix/wiki/Matrix-Android-TraceCanary#%E4%BB%80%E4%B9%88%E6%98%AF%E5%8D%A1%E9%A1%BF)
	> 1. 人眼识别的流程效果为：1秒显示60帧，每一帧都均匀分布耗时，即1帧≈16ms  
	> 2. FPS 意为 "帧/秒"，即1秒多少帧。  
	> 3. 若 FPS 低，只能说明1秒内显示的帧数较少，但不能表示一定发生了卡顿现象。假设，如果1秒只有30帧（即FPS低），但如果每一帧 "都耗时32ms"，则依然说明这30帧是连续的、均匀的，人眼看起来顶多觉得不流畅，但不会觉得卡顿。  
	> 4. 所谓发生卡顿，是指某一时间段内，发生了 "大量集中丢帧" 现象，即某1帧耗时突然超过了16ms，且这个超出值非常大，大到丢掉了后面非常多的帧。  
	> 5. Matrix引入 "掉帧程度" 的这个指标，来衡量卡顿程度(具体参见wiki文档)
	> 6. 综上，APM的 **==技术指标==** 应该是“单次连续掉了多少帧” ；**==治理手段==** ，是统计发生卡顿时，两帧之间的所有方法耗时。

- 原理知道了，代码写在什么位置？？
`onActivityResumed()` 开启监听 `onWindowFocusChanged()`

- 两种方案：
1. Message的消息监听（推荐）
```java
Choreographer.getInstance().postFrameCallback(new Choreographer.FrameCallback() {
    @Override    
    public void doFrame(long frameTimeNanos) {
        if(frameTimeNanos - mLastFrameNanos > 100) {
            ...
        }
        
        mLastFrameNanos = frameTimeNanos;
        
        Choreographer.getInstance().postFrameCallback(this);
    }
});
```

2. Choreographer（线上性能影响大）
```java
//推荐下面
public static void loop() {
    ...
    for (;;) {
        ...
        // This must be in a local variable, in case a UI event sets the logger
        Printer logging = me.mLogging;
        if (logging != null) {
            logging.println(">>>>> Dispatching to " + msg.target + " " + msg.callback + ": " + msg.what);
        }
        msg.target.dispatchMessage(msg);
        if (logging != null) {
            logging.println("<<<<< Finished to " + msg.target + " " + msg.callback);
        }
        ...
    }
}
```

5. **==启动耗时监控==**
- 冷启动、暖启动
- Activity的first Frame
- CP大法 ContentProvider。