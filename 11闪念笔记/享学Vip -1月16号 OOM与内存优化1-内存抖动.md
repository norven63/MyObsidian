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
3. adb shell dumpsys meminfo
	- VSS 虚拟内存
	- RSS 共享so动态链接库
	- A Service、B Service，进程优先级
	- PSS 实际实用的物理内存（a一个系统所有进程的PSS相加=真正PSS占用内存
	- USS 


## 核心指标
1. 