日期： 2022-05-30

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015384528007776&vid=387702300989258524

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.19-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8BNDK%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%BA%93%E7%BB%99Android%E7%94%A8%EF%BC%88%E4%B8%89%EF%BC%89---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

- 交叉编译：将Linux的执行文件，打包给Android系统用
-  非交叉编译的执行文件，不能够在Android系统中运行

- 交叉编译使用的gcc文件路径：`android-ndk-r17c/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-gcc`
	- 注意：**`arm-linux-androideabi-4.9`** 要根据目标Android机型的CPU架构而定
- 通过Linux的环境变量，把这个gcc文件的路径设置成全局环境变量 [[享学Vip - 2022年5月14日 【Linux学习 之 命令执行原理与文件用户组】#全局环境变量：]]
- 