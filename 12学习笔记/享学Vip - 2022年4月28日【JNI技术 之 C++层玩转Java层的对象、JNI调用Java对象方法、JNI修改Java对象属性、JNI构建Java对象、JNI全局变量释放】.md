日期： 2022-05-15

标签： #学习笔记 #技术 #Android 

学习资料： 
腾讯课堂 - https://ke.qq.com/webcourse/3060320/105200059#taid=13821187581719136&vid=387702299967880887

百度网盘 - 

---
<br>

### 一、Java层调用JNI层函数，并传入参数
- 之所以单独笔记“入参”调用的方式，是因为这种行为会存在高密度的上下层数据交互，会大量使用到JNIEnv函数中的**各种数据格式转换**。当然笔记无法枚举齐全所有case，只是起到一个抛砖引玉作用。

##### JNI层操作 基本类型、String类型

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
    env->ReleaseStringUTFChars(text_info, _text_info);

} // JNI函数结束，会自动释放，所有的局部成员
```

<br>

##### 2、JNI数组操作
- 在调用 `env->ReleaseIntArrayElements()` 释放内存时，可以通过传入不同的标识，选择对上层数组有不同的影响：
	1. `JNI_OK`：本次C++的修改的数组，刷新给JVM Java层，并且释放C++数组  
	2. `JNI_COMMIT`：本次C++的修改的数组，刷新给JVM Java层，但不释放C++数组  
	3. `JNI_ABORT`：只释放C++数组  

1. 修改数组元素值
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
  
    // 5、规范：释放内存，并将数组的修改动作，“同步刷新”到Java层  
    // JNI_OK     本次C++的修改的数组，刷新给JVM Java层，并且释放C++数组  
    // JNI_COMMIT 本次C++的修改的数组，刷新给JVM Java层，但不释放C++数组  
    // JNI_ABORT  只释放C++数组  
    env->ReleaseIntArrayElements(ints, _ints, JNI_OK);
  
  
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
        env->SetObjectArrayElement(strs, i, updateValue); // 内部会执行操纵杆刷新“同步刷新”到Java层
    }  
} // JNI函数结束，会自动释放，所有的局部成员
```

2. 数组排序
- 调用工具方法 `qsort()` 完成排序
```cpp

// 比较的函数  
int compare(const jint *number1, const jint *number2){  
    return *number1 - *number2;  
}

extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_15_1study_MainActivity_sort(JNIEnv *env, jobject thiz, jintArray arr) {  
    jint * intArray = env->GetIntArrayElements(arr, nullptr);  
  
    int length = env->GetArrayLength(arr);  
  
    // TODO  NDK是一个很大的工具链（包含 Java JNI，C++, stdlib， pthread ....）  
  
    // 第一个参数：void* 数组的首地址  
    // 第二个参数：数组的大小长度  
    // 第三个参数：数组元素数据类型的大小  
    // 第四个参数：数组的一个比较的函数指针（Comparable）  
    /**  
	    void qsort(
			void* __base,  // void*相当于 Java的Object、Kotlin的Any，内部数组的首地址 给 存好  
			size_t __nmemb,
			size_t __size,
			int (*__comparator)(const void* __lhs, const void* __rhs)
		);
	 */
	 qsort(intArray, length, sizeof(int), reinterpret_cast<int (*)(const void *, const void *)>(compare));  
  
    // 同步数组的数据给java 数组intArray 并不是arr ，可以简单的理解为copy  
    // JNI_OK: 既要同步数据给arr ,又要释放intArray，会排序  
    // JNI_COMMIT: 会同步数据给arr ，但是不会释放intArray，会排序  
    // JNI_ABORT: 不同步数据给arr ，但是会释放intArray，所以上层看到就并不会排序  
    env->ReleaseIntArrayElements(arr, intArray, JNI_COMMIT);  
}
```

<br>

