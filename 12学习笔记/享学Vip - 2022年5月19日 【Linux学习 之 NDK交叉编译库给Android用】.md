日期： 2022-05-30

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015384528007776&vid=387702300989258524

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.19-Linux%E5%AD%A6%E4%B9%A0%E4%B9%8BNDK%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%BA%93%E7%BB%99Android%E7%94%A8%EF%BC%88%E4%B8%89%EF%BC%89---derry%E8%80%81%E5%B8%88&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

### 一、基本概念
- 交叉编译：将Linux的执行文件，用gcc打包给Android系统用
-  非交叉编译的执行文件，不能够在Android系统中运行

##### 1、需要配置的路径
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

<br>


##### 2、完整的profile全局配置
```shell

# 配置NDK路径
export NDK="/root/DerryAll/Tools/android-ndk-r17c"


# 把NDK路径配置，添加到Linux环境变量里面去
export PATH=$NDK:$PATH


# 下面是交叉编译相关
# 一句话$【NDK_GCC地址】 --system $【库文件地址】 -system $【头文件地址】 -system $【asm地址】 -pie xxxxxxxxxxx

# 配置GCC路径
# 四大平台
export NDK_GCC_x86="$NDK/toolchains/x86-4.9/prebuilt/linux-x86_64/bin/i686-linux-android-gcc"
export NDK_GCC_x64="$NDK/toolchains/x86_64-4.9/prebuilt/linux-x86_64/bin/x86_64-linux-android-gcc"
export NDK_GCC_arm="$NDK/toolchains/arm-linux-androideabi-4.9/prebuilt/linuxx86_64/bin/arm-linux-androideabi-gcc"
export NDK_GCC_arm_64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-gcc"

# 配置 --system $【库文件地址】 -system $【头文件地址】 -system $【asm地址】 的路径
# 四大平台
export NDK_CFIG_x86="--sysroot=$NDK/platforms/android-21/arch-x86 -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/i686-linux-android"
export NDK_CFIG_x64="--sysroot=$NDK/platforms/android-21/arch-x86_64 -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/x86_64-linux-android"
export NDK_CFIG_arm="--sysroot=$NDK/platforms/android-21/arch-arm -isystem $NDK/sysroot/usr/include -isystem $NDK/sysroot/usr/include/arm-linuxandroideabi"
export NDK_CFIG_arm_64="--isysroot=$NDK/platforms/android-21/arch-arm64 -isystem $NDK/sysroot/usr/include -isystem -isystem $NDK/sysroot/usr/include/aarch64-linux-android"

# 配置静态编译库的路径
# 四大平台
export NDK_AR_x86="$NDK/toolchains/x86-4.9/prebuilt/linux-x86_64/bin/i686-linuxandroid-ar"
export NDK_AR_x64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-ar"
export NDK_AR_arm="$NDK/toolchains/arm-linux-androideabi-4.9/prebuilt/linuxx86_64/bin/arm-linux-androideabi-ar"
export NDK_AR_arm_64="$NDK/toolchains/aarch64-linux-android-4.9/prebuilt/linuxx86_64/bin/aarch64-linux-android-ar"


# 参考
# 静态库 动态库相关
export myd="$NDK_GCC_arm $NDK_CFIG_arm -fPIC -shared "
export myj="$NDK_AR_arm rcs "

```

<br><br>

### 二、编译动态库
- get.h
```C
#include<stdio.h>

int get();
```

- get.c
```C
#include<get.h>

int get() {
	return 9527;
}
```

##### 1、Linux上流程
- `-o` ：输出 libget.so 文件
```shell
gcc -fPIC -shared get.c -o libget.so
```

<br>

##### 2、交叉编译流程
```shell
$NDK_GCC_arm $NDK_CFIG_arm -fPIC -shared get.c -o libgetndk.so
```

<br><br>

### 三、编译静态库

##### 1、Linux上流程
第一步：先根据源文件，打出**目标文件** get.o
-  `-c` ：源文件
```shell
gcc -fPIC -c get.c -o get.o
```

第二步：根据目标文件 get.o，生成 **态库**
- 注意：这里目标文件和静态库的书写顺序，是和其他方式反着来的。即 **==静态库在前，目标文件在后==**
```shell
ar rcs -o libget.a get.o
```

<br>

##### 2、交叉编译流程
第一步：先 **==交叉编译==** (注意：千万不要用gcc编译的目标文件，要用交叉编译的)出目标文件 getndk.o
```shell
$NDK_GCC_arm $NDK_CFIG_arm -fPIC -c get.c -o getndk.o
```

第二步：根据目标文件 getndk.o，生成 **静态库**
- 使用NDK的AR命令
```shell
$NDK_AR_arm rcs -o libgetndk.a getndk.o
```

<br><br>

### 四、app工程配置
##### 1、CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.10.2)  
  
# 批量导入  
file(GLOB appCPP *.cpp)  
  
add_library(  
        native-lib  
        SHARED # 动态库  
        ${appCPP})  
  
# 导入"静态库" 【第二种方式】可读性更强，代码多  
add_library(getndk_a STATIC IMPORTED)  
# 开始真正导入  
set_target_properties(getndk_a PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/libgetndk.a)  
  
  
# 导入"动态库" 【第二种方式】可读性更强，代码多  
add_library(getndk_so SHARED IMPORTED)  
# 开始真正导入  
set_target_properties(getndk_so PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../jniLibs/${CMAKE_ANDROID_ARCH_ABI}/libgetndk.so)
  
# QQ 语音变声的时候，【第一种方式】 简洁，不好理解  环境变量知识  
# set(CMAKE_CXX_FLAGS)  
  
find_library(  
        log-lib  
        log)  
  
target_link_libraries(  
        # 如果是静态库，会把 libgetndk.a 直接copy到总库 libnative-lib.so 里面
        # 如果是动态库，在运行期间，总库 libnative-lib.so 去加载 libgetndk.so  
        
        native-lib # 总库 libnative-lib.so  
        
        ${log-lib}  
        
        getndk # 链接此静态库到总库 libnative-lib.so
```

<br>


##### 2、builde.gradle
```groovy
apply plugin: 'com.android.application'  
  
android {  
    compileSdkVersion 30  
    buildToolsVersion "30.0.3"  
    defaultConfig {  
        applicationId "com.kevin.ndk12_cmake"  
        minSdkVersion 16  
        targetSdkVersion 30  
        versionCode 1  
        versionName "1.0"  
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"  
        externalNativeBuild {  
            cmake {  
                // cppFlags "" 默认包含四大平台  
  
                abiFilters "armeabi-v7a"  
            }  
        }  
        ndk {  
            abiFilters "armeabi-v7a"  
        }  
    }  
    buildTypes {  
        release {  
            minifyEnabled false  
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'  
        }  
    }    externalNativeBuild {  
        cmake {  
            path "src/main/cpp/CMakeLists.txt"  
            version "3.10.2"  
        }  
    }}  
  
dependencies {  
    implementation fileTree(dir: 'libs', include: ['*.jar'])  
    implementation 'androidx.appcompat:appcompat:1.1.0'  
    implementation 'androidx.constraintlayout:constraintlayout:1.1.3'  
    testImplementation 'junit:junit:4.12'  
    androidTestImplementation 'androidx.test.ext:junit:1.1.1'  
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.2.0'  
}
```
