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
#include <jni.h>  
#include <string>  
#include <pthread.h> // 在AS上 pthread不需要额外配置，默认就有  
  
/**  
    什么是静态注册？  
    默认情况就是静态注册，静态注册比动态注册要简单
	但是在诸多系统源码中，会发现大量都是采用动态注册，因为动态注册虽然麻烦，但是比静态注册安全性高，不要暴露包名类名等信息  
	
    【静态注册】    
	    优点：      
			开发简单    
		缺点：  
		    1.JNI 函数名很长  
	        2.捆绑了上层的包名、类名等敏感信息  
	        3.运行期才会去匹配JNI函数，性能上低于一点点动态注册  
 */
extern "C" JNIEXPORT jstring JNICALL  
Java_com_mac_jni04_1study_MainActivity_stringFromJNI(  
        JNIEnv *env,  
        jobject /* this */) {  
  
    std::string hello = "默认就是静态注册的方式";  
  
    return env->NewStringUTF(hello.c_str());  
}  


// TODO ============ 下面是 动态注册区域  

/**  
 * 【全局持有JavaVM】
 *  用于后续创建JNIEnv
 */
// JavaVM *vm; // 这种声明方式不规范，系统会默认赋值 3532532  -3534255，属于野指针
JavaVM *vm = nullptr; // 规范的声明方式，默认赋值0


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

