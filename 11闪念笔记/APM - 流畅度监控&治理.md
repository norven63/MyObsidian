### 名词定义
1. 要做的是什么：建立线上的**用户交互流畅度**观察体系；建立定位线上发生卡顿时的排查工具。
2. 监控的是什么：
	- 卡顿帧：耗时 >= 64ms(16ms * 4)的帧
	- 卡顿率（每秒）：卡顿帧总时长 / 1秒
	- 

### 监控实现
```java
Window().addOnFrameMetricsAvailableListener(Window.OnFrameMetricsAvailableListener listener, Handler handler)
```

### 排查定位
