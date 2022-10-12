### Linux APi 汇总

标准C库的IO函数通常是可以跨平台的。标准C库会调用Linux OS提供的API。

#### 系统IO函数
文件描述符在进程的内核区的PCB（进程控制块）中的文件描述表中，通过系统调用返回给程序。文件描述符表是一个整型数组，默认大小是1024（也就是最多同时能打开1024个文件），前三个整型元素由系统占用，0表示STDIN，1表示STDOUT，2表示STDERR，每打开一个新文件就会占用一个文件描述符，而且是空闲的最小的一个文件描述符。调用Linux中的open方法就能够返回一个文件描述符。

~~~c
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
// 打开一个已经存在的文件
// flags：对文件的权限设置以及其他的设置：O_RDONLY、O_WRONLY、O_RDWR（这三个权限互斥）
// 成功返回值是一个文件描述符，失败返回的是-1
int open(const char *pathname, int flags);
// 打开创建一个新的文件
// pathname：要创建的文件路径
// flags：对文件的操作权限和其他设置：
//     - 必选项：O_RDONLY、O_WRONLY、O_RDWR（这三个权限互斥）
//     - 可选项：O_CREATE：如果文件不存在则新建文件
//     - flags是一个int型，32位，每一位就是一个标志位，所以如果要多个权限的话，使用逻辑|
// mode：八进制的数，表示创建出的新的文件的操作权限，比如：0777（0开头是八进制），最终的权限为：mode&~umask，umask的作用是抹去某些权限，使得权限更加合理
int open(const char *pathname, int flags, mode_t mode);


// errno：属于Linux系统函数库的，库里面的一个全局变量，记录的是最近的错误号
#include<stdio.h>
// 打印errno对应的错误描述
// s参数是用户描述，会在打印错误描述的时候一同打印出来
// 打印格式如下：s : errno
void perror(const char *s);


#include<unistd.h>
// 关闭一个文件描述符
int close(int fd);


#include<unistd.h>
// 将文件读进内存
// - fd：文件描述符，open得到
// - buf：需要读取数据存放的地方，传一个数组的地址，是一个传出参数
// - count：指定的数组的大小
// 返回0表示已经读到文件尾了，-1表示没有读取成功，>0表示返回了实际读取到的字节数
ssize_t read(int fd, void *buf, size_t count);
// 将数据写进文件
// - buf：要往磁盘写入的数据
// - count：要写的数据的实际的大小
// 成功：返回被写入的字节数量，失败，返回-1
ssize_t write(int fd, const void *buf, size_t count);


#include<unistd.h>
#include<fcntl.h>
#include<sys/types.h>
// 针对一个文件进行文件指针偏移，可以实现的操作有
// 1. 移动文件指针到头文件
// 2. 获取当前文件指针的位置
// 3. 获取文件长度
// 4. 拓展文件的长度
// - offset：off_t就是long，表示一个偏移量
// - whence：SEEK_SET（设置文件指针的偏移量，从头开始）、SEEK_END（文件大小+offset）、SEEK_CUR（从当前位置往后偏移offset）
// 返回文件指针的位置
off_t lseek(int fd, off_t offset, int whence)


#include <sys/stat.h>
// 获取一个文件的相关信息
// path：要操作的文件路径
// buf：是一个传出参数，保存获取到的文件信息（用一个stat的结构体保存）
// 成功，返回0，失败返回-1
// 获取的信息有：文件的设备编号、文件的类型和存取权限、硬链接数、用户ID、组ID、修改访问时间等
int stat(const char *restrict path, struct stat *restrict buf);
// 获取软连接的文件相关信息
int lstat(const char *restrict path, struct stat *restrict buf);
~~~

#### 文件属性操作函数

~~~c
// 用于判断某个文件是否有某个权限，或者检查某个文件是否存在
// - mode：R_OK、W_OK、X_OK、F_OK（判断文件是否存在）
// 成功返回0， 失败返回-1
int access(const char* pathname, int mode);
// 用于修改一个文件的权限
int chmod(const char* pathname, int mode);
// 改变文件所有者
int chown(const char* pathname, uid_t owner, gid_t group);
// 用于缩减或者扩展文件的尺寸到指定大小
// - len：需要最终文件变成的大小
int truncate(const char* path, off_t len);
~~~

