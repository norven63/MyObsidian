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


## 核心命令
1. adb shell cat /proc/meminfo
	- MemTotal - MemFree = 进程使用的内存
	- 
2. 