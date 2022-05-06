日期： 2022-05-05

标签： #学习笔记 #技术 #C语言 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821136042111584&vid=387702298741278473

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow&_at_=1651480206800#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F2%E6%9C%9F%2F%E3%80%9007%E3%80%91NDK%2F%EF%BC%8810%EF%BC%892021.3.16%20C%2B%2B%E8%AF%AD%E8%A8%80%E4%B9%8Bthis%E5%8E%9F%E7%90%86%E4%B8%8E%E5%8F%8B%E5%85%83%E5%87%BD%E6%95%B0%E5%8F%8B%E5%85%83%E7%B1%BB%EF%BC%88NDK%E7%AC%AC%E5%8D%81%E8%8A%82%E8%AF%BE%EF%BC%89%20--derry%E8%80%81%E5%B8%88

---
<br>

### 一、可变参数
- Java可变参数写法 `void foo(int ...)`、C++可变参数写法 `void foo(...)`
- **核心函数：**
	1. `va_list` ：声明变量
	2. `va_start` ：为可变参数变量加载信息
	3. `va_arg`：从可变参数中读取一个值
	4. `va_end`：关闭可变参数的读取（规范：例如file文件要关闭流一样）
- **越界：** 越界后仍然可以读取值，但会读取到一个系统值、乱码