#### 目录操作函数

~~~C
#include<sys/stat.h>
#include<sys/type.h>
// 新建一个文件夹，指定权限(八进制数)
// 成功返回0，失败返回-1
int mkdir(const char* pathname, mode_t mode);
// 删除一个文件夹
int rmdir(const char* pathname);
// 重命名一个文件夹/文件
int rename(const char* oldpath, const char* newpath);
// 修改进程当前工作目录
int chdir(const char* pathname);
// 获取当前的工作路径
// - buf：是传出参数
// - size：指定buf数组的大小
// 返回指向buf的首地址
char *getcwd(char* buf, size_t size);
~~~

#### 目录遍历函数

~~~C
#include<dirent.h>
#include<sys/types.h>
// 打开一个目录流
// - name：需要打开的目录的名称
// 返回一个指针，指向一个目录流，错误的话返回NULL
DIR* opendir(const char* name);
// 读取目录中的数据，调用一次，目录流指针将会指向下一个实体
// 读取到目录末尾或者失败返回NULL，成功则返回结构体dirent
struct dirent *readdir(DIR *dirp);
// 关闭一个目录流
int closedir(DIR *dirp);
~~~

#### 文件描述符操作函数

~~~C
#include<unistd.h>
// 复制文件描述符，将oldfd替换成当前可用的最小的文件描述符，这个新的文件描述符也指向oldfd指向的文件
// 返回这个最小的文件描述符
int dup(int oldfd);
// 重定向文件描述符
// 调用成功后，newfd指向的文件会close，并将newfd指向oldfd指向的文件
// 返回值是newfd
int dup2(int oldfd, int newfd);
// fcntl根据cmd行为不同
// 当cmd为F_DUPFD时，操作就和dup相同
// 还可以修改文件描述符状态、标志：
// 	- F_GETFL：获取指定文件描述符文件状态flag，获取的flag和我们通过open函数传递flag相同
//  - F_SETFL：设置文件描述符文件状态flag，其实就是文件的权限
//      必选项：O_RDONLY、O_WRONLY、O_RDWR
//      可选项：O_APPEND（追加数据），O_NONBLOCK（IO非阻塞）
int fcntl(int fd, int cmd, .../* arg */);
~~~

#### 进程控制相关函数

~~~C
进程控制相关函数#include<sys/types.h>
#include<unistd.h>
// 创建一个子进程，创建的方式是复制当前的进程，当前的进程为新建的进程的父进程
// 在父进程中如果成功，返回子进程ID，在子进程中返回的是0；在父进程中返回-1，表示创建子进程失败
// pid_t实质上是int
// fork完进程之后，后面的代码就是子进程和父进程都有的代码，但是是运行在不同的内存空间
// fork是通过读时共享、写时拷贝来实现的
pid_t fork(void);

// 获取当前进程ID
pid_t getpid();
// 获取当前进程的父进程ID
pid_t getppid();

// 退出进程
// - status: 退出状态
// void exit(int status)是标准c库的函数，比_exit()多做了刷新IO缓冲区，关闭文件描述符的工作
void _exit(int status);

#include<sys/wait.h>
// 针对僵尸进程，有下面的函数在父进程中回收子进程的资源
// 等待任意一个子进程结束后回收资源（不用等待父进程来回收子进程资源，从而防止生成僵尸进程），阻塞
// - wstatus： 进程退出时的状态信息，是一个传出参数，传入的是一个int类型的地址
// 成功，返回被回收的子进程，失败，返回-1
// 调用wait函数，进程会被阻塞，直到他的一个子进程退出或者收到一个不能忽略的信号
// 调用一次只能回收一个子进程
pid_t wait(int *wstatus);
// 可以指定等待某一个子进程，而且可以设置为非阻塞
// - pid: pid>0，回收某个子进程的pid；pid=0，回收当前进程组的所有子进程；pid=-1，回收所有的子进程，相当于wait()；pid<-1，后手某个进程组的组id的绝对值，回收指定进程组中的子进程
// - options：0表示阻塞，WNOHANG表示非阻塞
// 返回值>0，返回的是子进程id，=0表示还有子进程没有被回收，-1表示错误
pid_t waitpid(pid_t pid, int *wstatus, int options);
~~~

