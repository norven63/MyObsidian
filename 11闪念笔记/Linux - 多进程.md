日期： 2022-04-09

标签： #学习笔记 #技术 #Linux

学习资料： 
https://blog.csdn.net/weixin_40519315/article/details/104156838

https://blog.csdn.net/jobbofhe/article/details/82192092

http://c.biancheng.net/view/3492.html

https://blog.csdn.net/weibo1230123/article/details/82187572
---
<br>

## 基础背景知识
### 进程是什么
1. 进程是运行在 Linux 中的程序的一个**任务实例**，代表一坨程序文件被系统加载到内存中执行的**动态**过程。
2. 进程***大致***的几个生命周期：
	- 创建
	- 执行
	- 结束
	- 清除
3. 进程的状态
	- D（uninterruptible sleep，不可中断休眠状态）——进程正在休眠并且不能恢复，直到一个事件发生为止。
	- R（runnable，运行状态）——进程正在运行。
	- S（sleeping，休眠状态）——进程没有在运行，而在等待一个事件或是信号。
	- T（stopped，停止状态）——进程收到SIGSTOP, SIGSTP, SIGTIN, SIGTOU信号后停止运行运行。
	- Z（a defunct process，僵死状态）——进程已终止，但进程描述符存在，直到父进程调用wait4()系统调用后释放
<br>

### 关于PID
1. 每个进程在被创建时都会被分配到一个唯一 PID 标识，并在消亡时取消该 PID。
2. 被取消的 PID 会延时再次复用 , 但不会同时出多个相同的 PID。

<br>

### 进程空间
1. 每个进程有 4G 独立的进程空间，其中 0-3G 是用户空间，3G-4G是内核空间。
2. 每个进程也有4G虚拟地址空间，不是实际的内存，需要使用时，向系统申请。

<br><br>

## 多进程
### 父子进程
#### 基本概念
1. Linux中的进程都是由其它进程启动。如果 进程a 启动了 进程b，那么称 a 是 b 的父进程，b 是 a 的子进程。
2. Linux启动时，0号进程 启动 **1号进程(init)** 和 **2号进程(内核线程)**，后续其它进程是由1、2直接或间接产生。
3. **1号进程(init )** 是所有用户进程的祖先；**2号进程(内核线程)** 是所有内核进程的祖先。

#### 退出&回收
1. 子进程退出时，无论正常还是异常，父进程会收到信号，其内存资源必须由父进程负责回收。
2. 如果父进程不处理子进程的结束信号，子进程则变成**僵尸进程**。而当父进程退出时，子进程变成**孤儿进程**，并由 **1号进程** 后续负责回收销毁。
<br>

### fork()函数
#### 函数能力
调用fork()函数时，复制父进程的进程空间来创建子进程。此时子进程拷贝了父进程的所有变量、环境变量、程序计数器的当前空间和值，并且子进程修改自身变量的值时并不影响父进程的变量值。
 ![Engelbart|400](https://img-blog.csdnimg.cn/20200203193209959.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MDUxOTMxNQ==,size_16,color_FFFFFF,t_70)
 
#### 执行细节
 ```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
 
int main()
{
    printf("+++process %d start running!ppid = %d\n",getpid(),getppid());
 
    pid_t pid = fork();// for子线程

	// 由此开始的代码，分为两个进程分别执行。其中父进程的pid值为原PID号，子进程的pid值为0；fork失败则pid值为-1
    if(pid)//父进程
    {
        printf("parent:process %d start running!ppid = %d\n",getpid(),getppid());
        //do something        
    }
    else//子进程
    {
        printf("child:process %d start running!ppid = %d\n",getpid(),getppid());
        //do something
        
        exit(0);
    }
 
    exit(0);
}
 ```
 - 调用fork()后，代码分为两个进程分别执行，但是返回值pid会不一样。其中父进程的pid值为原PID号，子进程的pid值为0；如果fork失败则pid值为-1。
 - 父进程与子进程的执行顺序是不确定的，取决于CPU内核使用的调度算法，需要通过进程通信才能保证父子进程间的数据消息同步。

#### vfork()函数
vfork()也是用于创建一个进程，用法与fork()一致。但是它俩存在以下2个相异点：
1. 父子进程执行顺序：
	- fork()：不确定，由CPU调度器决定。
	- vfork()：先执行子进程，等子进程执行exit(1)后，再执行父进程。
2. 进程之间数据同步：
	- fork()：父子进程不共享一段地址空间，各自修改内容互不影响。
	- vfork()：在子进程调用exit之前，它在父进程的空间中运行，共享代码区和数据区，其地址和内容都是一 样的。也就是说子进程能够更改父进程的数据段、栈和堆。

<br><br>

## 常见的进程
### systemd进程



### idle进程
由系统自动创建，运行在内核态，pid=0。其前身是系统创建的第一个进程，也是唯一一个没有通过fork或者kernel_thread产生的进程。完成加载系统后，演变为进程调度、交换。
<br>

### init进程
由idle通过kernel_thread创建，在内核空间完成初始化后加载init程序，完成系统的初始化，pid = 1。它是系统中所有其它用户进程的祖先进程。
<br>

### kthreadd进程
由idle通过kernel_thread创建，并始终运行在内核空间，负责所有内核线程的调度和管理，pid = 2。它的任务就是管理和调度其他内核线程kernel_thread，会循环执行一个kthread的函数，该函数的作用就是运行kthread_create_list全局链表中维护的kthread，当我们调用kernel_thread创建的内核线程会被加入到此链表中，因此所有的内核线程都是直接或者间接的以kthreadd为父进程。