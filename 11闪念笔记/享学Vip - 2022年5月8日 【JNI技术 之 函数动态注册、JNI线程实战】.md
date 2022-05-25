日期： 2022-05-22

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - 

百度网盘 - 

---
<br>

日期： 2022-05-22

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=14015363053171296&vid=387702300516424594

百度网盘 - https://pan.baidu.com/s/1zjmJzrU-4kq0TJ7Yxu9tvA#list/path=%2Fsharelink1103492872705-314800681445689%2F%E3%80%9008%E3%80%91NDK%2F2022.5.8-JNI%E6%8A%80%E6%9C%AF%E4%B9%8B%E5%8A%A8%E6%80%81%E6%B3%A8%E5%86%8C%E4%B8%8EJNI%E7%BA%BF%E7%A8%8B%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89&parentPath=%2Fsharelink1103492872705-314800681445689

---
<br>

### 一、函数动态注册

##### 1、Java层代码
```java
public class MainActivity extends Activity {  
  
    static {  
        // 默认执行C层的 jint JNI_OnLoad(JavaVM *vm, void *args) 方法  
        System.loadLibrary("jni04_study");
    }  
  
    private ActivityMainBinding binding;  
  
    @Override  
    protected void onCreate(Bundle savedInstanceState) {  
        super.onCreate(savedInstanceState);  
    }  
  
	public native String stringFromJNI(); // 默认生成的，其实也是静态注册方式  
  
    public native void dynamicJavaMethod01(); // 动态注册1 ()V  
  
    public native int dynamicJavaMethod02(String valueStr); // 动态注册2  (Ljava/lang/String;)I
}
```


##### 2、C层代码
```cpp
#include <jni.h>  
#include <string>  
  
// 日志输出  
#include <android/log.h>  
  
#define TAG "JNISTUDY"  
// __VA_ARGS__ 代表 ...的可变参数  
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, TAG,  __VA_ARGS__);  
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG,  __VA_ARGS__);  
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG,  __VA_ARGS__);  
  
#include <jni.h>  
#include <string>  
#include <pthread.h> // 在AS上 pthread不需要额外配置，默认就有  
  
// TODO ============ 下面是 动态注册区域  
/**  
    什么是静态注册？  
    默认情况下，就是静态注册，静态注册比动态注册要简单    但是在诸多系统源码中，会发现大量都是采用动态注册，因为动态注册虽然麻烦，但是比静态注册安全性高，不要暴露包名类名等信息  
    【静态注册】    优点：      开发简单    缺点：  
      1.JNI 函数名很长  
      2.捆绑了上层的包名、类名等敏感信息  
      3.运行期 才会去 匹配JNI函数，性能上 低于一点点 动态注册  
 */
extern "C" JNIEXPORT jstring JNICALL  
Java_com_mac_jni04_1study_MainActivity_stringFromJNI(  
        JNIEnv *env,  
        jobject /* this */) {  
  
    std::string hello = "默认就是静态注册的方式";  
  
    return env->NewStringUTF(hello.c_str());  
}  


/**  
 * 【全局持有JavaVM】  
 */
// JavaVM *vm; // 不规范，系统会默认赋值 3532532  -3534255，属于野指针
JavaVM *vm = nullptr; // 规范，默认赋值0


/**  
 * 【5. C层的实现函数】  
 */
// void actionDerry1(JNIEnv * env, jobject mainThis) { // 这种声明方式也可以的，这样就可以在函数体里使用JNIEnv指针了  
void actionDerry1() {  
    // 我想用env，我想用 jobject怎么办？  
    LOGI("C++ 动态注册的函数 actionDerry1 执行了啊")  
}  
  
jint actionDerry2(JNIEnv *env, jobject mainThis, jstring str) {  
    // 我想用env，我想用 jobject怎么办？  
    const char *str_ = env->GetStringUTFChars(str, NULL);  
    LOGD("C++ 动态注册的函数 actionDerry2 str_%s\n", str_)  
    env->ReleaseStringUTFChars(str, str_);  
    return 8993;  
}  
  
  
/**  
 * 【3. 声明动态注册函数表】  
 */
 
/**  
 *  结构体 JNINativeMethod 的结构成分：  
  
    typedef struct {
		const char* name;      // 动态注册JNI的函数名 --- Java的动态注册函数  
        const char* signature; // 函数签名 --- Java的动态注册函数签名  
        void*       fnPtr;     // 函数指针 -- C层的实现函数  
    } JNINativeMethod;  
    
 */  
static const JNINativeMethod methods[] = {  
        {"dynamicJavaMethod01", "()V",                   (void *) (actionDerry1)},//注意：这里是把函数指针 actionDerry1 强转成 void* 指针  
        {"dynamicJavaMethod02", "(Ljava/lang/String;)I", (void *) (actionDerry2)}  
};  


/**  
 * 【0. Java层调用 System.loadLibrary() 时，触发C层 JNI_OnLoad() 函数】  
 */

// java:像 Java的构造函数，如果你不写构造函数，默认就有构造函数，如果你写了 会覆盖  
// JNI_OnLoad，如果你不写JNI_OnLoad，默认就有JNI_OnLoad，如果你写了，会覆盖  
// 逆向工程师，做坏事的  
// 在很多的系统源码，或者是其他源码，会大量采用动态注册，动态注册虽然很麻烦，但是这个是必学项  
// 动态的优点：1.被反编译后 安全性高一点， 2.在native中的调用，函数名简洁， 3.编译后的函数标记 较短一些  
jint JNI_OnLoad(JavaVM *vm, void *args) {  
    /**  
     * 【1. 缓存JavaVM】  
     */
     ::vm = vm;  
  
  
    /**  
     * 【2. 构建JNIEnv】  
     */
    JNIEnv *env;  
    jint r = vm->GetEnv(reinterpret_cast<void **>(&env), JNI_VERSION_1_6);  
  
    // C 中 0就是成功  
    // if (r) { // 非0就是ture  
    // if (r != 0) {
    if (r != JNI_OK) {  
        return -1; // 这个就是让程序奔溃  
    }  
  
    // 框架的设计是，一级指针，那么我们只需要传递地址即可   JNIEnv  env;   系统(&env)  
    // 框架的设计是，二级指针，那么我们只需要传递地址即可   JNIEnv * env;   系统(&env)  
  
  
    /**
	 * 【4. 动态注册C层函数】  
     */
    // env->RegisterMethods(一次性注册1000个 动态注册的JNI函数)  
    // jint RegisterNatives(jclass clazz, const JNINativeMethod* methods, jint nMethods)
    jclass mainActivityClass = env->FindClass("com/mac/jni04_study/MainActivity");  
    r = env->RegisterNatives(mainActivityClass, methods, sizeof methods / sizeof(JNINativeMethod));  
  
    if (r != JNI_OK) {  
        LOGD("哎哟，动态注册失败了")  
    } else {  
        LOGI("动态注册成功")  
    }  
  
    return JNI_VERSION_1_6; // 一般会使用最新的JNI版本标记  
}
```
