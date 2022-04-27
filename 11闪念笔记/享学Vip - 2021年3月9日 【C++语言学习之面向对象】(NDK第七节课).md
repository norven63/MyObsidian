日期： 2022-04-27

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821067322634848&vid=387702298740968272

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F2%E6%9C%9F%2F%E3%80%9007%E3%80%91NDK%2F%EF%BC%8807%EF%BC%892021.3.9C%2B%2B%E8%AF%AD%E8%A8%80%E5%AD%A6%E4%B9%A0%E4%B9%8B%E9%9D%A2%E5%90%91%E5%AF%B9%E8%B1%A1%EF%BC%88NDK%E7%AC%AC%E4%B8%83%E8%8A%82%E8%AF%BE%EF%BC%89--derry%E8%80%81%E5%B8%88

---
<br>

### 一、C++
##### 1、基础概念
- C++语言面向对象 + 标准特性
- C语言面向过程，函数+结构体
- C++里面可以运行C语言，可以调用C语言；反之则不行，C语言无法运行C++
- 打印函数 `std::cout << "C++语言的学习" << std::endl;` ，其中endl==\n，换行符
- 引入命名空间 `using namespace std;` ，这样一来就不用额外写 `std::`

```cpp
// #include <stdio.h> // C语言的标准支持

#include <iostream> // C++标准支持  C++的与众不同

using namespace std; // 命名空间 C++ 的特性 （Java语言的内部类）

int main() {

	// C++里面可以运行C语言，可以调用C语言，反之 就不行C语言无法运行C++
	printf("降龙十八掌(C版)\n");

	// std::cout << "C++语言的学习" << std::endl;
	cout << "C++语言的学习" << endl; // 因为你前面引入了命名空间，所以允许省略std::

	// endl == \n  都是换行的含义一样

	// << 不是属性里面的运算，操作符重载，后面会讲
	cout << "擒龙功" << endl;

	cout << "铁头功\n"
		<< "金刚腿\n"
		<< "铁布衫\n";

	return 0;
}
```
