日期： 2022-03-27

标签： #学习笔记 #技术  #Android 

学习源： 
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286771857804572&vid=387702295011839712

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8805%EF%BC%892022.1.23-Android%E5%90%AF%E5%8A%A8%E4%BC%98%E5%8C%96%EF%BC%8C%E6%9C%89%E5%90%91%E6%97%A0%E7%8E%AF%E5%9B%BE%E4%BB%BB%E5%8A%A1%E7%AE%A1%E7%90%86%E5%88%86%E6%9E%90---lance%E8%80%81%E5%B8%88

---
<br>

## 主题：Android启动优化，有向无环图任务管理分析

## 有向无环图DAG
- 入度、出度、边、有向无回环
- 拓扑排序
	- BFS 广度优先、DFS 深度优先
	- 排序结果不是唯一
	- 每个顶点出现且只出现一次、各节点前后顺序
	- 算法：
		- 找出0入度的顶点
		- 依次删除这些顶点
		- 重复1、2两步
		- ![[Pasted image 20220329001327.png|800]]
## 启动器
- 单例Cache类：前置Task将处理结果封装到Result中 -> 以前置Task的Class作为key放入单例Cache类中 -> 后置类去读取Result
- StartupManger：不需要单例，因为每个阶段均有一个独立的Manger类（类似ykBoot里的Project）
- 线程同步：