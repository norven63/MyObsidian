日期： 2022-12-05

标签： #学习笔记 #技术

学习资料： 
12月5日 https://iww0abxi5u.feishu.cn/minutes/obcnz6zdz7mz9l2c21s6s1vg?from_source=permission_change
12月9日 https://iww0abxi5u.feishu.cn/minutes/obcn3whe17e6bbl6k2q3oix6?from_source=permission_change

---
<br>

1. Sliver源码解读

2. 字节码
- 补基础：《JVM小册子》、《周志明虚拟机》、[美团的《字节码增强技术探索》博客](https://tech.meituan.com/2019/09/05/java-bytecode-enhancement.html)
- 字节码指令集，标识符，slot0 是指this
- 局部变量表，操作数栈、弹栈、入栈

4. asm框架：
- IBM Developer的asm板块，[官方文档](http://asm.ow2.io) 
- IDEA插件： [三方插件](https://plugins.jetbrains.com/plugin/5918-asm-bytecode-outline )、as商店里的 Jadx Class Decompiler
- jadx-gui 逆向工具

5. gradle
- 自定义grdle插件(建议先用6.5版本学习使用)：[参考官方文档](https://docs.gradle.org/current/userguide/custom_plugins.html)，创建一个plugin、上传maven仓库、在build.gradle中注册使用
- android-gradle-4.1.3、android-gradle-api-4.1.3
- Transform
	- Scope
	- Incremental 增量编译: apply、code、change原理
	- Task
- github上gralde实战的参考库
	- didi/booster
	- Hugo：自动日志