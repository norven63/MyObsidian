日期： 2022-02-21

标签： #学习笔记 #技术  #Android 

学习源：
腾讯课堂 - https://ke.qq.com/webcourse/347420/103755197#taid=12286780447739164&vid=387702295888841696

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow&_at_=1648737764421#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F3%E6%9C%9F%2F%E3%80%9006%E3%80%91%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%2F%EF%BC%8807%EF%BC%892022.2.10-%E5%8D%A1%E9%A1%BF%E5%92%8C%E5%B8%83%E5%B1%80%E4%BC%98%E5%8C%96---%E8%B7%AF%E5%93%A5


---

<br>

## Alpha启动框架
- 方案优化
	- 本身不支持线程切换执行Task
	- 后置Task列表用DAG排序


## 工具
### Proefile
- 不建议直接使用工具去抓，推荐用代码调用来控制监控的逻辑段
- Application.onCreate() 调用开始，Activity.onWindowFacusChanged() 调用结束
	- 开始：Debug.startMethodTracingSimpling("file path", 8 * 1024 * 1024, 1000);
	- 结束：Debug.stopMethodTracing();
- 导出.trace文件

### systrace
- Perfetto UI


## 线上监控
- 消息处理机制
- com.github.moduth.blockcanary框架
	- PerformanceUtils.java
	- /proc/stat CPU核心的数据
	- merrory
- epic框架
