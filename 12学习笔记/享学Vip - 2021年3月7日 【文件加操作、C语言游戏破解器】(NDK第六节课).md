日期： 2022-04-24

标签： #学习笔记 #技术 #C语言 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821032962896480&vid=387702298740321512

百度网盘 - https://pan.baidu.com/disk/main?from=homeFlow#/index?category=all&path=%2F%E5%AD%A6%E4%B9%A0%2F%E4%BA%AB%E5%AD%A6VIP%E8%AF%BE%E7%A8%8B%2F2%E6%9C%9F%2F%E3%80%9007%E3%80%91NDK%2F%EF%BC%8806%EF%BC%892021.3.7C%E8%AF%AD%E8%A8%80%E6%B8%B8%E6%88%8F%E7%A0%B4%E8%A7%A3%E5%99%A8%E4%B8%8E%E6%96%87%E4%BB%B6%E5%8A%A0%E8%A7%A3%E5%AF%86%EF%BC%88NDK%E7%AC%AC%E5%85%AD%E8%8A%82%E8%AF%BE%EF%BC%89

---
<br>

### 一、文件操作
##### 1、打开文件流
- 库引入： **`#include <stdlib.h>`** 
- 打开文件： **`FILE* fopen (const char* fileName, const char* mode);`**
mode参数说明
![600](../99附件/20220426081957.png)
- 【重要】关闭文件流： **`fclose(FILE* stream);`**

<br>


##### 2、读文件
- 读取文件：**`char* fgets( char *buf, int n, FILE *fp );`**

```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	// fopen打开文件的意思（参数1：文件路径 文件源，  参数2：模式 r(读) w(写)  rb(作为二进制文件读) rw(作为二进制文件写)  返回值 FILE 结构体）
	// FILE * fopen (const char *, const char *);

	char* fileNameStr = "D:\\Temp\\DerryFile.txt";

	// 因为使用了r，所以要提前生成好文件
	FILE* file = fopen(fileNameStr, "r"); // file == 指针

	if (!file) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	// 定义缓存区buffer (容器)
	char buffer[10];

	while (fgets(buffer, 10, file)) { // 1.缓冲区buffer， 2:读取长度， 3:文件指针
		printf("%s", buffer);
	}

	// 【重要】关闭文件
	fclose(file);

	return 0;
}
```

<br>

##### 3、写文件
- 写入文件：**`char* fputs( char* buf, FILE* fp );`**

```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	char* fileNameStr = "D:\\Temp\\DerryFileW.txt";

	// 因为使用了w，所以会自动新建一个 0kb 的文件
	FILE* file = fopen(fileNameStr, "w"); // file == 指针

	if (!file) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	fputs("Derry Success run...", file);

	// 【重要】关闭文件
	fclose(file);

	return 0;
}
```

<br>

##### 4、复制文件
```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

// 二进制文件来复制 rb rw
int main() {

	char* fileNameStr = "D:\\Temp\\DerryFile.txt"; // 来源
	char* fileNameStrCopy = "D:\\Temp\\DerryFileCopy.txt"; // 目标

	// rb 读取二进制数据
	FILE* file = fopen(fileNameStr, "rb");

	// wb 写入二进制数据
	FILE* fileCopy = fopen(fileNameStrCopy, "wb");

	if (!file || !fileCopy) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	int buffer[514];
	int len; // 每次读取的长度

	/*
		fread()

		参数1：容器buffer，
		参数2：每次偏移多少，
		参数3：容器大小，需要与容器声明的大小相等

	*/
	while ((len = fread(buffer, sizeof(int), sizeof(buffer) / sizeof(int), file)) != 0) {
		fwrite(buffer, sizeof(int), len, fileCopy);
	}

	// 关闭文件
	fclose(file);
	fclose(fileCopy);

	return 0;
}
```

<br>

##### 5、获取文件大小
- 没有专门的 文件大小获取 API
- 【思路】：读取文件头指针，将头指针挪动位置并记录挪动的信息，当挪动到最后，就可以求得文件大小

```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	char* fileNameStr = "D:\\Temp\\DerryFile.txt"; // 来源

	// 既然是使用了w，他会自动生成文件 0kb
	FILE* file = fopen(fileNameStr, "rb"); // file == 指针

	if (!file) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	// SEEK_SET（开头）  SEEK_CUR（当前）  SEEK_END（结尾）
	fseek(file, 0, SEEK_END);
	// 走到这里之后：file有了更丰富的值，给你的file指针赋值，挪动的记录信息

	// 读取刚刚给file赋值的记录信息
	// ftell函数目的是：计算偏移的位置，ftell 从 0 开始统计到当前（SEEK_END）
	long file_size = ftell(file);
	printf("%s文件的字节大小是:%ld\n", fileNameStr, file_size);

	// 关闭文件
	fclose(file);

	return 0;
}
```