#### exec函数族

exec函数族是根据指定的文件名找到可执行文件，并用它来**取代**调用进程的内容。一般在子进程中调用exec来取代子进程中的内容。执行成功不会返回，调用失败返回-1。那么我们就可以fork一个子进程之后，调用exec函数让他执行指定的任务。

~~~c
// - path: 需要执行文件的路径名称
// - arg: 是可执行文件的参数列表，参数最后需要以NULL结束
// 只有出错的时候才会有返回值，返回-1，并设置errno
int execl(const char *path, const char *arg, ... /* (char *) NULL */);

// - file: 需要执行的可执行文件名，会在环境变量中查找对应的文件名，找到则执行，找不到返回错误
int execlp(const char *file, const char *arg, ... /* (char *) NULL */)

// - argv: 需要的参数的一个字符串数组
int execv(const char *path, char *const argv[]);

// 这一组函数族还有几个，就不一一列出，实现的功能都是一样的，就是传入的参数会有些点点变化
// l:list	v:vector p:path	e:environment

~~~

#### 进程间通讯相关函数

~~~C
// 匿名管道的创建
#include<unistd.h>
// 创建一个匿名管道，用于进程间通讯，只能用于具有关系的进程之间的通讯
// 在fork子进程之间创建管道，默认阻塞
// - pipefd: 传出参数，pipefd[0]是读端文件描述符, pipefd[1]是写端文件描述符
// 成功返回0，失败返回-1
// 在实际的开发环境中，一般一个进程只用一端，要么是写段，要么是读段，因为如果同时用的话，一个进程会读取到自己想要发送的内容
int pipe(int pipefd[2]);



// 有名管道FIFO的创建
// 可用于没有关系的进程间通讯，实质上是一个特殊的文件，只要能访问文件所在的路径
// 不支持lseek来改变读写指针
// 创建完有名管道之后，还需要分别以只读、只写打开该管道才能进行进程间通讯
// 如果FIFO读端没有打开，写端会在open处阻塞
#include<sys/types.h>
#include<sys/stat.h>
// - pathname：管道名称的路径
// - mode: 文件的权限，相当于open函数中的mode
// 成功，返回0，失败，返回-1
int mkfifo(const char *pathname, mode_t mode);



// 内存映射：将磁盘文件的数据映射到内存中，用户通过修改内存就能够修改磁盘文件
// 非阻塞
#include<sys/mman.h>
// 将一个文件或者设备的数据映射到内存中
// - addr：映射内存的首地址，一般传NULL，由内核决定
// - length：要映射的数据的长度
// - prot：对申请的内存映射区的操作权限：PROT_EXEC、PROT_READ、PROT_WRITE、PROT_NONE
// - flags：标志映射区的数据是否和磁盘文件同步：MAP_SHARED、MAP_PRIVATE
// - fd：需要操作的文件的文件描述符
// - offset：偏移量，一般不用，即指定从文件的offset处开始映射
// 返回值是创建的内存映射的首地址，失败，则返回MAP_FAILED
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
// 释放内存映射，从内存地址addr开始，释放length长度的内存
int munmap(void *addr, size_t length);
// 内存映射的注意事项：
// 如果对mmap的返回值ptr做++操作，munmap能否成功？可以++操作，但是不能够munmap
// 如果open fd的时候O_RDONLY，但是mmap是prot参数指定PROT_READ|PROT_WRITE会怎样？失败，prot必须小于open的权限
// 如果文件偏移量为1000会怎样？偏移量必须是4k的整数倍，偏移1000会失败
// 可以open的时候O_CREAT一个新文件来创建映射区吗？可以，但是创建的文件的大小如果为0，是会报错的，可以使用lseek或者truncate来扩展文件的大小
// mmap后关闭文件描述符，对mmap映射有没有影响？映射区还存在，没有任何影响
// 对ptr越界操作会怎样？会出现段错误
// 内存映射还可以实现文件复制功能
// 还可以匿名映射，即不需要文件实体进行一个内存映射



