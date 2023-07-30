日期： 2023-07-30

标签： #学习笔记 #技术

学习资料： 
https://itbaima.net/document
https://blog.csdn.net/qq_25928447/article/details/122438913

---
<br>

### IoC容器
- 控制反转，依赖注入，即面向接口编程

#### <bean/>标签
- 默认情况是单例，并且在程序启动时就会创建，可以通过 `scope` 属性改变
- 通过 `depends-on` 标签控制加载顺序
- `autowire` 自动装配，分为 byName、byType 两种模式