<br><br>

### 二、文件加解密
##### 1、加密、解密的思路
- 加密：破坏文件
	1. （全部加密）把每一个字节都拿出来，对每一个字节都全部处理
	2. （部分加密）把某一部分内容拿出来处理
- 解密：还原文件之前的样子

<br>


##### 2、文件加密、解密
- 加密的算法：
	1. while 循环遍历取出来的值 x
	2. x ^异或 5，就变成这了 yyyy

```C
// 1.【文件的加密】

#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {
	char* fileNameStr = "D:\\Temp\\IMG.jpg"; // 来源
	char* fileNameStrEncode = "D:\\Temp\\IMG_encode.jpg"; // 加密后的目标文件

	FILE* file = fopen(fileNameStr, "rb"); // r 必须字节提前准备好文件
	FILE* fileEncode = fopen(fileNameStrEncode, "wb"); // w 创建一个0kb的文件

	if (!file || !fileEncode) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	int c; // 接收读取的值

	// fgetc(文件指针) 读取文件信息，当返回值=EOF(end fo file)时，表示到文件末尾
	while ((c = fgetc(file)) != EOF) {
		// 加密操作，异或5
		fputc(c ^ 5, fileEncode); // 写入到 fileEncode  D:\Temp\IMG_encode.jpg（加密后的图片）
	}

	// 关闭文件
	fclose(file);
	fclose(fileEncode);

	return 0;
}
```

- 解密的算法：
	1. while 循环遍历取出来的值 yyyy
	2. yyyy ^异或 5，就还原成 x

```C
// 2.【文件的解密】

#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	char* fileNameStr = "D:\\Temp\\IMG_encode.jpg"; // 来源
	char* fileNameStrDecode = "D:\\Temp\\IMG_decode.jpg"; // 解密后的目标文件

	FILE* file = fopen(fileNameStr, "rb"); // r 必须字节提前准备好文件
	FILE* fileEncode = fopen(fileNameStrDecode, "wb"); // w 创建一个0kb的文件

	if (!file || !fileEncode) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	int c; // 接收读取的值

	while ((c = fgetc(file)) != EOF) {
		// 解密操作 1111 ^ 5 = 10；（还原）
		fputc(c ^ 5, fileEncode);
	}

	fclose(file);
	fclose(fileEncode);

	return 0;
}
```

<br><br>

##### 3、使用密钥加密、解密
- 密钥加密
```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	char* fileNameStr = "D:\\Temp\\IMG.jpg"; // 来源
	char* fileNameStrEncode = "D:\\Temp\\IMG_encode.jpg"; // 加密后的目标文件

	// 密钥
	char* password = "123456"; // 我现在做的事情：我的密钥 必须生效

	FILE* file = fopen(fileNameStr, "rb"); // r 必须字节提前准备好文件
	FILE* fileEncode = fopen(fileNameStrEncode, "wb"); // w 创建一个0kb的文件

	if (!file || !fileEncode) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	int c;
	int index = 0;
	int pass_len = strlen(password);
	while ((c = fgetc(file)) != EOF) {
		char item = password[index % pass_len]; // 长度取模
		// 1 2 3 4 5 6  1 2 3 4 5 6  1 2 3 4 5 6 ...

		printf("item:%c%\n", item);

		fputc(c ^ item, fileEncode);

		index++;
	}

	// 关闭文件
	fclose(file);
	fclose(fileEncode);
}
```

- 密钥解密
```C
#include <stdio.h>
#include <stdlib.h> // 文件的操作，是在这个头文件里面的
#include <string.h>

int main() {

	char* fileNameStr = "D:\\Temp\\IMG_encode.jpg"; // 来源
	char* fileNameStrDecode = "D:\\Temp\\IMG_decode.jpg"; // 解密后的目标文件

	FILE* file = fopen(fileNameStr, "rb"); // r 必须字节提前准备好文件
	FILE* fileDecode = fopen(fileNameStrDecode, "wb"); // w 创建一个0kb的文件

	if (!file || !fileDecode) {
		printf("文件打开失败，请你个货检测：路径为%s路径的文件，看看有什么问题\n", fileNameStr);
		exit(0); // 退出程序
	}

	// 密钥
	char* password = "123456"; // 我现在做的事情：我的密钥 必须生效

	int c;
	int index = 0;
	int pass_len = strlen(password);
	while ((c = fgetc(file)) != EOF) {
		fputc(c ^ password[index % pass_len], fileDecode);

		index++;
	}

	fclose(file);
	fclose(fileDecode);

	return 0;
}
```
