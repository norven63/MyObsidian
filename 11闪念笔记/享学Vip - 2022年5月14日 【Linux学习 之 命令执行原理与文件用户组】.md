日期： 2022-05-29

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - 

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.14-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%8E%9F%E7%90%86%E4%B8%8E%E6%96%87%E4%BB%B6%E7%94%A8%E6%88%B7%E7%BB%84%E7%AD%89%EF%BC%88%E4%B8%80%EF%BC%89---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

- Linux系统本质：
Linux系统中所见即文件（哪怕驱动也是文件本质） , bin 目录一些执行文件，home 目录用户，lib 目录常用的 so ，opt 和 proc 是与进程相关的


- 常用命令
cd DerryAll 【进入到DerryAll目录】
cd.. 【返回到上一个目录】
cd . 【啥也没有做 就在当前目录 .代表当前目录】
ls 【当前文件夹下面的所有文件/文件夹等】
ls -all 【当前文件夹下面的所有文件/文件夹等 的详细显示】
ls -lh 【当前文件夹下面的所有文件/文件夹等 的大小详细显示】
pwd 【当前所在的目录路径】
cd / 【回到根目录】
./date 【执行 date可执行文件】 注意是在 /bin目录下
mkdir New01 【创建 New10名称 的文件夹】
touch file01.txt 【创建 file01名称 的文件】
rm -rf file01.txt 【删除file01文件】
ls -R 【递归当前文件夹 到 文件，有点像 树形结构输出的效果】
rmdir 文件夹 【只能清空空目录文件夹，如果文件夹里面有内容，就无法删除】
rm -r 文件夹 【递归清空目录文件夹】
rm hello.c 【删除文件】
cp hello.c 目标文件夹 【拷贝文件 到 目标文件夹】


- Linux文件读取操作
cat file01.txt 【快速查看文件内容】
vim file01.txt 【使用vim编辑器查看文件内容】
tac file01.txt 【倒序快速查看文件内容】
more file01.txt 【每次只查看一页，回车查看下一页】
head -2 file01.txt 【查看前面2行内容】
tail -3 file01.txt 【查看后面2行内容】


- Linux中的用户与用户组
【#】代表 root权限
【$】、【%】代表普通用户
sudo su root 【从普通用户 切换到 root用户，注意：要输入密码 是看不见的】
exit 【 退出 root 用户，到普通用户】
whoami 【查看当前用户】


- 文件的用户权限
1. 数字修改用户文件权限
chmod 777 file01.txt  --> 【执行完后】 -rwxrwxrwx 1 root root 323 Mar 27 15:53 file01.txt三组都 可读可写可执行
chmod 111 file01.txt 【执行完后 ---x--x--x 1 root root 323 Mar 27 15:53
file01.txt】三组都 可执行
chmod 412 file02.txt 【执行完后 -r----x-w- 1 root root 323 Mar 27 15:53
file01.txt】一组(可读) 二组(可执行) 三组(可写)

3. 名字限定法
4. 创建修改用户和用户组



- 文件信息详述：
-rw-r--r--            1              root        root         0        Mar 27 14:12    file01.txt
文件权限    硬链接计数    所有者    所属组    大小            时间              名称


- Linux文件类型：
1. 常用
“-” 【普通文件】
d 【文件夹】

2. 不常用
l 【软链接，硬链接软件接：相当于 windows 的快捷图标】
c 【字符设备文件】
b 【块设备文件】
p 【管道文件】
s 【套接字】


-  命令执行原理：
![650](../99附件/20220529_175429_1.png)


- 临时环境变量介绍：（只在当前会话窗口下生效，新开一个会话就失效了）
export AAAA=1234567
echo $AAAA


- 全局环境变量介绍：
vim /etc/profile 修改好profile后 （export derry="Derry真牛逼"）
让其修改生效 source /etc/profile
echo $derry
echo $BBBB


