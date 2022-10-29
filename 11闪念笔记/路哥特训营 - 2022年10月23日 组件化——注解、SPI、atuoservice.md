日期： 2022-10-23

标签： #学习笔记 #技术

学习资料： https://iww0abxi5u.feishu.cn/minutes/obcn6ex78wylm54xa39pr6wx


---
<br>

## 一、组件化
### 1、注解
1. `@Retention`
	- `RetentionPolicy.SOURCE`
	- `RetentionPolicy.CLASS // 编译期注解`
	- `RetentionPolicy.RUNTIME // 运行期注解，需要反射技术，耗损性能
		- `Class cls = Class.forName("com.demo.AnnotationDemo"); cls.getAnnotations(); cls.getAnnotation(MyAnnotation.class);`
2. `@Target、ElementType`
3. 获取注解 --> 获取注解对应的元素数据 --> 处理元素数据
```java

```

<br>


### 2、SPI
[知乎: 深入理解 Java 中 SPI 机制](https://zhuanlan.zhihu.com/p/84337883)
![650](../99附件/20221029_SPI.jpg)
1. 先发布一个SPI

<br>


### 3、autoservice