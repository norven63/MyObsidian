日期： 2022-06-05

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015393117942368&vid=387702301287394256

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA?_at_=1654176986294#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.26-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8BNDK%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91FFmpeg%E4%B8%8E%E9%9B%86%E6%88%90FFmpeg---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

### FFMpeg
-  http://www.ffmpeg.org/releases/ （ffmpeg历史版本下载）
-  `wget http://www.ffmpeg.org/releases/ffmpeg-4.0.2.tar.bz2`
-  解压：`tar -xjf ffmpeg-4.0.2.tar.bz2`
- 查看帮助文档：`./configure --help`

```shell
#!/bin/bash

# 首先定义一个NDK目录的变量 NDK_ROOT
NDK_ROOT=/root/DerryAll/Tools/android-ndk-r17c

# 此变量执行ndk中的交叉编译gcc所在目录
TOOLCHAIN=$NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64

#从as的 externalNativeBuild/xxx/build.ninja， 反正下面的配置，可以压制警告的意思
FLAGS="-isystem $NDK_ROOT/sysroot/usr/include/arm-linux-androideabi -D__ANDROID_API__=21 -g -DANDROID -ffunction-sections -funwind-tables -fstack-protector-strong -no-canonical-prefixes -march=armv7-a -mfloat-abi=softfp -mfpu=vfpv3-d16 -mthumb -Wa,--noexecstack -Wformat -Werror=format-security -O0 -fPIC"

INCLUDES=" -isystem $NDK_ROOT/sources/android/support/include"

PREFIX=./android/arm # 1.定义编译后，所存放的目录
# 2.--enable-small 优化大小 非常重要，必须优化才行的哦
# 3.--disable-programs 不编译ffmpeg程序（命令行工具），我们是需要获取静态、动态库
# 4.--disable-avdevice 关闭avdevice模块，此模块在android中无用
# 5.--disable-encoders 关闭所有编码器（播放不需要编码）
# 6.--disable-muxers 关闭所有复用器（封装器），不需要生成mp4这样的文件，所有关闭
# 7.--disable-filters 关闭所有滤镜
# 8.--enable-cross-compile 开启交叉编译（ffmpeg是跨平台的，注意：并不是所有库都有这么happy的选项）
# 9.--cross-prefix 看右边的值就知道是干嘛的，gcc的前缀..
# 10.disable-shared / enable-static 这个不写也可以，默认就是这样的，（代表关闭动态库，开启静态库）
# 11.--sysroot
# 12.--extra-cflags 会传给gcc的参数
# 13.--arch --target-os

./configure \
--prefix=$PREFIX \
--enable-small \
--disable-programs \
--disable-avdevice \
--disable-encoders \
--disable-muxers \
--disable-filters \
--enable-cross-compile \
--cross-prefix=$TOOLCHAIN/bin/arm-linux-androideabi- \
--disable-shared \
--enable-static \
--sysroot=$NDK_ROOT/platforms/android-21/arch-arm \
--extra-cflags="$FLAGS $INCLUDES" \
--extra-cflags="-isysroot $NDK_ROOT/sysroot/" \
--arch=arm \
--target-os=android

make clean

make install
```