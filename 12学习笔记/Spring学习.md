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
- `scope` ：默认情况生产出来的bean对象是单例，并且在程序启动时就会创建，可以通过该属性改变
- `depends-on` ：控制加载依赖顺序
- `autowire` 自动装配，分为 byName、byType、constructor 几种模式；对不想参与自动配候选的bean使用 `autowire-candidate=false` 熟悉，即可关闭；使用primary=true，可让该bean在自动装配候选时，优先选择
- 生命周期：
	- `init-method` 
	- `destory-method` 
	- `lazy-init`
- 继承关系：`parent` ，指定继承某个bean的属性，**注意，这里仅仅时属性继承**，和extends不是一回事；`abstract=true` 标识该bean仅仅作为给其他bean继承属性用，不可以直接依赖注入获取
- 