日期： 2022-03-19

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286767562837276&vid=387702294871766328

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8804%EF%BC%892022.1.20-Android%E9%9D%A2%E8%AF%95%E5%BF%85%E5%A4%87Application%E5%90%AF%E5%8A%A8%E8%BF%87%E7%A8%8B%E4%B8%8E%E8%80%97%E6%97%B6%E5%88%86%E6%9E%90---Alvin

---
<br>

## 启动监控

## 卡顿监控

## 工具、耗时统计 看《补充资料》，第二期 第四节课

## 启动流程
- 看《预习资料》
- 流程图：![[Pasted image 20220322224704.png|650]]
	1. 点击桌面icon，Launcher，AMS通信（Framework层，要学）
	2. 黑白屏优化：
		- theme、PhoneWindow、windowsSplashscreenContent（26以前是background）、jetpack：splashScreeen、
		- ActivityStack.startActiviytLocked() -> showStartingWindow() -> addStartingWindow() -> scheduleAddStartingWindow() -> AnimationHandler.postAtFrontOfQueue() -> WindowManagerPolicy.StartingSurface = SplashScreenStartingData.createStartingSurface() -> PhoneWindowManager.addSplashScreen() -> PhoneWindowManager.addSplashscreenContent() -> R.styleable.Window_windowSplashscreenContent -> PhoneWindow.setContent()
		- 什么时候显示Window：WindowManager.addView()，WMS
	3. Application
		1. attachBaseContext：dex（加固、热修复）；Provider加载；优化，启动Class编排进主dex
		2. onCreate：解决线程拥挤，降低CPU切换成本
	4. MainAtivity
		- attach：**WMS**，绑定Context、new PhoneWindow()、window.setWindowManager()
		- 
		- 
	5. 
