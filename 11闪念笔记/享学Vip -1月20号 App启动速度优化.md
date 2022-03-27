日期： 2022-03-19

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286767562837276&vid=387702294871766328

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8804%EF%BC%892022.1.20-Android%E9%9D%A2%E8%AF%95%E5%BF%85%E5%A4%87Application%E5%90%AF%E5%8A%A8%E8%BF%87%E7%A8%8B%E4%B8%8E%E8%80%97%E6%97%B6%E5%88%86%E6%9E%90---Alvin

---
<br>

## 主题：Android面试必备Application启动过程与耗时分析

## 启动监控

## 卡顿监控

## 工具、耗时统计 看《补充资料》，第二期 第四节课

## 启动流程
- 看《预习资料》
- 流程图：
 ![[Pasted image 20220322224704.png|650]]
	1. 点击桌面icon，Launcher，AMS通信（Framework层，要学）
	2. 启动“黑白屏”阶段优化：
		- theme、PhoneWindow、windowsSplashscreenContent（26以前是background）、jetpack：splashScreeen、
		- 启动Activity流程：ActivityStack.startActiviytLocked() -> showStartingWindow() -> addStartingWindow() -> scheduleAddStartingWindow() -> AnimationHandler.postAtFrontOfQueue() -> WindowManagerPolicy.StartingSurface = SplashScreenStartingData.createStartingSurface() -> PhoneWindowManager.addSplashScreen() -> PhoneWindowManager.addSplashscreenContent() -> R.styleable.Window_windowSplashscreenContent -> PhoneWindow.setContent()
		- 什么时候显示第一个Window？：第一个Acitivity.onResume()后、WindowManager.addView()的时候，**会回调windowFocusChanged()**，WMS
	3. Application
		- attachBaseContext：
			- dex（加固、热修复）
			- Provider加载。优化：减少不必要的Provider
			- 优化：启动Class编排进主dex（字节的BoostMultiDex方案）
		- onCreate：解决线程拥挤，降低CPU切换成本
	4. MainAtivity
		- attach：
			- **WMS**
			- 绑定Context
			- new PhoneWindow()
			- window.setWindowManager()
		- onCreate：
			- setContentView()创建decorView
			- inflate的View比自定义View效率低(用反射)
			- 精简xml布局层级，优化解析耗时
			- compose优化(new组件，效率高)
		- onResume：
			- 可见可交互状态
			- 将onCreate时由setContentView()构建的decorView，通过WMS执行WM.addView()，上传到屏幕上，即实际**UI展示的时间**
			- 懒加载：先简单的占位，延后初始化复杂逻辑，例如 ViewPager + Fragment、ViewStub、空View
			- 精简xml布局层级，优化渲染耗时
			- 实用ConstraintLayout，减少嵌套（一期、二期的课程有讲）
			- Handler闲时：Looper.myQueue().addIdleHandler(new IdleHandler())、执行GC
			- GC 内存抖动：stop the world、（回顾JVM课程）
