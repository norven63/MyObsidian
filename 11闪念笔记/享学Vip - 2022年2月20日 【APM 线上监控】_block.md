日期： 2022-03-06

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - 
https://ke.qq.com/webcourse/347420/103755197#taid=12286797627608348&vid=387702296383669027 （上）
https://ke.qq.com/webcourse/347420/103755197#taid=13385596290813212&vid=387702296478569180 （下）

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8811%EF%BC%892022.2.20-%E7%BA%BF%E4%B8%8A%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96---%E8%B7%AF%E5%93%A5


---
<br>

### Tips

目的：

- 知识点的沉淀、总结

- Mem（2种方案 手动GC[Matrix]、阈值的处理[Koom]）

- FPS(Handler机制、Printer)、idleHandler（）

-

延迟操作 Handler.postDelayed(Runnable r,long time)

~~~
Looper.myQueue().addIdelHandler(new Message.IdelHandler(){
          //queueIdle return true/false

})
~~~

so动态加载

Tinker的so的加载流程

- https://github.com/KeepSafe/ReLinker

UnsatisfiedLinkError : 主要的原因是兼容性的问题。包so的裁剪由于国内的厂商魔改ROM

改的是so加载的路径（3种）。ReLinker最牛逼的地方就是解析SO的2进制文件，获取so的依赖属性。

**性能优化的总结**

https://github.com/SusionSuc/rabbit-client

https://github.com/Tencent/matrix/wiki/Matrix-Android-TraceCanary

做？怎么做？设计还有架构？

主流的开源项目 调研 怎么用？

- Matrix：功能大而全、相对比较重力度，不适合公司的业务的迭代，经常Crash

- 听云SDK（>8.0 CPU 指标的问题）

- 网易 腾讯GT （时间非常老）16年

- 360的APM gradle 集成的时候会有很多的问题

**指标的问题**

- 稳定性的问题（崩溃的问题）

breakpad+bugly+Firebase

- 流量/网络 （Http协议的可达率、流量的大小）OKHTTP的拦截器

全链路的网络监控APM、网络一体化的问题、协议本身（Socket）统一的处理

**建议大家重点关注的APM的性能指标：**

- 电量（battery historian、广播）

- 流量消耗

TrafficStats / getUidRxBytes(int uid) /getTotalbytes()  

后台偷跑:后台定时任务，获取时间间隔流量，计算

- 内存指标的统计/内存的泄漏

```java
 /**
   * 只能用在debug model,
   * */

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

    //pss
    mActivityManager?.getProcessMemoryInfo(intArrayOf(Process.myPid())) ?: return 0

    //内存的泄漏  application的 生命周期的监听
    weakreference
    activity，activity.class.simplename
    activity onStop的时候 手动GC 2次 sleep
```

- FPS 原理知道了 代码写在什么位置？？

  ~~~java
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
  ~~~

  OnActivityResumed（）开启监听 onWindowFocusChanged

  建议大家用 Message的消息监听，不要用Choreographer。

- 启动耗时监控

冷启动:APP

暖启动：

activity的first Frame

CP大法 ContentProvider。