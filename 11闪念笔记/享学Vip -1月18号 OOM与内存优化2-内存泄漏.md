日期： 2022-03-07

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286763267869980&vid=387702294779338800

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8803%EF%BC%892022.1.18-%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E7%AC%AC%E4%B8%89%E6%AC%A1%E8%AF%BE%EF%BC%88%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%20%E5%86%85%E5%AD%98%E7%AF%87%EF%BC%89---%E8%B7%AF%E5%93%A5

---
<br>

# 常见内存泄漏的原因
1. 根本原因：长生命周期持有短寿命周期，导致短无法被gc回收
	- 静态变量、单例（不要持有activity、view）
	- 内部类、匿名内部类（new Handler）
	- 动画未在activity销毁时cancel
	- 文件fd没有close


# Koom
1. Native Heap泄漏
	- 借助 Tracing Garbage Collection，可跟踪垃圾回收算法
	- libmemunreachable.so
		- google提供的库，进行堆空间检测
		- 从官网上巴拉源码，自己通过ndk编译成so，即可检测 “Native Heap泄漏”
		- breakpad，通过地址追踪还原对象
		- 底层通过 Malloc Debug 对C语音的内存操作进行hook

## 源码
1. 1:34:00开始
2. xhook，把某个so的malloc等函数hook替换成自己的
3. ida逆向so
4. 核心代码：leak_monitor.cpp