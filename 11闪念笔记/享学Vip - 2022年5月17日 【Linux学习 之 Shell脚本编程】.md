 日期： 2022-05-29

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015380233040480&vid=387702300892069033

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.17-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8BShell%E8%84%9A%E6%9C%AC%E7%BC%96%E7%A8%8B%EF%BC%88%E4%BA%8C%EF%BC%89---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

linux中sh是链接到bash上的，所以sh与bash在功能上是没有区别的，相当于bash解析器是sh的增强版本。我们现在常用bash。

- 写一个Hello World
test.sh：
```shell
#!bin/bash

#【打印】
echo "Hello World"
#也可以不用加双引号
echo Hello World


#【定义临时变量】
#注意，=前后不允许有空格
age=10
echo age: $age


#【常用的系统全局变量】

#查看上一条命令是否执行成功。0=成功、非0=不成功
echo $?

#打印当前文件目录路径
echo $PWD

#打印当前文件名称
echo $0


#【打印入参】

#如果执行命令 sh test.sh abc 123 ，则参数一为abc ，参数二为123
echo 参数一: $1
echo 参数一: $2

#读取传入的所有参数
echo 传入的所有参数: $*

#读取传入了多少参数
echo 传入的参数数量: $#


#【if判断】
if(($?));then
	echo "上一条命令执行失败"
else
	echo "上一条命令执行失败"
fi

num1=100
num2=200
if(($num1>$num2));then
	echo "num1>num2"
else
	echo "num1<=num2"
fi

#使用[ ]语法判断，表示执行指令
#注意空格的写法
#可以不用;结尾，直接写then

#只有一个=，不要写成==
num3=100
num4=100
if [ $num3 = $num4 ]
then
	echo "num3=num4"
fi

#判断testAbc目录是否存在
if [ ! -d `pwd`/testAbc ]
then
	echo "testAbc目录不存在"
else
	echo "testAbc目录已经存在"
fi


#【for循环】
#循环累加，`expr 10 + 20`表示10+20
#a=`expr 10 + 20`表示把命令执行结果赋值给a
a=1
for((f=0;f<=100;f++))
do
	a=`expr $f + $a`
	
	echo "当前a= $a"
done

#使用`seq 1 20`作为循环数据源，表示从1到20依次取数
for i in `seq 1 20`
do
	echo "遍历算子i: $i"
done 


#【while循环】
b=0
while((b<100))
do
	b=`expr $b + 1`
	echo "当前i= $b"
done


#【读取文件】
#读取当前文件目录下的file01.txt文件
while read lineAbc
do
	echo $lineAbc
done<`pwd`/file01.txt


#【字符串操作】
str1="abc"
str2="xyz"

#判断字符串是否为空
if [ $str1 ]
then
	echo "str1不为空，值为: $str1"
else
	echo "str1为空"
fi

#判断两个字符串是否相等
if [ $str1 = $str2 ]
then
	echo "str1等于str2"
else
	echo "str1不等于str2"
fi
```

- 执行 .sh 文件的三种方式
1. `./test.sh` (进入到文件所在目录下)
2. `/bin/bash test.sh`
3. **`sh test.sh`**（最优）

##### 重定向（写文件）
1. 把AAA重定向（写入）到 file01.txt 文件中，并覆盖原来的内容
```shell 
echo AAA > file01.txt
```

2. 查看屏幕（Linux中，0是屏幕的文件），并把file01.txt文件的内容重定向（写入）屏幕中
```shell
cat 0<file01.txt
```

<br>

##### 函数
```shell
#!bin/bash
#声明函数
function foo(){
	var1="v1"
	var2="v2"
	echo "函数 foo() var1=$var1 var2=$var2"
	echo "入参=$1"
}
#调用函数
foo "参数1"
#调用函数，并把自己的入参传递给该函数
foo $1
```
