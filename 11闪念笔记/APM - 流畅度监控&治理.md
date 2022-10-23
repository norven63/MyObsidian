### 名词定义
1. 要做的是什么：建立线上的**用户交互流畅度**观察体系；建立定位线上发生卡顿时的排查工具。
2. 监控的是什么：
	- 卡顿帧：耗时 >= 64ms(16ms * 4)的帧
	- liu'c'lü率（每秒）：卡顿帧总时长 / 1秒
	- 开始时间、结束时间：
		- 全局onTouch的开始&结束事件
		- 全局onScroll的开始&结束事件
		- 重要组件onTouch、onScroll的开始&结束事件


### 监控实现
```java
Window().addOnFrameMetricsAvailableListener(Window.OnFrameMetricsAvailableListener listener, Handler handler)
```


### 排查定位
- trace跟踪
- dump信息