// 信号，有时也可以叫做软件中断，他是在软件层次上对中断机制的一种模拟，是一种异步通讯方式
// 信号通常是由内核产生
// core文件可以在gdb中使用core-file core来查看程序在哪里出现了错误
#include<sys/types.h>
#include<signal.h>
// 给任意进程或进程组pid发送某个信号sig
// - pid：如果是0，则发送给该进程组中的所有进程；>0，发送给指定的进程；-1，发送给每一个有权限接受这个信号的进程；<-1，这个pid=某个进程组的ID取反
// - sig：需要发送的信号的编号或者宏值，0表示不发送任何信号
int kill(pid_t pid, int sig);
// 给当前进程发送信号
// - sig：要发送的信号
// 成功，返回0，失败，返回非0
int raise(int sig);
// 发送SIGABRT信号给当前进程，杀死当前进程
void abort(void);
// 设置定时器，函数调用，开始倒计时，当倒计时为0时，函数会给当前的进程发送一个信号：SIGALRM
// - second：倒计时时间，单位为秒
// 返回值：之前无定时器则返回0，之前有定时器，则返回倒计时剩余的时间
// SIGALRM，默认终止当前的进程，每个进程都有且只有一个定时器
#include<unistd.h>
unsigned int alarm(unsigned int seconds);
// 设置定时器，可以替代alarm函数，精度为微秒，可以实现周期性定时器
// - which：定时器以什么时间计时：ITIMER_REAL，真实时间，时间到达，发送SIGALRM，常用；ITIMER_VIRTUAL，用户时间，时间到达，发送SIGVTALRM；ITIMER_PROF，以该进程在用户态和内核态下所消耗的时间来计算，时间到达发送SIGPROF
// - new_val：设置定时器的属性，每隔多少时间执行、延迟多长时间执行，例如：过10s后，每隔2s执行一次
// - old_value：记录上一次的定时的时间参数，一般为NULL，不使用
// 成功，返回0，失败返回-1
#include<sys/time.h>
int setitimer(int which, const struct itimerval *new_val, struct itimerval *old_value);
// 设置收到指定信号之后的相应操作
// - signum：被捕捉的信号，一般使用宏值
// - handler：捕捉到信号之后要怎么处理，SIG_IGN，忽略信号；SIG_DFL，使用信号默认行为；还可以是回调函数，可以自定义
// 返回值：如果成功，返回上一次注册的信号处理函数的地址，第一次调用返回NULL；失败，返回SIG_ERR
// SIGKILL SIGSTOP不能够被捕捉和忽略
#include<signal.h>
typedef void (*sighandler_t)(int)
sighandler_t signal(int signum, sighanler_t handler);
// 要了解sigaction这个函数，得先了解信号集：阻塞信号集、未决信号集
// 未决：从信号的产生到信号被处理前的这一段时间
// 阻塞：阻止信号被处理，不是阻止信号被产生；阻塞信号集默认不阻塞任何信号，想要阻塞信号的话需要用户自己调用相应的API
// 清空信号集中的数据，将信号集中的所有标志位置为0
// 以下函数都是对自定义的信号集进行操作
int sigemptyset(sigset_t *set);
// 将信号集中的所有标志置为1
int sigfillset(sigset_t *set);
// 设置信号集中的某一个信号对应的标志位为1，表示阻塞这个信号
int sigaddset(sigset_t *set, int signum);
// 设置信号集中的某一个信号对应的标志位为0，表示不阻塞这个信号
int sigdelset(sigset_t *set, int signum);
// 这个函数和signal函数实现的功能差不多，只是实现的方法不一样
// - signum：需要捕捉的信号
// - act：捕捉到信号之后相应的处理动作：结构体中存放有处理函数指针，临时阻塞信号集，信号以哪种方式处理
// - oldact：上一次对信号捕捉的相关设置，一般不使用，传递NULL
// 成功返回0，失败返回-1
int sigaction(int signum, const stuct sigaction *act, struct sigaction *oldact);



