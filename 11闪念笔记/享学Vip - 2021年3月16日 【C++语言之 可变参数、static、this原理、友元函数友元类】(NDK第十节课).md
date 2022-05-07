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

```cpp
#include <iostream>
#include <stdarg.h> // 可变参数的支持
using namespace std;

// Java的可变参数: int ...
// C++的可变参数写法：...
// count建议传入可变参数的个数，可以用于循环遍历
void sum(int count, ...) {
	// 1. 声明可变参数变量
	va_list vp;

	// 2. 为可变参数变量加载信息
	// 参数一，vp：可变参数变量
	// 参数二，count：此地建议是用函数的形参传入。内部需要一个，存储地址用的参考值，如果没有第二个参数，内部他无法处理存放参数信息
	va_start(vp, count);

	// 3. 到这里后：vp就已经有丰富的信息

	// 4. 从可变参数中读取值（遍历读取）
	for (int i = 0; i < count; ++i) {
		int arg = va_arg(vp, int);

		cout << "可变参数值：" << arg << endl;
	}

	// 5. 继续取出可变参数的一个值
	// 这里会导致越界，读取到一个系统值、乱码
	int number = va_arg(vp, int);
	cout << endl << "越界系统值：" << number << endl;

	number = va_arg(vp, int);
	cout << "越界系统值：" << number << endl;

	// 6. 关闭可变参数的读取（规范：例如file文件要关闭流一样）
	va_end(vp);
}


int main() {
	sum(3, 6, 7, "abc");

	return 0;
}
```

<br><br>

### 二、关键字：static
1. 可以直接通过 **`Class名::静态成员`** 的方式，引用、调用
2. **静态属性**必须要被初始化，否则无论哪里引用都会运行crash
3. **静态属性、函数**必须要先在`.h`文件中声明，然后再在`.cpp`文件中实现初始化（实现的时候直接使用`Class名::`即可，不需要`static`）
4. 静态函数只能操作静态的属性、函数（与Java一样）

```cpp
#include <iostream>

using namespace std;

class Dog {
public:
	char* info;
	int age;

	// 1. 声明静态成员变量
	static int id;

	// 1.1 声明静态函数 
	static void update();

	void update2() {
		id = 13;
	}
};

// 2.1 实现静态成员变量的初始化
// 不需要 static 关键字
int Dog::id = 9;

// 2.2 实现静态函数 
// 静态函数不能调用非静态函数（与Java一样）
void update() {
	id += 100;// 如果id没有初始化过，这里会运行报错

	// 报错：静态函数不能调用非静态函数（与Java一样）
	// update2();
}

int main() {
	Dog dog;
	dog.update2(); // 调用普通函数
	Dog::update(); // 调用静态函数
	dog.update(); // 对象名.静态函数（一般都是使用::调用静态成员，这种方式也可以，知道就行）

	cout << Dog::id << endl;
	return 0;
}
```

<br><br>

### 三、关键字：this
1. 当声明对象时，**构造函数**会创建一个`this`的指针，指向当前对象的地址。当对象的**成员函数**都在**代码区**运行，当被调用时，会传入对象的`this`指针到代码区。同理，构造函数、栈区空间，也会传入。

2. `this`指针默认被 **`const` 修饰成"指针常量"**，使其指向地址不可修改，但是成员变量允许修改。

3. 当在成员函数的**末尾**使用`const`修饰时，等价于将该函数传入的`this`指针，修饰成**常量指针常量**，使其无法被修改成员变量值，只读。例如 `void foo() const { ... }`

4. 参见`const`修饰指针的细节：[[享学Vip - 2021年3月9日 【C++语言学习基础 之 打印、命名空间、常量、引用、函数重载、默认形参、无名形参、对象、头文件、实现文件】(NDK第七节课)#3、常量指针、指针常量、常量指针常量]]中的 **"指针常量"、"常量指针常量"**。


- **this与函数的关系：**
![650](../99附件/20220506193846.png)
- **const修饰函数的this意义何在：**
```cpp
#include <iostream>

using namespace std;

class Worker {
public:
	char* name;
	int age = NULL; // C++中不像Java，Java有默认值， 如果你不给默认值，那么就是系统值 -64664

	// int * const  指针常量 指针常量【地址对应的值能改，地址不可以修改】
	// const int *  常量指针 常量指针【地址可以修改，地址对应的值不能改】

	// 纠结：原理：为什么可以修改age
	// 默认持有隐式的this【类型 * const this】
	// 类型 * const 指针常量：代表指针地址不能被修改，但是指针地址的值是可以修改的
	void change1() {
		// 代表指针地址不能被修改
		// this = 0x6546;  // 编译不通过，地址不能被修改，因为是指针常量
		// 地址不可以修改
		// this = 0x43563;

		// 隐式的this
		// 但是指针地址的值是可以修改的
		// 地址对应的值能改
		this->age = 100;
		this->name = "JJJ";
	}

	// 默认现在：this 等价于 const Student * const  常量指针常量（地址不能改，地址对应的值不能改）
	void changeAction() const {
		// 地址不能改
		// this = 0x43563;

		// 地址对应的值不能改
		// this->age = 100;
	}

	// 原理：修改隐式代码  const 类型 * const 常量指针常量
	void showInfo() const {
		// this->name = "";
		// this->age = 88;

		// 只读的
		cout << "age:" << age << endl;
	}
};

int main() {
	return 0;
}
```

<br><br>

### 四、友元
##### 1、友元函数
- 关键字：**`friend`**
- 在`.h`头文件中声明函数`friend void foo(Persion* p);`，在`.cpp`中实现函数时，就可以对`Persion`**访问私有成员**。
- 实现友元函数时，不需要 **`friend`** 关键字，也不需要 **`Class名::`** ，只需要保证函数签名一致即可

```cpp
#include <iostream>

using namespace std;

class Person {
private:
	// 私有的age，外界不能访问
	int age = 0;

public:
	Person(int age) {
		this->age = age;
	}

	int getAge() {
		return this->age;
	}

	// 1. 声明定义友元函数
	friend void updateAge(Person* person, int age);
};

// 2. 实现友元函数
// 不需要 friend 关键字，也不需要 Class名:: ，只需要保证函数签名一致即可
void updateAge(Person* person, int age) {
	person->age = age;
}

int main() {
	Person person = Person(9);
	updateAge(&person, 88);

	cout << person.getAge() << endl;

	return 0;
}
```

<br>

##### 2、友元类
- 关键字：**`friend`**
- 类似声明一个Java的内部类，允许该类**访问自己的私有成员**

