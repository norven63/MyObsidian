日期： 2022-04-06

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286789037673756&vid=387702296136380051

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8809%EF%BC%892022.2.15-%E7%BD%91%E7%BB%9C%E5%92%8C%E7%94%B5%E9%87%8F%E7%9A%84%E4%BC%98%E5%8C%96---%E8%B7%AF%E5%93%A5

---
<br>

### 一、网络优化
##### 1、DNS优化：
- DNS解析：域名 -> IP
	- HOOK
	- 运营商劫持
	- 公网的路由（映射耗时）
- HttpDNS
	- 引入阿里云SDK，com.aliyun.ams:alicloud-android-httpdns，调用okhttp的dns()接口
	- 域名映射到多个ip地址
	- 客户端通过httpdns服务获取ip地址 -> 选择最优的ip地址（ping，延时低） -> 缓存 -> 容灾（localdns兜底处理）
	- 直连IP：将header中的host字段设置成 ip
	- InetAddress.getAllByName(ip) 可以传入ip，也可以是hostname
	- 优化TCP时延高：
		- 缓存，Map，hostname：ips
			- 120s~300s 过期时间，过期更新
			- 网络切换时更新
		- 异步解析httpdns

![[20220407234718.png|500]]
- json示例
```json
"dns": [  
	{ 
		"host": "api.bilibili.com", 
		"client_ip": "58.49.114.214", 
		"ips": [ "116.207.118.12" ], 
		"ttl": 95, 
		"origin_ttl": 180 
	}, 
	{ 
		"host": "app.bilibili.com", 
		"client_ip": "58.49.114.214", 
		"ips": [ "116.207.118.12" ], 
		"ttl": 180, 
		"origin_ttl": 180 
	}
]
```

<br>

##### 2、GZip压缩传输
**优先看： https://blog.csdn.net/newone_helloworld/article/details/52472950**
https://www.jianshu.com/p/cf7ae9c99d50
https://blog.csdn.net/clerk0324/article/details/51672933

<br><br>

### 二、电量优化
##### 影响耗电的几个因素：
- CPU
- Network
- Location
- Wake Locks
- Alarms & Jobs


##### 1、一些API
1. 低电量测试（看文档adb）
2. 待机模式（看文档）
3. 加白名单：`new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)`

##### 2、Android中的WakeLock机制
1. CPU分 AP、BP
	- AP（Application Processor）：ARM架构的处理器，用于运行Linux+Android用户界面、app开发
	- BP（Baseband Processor）：用于运行实时操作系统(RTOS)，运行手机“射频通信”控制软件。
2. WakeLock：当app申请了WakeLock，会阻止AP挂起，导致系统无法进入休眠，保证app的任务即使在灭屏的时候可以正确执行。
```Java
<!--WakeLock需要的权限-->
<uses-permission android:name="android.permission.WAKE_LOCK"/>


PowerManager pm= (PowerManager) this.getSystemService(Context.POWER_SERVICE);
PowerManager.WakeLock
wakeLock=pm.newWakeLock(PowerManager.ON_AFTER_RELEASE|PowerManager.PARTIAL_WAKE_LOCK, "Tag");


//申请WakeLock，避免AP挂起
wakeLock.acquire();

// TODO ... do work...

//在适当的时机释放申请WakeLock
//注：当使用wakeLock.acquire(timeout)的方式时系统会自动释放
wakeLock.release();


//通过 adb 命令过滤电量日志
adb shell dumpsys "power|grep -i wake"
```

adb 日志
```shell
//加锁时
no_cached_wake_locks=true
mWakefulness=Awake
mWakefulnessChanging=false
mWakeLockSummary=0x1
mLastWakeTime=509144080 (30113 ms ago)
mHoldingWakeLockSuspendBlocker=true
mWakeUpWhenPluggedOrUnpluggedConfig=true
mWakeUpWhenPluggedOrUnpluggedInTheaterModeConfig=false
mDoubleTapWakeEnabled=false
Wake Locks: size=1
mLock:176961948 PARTIAL_WAKE_LOCK 'Tag' ON_AFTER_RELEASE
ACQ=-2s581ms (uid=10155 pid=26429)
PowerManagerService.WakeLocks: ref count=1
Proxyed WakeLocks State


//去锁后
no_cached_wake_locks=true
mWakefulness=Awake
mWakefulnessChanging=false
mWakeLockSummary=0x0
mLastWakeTime=509144080 (271089 ms ago)
mHoldingWakeLockSuspendBlocker=false
mWakeUpWhenPluggedOrUnpluggedConfig=true
mWakeUpWhenPluggedOrUnpluggedInTheaterModeConfig=false
mDoubleTapWakeEnabled=false
Wake Locks: size=0
PowerManagerService.WakeLocks: ref count=0
Proxyed WakeLocks State
```


##### 3、WorkManager