// 共享内存，最高效的进程间通讯方法
// 允许两个或者多个进程共享物理内存的同一块区域（通常被称为段），不需要内核介入，所以高效
// 涉及到进程同步的问题
// 和管道不同的是，管道需要讲内存从用户空间复制到内核空间
// 步骤：shmget、shmat、shmdt、shmctl
#include<sys/ipc.h>
#include<sys/shm.h>
// 创建一个新的共享内存段，或者获取一个既有的共享内存段的标识。新创建的内存段中的数据都会被初始化为0.
// - key：key_t是一个整型，通过这个找到或者创建一个共享内存，16进制，非0
// - size：共享内存的大小，页对其
// - shmflg：共享内存的属性，访问权限，附加属性(创建：IPC_CREAT；是否存在，IPC_EXCL)
// 失败，返回-1，成功返回共享内存的引用ID
int shmget(key_t key, size_t size, int shmflg);
// 和当前的进程进行关联
// - shmid：共享内存的标识，有shmget返回
// - shmaddr：共享内存的起始地址，一般为NULL，由内核决定
// - shmflg：对共享内存的操作权限设置（读、写、执行权限）
// 成功，返回共享内存的首地址，失败返回-1
void *shmat(int shmid, const void *shmaddr, inst shmflg);
// 解除当前进程和共享内存的关联
// - shmaddr：共享内存的首地址
int shmdt(const void *shmaddr);
// 删除共享内存，共享内存要删除才会消失，创建共享内存的进程被销毁了对共享内存是没有任何影响的
// - shmid：共享内存的标识
// - cmd：要做的操作（IPC_STAT，获取当前共享内存状态，IPC_RMID，标记共享内存被销毁）
// - buf：需要设置或者要获取的共享内存相关的属性信息
int shmctl(int shmid, int cmd, struct shmid_ds *buf);
// 根据指定的路径名和int值，生成一个共享内存的key，生成的key可用于shmget
// - pathname：文件路径
// - proj_id：int类型的值，但是系统调用只会使用其中的一个字节
key_t ftok(const char *pathname, int proj_id);
// 注意事项：
// 操作系统如何知道一个共享内存被多少个进程关联？共享内存中有一个结构体会记录关联的进程个数，可用`ipcs -m`来进行查看
// 可不可以对共享内存进行多次删除shmctl？可以，因为shmctl是标记删除共享内存，而不是直接删除
// 共享内存可以直接创建，内存映射需要磁盘文件，共享内存效率更高

~~~

#### 进程组、会话操作函数

~~~C
// 获取当前进程组ID
pid_t getpgrp(void);
// 获取获取指定进程进程组ID
pid_t getpgid(pid_t pid);
// 设置指定进程进程组ID
int setpgid(pid_t pid, pid_t pgid);
// 获取指定进程的会话ID
pid_t getsid(pid_t pid);
// 设置当前进程的会话ID
pid_t setsid(void);
~~~

#### 线程相关函数

