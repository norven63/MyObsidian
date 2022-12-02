日期： 2022-12-02

标签： #学习笔记 #技术

学习资料： 


---
<br>

### 核心源码与机制
1. 老罗的《Dalvik虚拟机进程和线程的创建过程分析》博客
2. 熟悉 /art/Android.bp 中写的编译后so文件
3. 虚拟机栈：
	1. 局部变量表 Slot
	2. /art/runtime/stack.cc、::GetMethod、quick_method、/art/runtime/stackvisitor.cc、StackVisitor、顶上那张current stack layout图
	3. 操作数栈
	4. 动态链接
5.   /art/runtime/ 下的几个核心类
- signal_catcher.cc - 信号捕捉器
- runtime.cc
- thread_list.cc
- intern_table.cc
- class_linker.cc
- java_vm_ext.cc
- thread.cc
	1. tls32：结构体，封装线程相关的信息。thin_loc_thrad_id、tid
	2. jobject peer、线程句柄
	3. suspend


### so hook框架
github
- avs333/Nougat_dlfunctions - 学习思路
	- fake_dlfcn.c - define fatal()
- xDL - 直接用
	- xdl.c - 
- DLHook
- XCrash
- Linker
