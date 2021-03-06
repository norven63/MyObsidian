日期： 2022-04-22

标签： #学习笔记 #技术 #C语言 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821002898125408&vid=387702298740270868

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F2%E6%9C%9F%2F%E3%80%9007%E3%80%91NDK%2F%EF%BC%8805%EF%BC%892021.3.4%E7%BB%93%E6%9E%84%E4%BD%93%E4%B8%8E%E7%BB%93%E6%9E%84%E4%BD%93%E6%8C%87%E9%92%88%E6%95%B0%E7%BB%84%EF%BC%88NDK%E7%AC%AC%E4%BA%94%E8%8A%82%E8%AF%BE%EF%BC%89

---
<br>

### 结构体基础
##### 声明与使用
- 相当于Java中的Class
- 关键字 **`struct`**
- 成员变量没有初始化时，都是系统值
- 结构体对自己成员变量的调用，使用关键字 **`.`** ，注意：后面会讲到 "结构体**指针**" 对成员变量的调用，是用关键字 **`->`**

```C
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <malloc.h>

struct Person {
	// 成员
	char* name;
	int age;
	char sex;
}
/*
  在结构体末尾，可以直接声明该结构体的变量
*/
persion1 = { "Derry", 33, 'M' }, // 这里可以直接初始化赋值
persion2,
persion3
// ...
; // 必须给写;表示struct声明结束

int main4() {
	// 声明（栈中开辟内存，静态申请）
	struct Person xiaoLi; // 这样写完，成员是没有任何初始化的，成员默认值是系统值，不能直接使用

	// 赋值
	xiaoLi.name = "XiaoLi22";
	strcpy(xiaoLi.name, "xiaoLi");
	xiaoLi.age = 24;
	xiaoLi.sex = 'F';

	// 声明 + 初始化赋值
	struct Person persion3 = { "persion3",34,'M' };

	printf("persion1{name:%s, age:%d, sex:%c} \n", persion1.name, persion1.age, persion1.sex);
	printf("xiaoLi{name:%s, age:%d, sex:%c} \n", xiaoLi.name, xiaoLi.age, xiaoLi.sex);
	printf("persion3{name:%s, age:%d, sex:%c} \n", persion3.name, persion3.age, persion3.sex);

	return 0;
}
```

<br>

##### 结构体嵌套声明

```C
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <malloc.h>

struct Study {
	char* studyContent;
};

struct Student {
	char name[10];
	int age;
	char sex;

	struct Study myStudy;

	struct Wan {
		char* what;
	} wan;
};

int main5() {

	struct Student student =
	{ "李元霸", 88, 'm' ,
	 {"学习C"},
	 {"王者农药"}
	};

	printf("name:%s, age:%d, sex:%c，study:%s, wan:%s \n",
		student.name, student.age, student.sex, student.myStudy.studyContent, student.wan.what);

	return 0;
}
```

<br><br>

### 结构体指针
- 结构体指针对自己成员的调用，使用关键字 **`->`**，例如 `man->age = 3;` 

```C
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct Cat {
	char name[10];
	int age;
};

int main7() {

	// 1. 申请【栈】中的内存空间
	struct Cat cat = { "小花猫", 2 };// 1）第一步，先声明结构体（栈中的内存开辟）

	struct Cat* catP = &cat;// 2）第二步，取前面声明好的结构体的地址
	
	catP->age = 3; // 成员变量的调用使用关键字 ->
	strcpy(catP->name, "小花猫2");

	printf("catP{name:%s, age:%d} \n\n", catP->name, catP->age);


	// 2. 申请【堆】中的内存空间
	struct Cat* cat2 = (struct Cat*)malloc(sizeof(struct Cat));

	strcpy(cat2->name, "金色猫");
	cat2->age = 5;

	printf("cat2{name:%s, age:%d} \n", cat2->name, cat2->age);

	// 堆区的必须释放
	free(cat2);
	cat2 = NULL;

	return 0;
}
```

<br><br>

### 结构体数组
- 整体知识点与数组差不多，但元素是结构体
- 声明结构体数组时，需要用 **`struct`** 关键字作为开头

