日期： 2022-02-08

标签： #学习笔记 #技术 #Android

学习源： 
百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9005%E3%80%91FrameWork%E5%B1%82%E6%BA%90%E7%A0%81%E8%A7%A3%E6%9E%90%2F%EF%BC%8801%EF%BC%892021.12.9-Handler%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90---Alvin%E8%80%81%E5%B8%88

腾讯课堂 - 
3期： https://ke.qq.com/webcourse/347420/103755197#taid=12286694548393244&vid=387702292645177658
2期： https://ke.qq.com/webcourse/347420/103755197#taid=13024037353901340&vid=387702292621512076

---

## 如何评估对Hanlder的理解程度
1. 线程间如何通信（内存共享）
2. 线程间不会干扰
3. 为什么 wait/notify 用处不大

## 课程大纲
源码epoll，设计思路，设计模式， 异步消息和同步消息，消息屏障/ handlerThread IntentServer



源于生活高于生活

Choreographer，艺术，舞蹈者，跳舞 节奏

屏幕的点击。



handler： 地下 - 地上《 消息管理机制：消息-》事务

子线程（bean）  -》 主线程（显示）


ActivityThread： handler

  

java main（）jvm

功能机：FATAL error，所有的代码，都是handler

lancher （app）：zygote -》 jvm -》 ActvityThread.main

  

子线程

handler -> sendMessage -> messasgeQueue.enqueueMessage   //消息队列队列的插入节点

  

looper.loop() -> messasgeQueue.next() -> handler.dispatchMessage() -> handler.handleMessage()

  

主线程

Message,在动的过程，内存

new Messaage() obtain()

  

## 数据结构

  

用单链表实现的优先级队列，

Messge-》next-》Message -》Next（Message）

排序算法？插入

先后顺序，时间，怎么排序的 ，队列？

  

先进，先出

  

--- 基本内容懂了

  

looper 源码？ 核心： 构造函数， loop，  ThreadLocal

初始化？

  

new Looper()

ThreadLocal, 多线程，线程上下文的存储变量

  

线程 - Looper 不能改的？

  

key value

<key, value>< set(key1, value1); set(key1, value2);

  

线程1 -> ThreadLocalMap 1 -> <唯一的ThreadLocal, valuse> Looper1 -> 唯一的MessageQueue1

  

线程2 -> ThreadLocalMap 2 -> <唯一的ThreadLocal, valuse> Looper2 -> 唯一的MessageQueue2

  

final MessageQueue mQueue;

  

static :

  

内部类持有外部类的对象：学习，群，Java编程思想 2~7章

  

recycleVIew  adpater  ViweHolder》一定？ 生命周期的问题。

  

内存泄漏原因——内部类持有外部类：

enqueueMessage{

 msg.target = this;

}

Activity中new一个Handler匿名内部类 -> new Message() -> Message持有Handler对象 -> Handler持有Activity对象 -> GC：JVM 可达性算法，无法回收Activity对象

  

很多通信，quit

  

消息睡眠和唤醒机制

  

生产者-消费者设计模式：

多线程： 10个事件，11

  

## MessageQueue源码分析

  

1. enqueueMessage()没有设置上限阻塞，可以无限入队。所以如果逻辑处理不当，会导致内存溢出卡死。

  

2. next()有两个方面的阻塞，通过调用MessageQueue.nativePollOnce(long,ptr, int timeoutMillis)实现：

1）获取到队列头的 首个message，发现未到执行时刻 ，自动唤醒

2）messageQueue队列为空，没有message，则无限等待，直到有入队行为发生，通过NativeWake唤醒自己

  

## Looper.quit()

  

如果子线程中创建的Looper对象调用quit(): 唤醒线程 -> messagequeue -> null -> 退出loop的for循环；

主线程的Looper对象不允许调用quit()，会抛 "Main thread not allowed to quit." 异常。

  

## MessageQueue同步机制

  

通过synchronized对象锁实现，所有的函数、代码块，都会受限

  

一个线程只有一个Looper对象（ThreadLocal实现） -> 1个线程只有一个可以操作的 MessageQueue 对象

  

## 到底Message如何做到 子线程 -> 主线程

  

核心是内存共享。

内存不分线程，函数分线程。

子线程里面执行的函数 ，这个函数就在子线程里面。

  

子Thread构建msg对象 -> 调用Handler.sendMessage(msg) -> MessageQueue.enequeMessage(msg)

主线程Loop() -> 轮询 MessageQueue -> 获取msg对象 -> 执行目标逻辑

  

```java

static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>(); -> 所有的线程共享操作同一个 主线程里的sThreadLocal对象

```

  

## 构建Message对象

  

Message.obtain() -> 享元设计: 内存复用 -> 防止抖动,发生OOM：

new BitMap()、RecycleView等等

  

## Looper死循环 block为什么不会导致应用卡死

  

Msg超过5s -> Handler 发送ANR消息 -> 立刻处理，弹出系统ANR提示窗

  

主线程执行loop死循环，表示线程没事做了，交出CPU资源，并不是指某个Msg超过5s

  

立刻处理

  

同步屏障： 架构思维

  

刷新UI

16ms左右 刷新UI：

  

同步： 立刻执行  messageQueue.postSyncBarrier（） -》立刻执行，不能等别的消息

异步：

  

next： 队列得第一个消息先执行

  

源码？看 AMS  流程，具体  binder 3 1 dex 1， 3 /

  

解决这个有可能得异步问题

面试： 多线程得锁

  

wait();   synchronized（）

nofityall（） 

最简单得： okhttp glide，

  
  

IntentService 

 应用：

 service：？ 处理后台耗时任务

 new Thread

 service 后台

 handler源码？源码有什么用

 处理完》 service 自动停止：内存释放

 同一个线程-》1 2 3 4 ： 对线程的控制么

 到底还有别的地方用么？

 很多地方有这么用

 fragment什么生命周期管理

 整理文章：原创 写的好的问题，我们收录： 200

 周周

 Glide.with(context).from（url）.into(iamgeView)

  

 context:? fragment.getAppalicationContext

  

```java

RequestManagerFragment getRequestManagerFragment(final android.app.FragmentManager fm) {

 pendingRequestManagerFragments = new HashMap<Fragment>();

 //尝试根据id去找到此前创建的RequestManagerFragment

 RequestManagerFragment current = (RequestManagerFragment) fm.findFragmentByTag(FRAGMENT_TAG);

 if (current == null) {

 //如果没有找到，那么从临时存储中寻找

 current = pendingRequestManagerFragments.get(fm);

 if (current == null) {

 //如果仍然没有找到，那么新建一个RequestManagerFragment，并添加到临时存储中。

 //然后开启事务绑定fragment并使用handler发送消息来将临时存储的fragment移除。

 current = new RequestManagerFragment();

 pendingRequestManagerFragments.put(fm, current);

 fm.beginTransaction().add(current, FRAGMENT_TAG).commitAllowingStateLoss();

 handler.obtainMessage(ID_REMOVE_FRAGMENT_MANAGER, fm).sendToTarget();

 }

 }

}

```

  

 多线程：调用一次？ 线性事件，线性执行.源码

 handler  必须应用

 binder    广播怎么 binder/研究

 2节课

 第一个： Handler loop 休眠为什么不会导致ANR

 第二个： Messagequeue 队列处理机制，在fragment 生命周期管理中的应用，整理。 2周

 第三个： 同步屏障研究一下

  
  
  

msg.target = null -> msg1-> msg2->msg3->msg4

  

20 ： 第20个 非常重要得，必须马上执行：如何去做