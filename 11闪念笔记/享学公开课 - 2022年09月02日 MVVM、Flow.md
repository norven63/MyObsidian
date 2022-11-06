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
