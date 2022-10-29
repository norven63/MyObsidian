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
4. Processor、AbstraceProcessor、ProcessingEnvironment
5.  .gradle文件中，在dependencies下配置  `annotationProcessor project(":xxx-module")`
<br>


### 2、SPI
[知乎: 深入理解 Java 中 SPI 机制](https://zhuanlan.zhihu.com/p/84337883)
![650](../99附件/20221029_SPI.jpg)

#### 实践示例：
**1. 定义一个接口HelloSPI。**
```java
package com.vivo.study.spidemo.spi;
public interface HelloSPI {
    void sayHello();
}
```

**2. 完成接口的多个实现。**
```java
package com.vivo.study.spidemo.spi.impl;
import com.vivo.study.spidemo.spi.HelloSPI;
public class ImageHello implements HelloSPI {
    public void sayHello() {
        System.out.println("Image Hello");
    }
}
package com.vivo.study.spidemo.spi.impl;
import com.vivo.study.spidemo.spi.HelloSPI;
public class TextHello implements HelloSPI {
    public void sayHello() {
        System.out.println("Text Hello");
    }
}
```

在META-INF/services/目录里创建一个以com.vivo.study.spidemo.spi.HelloSPI的文件，这个文件里的内容就是这个接口的具体的实现类。
![](https://pic4.zhimg.com/80/v2-d6dea7b337e0c032b55731fa97183473_1440w.webp)

具体内容如下：
```java
com.vivo.study.spidemo.spi.impl.ImageHello
com.vivo.study.spidemo.spi.impl.TextHello
```

**3. 使用 ServiceLoader 来加载配置文件中指定的实现**
```java
package com.vivo.study.spidemo.test
import java.util.ServiceLoader;
import com.vivo.study.spidemo.spi.HelloSPI;
public class SPIDemo {
    public static void main(String[] args) {
        ServiceLoader<HelloSPI> serviceLoader = ServiceLoader.load(HelloSPI.class);
        // 执行不同厂商的业务实现，具体根据业务需求配置
        for (HelloSPI helloSPI : serviceLoader) {
            helloSPI.sayHello();
        }
    }
}
```

输出结果如下：
```java
Image Hello
Text Hello
```

<br>


### 3、autoservice
[腾讯云: 使用Google开源库AutoService进行组件化开发](https://cloud.tencent.com/developer/article/1415083)

#### 实践示例：
1. 引入

```bash
compile 'com.google.auto.service:auto-service:1.0-rc4'
```

2. 官方示例说明

```kotlin
package foo.bar;

import javax.annotation.processing.Processor;

@AutoService(Processor.class)
final class MyProcessor implements Processor {
  // …
}
```

AutoService会自动在build/classes输入目录下生成文件META-INF/services/javax.annotation.processing.Processor，文件的内容如下

```text
foo.bar.MyProcessor
```

在javax.annotation.processing.Processor的情况下，如果一个jar中包含metadata文件，并且在javac的classpath下，javac会自动加载这个jar，同时包含它的普通注解编译环境。