##### 3、JNI对象操作
- 细节参考  [[享学Vip - 2022年4月26日【JNI技术 之 签名对应表、JIN函数签名结构、JNI层调用Java层示例】#4、JNI层调用Java层示例]] 中函数调用部分

```cpp
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_putObject(JNIEnv *env,  
                                                 jobject thiz,  
                                                 jobject student,  
                                                 jstring str) {  
  
    const char *_str = env->GetStringUTFChars(str, NULL);  
    LOGD("_str:%s\n", _str)  
    // 作为C工程师，要记住一句话（时时刻刻想着回收你的代码）  
    env->ReleaseStringUTFChars(str, _str); // 已经释放了  
  
    // 只玩Student对象里面的成员，获取Student.class对象  
    jclass studentClass = env->FindClass("com/derry/as_jni_2/Student");  
  
    // String toString()
    jmethodID toStringMethod = env->GetMethodID(studentClass, "toString", "()Ljava/lang/String;");  
    jstring toStringValueS = (jstring) env->CallObjectMethod(student, toStringMethod);  
    const char *toStringValueC = env->GetStringUTFChars(toStringValueS, NULL);  
    LOGD("toStringValueC:%s\n", toStringValueC);  
    env->ReleaseStringUTFChars(toStringValueS, toStringValueC); // 已经释放了  
  
    // void setName(String)
    jmethodID setNameMethod = env->GetMethodID(studentClass, "setName", "(Ljava/lang/String;)V");  
    jstring value1 = env->NewStringUTF("李元霸");  
    env->CallVoidMethod(student, setNameMethod, value1);  
  
    // String getName(String)
    jmethodID getNameMethod = env->GetMethodID(studentClass, "getName", "()Ljava/lang/String;");  
    jstring nameS = (jstring) env->CallObjectMethod(student, getNameMethod);  
    const char *nameC = env->GetStringUTFChars(nameS, NULL);  
    LOGD("nameC:%s\n", nameC)  
    env->ReleaseStringUTFChars(nameS, nameC); // 已经释放了  
  
    // void setAge(int) 
    jmethodID setAgeMethod = env->GetMethodID(studentClass, "setAge", "(I)V");  
    env->CallVoidMethod(student, setAgeMethod, 99);  
  
    // int getAge()  
    jmethodID getAgeMethod = env->GetMethodID(studentClass, "getAge", "()I");  
    int age1 = env->CallIntMethod(student, getAgeMethod);  
    LOGD("age1:%d\n", age1)  
  
    /**
     * 调用静态方法  
     */    
    // void showInfo(String)
	jmethodID showInfo = env->GetStaticMethodID(studentClass, "showInfo", "(Ljava/lang/String;)V");  
    jstring value2 = env->NewStringUTF("静态的函数 李元霸");  
    env->CallStaticVoidMethod(studentClass, showInfo, value2);  
  
    // 释放本地引用（这里只是为了让我们记得要有释放内存空间的好习惯）
    // 即使这里不手动释放，函数在执行完毕后也会自动释放（因为这里是一个局部变量，存在于栈空间里）
    // 因为这里释放了jclass引用，所以会把所有关联过的jmethodID引用也一起释放，不需要手动释放
    env->DeleteLocalRef(studentClass);  
}
```

<br><br>

### 二、JNI层构建Java对象

##### 1、AllocObject() 构建
- C++ alloc分配出一个内存空间给这个对象，**“不会”** 调用此对象构建函数

```cpp
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_insertObject(JNIEnv *env, jobject thiz) {  
  
    // 1. 构建Student对象  
    jclass studentClass = env->FindClass("com/derry/as_jni_2/Student");  
    jobject student = env->AllocObject(studentClass); // C++ alloc分配出一个内存空间给这个对象，“不会”调用此对象构建函数  
    // env->NewObject();  // C++ 实例化一个对象出来，“会”调用此对象的构造函数，相当于：new XXX();  
  
    // setName
    jmethodID setNameMethod = env->GetMethodID(studentClass, "setName", "(Ljava/lang/String;)V");  
    jstring value1 = env->NewStringUTF("刘奋");  
    env->CallVoidMethod(student, setNameMethod, value1);  
    // setAge  
    jmethodID setAgeMethod = env->GetMethodID(studentClass, "setAge", "(I)V");  
    env->CallVoidMethod(student, setAgeMethod, 99);  
  
  
    // 2. 构建Person对象  
    jclass personClass = env->FindClass("com/derry/as_jni_2/Person");  
    jobject person = env->AllocObject(personClass); // C++ alloc分配出一个内存空间给这个对象，“不会”调用此对象构建函数  
  
    // void setStudent(Student)  
    jmethodID setStudent = env->GetMethodID(personClass, "setStudent", "(Lcom/derry/as_jni_2/Student;)V");  
    env->CallVoidMethod(person, setStudent, student);  
  
    // static void putStudent(Student)
    jmethodID putStudent = env->GetStaticMethodID(personClass, "putStudent", "(Lcom/derry/as_jni_2/Student;)V");  
    env->CallStaticVoidMethod(personClass, putStudent, student);  
  
  
    /**  
     * 释放工作  
     */  
    // 释放场景一：通过JNIEnv得到的对象（当然其实可以不用释放，因为JNIEnv内部自己会释放，这里是为了养成好习惯）  
    env->DeleteLocalRef(personClass);  
    env->DeleteLocalRef(student);  
    env->DeleteLocalRef(value1);  
    env->DeleteLocalRef(personClass);  
    env->DeleteLocalRef(person);  
  
    // 释放场景二：构建String  
    // env->GetStringUTFChars(); // 构建String  
    // env->ReleaseStringUTFChars(); // 释放String  
  
    // 释放场景三：自己new一个C++对象  
    // StudentCPP student = new StudentCPP(); // 构建对象  
    // delete StudentCPP; // 释放对象  
}
```

<br>

##### 2、NewObject()方式
- C++ 实例化一个对象出来，**“会”** 调用此对象的构造函数，相当于：`new XXX();`

```cpp
extern "C"  
JNIEXPORT  
void  
JNICALL  
Java_com_derry_as_1jni_12_MainActivity_testQuote(JNIEnv *env, jobject thiz) {  
    jclass dogClass = env->FindClass("com/derry/as_jni_2/Dog");  
  
    jmethodID dogInit = env->GetMethodID(dogClass, "<init>", "()V");  
    jobject dog = env->NewObject(dogClass, dogInit); // 相当于Dog dog = new Dog();  
  
    jmethodID dogInit1 = env->GetMethodID(dogClass, "<init>", "(I)V");  
    jobject dog2 = env->NewObject(dogClass, dogInit1, 1); // Dog dog = new Dog(1);  
  
    jmethodID dogInit3 = env->GetMethodID(dogClass, "<init>", "(II)V");  
    jobject dog3 = env->NewObject(dogClass, dogInit3, 1, 2); // Dog dog = new Dog(1, 2);  
}
```

<br><br>

### 三、全局变量释放
> 在JNI函数中会有，局部引用、全局引用。默认情况下，都是局部引用。
> 在JNI函数结束执行后，会自动回收所有的局部引用内存，但是我们必须养成时时刻刻及时手动回收的好习惯。
> **==全局引用，需要开发者在分配内存时，手动去提升为全局引用，然后再手动释放，否则这个内存不会被回收。所以通常情况下，会在Activity.onDestroy()中释放全局引用。==**
> 【注意】无论哪种释放，都不会把对象设置成null，需要手动设置。


```cpp
// 声明一个全局引用  
jclass dogClass = nullptr;  
  
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_testQuote(JNIEnv *env, jobject thiz) {  
  
    if (!dogClass) {  
        // dogClass = env->FindClass("com/derry/as_jni_2_02/Dog"); // 这样只是把dogClass变为一个局部变量
  
        // 提升为全局引用，让JNI函数结束后，不要自动去回收
        jclass tempDogClass = env->FindClass("com/derry/as_jni_2/Dog");
        dogClass = (jclass) env->NewGlobalRef((jobject) tempDogClass); // 提升为全局引用  
  
        env->DeleteLocalRef(tempDogClass);  
    }  
  
    jmethodID dogInit = env->GetMethodID(dogClass, "<init>", "()V");  
    jobject dog = env->NewObject(dogClass, dogInit);  
}  
// 如果这里不升级成全局变量，那么默认是局部变量。在JNI函数弹栈结束后，会自动释放局部引用成员dogClass，但是又“不会把dogClass置为NULL”，所以第二次调用时会奔溃（因为dogClass不会初始化赋值）
  
extern "C"  
JNIEXPORT void JNICALL  
Java_com_derry_as_1jni_12_MainActivity_delQuote(JNIEnv *env, jobject thiz) {  
    if (dogClass) {  
        env->DeleteGlobalRef(dogClass); // 手动释放全局引用成员dogClass  
  
        dogClass = nullptr; // 手动设置成null  
    }  
}
```
