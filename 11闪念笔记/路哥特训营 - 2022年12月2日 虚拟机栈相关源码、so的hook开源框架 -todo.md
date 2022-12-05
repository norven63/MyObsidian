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
4.   /art/runtime/ 下的几个核心类
	- signal_catcher.cc - 信号捕捉器
	- runtime.cc
	- thread_list.cc
	- intern_table.cc
	- class_linker.cc
	- java_vm_ext.cc
	- thread.cc
		1. tls32：结构体，封装线程相关的信息
		2. tid
		3. jobject peer、线程句柄
		4. suspend
		5. monitor enter exit
		6. thin_loc_thrad_id
        初始化流程:
  ```c++
  bool Thread::Init(ThreadList* thread_list, JavaVMExt* java_vm, JNIEnvExt* jni_env_ext) {
   tls32_.thin_lock_thread_id = thread_list->AllocThreadId(this);
  }
  
  uint32_t ThreadList::AllocThreadId(Thread* self) {
    MutexLock mu(self, *Locks::allocated_thread_ids_lock_);
    for (size_t i = 0; i < allocated_ids_.size(); ++i) {
   if (!allocated_ids_[i]) {
     allocated_ids_.set(i);
     return i + 1;  // Zero is reserved to mean "invalid".
   }
    }
    // 这里会不会就是 线程超上限oom?
    UNREACHABLE();
  }
  ```
 结论:thin_lock_thread_id就是线程ThreadList中的线程的index



### so hook框架
github
- avs333/Nougat_dlfunctions - 学习思路
	- fake_dlfcn.c - define fatal()
- xDL - 直接用
	- xdl.c 
	- [Android 7.0+ linker namespace 的限制。](https://zhuanlan.zhihu.com/p/401547387 "Android 7.0+ linker namespace 的限制。")
- xHook bhook
- XCrash
- xUnwind
- Linker