~~~c
// 线程之间非共享的数据有：线程ID、代码段、栈空间
// 编译的时候要加上-pthread参数，意思是指定链接的库
#include<pthread.h>
// 获取当前线程的线程ID
pthread_t pthread_self(void);
// 比较两个线程ID是否相等
// 不同的操作系统，pthread_t类型的实现不一样，有的是无符号长整型，有的是结构体实现
// 所以，不用直接==去判断
int pthread_equal(pthread_t t1, pthread_t t2);
// 创建一个新子线程
// - thread：传出参数，线程创建成功后，子线程的线程ID保存在这个变量中
// - attr：设置线程的属性，一般使用默认值，NULL
// - start_toutine：函数指针，需要线程执行的函数
// - arg：给前面的函数指针传递的参数
// 成功，返回0，失败返回一个错误号，和errno不太一样，不能通过perror获得，可以通过strerror(pthread_create的返回值)来获取发生了什么错误
// 如果执行的函数需要两个及以上的参数，那么可以将参数封装到一个结构当中
int pthread_create(pthread_t *thread, const pthread_attr_t *attr, void *(*start_toutine) (void *), void *arg);
// 终止一个线程，在哪个线程中调用就终止哪个线程
// - retval：作为一个返回值，可以在pthread_join中获取到
// 主线程退出不会影响其他线程
void pthread_exit(void *retval);
// 和一个已经终止的线程进行连接
// 为什么要连接？和进程的wait()相似，但是任意一个线程都能回收其他的线程，不一定要父子关系。连接，就能对连接的线程进行资源回收，要不然也会出现僵尸线程
// 这是一个阻塞函数
// - thread：需要回收的子线程的ID
// - retval：是一个二级指针，接受子线程退出时的返回值，不需要这个返回值的话就设置为NULL
// 成功，返回0，失败，返回错误号
int pthread_join(pthread_t thread, void **retval);
// 分离一个线程，当一个被分离的线程结束的时候，会自动回收资源
// - thread：要分离的线程
// 不能够多次detach一个线程
// 不能去join一个被分离的线程，强行操作会报错
int pthread_detach(pthread_t thread);
// 发送一个取消请求给线程，取消掉指定线程（线程终止）
// - thread：要取消的线程
// 要取消一个线程需要满足一些条件：线程能否取消、线程取消类型
// 并不是马上取消，只有当线程执行到取消点才能被取消，这些取消点通常是一些系统调用
int pthread_cancel(pthread_t thread);



// 初始化线程属性变量
int pthread_attr_init(pthread_attr_t *attr);
// 释放线程属性的资源
int pthread_attr_destory(pthread_attr_t *attr);
// 获取线程分离的状态属性
int pthread_attr_getdetachstate(const pthread_attr_t *attr, int *detachstate);
// 设置线程分离的状态属性
int pthread_attr_setdetachstate(pthread_attr_t *attr, int detachstate);
~~~

#### IO多路复用

~~~c
// select
// 主旨思想：
// 1.构建一个关于文件描述符的列表，将要监听的文件描述符添加到该列表
// 2.调用系统函数，监听该列表中的文件描述符，直到这些描述符中的一个或者多个进行IO操作时，该函数才返回；这个函数是阻塞；函数对文件描述符的检测操作是由内核完成的
// 3.在返回时，它会告诉进程有多少（哪些）描述符要进行IO操作
// 在调用accept之前使用select来监听socket对应的文件描述符，当select返回，判断socket对应的文件描述符发生了改变，发生了改变，就说明有新的链接，再调用accept，这样accept就不会阻塞
#include<sys/time.h>
#include<sys/types.h>
#include<unistd.h>
#include<select.h>
// 主要的功能就是完成上面的主旨思想，fd_set是一个bitmap
// - nfds: 委托内核检测的最大文件描述符的值+1；为什么要加1？因为文件描述符是从0开始算的。
// - readfds：要检测的文件描述符读的集合，委托内核检测哪些文件描述符的读的属性；一般检测读操作，对应的是对方发送过来的数据，因为读是被动的接收数据，检测的就是读缓冲区；是一个传入传出参数
// - writefds：要检测的文件描述符的写的集合，委托内核检测哪些文件描述符的写的属性，一般不检测
// - exceptfds：检测发生异常的文件描述符的集合
// - timeout：设置的超时时间；如果为NULL，永久阻塞；如果结构体的值都为0，则是不阻塞；值大于零，阻塞对应的时间
// 返回值：如果是-1，调用失败；如果大于0，返回值表示集合中有多少个文件描述符发生了变化
// 例子：如果需要检测3、4、100、101这四个文件描述符，那么使用FD_SET将fd_set类型的reads对应的标志位置1，然后传入select---->select(101+1, &reads, NULL, NULL, NULL);
int select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout);
// 将fd_set中参数文件描述符fd对应的标志位设置为0
void FD_CLR(int fd, fd_set *set);
// 判断fd对应的标志位是0还是1
int FD_ISSET(int fd, fd_set *set);
// 将参数文件描述符fd对应的标志位设置为1
void FD_SET(int fd, fd_set *set);
// fd_set全部初始化为0
void FD_ZERO(fd_set *set);
// 缺点：
// 1.因为在select中，readfds是传入参数，内核也会在readfds上进行修改，所以传出的时候可能会发生变化，因此不能重用；想要重用，那么在开始前将原来的fd_set复制一份
// 2.每次将fds从用户态到内核态拷贝，耗时
// 3.文件描述符只能有1024个
// 4.在内核态需要遍历O(n)



