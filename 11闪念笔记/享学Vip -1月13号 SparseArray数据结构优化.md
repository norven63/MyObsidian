日期： 2022-03-05

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286754677935388&vid=387702294543295533

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
2. hashCode()：hash冲突，扰动函数降低hash碰撞，无符号右位移16位、混合原始hash码的高位和低位以增加低位随机性、混合后的低位参杂（变相保留）高位部分特征
3. tableSizeFor()
4. getNode()
5. 负载因子
6. 红黑树
7. 