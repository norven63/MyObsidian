日期： 2022-06-02

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015388822975072&vid=387702301203181684

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA?_at_=1654176986294#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.24-Cmake%E5%8E%9F%E7%94%9F%E6%9E%84%E5%BB%BA%E5%B7%A5%E5%85%B7%E5%AD%A6%E4%B9%A0&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

### 一、CMakeList.txt 完整语法
```cmake
# 【一、最低支持的版本】  
# 注意：这里并不能代表最终的版本，最终版本在 build.gradle 中设置的。  
cmake_minimum_required(VERSION 3.10.2)  
  
  
# 【二、当前工程名】  
# 以前的旧版本，是没有设置的，这个可以设置，也可以不设置  
project("ndk28_cmake")  
  
  
# 【三、批量导入 cpp c源文件】  
# file 可以定义一个变量 SOURCE， GLOB（使用GLOB从源树中收集源文件列表，就可以开心的 *.cpp *.c *.h）  
# https://www.imooc.com/wenda/detail/576408  
file(GLOB SOURCE *.cpp *.c)  
  
  
# 【四、添加一个库】  
# 动态库：SHARED  
# 静态库：STATIC  
add_library(  
        native-lib # 库的名字 ---> 完整文件：libnative-lib.so（如果是静态库，则是 .a 文件）  
        SHARED  
        ${SOURCE}  # cpp的源文件：把cpp源文件编译成 libnative-lib.so 库  
)  
  
  
# 【五、查找一个 NDK 工具中的动态库(liblog.so)】  
# 最终的动态库查找路径：D:\Android\Sdk\ndk\21.0.6113669\toolchains\llvm\prebuilt\windows-x86_64\sysroot\usr\lib\arm-linux-androideabi\16\liblog.so  
  
# 思考1：如何知道哪些库名称是可以写的，例如写log就可以？  
# 答：请查看 D:\Android\Sdk\ndk\21.4.7075529\build\cmake\system_libs.cmake  

# 思考2：为什么是在 21.0.6113669 文件夹下？  
# 答：因为local.properties知道了NDK版本，或者是你当前的NDK版本  
  
# 思考3：为什么是在 arm-linux-androideabi 文件夹下？  
# 答：因为测试机是arm32的，并且在build.bradle中配置了abiFilters "armeabi-v7a"，所以选择 arm-linux-androideabi  

# 思考4：为什么是在 16 文件夹下？  
# 答：因为build.bradle中配置的

minSdkVersion 16find_library(  
        log-abcdafasfsafasf # 变量名称，后面可以复用  
        log # NDK工具中的动态库  
)  


# 【六、把log库链接到总库中去】  
# native-lib是我们的总库，也就是在 apk/.../cpp/libnative-lib.so# 只有完成这部链接工作，总库的cpp代码才可以正常调用 android/log.h 的库实现代码  
target_link_libraries(  
        native-lib # 被链接的总库  
        ${log-abcdafasfsafasf} # 链接的具体NDK工具库，这里用的变量名  
        # getndk # 链接的某个三方库 
)  
  
  
# TODO ---------------------------函数语法---------------------------  
  
# TODO 0. log 信息输出的查看】  
# 以前的Cmake版本都是在output.txt, 现在最新版本Cmake在metadata_generation_stderr.txt或cmake_server_log，害我寻找了半天  
# 想及时更新你的日志，请安装一次即可 or Linked_C++_Projects# 在Build也可以查看，注意：是点击Sync Now 才会看到  
  
#[[  
TAG释义  
  
(无) = 重要消息；  
STATUS = 非重要消息；  
WARNING = CMake 警告, 会继续执行；  
AUTHOR_WARNING = CMake 警告 (dev), 会继续执行；  
SEND_ERROR = CMake 错误, 继续执行，但是会跳过生成的步骤；  
FATAL_ERROR = CMake 错误, 终止所有处理过程；  
]]  
  
message(STATUS "CMake Hellow World!")  
message(STATUS "2DerrySuccessD>>>>>>>>>>>>>>>>>>>>>>>>>>>>")  
message(STATUS "3DerrySuccessD>>>>>>>>>>>>>>>>>>>>>>>>>>>>")  
message("10 OldCmakeVersion:output.txt, NewCmakeVersion:cmake_server_log.txt")  
  
# TODO 1. CMake变量  
# CMake中所有变量都是string类型。可以使用set()和unset()命令来声明或移除一个变量  
  
# CMAKE_CXX_FLAGS是CMake内置的环境变量  
# set(CMAKE_CXX_FLAGS abcd123)  
  
# 声明变量：set(变量名 变量值)  
set(var1 666)  
# 引用变量：message 命令用来打印  
message("var = ${var1}")  
# 移除变量  
unset(var1)  
message("my_var = ${var1}") # 会取不到值，因为被移除了  
  
# TODO 2. CMake列表（lists）  
# 声明列表：set(列表名 值1 值2 ... 值N) 或 set(列表名 "值1;值2;...;值N")  
set(list_var1 1 2 3 4 5) # 字符串列表呢？ CMake中所有变量都是string类型  
# 或者  
set(list_var2 "1;2;3;4;5") # 字符串列表呢？  CMake中所有变量都是string类型  
  
message("list_var = ${list_var1}")  
message("list_var2 = ${list_var2}")  
  
# TODO 3. CMake流程控制-条件判断  
# true：1、ON、YES、TRUE、Y，所有非0的值，都 = true# false：0、OFF、NO、FALSE、N、IGNORE、NOTFOUND，都 = falseset(if_tap OFF) # 定义一个变量if_tap，值为false  
set(elseif_tap ON) # 定义一个变量elseif_tap，值为ture  
  
if (${if_tap})  
    message("if")  
elseif (${elseif_tap})  
    message("elseif")  
else (${if_tap})   # 可以不加，但规范性上考虑要加  
    message("else")  
endif (${if_tap})  # 结束if  
# 注意：elseif和else部分是可选的，也可以有多个elseif部分，缩进和空格对语句解析没有影响  
  
# TODO 4. CMake流程控制-循环命令  
  
# 4.1 while循环  
# STREQUAL：是否等于  
# NOT：取反，即 ！的意思  
# 注意：break()命令可以跳出整个循环、continue()可以继续当前循环  
set(a "")  
while (NOT a STREQUAL "xxx")  
    set(a "${a}x")  
    message(">>>>>>a = ${a}")  
endwhile ()  
  
# 4.2 for循环  
foreach (item 1 2 3)  
    message("1item = ${item}")  
endforeach (item) # 结束for  
  
# 定义 “区间” 来循环  
foreach (item RANGE 2) # RANGE 默认从0开始，所以是：0 1 2  
    message("2item = ${item}")  
endforeach (item)  
  
# 跳级循环  
foreach (item RANGE 1 6 2) # 从1开始，到6结束，每次跳2级，所以是：1 3 5  
    message("3item = ${item}")  
endforeach (item)  
  
# 循环遍历列表  
set(list_va3 1 2 3) # 声明列表  
foreach (item IN LISTS list_va3)  
    message("4item = ${item}")  
endforeach (item)  
  
# TODO 5. CMake自定义函数  Shell的函数很类似  
#[[  
ARGC：表示传入参数的个数  
ARGV：表示所有参数，以分号 ; 相隔  
ARGV0：表示第一个参数，ARGV1、ARGV2以此类推  
]]  
function(num_method n1 n2 n3)  
    message("call num_method method")  
    message("n1 = ${n1}")  
    message("n2 = ${n2}")  
    message("n3 = ${n3}")  
    message("ARGC = ${ARGC}")  
    message("arg1 = ${ARGV0} arg2 = ${ARGV1} arg3 = ${ARGV2}")  
    message("all args = ${ARGV}") # 输出 10000;20000;30000endfunction(num_method)  
num_method(10000 2000 3000)  # 调用num_method函数
```

<br><br>

### 二、静态库与动态库原理