```C
// 4.结构体的数组。

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Dog {
	char* name;
	int age;
};

int main8() {

	// 1. 【栈区】静态申请
	// 声明一个结构体数组，注意要用 struct 作为开头
	struct Dog dogArr[3] = {
			{"小黄", 1},
			{"小白", 2},
			{"小黑", 3}
	};

	struct Dog cat2 = { "小黑2", 2 };
	struct Dog cat3 = { "小333", 3 };
	
	dogArr[1] = cat9;
	*(dogArr + 2) = cat6;
	printf("dogArr{name:%s, age:%d} \n", dogArr->name, dogArr->age);
	printf("dogArr[+1]{name:%s, age:%d} \n", (dogArr + 1)->name, (dogArr + 1)->age);
	printf("dogArr[+2]{name:%s, age:%d} \n\n", (dogArr + 2)->name, (dogArr + 2)->age);


	// 2. 【堆区】动态申请
	// 声明一个结构体数组，注意要用 struct 作为开头
	struct Dog* dogArr2 = (struct Dog*)malloc(sizeof(struct Dog) * 3);

	// 给第1个元素赋值（数组默认指向首元素的地址）
	dogArr2->name = "小花猫000";
	dogArr2->age = 11;
	printf("dogArr2{name:%s, age:%d} \n", dogArr2->name, dogArr2->age);

	// 给第3个元素赋值
	struct Dog* dogArr2Tmp = dogArr2 + 2;
	dogArr2Tmp->name = "小花猫222";
	dogArr2Tmp->age = 22;
	printf("dogArr2 Tmp{name:%s, age:%d} \n", dogArr2Tmp->name, dogArr2Tmp->age);
	printf("dogArr2[+2]{name:%s, age:%d} \n", (dogArr2 + 2)->name, (dogArr2 + 2)->age);

	// 动态申请的内存都要释放！！！
	free(dogArr2);
	dogArr2 = NULL;

	return 0;
}
```

<br><br>

### 结构体别名
- 别名作用：兼容不同平台代码的写法，保持一致
- 别名关键字
	1. 结构体别名：**`typedef struct Person_ Person;`**
	2. 结构体指针别名：**`typedef struct Workder_* WorkderP;`**

```C
#include <stdio.h>
#include <stdlib.h>


/*
	【普通结构体】的别名
*/
struct Workder_ {
	char name[10];
	int age;
	char sex;
};

typedef struct Workder_ Workder; // 1. 给结构体取别名
typedef struct Workder_* WorkderP; // 2. 给结构体指针取别名


/*
	【匿名结构体】的别名
*/
// 1. 这样写的意义不大，因为没有名字，没人可以正常引用
typedef struct {
	char name[10];
	int age;
	char sex;
};

// 2. “正确”写法：给结构体取了一个别名等于AV
typedef struct {
	char name[10];
	int age;
	char sex;
} AV;


/*
	【使用案例】
*/
int main10() {
	/*
		1. 普通结构体
	*/
	// 【以前】例如Clion工具，指针、结构体的声明都要必须加上 “struct” 关键字，而VS工具又不用加，工具间的代码差异化大
	struct Workder_* workder1 = malloc(sizeof(struct Workder_));

	// 【现在】使用别名后Workder，无论是指针、结构体，全都不需要 “struct” 关键字
	WorkderP workder2 = malloc(sizeof(Workder));


	/*
		2. 匿名结构体
	*/
	AV av = { "VideoInfo", 54, 'M' }; // 声明结构体
	AV* avp = malloc(sizeof(AV)); // 声明结构体指针

	return 0;
}


// 声明函数入参时，可以不用加struct关键字
void show(Workder work) {

}
```

<br><br>

### 枚举
- 枚举，本质属于 int 类型的
- 当第一个枚举的值定义好后，后续枚举的值依次+1

```C
#include <stdio.h>

// 枚举，本质属于 int 类型的
enum CommentType {
	TEXT = 10, // 第一个枚举的值定义好后，后续枚举的值依次+1
	TEXT_IMAGE, // 11
	IMAGE // 12
};

// 取别名，代码统一
typedef enum CommentType CommentType;

int main9() {
	CommentType commentType = TEXT;
	CommentType commentType1 = TEXT_IMAGE;
	CommentType commentType2 = IMAGE;

	// 因为枚举是int类型，所以print函数用%d占位
	printf("TEXT=%d, \nTEXT_IMAGE=%d, \nIMAGE=%d \n", commentType, commentType1, commentType2);

	return 0;
}
```