// poll
// - fds：pollfd类型的数组，这是一个需要检测的文件描述符的集合
// - nfds：这个是第一个参数数组中最后一个有效元素的下表+1，就相当于select中的第一个参数，指定需要循环多少次
// - timeout：和select中的相同
// 返回值为-1，表示失败；>0表示成功，表示检测到集合中有多少个文件描述符发生变化
#include <poll.h> 
int poll(struct pollfd *fds, nfds_t nfds, int timeout);
struct pollfd{
	int fd; // 委托内核该检测的文件描述符
	int events; // 委托内核检测文件描述符的什么事件
	int revents; // 文件描述符实际发生的事件
}
// 解决select的问题：
// 1.pollfd数组大小不受限制，可以超过1024
// 2.文件描述符集合可重用，因为内核只修改pollfd结构体中的revents来通知用户



// epoll
// 调用顺序：epoll_create --> epoll_ctl --> epoll_wait
struct eventpoll{
	.... 
	struct rb_root rbr;  // 红黑树，存放需要检测的文件描述符信息
	struct list_head rdlist; // 双向链表，存放状态发生改变的文件描述符
	.... 
};
// 创建一个新的epoll实例。在内核中创建了一个数据，这个数据中有两个比较重要的数据，
// 一个是需要检测的文件描述符的信息（红黑树），还有一个是就绪列表，存放检测到数据发生
// 改变的文件描述符信息（双向链表）。 
// - size : 目前没有意义了。随便写一个数，必须大于0 
// 返回值： -1 : 失败 ; >0 : 文件描述符，操作epoll实例的
int epoll_create(int size); 
// 对epoll实例进行管理：添加文件描述符信息，删除信息，修改信息 
// - epfd : epoll实例对应的文件描述符 
// - op : 要进行什么操作 
//		- EPOLL_CTL_ADD: 添加 
//		- EPOLL_CTL_MOD: 修改 
//		- EPOLL_CTL_DEL: 删除 
// - fd : 要检测的文件描述符 
// - event : 检测文件描述符的什么事情，要检测读啊还是检测写啊，是这个意思
// 常见的epoll检测事件：EPOLLIN、EPOLLOUT、EPOLLERR、EPOLLET
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event); 
// 检测函数 
// - epfd : epoll实例对应的文件描述符 
// - events : 传出参数，保存了发送了变化的文件描述符的信息 
// - maxevents : 第二个参数结构体数组的大小 
// - timeout : 阻塞时间, 0 : 不阻塞; -1 : 阻塞，直到检测到fd数据发生变化，解除阻塞; > 0 : 阻塞的时长（毫秒） 
// 返回值： 成功，返回发送变化的文件描述符的个数 > 0 ；失败 -1
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout); 
// epoll_wait和epoll_ctl都有epoll_event数据结构，因此贴出
struct epoll_event{
	uint32_t events; // epoll事件
	epoll_data_t data;; // 用户变量
}
// 解决select问题：
// 1.由红黑树来存放需要检测的文件描述符集合，所以可以检测的文件描述符多少不受限制
// 2.在内核中维护文件描述符集合状态，通过epoll_ctl来操作状态，可重用
// 3.直接在内核中维护集合，而且用红黑树维护，效率高，不需要两次内核态用户态复制
// 4.epoll_wait直接返回哪些文件描述符发生了状态改变，不需要O(n)

