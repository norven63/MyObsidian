### Binder 核心机制精讲

![[Pasted image 20251017002855.png]]

**核心角色：**
- **Client进程：** 服务调用方。    
- **Server进程：** 服务提供方。    
- **ServiceManager：** 大管家，负责服务的注册与查询。    
- **Binder驱动：** 内核层，整个通信机制的核心枢纽。

**工作流程详解：**
1. **服务注册**    
    - Server进程启动后，将其提供的 **Binder实体**（服务的引用）和一个 **字符串名称** 传递给Binder驱动。        
    - Binder驱动为该实体创建位于内核的 **“引用”**，并通知ServiceManager。        
    - ServiceManager将此名称与引用记录在册，完成服务发布。
        
2. **服务获取**    
    - Client进程向ServiceManager查询指定名称的服务。        
    - ServiceManager将对应的Binder引用返回给Client。此引用是一个指向Server进程中Binder对象的“句柄”。
        
3. **发起调用（核心：数据封装与转发）**    
    - Client进程将方法参数序列化为 `Parcel` 数据。        
    - 通过系统调用 `ioctl` 将数据、Binder引用和目标方法码一并提交给 **Binder驱动**。
        
4. **驱动中转（核心：线程切换与内存映射）**    
    - Binder驱动根据Binder引用找到目标Server进程。        
    - 它将Client的数据包**直接拷贝**到Server进程的内核映射的一块**共享内存**中，从而避免了一次中间临时拷贝。        
    - 驱动唤醒在Server进程目标线程池中等待的线程，将工作交给它。
        
5. **执行与返回**    
    - Server进程的 `Binder线程` 被唤醒，从共享内存中反序列化出参数，并执行真实的服务方法。        
    - 将返回结果同样序列化，通过原路径交给Binder驱动。        
    - 驱动再将结果数据拷贝回Client进程的地址空间。        
    - Client进程的等待线程被唤醒，收到返回结果，完成一次调用。
        
---

### 核心原理与优势

- **一次拷贝：** 通过内存映射，Client数据由内核直接拷贝到Server内核缓冲区，无需经用户空间中转，效率极高。    
- **线程池模型：** Server端采用线程池处理并发请求，无需自身管理。    
- **引用计数：** 驱动维护Binder对象的引用计数，实现跨进程的生命周期管理。    
- **安全性：** 基于进程UID/PID的校验机制，由驱动保障安全。


获取Binder线程名，格式为`Binder_x`, 其中x为整数。每个进程中的binder编码是从1开始，依次递增; 只有通过spawnPooledThread方法来创建的线程才符合这个格式，对于直接将当前线程通过joinThreadPool加入线程池的线程名则不符合这个命名规则。 另外,目前Android N中Binder命令已改为`Binder:<pid>_x`格式, 则对于分析问题很有帮忙,通过binder名称的pid字段可以快速定位该binder线程所属的进程p.

---

Binder IPC机制，就是指在进程间传输数据（binder_transaction_data），一次数据的传输，称为事务（binder_transaction）。对于多个不同进程向同一个进程发送事务时，这个同一个进程或线程的事务需要串行执行，在Binder驱动中为binder_proc和binder_thread都有todo队列。
也就是说对于进程间的通信，就是发送端把binder_transaction节点，插入到目标进程或其子线程的todo队列中，等目标进程或线程不断循环地从todo队列中取出数据并进行相应的操作。
在Binder驱动层，每个接收端进程都有一个todo队列，用于保存发送端进程发送过来的binder请求，这类请求可以由接收端进程的任意一个空闲的binder线程处理；接收端进程存在一个或多个binder线程，在每个binder线程里都有一个todo队列，也是用于保存发送端进程发送过来的binder请求，这类请求只能由当前binder线程来处理。binder线程在空闲时进入可中断的休眠状态，当自己的todo队列或所属进程的todo队列有新的请求到来时便会唤醒，如果是由所需进程唤醒的，那么进程会让其中一个线程处理响应的请求，其他线程再次进入休眠状态。