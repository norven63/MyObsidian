日期： 2022-08-19

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - 

百度网盘 - 

---
<br>

1. 数据的双向流处理，数据源变动 --> UI变动、UI变动 --> 数据源变动
2. LiveData
	1. 数据粘性
	2. 观察者模式
3. Flow
	1. 生产者消费者模型
	2. 背压问题的解决策略
		1. LRU，最近最少
	3. 常用操作符：末端操作符（冷流数据）、中间操作符；本质，为扩展函数。
		- map
		- take
		- filter
		- collect
		- launchIn
		- toList
		- toSet
		- reduce
		- fold
		- retry
		- debounce
		- cancellable
		- zip
		- combine
		- flatMapConcat
		- flatMapMerge
		- flatMapLastes
4. 用Flow替换LiveData

1. 确认停车位的矩形范围
2. 确认自己的车体、车头方向与矩形范围的位置关系
3. 确认观察后视镜：在矩形范围那一边的后视镜，即为观察后视镜
4. 确认锚点P：矩形范围中，最靠近观察后视镜的那个顶点，即为P点
5. 调整车体，使得车体与矩形保持50cm（尽量不要太远）；使得车头、观察后视镜、P点的距离