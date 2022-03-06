日期： 2022-03-06

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286758972902684&vid=387702294683480712

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8802%EF%BC%892022.1.16-%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E7%AC%AC%E4%BA%8C%E6%AC%A1%E8%AF%BE---%E8%B7%AF%E5%93%A5

---
<br>

# ADB命令
==参考《性能优化内存篇.pdf》==

## 基础
 
1. 官网“ADB 调试桥”
2. 手机型号
3. mDisplayId=0，显示屏编号
4. adb shell cat /system/build.prop 
5. xlog 日志系统


## 核心命令
1. ==学习 Linux内核 内存分配机制==
2. adb shell cat /proc/meminfo
	- 进程使用的内存 = MemTotal - MemFree
	- MemAvailable = MemFree + 正在用但可回收的内存(cache、buffer、slab)
	- Buffers、Cached、SwapCached，内存黑洞，搜“Linux kernel 动态内存分配”
	- KernelStack，内核栈
	- A、B Service
3. adb shell dumpsys meminfo
4. adb shell procrank
5. adb shell top meminfo
6. adb shell cat /proc/pid/oom_adj
	- 进程类别，值越高越容易被杀死
7. adb shell vmstat 2
	- si输入、so输出
	- bi、bo


## 核心指标
1. VSS：Virtual Set Size 虚拟耗用的内存(包含与其他进程共享占用的虚拟内存）
2. RSS：Resident Set Size 实际使用的物理内存（包含与其他进程共享占用的内存）
3. PSS：Proportional Set Size 实际使用的物理内存（按比例包含与其他进程共享占用的内存）
4. USS：Unique Set Size 进程独自占用的物理内存（不包含与其他进程共享占用的内存）
5. 用户CPU时间、系统CPU时间、Linux的TMS、Walltime、Cmos RTC


## Java内存分配和垃圾回收算法
补习2期课件：《OOM与内存优化.pdf》
1. 本地方法栈
2. 程序计数器
3. 虚拟机栈，栈帧
4. 堆，新生代、老生代
5. 垃圾回收算法
6. android kill机制，lowmemorykill，ADJ值，adb shell cat /proc/pid/oom_adj
7. 强、软、弱引用，Reference构建函数、ReferenceQueue、WeakHashMap


## LeakCanary
读讲义
1. 源码分析


## 线上内存监测
1. 目标：监测Activity泄漏
2. WeakHashMap
3. 如何识别Activity回收的时机，LifeCycle.onDestory()，WeakHashMap<Activity,String>
4. 如何判断Activity无法回收 
5. 监控后台时机，然后gc()，遍历WeakHashMap
6. Debug.MemoryInfo，debugMemoryInfo.nativePass>>10 堆内存（OOM核心原因）、getTotalPss()整体内存