// epoll的两种工作模式
// LT: Level-Triggered，水平触发，同时支持阻塞和非阻塞。如果你不做任何操作、或者只处理了一部分的数据，内核还是会继续通知你（下一次epoll_wait的时候）。默认的工作模式。
// ET: Edge-Triggered，边沿触发，只支持非阻塞，高效。文件描述符状态发生改变，内核只会通知一次。所以，第一次通知的时候，就需要把文件描述符对应的缓冲区全部读取完（需要使用非阻塞才会不出现问题）。
// ET模式设置是在epoll_ctl中的event参数里设置的，比如说可以设置为EPOLLIN | EPOLLET
// 当read设置为非阻塞，且返回的是-1的时候，需要判断errno，如果errno为EAGAIN，那么表示数据读完




// 两种事件处理模式
// 同步IO通常用于实现Reactor模式，异步IO通常用于实现Proactor
// Reactor：要求主线程只负责监听文件描述符上是否有事情发生，有的话就立即将该事件通知工作线程，将socket可读可写事件放入请求队列，交给工作线程处理。除此之外，主线程不做任何其他实质性的工作。读写数据，接受新的链接，以及处理客户请求均在工作线程中完成。
// Proactor：将所有的IO操作都交给主线程和内核来处理，工作线程仅仅负责业务逻辑。

~~~

#### C语言可变参数

~~~c
// 宏定义了一个指针类型，这个指针类型指向参数列表中的参数
va_list ap;

// 修改了用va_list申明的指针，比如ap，使这个指针指向了不定长参数列表省略号前的参数
void va_start(va_list ap, last_arg)

// 获取参数列表的下一个参数，并以type的类型返回
type va_arg(va_list, type);

// 参数列表访问完以后，参数列表指针与其他指针一样，必须收回，否则出现野指针。一般va_start 和va_end配套使用
void va_end(va_list ap);
~~~

#### 协程

主要是通过`ucontext`库里面的方法

~~~c
/*初始化ucp结构体，将当前的上下文保存到ucp中*/
int getcontext(ucontext_t *ucp);

/*设置当前的上下文为ucp，setcontext的上下文ucp应该通过getcontext或者
makecontext取得，如果调用成功则不返回。如果上下文是通过调用getcontext()
取得,程序会继续执行这个调用。如果上下文是通过调用makecontext取得,程序会调
用makecontext函数的第二个参数指向的函数，如果func函数返回,则恢复
makecontext第一个参数指向的上下文第一个参数指向的上下文context_t中指向的
uc_link.如果uc_link为NULL,则线程退出。*/
int setcontext(const ucontext_t *ucp);

/*makecontext修改通过getcontext取得的上下文ucp(这意味着调用
makecontext前必须先调用getcontext)。然后给该上下文指定一个栈空间ucp->stack，
设置后继的上下文ucp->uc_link.

当上下文通过setcontext或者swapcontext激活后，执行func函数，argc为func
的参数个数，后面是func的参数序列。当func执行返回后，继承的上下文被激活，如
果继承上下文为NULL时，线程退出。*/
void makecontext(ucontext_t *ucp, void (*func)(), int argc, ...);

/*保存当前上下文到oucp结构体中，然后激活upc上下文。 

 如果执行成功，getcontext返回0，setcontext和swapcontext不返回；如果执
 行失败，getcontext,setcontext,swapcontext返回-1，并设置对于的
 errno.*/
int swapcontext(ucontext_t *oucp, ucontext_t *ucp);

// 简单说来，getcontext获取当前上下文，setcontext设置当前上下文，swapcontext切换上下文，makecontext创建一个新的上下文。
~~~

