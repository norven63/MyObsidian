日期： 2022-05-15

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821187581719136&vid=387702299967880887

百度网盘 - 

---
<br>

### 一、Java层“入参”调用JNI层
- 之所以单独笔记“入参”调用的方式，是因为这种行为会存在高密度的上下层数据交互，会大量使用到JNIEnv函数中的**各种数据格式转换**。当然笔记无法枚举齐全所有case，只是起到一个抛砖引玉作用。

##### 1、入参类型：基本类型、引用类型

```cpp
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_testArrayAction(JNIEnv *env,  
                                                       jobject thiz,  
                                                       jint count,  
                                                       jstring text_info) {  
  
    /**  
     * 【一、调用上层传入的基本类型】  
     */
     
    // int直接使用即可，不需要转换  
    int _count = count;  
    LOGD("C++ _count:%d\n", count)  
  
  
    /**  
     * 【二、调用Java层传入的引用类型】  
     */
     
    // jstring需要转成C用语言字符串才能使用  
    const char *_text_info = env->GetStringUTFChars(text_info, NULL); // NULL = 0 = false，在本地内部完成翻译转换，不需要开辟Copy机制转换  
    LOGD("C++ _text_info:%s\n", _text_info)  
  
    // 规范：作为C工程师，一定要时时刻刻想着回收自己的内存  
    env->ReleaseStringUTFChars(text_info, _text_info); // 已经释放了  

} // JNI函数结束，会自动释放，所有的局部成员
```

<br>

##### 2、入参类型：数组

```cpp
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_testArrayAction(JNIEnv *env,  
                                                       jobject thiz,  
                                                       jint count,  
                                                       jstring text_info,  
                                                       jintArray ints,  
                                                       jobjectArray strs) {  
  
    /**  
     * 【一、调用上层传入的 “基本类型” 数组】  
     */  
    
    // 1、获取元素地址  
    // 这是第一次调用，所以相当于拿到了 “首元素” 的地址，而C语言中首元素地址即为数组地址  
    jint *_ints = env->GetIntArrayElements(ints, NULL);  
  
    // 2、获取数组的长度Length
    // jarray父类——jintArray子类、jobjectArray子类、jxxxArray子类  
    // sizeof(_ints) / sizeof(int) 是C语言的方式，不需要这么底层  
    int intsLen = env->GetArrayLength(ints);  
  
    // 3、通过挪动指针遍历数组  
    for (int i = 0; i < intsLen; ++i) {  
  
        LOGI("修改前 C++ ints item:%d\n", *(_ints + i))  
  
        // 4、修改指针对应的值  
        *(_ints + i) = (i + 100001);  
  
        LOGI("修改后 C++ ints item:%d\n", *(_ints + i))  
    }  
  
    // 5、规范：释放内存，并将修改值同步刷新到Java层  
    // JNI_OK     本次C++的修改的数组，刷新给JVM Java层，并且释放C++数组  
    // JNI_COMMIT 本次C++的修改的数组，刷新给JVM Java层，但不释放C++数组  
    // JNI_ABORT  只释放C++数组  
    env->ReleaseIntArrayElements(ints, _ints, JNI_OK); // 已经释放了  
  
  
    /**  
     * 【二、String[] “引用类型”的数组】  
     *  无论 Student[]、Person[]、Test[]、String[] 都一样，都属于引用类型
     */
    
    // 1、获取数组的长度Length  
    int strsLen = env->GetArrayLength(strs);  
  
    // 2、与基本类型数组不同，引用类型的数组不通过挪动指针来遍历，而是通过 GetObjectArrayElement(jobjectArray array, jsize index) 函数来遍历
    for (int i = 0; i < strsLen; ++i) {  
  
        // 3、传入index索引，通过 GetObjectArrayElement() 获取对应下标的元素  
        jstring strItemS = (jstring) env->GetObjectArrayElement(strs, i);  
  
        const char *strItemC = env->GetStringUTFChars(strItemS, NULL); // 将jstring转换成C语言字符串  
        LOGI("C++ strItemC:%s\n", strItemC)  
          
        env->ReleaseStringUTFChars(strItemS, strItemC); // 规范：一旦不用了，就需要释放（养成好习惯）  
  
        // 4、直接调用 SetObjectArrayElement() 来修改数组的元素  
        jstring updateValue = env->NewStringUTF("Beyond");  
        env->SetObjectArrayElement(strs, i, updateValue); // 内部会操纵杆刷新  
    }  
} // JNI函数结束，会自动释放，所有的局部成员
```

<br>

##### 3、 入参类型：对象

```cpp

```
