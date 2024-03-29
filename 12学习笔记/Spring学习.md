日期： 2023-07-30

标签： #学习笔记 #技术

学习资料： 
https://itbaima.net/document
Spring核心技术：[笔记](https://sqihr3trvt9.feishu.cn/docx/HcWJd1z5QoJkhIxkZdycUjD9nHf) 、[视频](https://www.bilibili.com/video/BV1Kv4y1x7is/?p=8&spm_id_from=pageDriver&vd_source=26c21cff608e4193bcf69f197e433f67)
SpringMvc：[笔记](https://sqihr3trvt9.feishu.cn/docx/Otkqdyc5koNj6wxrAwKc2vFNnFh)、[视频](https://www.bilibili.com/video/BV1Lh4y1M7kx/?spm_id_from=333.999.0.0)
SpringSecurity：[笔记](https://sqihr3trvt9.feishu.cn/docx/HV79dE5LuoLxOAxCG2pcDu2Mnog)、[视频](https://www.bilibili.com/video/BV1fV411M7aS/?spm_id_from=333.999.0.0)
SpringBoot：

---
<br>

### IoC容器
- 控制反转，依赖注入，即面向接口编程

#### <bean/>标签
- `scope` ：默认情况生产出来的bean对象是单例，并且在程序启动时就会创建，可以通过该属性改变
- `depends-on` ：控制加载依赖顺序
- `autowire` ：标识该bean下的属性都通过依赖注入来**自动装配**，可使用 `byName、byType、constructor` 几种模式；对不想参与自动配候选的bean使用 `autowire-candidate=false` 属性，即可关闭；使用`primary=true`，可让该bean在被其他bean自动装配候选时，优先被选择
- 生命周期：
	- `init-method` 
	- `destory-method` 
	- `lazy-init`
- 继承关系：
	- `parent` 指定继承某个bean的属性，**注意，这里仅仅时属性继承**，和extends不是一回事；
	- `abstract=true` 标识该bean仅仅作为给其他bean继承属性用，不可以直接依赖注入获取
- 工厂方法：