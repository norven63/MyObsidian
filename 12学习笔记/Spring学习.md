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
- `autowire` 自动装配，分为 byName、byType、constructor 几种模式；对不想参与自动配候选的bean使用 `autowire-candidate=false` 熟悉，即可关闭；使用primary=true，可让该bean在自动装配候选时，优先选择
- 生命周期：`init-method` 、`destory-method`
- 属性继承：