日期： 2022-03-05

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286754677935388&vid=387702294543295533

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8801%EF%BC%892021.1.13-%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E7%AC%AC%E4%B8%80%E6%AC%A1%E8%AF%BE%EF%BC%88%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E7%AF%87%EF%BC%89---%E8%B7%AF%E5%93%A5

---
<br>

# 线上APM监控相关的知识点

## 技术点
Bytecode
Hook（PLT）
JS注入
Gradle（ASM、javapoet）

## Java层实现
CPU
内存
FPS
ANR
卡顿
内存（GC、OOM）
网络（http hook）
功耗（电量、发热、wifi）
远程下发、日志回捞

## APM
1. 配置（注解 + json）
2. 数据链的保存
	- App启动
3. Crash
	- Thread UnCaought
4. CPU、GC、电量
	- /prco/stat、/prco/pid/stat、BatterMonitor
5. ANR
	- 文件的检查，/data/anr/traces.txt

# 数据结构
## ArrayList
1. 构建函数的源码
	- 数组
	- 默认size
2. add()的源码

## HashMap 源码 
1. 数组+链表+红黑树，结合各方的优点
	![[Pasted image 20220306155555.png]]
2. Node对象
3. hashCode()：hash冲突，扰动函数降低hash碰撞，无符号右位移16位、混合原始hash码的高位和低位以增加低位随机性、混合后的低位参杂（变相保留）高位部分特征
4. tableSizeFor()
5. putMapEntries()
6. remove()
7. get() -> getNode()：
	![[Pasted image 20220306155704.png]]
8. 位运算：一个数求余的%等价为 X&(2^N-1)，(n-1)&hash求index
9. 负载因子
10. 红黑树
11. Hash桶
![[Pasted image 20220306155624.png]]


## SparseArray
