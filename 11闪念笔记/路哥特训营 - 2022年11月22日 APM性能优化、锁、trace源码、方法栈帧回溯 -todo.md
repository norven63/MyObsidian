日期： 2022-11-22

标签： #学习笔记 #技术

学习资料： 
[视频](https://iww0abxi5u.feishu.cn/minutes/obcnq9v699489uhbj1614lq4) 、 [讲义](https://kdocs.cn/l/ciqwIcJ9jOhO)

[掘金上的对标文章](https://juejin.cn/post/7107137302043820039)
[西瓜视频抓栈Sliver](https://mp.weixin.qq.com/s/LW3eMK9O2tfFtZcu5eqitg)

[B站南京大学操作系统](https://www.bilibili.com/video/BV1Cm4y1d7Ur/?spm_id_from=333.999.0.0)
[大佬博客](https://brendangregg.com)
[Linux 内核调度全景图](https://makelinux.github.io/kernel/map)

---
<br>

### 锁
1. 互斥锁
	1. 同一个时间分片，只能有一个线程持有该锁
2. 自旋锁
		1. 当等待一个短耗时任务锁时，没必要让CPU频繁切换线程上下文，就可以通过自旋锁持续占住CPU分片，减少开销。但是因为一直占住CPU，所以不适合在等待长耗时任务锁
		2. spinlock_t、volatile
3. 信号量：（todo补）
		1. 本质是一个技术器，如果初始值为1，那么此为二元信号量
		2. P/V操作；P申请，计数器-1；V释放，计数器+1
		3. POSIX信号量
		4. 有名信号量、无名信号量
		5. 匿名共享内存，匿名信号量，内存块里找对应地址的文件，a map机制 把文件映射到内存的一个地址空间
		6. 有名信号量由 `sem_open` 打开，`sem_unlink` 删除；无名信号量由 `sem_init` 打开，`sem_destroy` 删除
		7. 有名信号量进程之间使用；无名信号量线程之间使用，也可以搭建共享内存在进程之间使用

<br>

### Memory
1. 用户空间的进程模型==**<todo补>**==
	- Text Segment：二进制可执行代码
	- Data Segment：静态常量
	- BSS Segment：未初始化的静态变量
	- 堆：
		- 堆是往高地址增长的，用来动态分配内存的区域
		- malloc就是这里面分配的
	- Memory MappingSegment：
		- 把文件映射进内存里用的，二进制的执行文件依赖某个动态链接库
		- 就是在这个区域里面将so文件映射到内存中
	- 栈：主线程的函数调用栈就是用这里的，function frame、function stock、frame pointer
1. 虚拟内存&物理内存之间的相互映射==**<todo补>**==
	1. 分段
		- 段号、段表
		- 段选择因子
		- 段内偏移量
		- 段基地址
		- 段界限
		- 高地址、低地址
		- 好处：连续的内存空间；坏处：内存碎片、内存交换的空间太大
	2. 分页
		- 页号
		- 页内偏移量
		- 虚拟页号、物理页号
		- 页表

<br>


### Ftrace
1. mount | grep debugs
2. echo function_graph > current_tracer
3. trace-cmd
apt install trace-cmd

<br><br>


### trace源码
ftrace

堆栈信息：
[/art/runtime/backtrace_helper.h](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/backtrace_helper.h) [/art/runtime/backtrace_helper.cc](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/backtrace_helper.cc)

[/art/runtime/trace.h](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/trace.h) [/art/runtime/trace.cc](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/trace.cc)
- TraceMode：跟踪模式
	- kMethodTracing 插桩
	- kSampling 时间周期采样

- [android.os.Debug](http://aospxref.com/android-11.0.0_r21/xref/frameworks/base/core/java/android/os/Debug.java).startMethodTracing()

Trace产物文件: 14B = 2B(ThreadID)+4B(EncodeTraceMrthodAndAction)+4B(Thread_cpu_diff)+4B(wall_clock_diff)

// Create Trace object.
new Trace(...)
-  ringbuffer 环线缓冲区

trace.cc#RunSamplingThread()
- `runtime->GetThreadList()->ForEach(GetSample, the_trace);`
- GetSample()
```cpp
static void GetSample(Thread* thread, void* arg) REQUIRES_SHARED(Locks::mutator_lock_) {

  std::vector<ArtMethod*>* const stack_trace = Trace::AllocStackTrace();

  StackVisitor::WalkStack(

      [&](const art::StackVisitor* stack_visitor) REQUIRES_SHARED(Locks::mutator_lock_) {

        ArtMethod* m = stack_visitor->GetMethod();

        // Ignore runtime frames (in particular callee save).

        if (!m->IsRuntimeMethod()) {

          stack_trace->push_back(m);

        }

        return true;

      },

      thread,

      /* context= */ nullptr,

      art::StackVisitor::StackWalkKind::kIncludeInlinedFrames);

  Trace* the_trace = reinterpret_cast<Trace*>(arg);

  the_trace->CompareAndUpdateStackTrace(thread, stack_trace); // 对比前后2次栈帧的结果，为了判断函数的状态（是否出栈了）.方法栈的调度回溯核心算法

}
```
- ==**StackVisitor**==
- CompareAndUpdateStackTrace() 
```cpp
void Trace::CompareAndUpdateStackTrace(Thread* thread,

                                      std::vector<ArtMethod*>* stack_trace) {

 CHECK_EQ(pthread_self(), sampling_pthread_);

 std::vector<ArtMethod*>* old_stack_trace = thread->GetStackTraceSample();

 // Update the thread's stack trace sample.

 thread->SetStackTraceSample(stack_trace);

 // Read timer clocks to use for all events in this trace.

 uint32_t thread_clock_diff = 0;

 uint32_t wall_clock_diff = 0;

 ReadClocks(thread, &thread_clock_diff, &wall_clock_diff);

 if (old_stack_trace == nullptr) {

   // If there's no previous stack trace sample for this thread, log an entry event for all

   // methods in the trace.

   for (auto rit = stack_trace->rbegin(); rit != stack_trace->rend(); ++rit) {

     LogMethodTraceEvent(thread, *rit, instrumentation::Instrumentation::kMethodEntered,

                         thread_clock_diff, wall_clock_diff);

   }

 } else {

   // If there's a previous stack trace for this thread, diff the traces and emit entry and exit

   // events accordingly.

   auto old_rit = old_stack_trace->rbegin();

   auto rit = stack_trace->rbegin();

   // Iterate bottom-up over both traces until there's a difference between them.

   while (old_rit != old_stack_trace->rend() && rit != stack_trace->rend() && *old_rit == *rit) {

     old_rit++;

     rit++;

   }

   // Iterate top-down over the old trace until the point where they differ, emitting exit events.

   for (auto old_it = old_stack_trace->begin(); old_it != old_rit.base(); ++old_it) {

     LogMethodTraceEvent(thread, *old_it, instrumentation::Instrumentation::kMethodExited,

                         thread_clock_diff, wall_clock_diff);

   }

   // Iterate bottom-up over the new trace from the point where they differ, emitting entry events.

   for (; rit != stack_trace->rend(); ++rit) {

     LogMethodTraceEvent(thread, *rit, instrumentation::Instrumentation::kMethodEntered,

                         thread_clock_diff, wall_clock_diff);

   }

   FreeStackTrace(old_stack_trace);

 }

}
```

// 代理类、钩子函数，对所有函数进行各种行为的监控
[/art/runtime/instrumentation.h](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/instrumentation.h) [/art/runtime/instrumentation.cc](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/instrumentation.cc)
- kMethodEntered、kMethodExited
- kMethodUnwind 栈帧溯源（可以参考Matrix的unwind算法）
- EnableSingleThreadDeopt()、UpdateStubs()
- `class InstallStubsForClass extends ClassVisitor`
- MethodEnterEventImpl()、MethodExitEventImpl()  监听函数的进栈、出栈，回调trace.cc的MethodEntered()、MethodExited()

trace.cc#EncodeTraceMrthodAndAction()
trace.cc#FinishTracing()

Suspend -> WalkStack
TraceLogMethodTraceEvent


总结：
1. trace.cc文件，关键入口，开启跟踪、结束跟踪、采样和插桩2种方式
2. trace文件的组成形式，14b + content
3. 理解谷歌提供的2种采集方式，采样 vs 插桩，采样不精准，所以线上一般用插桩
4. 简单了解小册子上的JVM调用栈内容

思路：
- start函数会传入目标线程
	private volatile long nativepeer; // Java JNil的代码反射获取到这个变量，然后保存给JNI
- HOOK d1动态API open dlsym close
- elf文件 /proc/self/maps 获取sht_dynsym sht_strtab\sht_progbits mmap odm/1ib64 /system/lib64 vendor/lib64
- [/art/runtime/runtime.h](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/runtime.h)  [/art/runtime/runtime.cc](http://aospxref.com/android-11.0.0_r21/xref/art/runtime/runtime.cc)