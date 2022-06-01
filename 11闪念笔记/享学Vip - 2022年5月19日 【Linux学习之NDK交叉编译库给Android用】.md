日期： 2022-05-30

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015384528007776&vid=387702300989258524

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.19-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8BNDK%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%BA%93%E7%BB%99Android%E7%94%A8%EF%BC%88%E4%B8%89%EF%BC%89---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

- 交叉编译：将Linux的执行文件，用gcc打包给Android系统用
-  非交叉编译的执行文件，不能够在Android系统中运行

- 交叉编译使用的gcc文件路径：`android-ndk-r17c/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-gcc`
	- 注意：**`arm-linux-androideabi-4.9`** 要根据目标Android机型的CPU架构而定
- 通过Linux的环境变量，把这个gcc文件的路径设置成全局环境变量 [[享学Vip - 2022年5月14日 【Linux学习 之 命令执行原理与文件用户组】#全局环境变量：]]
- 把依赖库的头文件、库文件路径指定好
- 拆卸分析：（注意：拆卸后，不能运行，因为换行了，必须用 **==英文空格==** 做间隔）
```shell
export AAA=
"
--sysroot=/root/DerryAll/Tools/android-ndk-r17c/platforms/android-21/arch-arm 【stdio.h寻找的库路径，注意版本号】
-isystem /root/DerryAll/Tools/android-ndk-r17c/sysroot/usr/include 【stdio.h 的头文件】
-isystem /root/DerryAll/Tools/android-ndk-r17c/sysroot/usr/include/arm-linuxandroideabi 【asm的问题解决】
" 
```
- 一句话总结：`$【NDK_GCC地址】 --system $【库文件地址】 -system $【头文件地址】 -system $【asm地址】 -pie xxxxxxxxxxx`

- 完整的profile中的定义
```shell

# NDK Linux平台的支持
export NDK="/root/DerryAll/Tools/android-ndk-r17c"


# NDK的命令操作 配置到 Linux环境变量里面去
export PATH=$NDK:$PATH


# 下面是交叉编译相关
# 一句话$【NDK_GCC地址】 --system $【库文件地址】 -system $【头文件地址】 -system $【asm地址】 -pie xxxxxxxxxxx

# GCC路径
# 四大平台
export NDK_GCC_x86="$NDK/toolchains/x86-4.9/prebuilt/linux-x86_64/bin/i686-linux-android-gcc"
export NDK_GCC_x64="$NDK/toolchains/x86_64-4.9/prebuilt/linux-x86_64/bin/x86_64-linux-android-gcc"
export NDK_GCC_arm="$NDK/toolchains/arm-linux-androideabi-4.9/prebuilt/linuxx86_64/bin/arm-linux-androideabi-gcc"
export NDK_GCC_arm_64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-gcc"

# --system $【库文件地址】 -system $【头文件地址】 -system $【asm地址】 
# 四大平台
export NDK_CFIG_x86="--sysroot=$NDK/platforms/android-21/arch-x86 -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/i686-linux-android"
export NDK_CFIG_x64="--sysroot=$NDK/platforms/android-21/arch-x86_64 -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/x86_64-linux-android"
export NDK_CFIG_arm="--sysroot=$NDK/platforms/android-21/arch-arm -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/arm-linuxandroideabi"
export NDK_CFIG_arm_64="--isysroot=$NDK/platforms/android-21/arch-arm64 -isystem $NDK/sysroot/usr/include -isystem -isystem $NDK/sysroot/usr/include/aarch64-linux-android"

# 四大平台 后面讲 输出 安卓交叉编译的 静态库 xxxx.a
export NDK_AR_x86="$NDK/toolchains/x86-4.9/prebuilt/linux-x86_64/bin/i686-linuxandroid-ar"
export NDK_AR_x64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-ar"
export NDK_AR_arm="$NDK/toolchains/arm-linux-androideabi-4.9/prebuilt/linuxx86_64/bin/arm-linux-androideabi-ar"
export NDK_AR_arm_64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-ar"


# 参考
# 静态库 动态库相关
export myd="$NDK_GCC_arm $NDK_CFIG_arm -fPIC -shared "
export myj="$NDK_AR_arm rcs "


```
