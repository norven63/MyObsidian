日期： 2022-05-22

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015367348138592&vid=387702300600034050

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.10-JNI%E6%8A%80%E6%9C%AF%E4%B9%8B%E6%89%8B%E5%86%99JNIEnv%E4%B8%8E%E9%9D%99%E6%80%81%E7%BC%93%E5%AD%98%E4%B8%8Enative%E5%BC%82%E5%B8%B8%EF%BC%88%E4%BA%94%EF%BC%89---derry&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

### 一、静态缓存

```cpp
static jfieldID f_name1_id = nullptr;  
static jfieldID f_name2_id = nullptr;  
static jfieldID f_name3_id = nullptr;  
  
// 看WebRTC，OpenGL，... 规则 静态缓存  
  
extern "C" // 【初始化】 - 构造函数里面一次性初始化完毕所有static缓存  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_15_1study_MainActivity2_initStaticCache(JNIEnv *env, jclass clazz) {  
    // 初始化全局静态缓存  
    f_name1_id = env->GetStaticFieldID(clazz, "name1", "Ljava/lang/String;");  
    f_name2_id = env->GetStaticFieldID(clazz, "name2", "Ljava/lang/String;");  
    f_name3_id = env->GetStaticFieldID(clazz, "name3", "Ljava/lang/String;");  
    // 省略....  
}  
  
extern "C" // 【干活】  - 重复调用多次，全部使用实现创建好的static缓存  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_15_1study_MainActivity2_staticCache(JNIEnv *env, jclass clazz,  
                                                           jstring name) {  
    // 如果这个方法会反复的被调用，那么不会反复的去获取jfieldID，因为是先初始化静态缓存，然后再执行此函数的  
    env->SetStaticObjectField(clazz, f_name1_id, name);  
    env->SetStaticObjectField(clazz, f_name2_id, name);  
    env->SetStaticObjectField(clazz, f_name3_id, name);  
}  
  
extern "C" // 【释放】  onDestroy 调用一次，释放静态缓存
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_15_1study_MainActivity2_clearStaticCache(JNIEnv *env, jclass clazz) {  
    f_name1_id = nullptr;  
    f_name2_id = nullptr;  
    f_name3_id = nullptr;  
    LOGD("静态缓存清除完毕...");  
}
```

<br><br>

### 二、异常处理
##### 1、JNI异常处理——自己捕获拦截
- 在可能抛异常的代码 “下面一行**紧接着**” 调用 `env->ExceptionOccurred()` ，判断是否发生了异常
- 调用 `env->ExceptionClear();` 消除异常

```cpp
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_15_1study_MainActivity3_exception(JNIEnv *env, jclass clazz) {  
    jfieldID f_id = env->GetStaticFieldID(clazz, "name999", "Ljava/lang/String;");  
    
    // 补救措施：name999() 方法找不到报错的话， 那么就拿 name1() 方法  
    jthrowable throwable = env->ExceptionOccurred(); // 检查本次函数执行，有没有异常    
	if (throwable) {  
        // 补救措施，先把异常清除，先不要奔溃  
        LOGD("检查到有异常 native层")  
  
        // 清除异常  
        env->ExceptionClear();  
  
        // 重新获取 name1() 方法  
        jfieldID f_id = env->GetStaticFieldID(clazz, "name1", "Ljava/lang/String;");  
    }  
}
```

<br>

##### 2、JNI异常处理——将异常抛给Java层

- Java层调用
```java
/**  
 * 方法签名自带throws异常  
 * @throws NoSuchFieldException  
 */  
public static native void exception2() throws NoSuchFieldException;  
  
public void exceptionAction(View view) {
    try {  
        exception2(); // 捕获C++抛上来的异常  
    } catch (NoSuchFieldException e) {  
        e.printStackTrace();
        
        Log.d("Derry", "JNI层的异常被捕获到了...");  
    }
}
```

- JNI层实现
```cpp

```
