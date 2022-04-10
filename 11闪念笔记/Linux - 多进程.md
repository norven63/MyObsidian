日期： 2022-04-09

标签： #学习笔记 #技术 #Linux

学习资料： 
https://blog.csdn.net/weixin_40519315/article/details/104156838

https://blog.csdn.net/jobbofhe/article/details/82192092

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
	- D（不可中断休眠状态）——进程正在休眠并且不能恢复，直到一个事件发生为止。
	- R（运行状态）——进程正在运行。
	- S（休眠状态）——进程没有在运行，而在等待一个事件或是信号。
	- T（停止状态）——进程被信号停止，比如，信号 SIGINT 或 SIGSTOP。
	- Z（僵死状态）——标记为 defunct 的进程是僵死的进程，它们之所以残留是因为父进程没有处理回收销毁它们。

<br>


### 关于PID
1. 每个进程在被创建时都会被分配到一个唯一 PID 标识，并在消亡时取消该 PID。
2. 被取消的 PID 会延时再次复用 , 但不会同时出多个相同的 PID。

<br>

### 进程空间
1. 每个进程有 4G 独立的进程空间，其中 0-3G 是用户空间，3G-4G是内核空间。
2. 每个进程也有4G虚拟地址空间，不是实际的内存，需要使用时，向系统申请。

<br>

### 1号进程
- Linux启动时，0号进程 启动 **1号进程(init)** 和 **2号进程(内核线程)**，之后0号进程退出，后续其它进程是由1、2直接或间接产生。
- **1号进程(init )** 是所有用户进程的祖先；**2号进程(内核线程)** 是所有内核进程的祖先。
<br><br>

## 多进程
### 父子进程
1. Linux中的进程都是由其它进程启动。如果 进程a 启动了 进程b，那么称 a 是 b 的父进程，b 是 a 的子进程。
2. 子进程退出时，无论正常还是异常，父进程会收到信号，其内存资源必须由父进程负责回收。
3. 如果父进程不处理子进程的结束信号，子进程则变成**僵尸进程**。而当父进程退出时，子进程变成**孤儿进程**，并由 **1号进程** 后续负责回收销毁。

<br>

### fork函数
1. 调用fork函数时，复制父进程的进程空间来创建子进程。
 ![Engelbart|400](https://img-blog.csdnimg.cn/20200203193209959.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MDUxOTMxNQ==,size_16,color_FFFFFF,t_70)
 ```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
 
int main()
{
    printf("+++process %d start running!ppid = %d\n",getpid(),getppid());
 
    pid_t pid = fork();
 
    if(pid)//父进程
    {
        printf("parent:process %d start running!ppid = %d\n",getpid(),getppid());
        //do something
        //...
    }
    else//子进程
    {
        printf("child:process %d start running!ppid = %d\n",getpid(),getppid());
        //do something
        //...
        exit(0);
    }
 
    exit(0);
}
 
 ```
2. 