// java:'
;0-像Java的构造函数，如果你不写构造函数，默认就有构造函数，如果你写了 会覆盖  
// JN90-5I_OnLoad，如果你不写JNI_OnLoad，默认就有JNI_OnLoad，如果你写了，会覆盖  
// 逆向工程师，做坏事的  
// 在很多的系统源码，或者是其他源码，会大量采用动态注册，动态注册虽然很麻烦，但是这个是必学项  
// 动态的优点：1.被反编译后 安全性高一点， 2.在native中的调用，函数名简洁， 3.编译后的函数标记 较短一些  
jint JNI_OnLoad(JavaVM *vm_param, void *args) {  
    /**  
     * 【1. 缓存JavaVM】  
     */
     ::vm = vm_param;  
  
  
    /**  
     * 【2. 构建JNIEnv】  
     */
    JNIEnv *env;  
    jint r = vm_param->GetEnv(reinterpret_cast<void **>(&env), JNI_VERSION_1_6);  
  
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

<br><br>

### 二、JNI线程
##### 1、JavaVM、JNIEnv、jobject 的作用域
- `JavaVM` 是全局的，是相当于APP进程的全局成员，可以跨线程、跨函数
- `JNIEnv` 绑定当前JNI函数所在的线程，所以不能跨线程传递。即使提升全局也没有用，主线程的env不能切换到子线程使用。
- `jobject` 与当前实例绑定，不能跨线程传递，也不能跨函数传递；但是它允许被提升到全局变量，就可以跨线程传递

<br>


##### 2、pthread_create
```cpp
int pthread_create(  
	pthread_t* __pthread_ptr,        // 参数一：线程标记，
	pthread_attr_t const* __attr,    // 参数二：pthread配置的参数集，我目前还没用到  
	void* (*__start_routine)(void*), // 参数三：函数指针，相当于 Java 中的 Runnable.run()
	void*                            // 参数四：指定传递给 start_routine 函数的参数，如果不需要传递任何数据时，传递void*
);                         
```

<br>


##### 3、构建JNIEnv
- 方法一
```cpp
JNIEnv *env;
jint r = vm->GetEnv(reinterpret_cast<void **>(&env), JNI_VERSION_1_6);  
  
// C 中 0就是成功  
// if (r) { // 非0就是ture  
// if (r != 0) {
if (r != JNI_OK) {  
    return -1; // 这个就是让程序奔溃  
}  
```

- 方法二
```cpp
// 新创建JNIEnv  
JNIEnv *env;  

// AttachCurrentThread函数签名：jint AttachCurrentThread(JNIEnv** p_env, void* thr_args)  
jint r = ::vm->AttachCurrentThread(reinterpret_cast<JNIEnv **>(&env), nullptr); // 传入env二级指针  
if (r) { // 非0 = true = 失败  
    return reinterpret_cast<void *>(123);  
}
```




##### 4、代码示例
```cpp
/**  
 * 【1. 全局引用缓存】  
 */
class MyContext {  
public:  
    // 1. JavaVM是全局的，是相当于APP进程的全局成员，可以跨线程、跨函数  
    JavaVM *vm = nullptr;  
  
    // 2. JNIEnv绑定当前JNI函数所在的线程，所以不能跨线程传递。即使提升全局也没有用，主线程的env不能切换到子线程使用  
    JNIEnv *jniEnv = nullptr;  
  
    // 3. jobject与当前实例绑定，不能跨线程传递，也不能跨函数传递；但是它允许被提升到全局变量，就可以跨线程传递  
    jobject instance = nullptr;  
};  
  
  
/**  
 * 【2. 声明子线程执行的函数】  
 */
// 1. 这个函数定位相当于 Java 中的 Runnable.run() 方法  
// 2. 签名与 void* (*__start_routine)(void*) 一致，因为pthread_create()入参要求即如此  
// 3. 返回值是 void*，所以“必须”要有return语句，哪怕是 return nullptr 也可以，否则会崩溃  
// 4. 因为返回值是 void*，所以不论 return 34535.4f、return 543532.5、return 6、return "sads" 都可以  
void *cpp_thread_run(void *args) {  
    LOGD("C++ Pthread 的 异步线程 启动啦")  
  
    MyContext *context = static_cast<MyContext *>(args);  
  
    // 新创建JNIEnv  
    JNIEnv *env;  
  
    // AttachCurrentThread函数签名：jint AttachCurrentThread(JNIEnv** p_env, void* thr_args)  
    jint r = ::vm->AttachCurrentThread(reinterpret_cast<JNIEnv **>(&env), nullptr); // 传入env二级指针  
    if (r) { // 非0 = true = 失败  
        return reinterpret_cast<void *>(123);  
    }  
  
    jclass mainActivityCls = env->GetObjectClass(context->instance);  
    jmethodID updateActivityUI = env->GetMethodID(mainActivityCls, "updateActivityUI", "()V");  
    env->CallVoidMethod(context->instance, updateActivityUI);  
  
    ::vm->DetachCurrentThread(); // 解除新创建的 JNIEnv  
    return nullptr; // 这个return必须要有吗，否则会崩溃  
}  
  
extern "C"  
JNIEXPORT void JNICALL  
Java_com_mac_jni04_1study_MainActivity_naitveThread(JNIEnv *env, jobject thiz) {  

    /**  
     * 【3. 创建全局引用变量】  
     */
    MyContext *context = new MyContext;  
    context->instance = env->NewGlobalRef(thiz); // 把"局部成员"提升为"全局成员"，这里实际缓存的是MainActivity对象实例，主要为了拿到Java层的调用对象实例
  
  
    /**
	 * 【4. 创建并启动线程】  
     */
	pthread_t pid;  
  
    /*p_void_start; // 视频播放的 线程标记  
    p_audio_start; // 音频播放的 线程标记*/  
  
    // 传入一级指针、函数指针  
    pthread_create(&pid, nullptr, cpp_thread_run, context);  


    /**  
     * 【5. 释放全局引用变量】  
     */
     
	// 阻塞等待子线程（pid）执行完成后，才开始执行下面代码释放  
    pthread_join(pid, nullptr);  
  
    // 【注意】哪个线程的 env 创建的GlobalRef，就由哪个 env 来释放  
    env->DeleteGlobalRef(context->instance);  
    delete context;  
    context = nullptr;  
}
```

<br>

##### 5、线程常用函数
1. **pthread_exit** 函数：`void pthread_exit(void *value_ptr);`

> - `pthread_exit()` 函数唯一的参数 `value_ptr` 是函数的返回代码，只要 `pthread_join()` 中的第二个参数 `value_ptr` 不是 `NULL`，这个值将被传递给 `value_ptr`。
> - 线程的结束退出，可以是隐式的退出（执行完函数，或者执行到 `return` 语句），也可以显式的调用 `pthread_exit()` 函数来退出。
> - `pthread_exit()` 函数只会终止当前线程，不会影响进程中其它线程的执行；`return` 语句不仅会终止主线程执行，还会终止该线程中开启的其它子线程。
> - 执行 `pthread_exit()` 函数后，会立刻释放线程资源；`return` 语句并不会立刻释放。


2. **pthread_join** 函数：`int pthread_join(pthread_t thread, void **value_ptr);`

> - 调用 `pthread_join()` 的线程将被**挂起**，**线程阻塞**等待直到参数thread所代表的线程结束退出为止。
> - 如果 `value_ptr` 不为 `NULL`，那么线程thread的返回值存储在该指针指向的位置。该返回值可以是调用 `pthread_exit()` 时传入的值，或者该线程被取消而返回 `PTHREAD_CANCELED`。