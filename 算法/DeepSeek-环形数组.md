# 环形数组（Circular Array）详解

## 什么是环形数组？

环形数组是一种逻辑上将线性数组的首尾相连形成环状结构的数据结构。虽然物理存储上仍然是线性数组，但通过特定的索引计算方法，可以实现循环访问的效果。

## 环形数组的核心特点

1. **循环利用**：当索引到达数组末尾时，会自动回到数组开头
2. **固定大小**：数组大小在创建时确定，不会动态扩容
3. **高效操作**：插入和删除操作的时间复杂度通常为 O(1)

## 环形数组的实现原理

### 关键变量
- `array[]`：存储数据的数组
- `capacity`：数组的总容量
- `size`：当前存储的元素数量
- `front`/`head`：指向队列头部的索引
- `rear`/`tail`：指向队列尾部的索引

### 核心操作：循环索引计算

```java
// 计算下一个位置的索引（关键！）
int nextIndex(int currentIndex) {
    return (currentIndex + 1) % capacity;
}

// 计算前一个位置的索引
int prevIndex(int currentIndex) {
    return (currentIndex - 1 + capacity) % capacity;
}
```

## 完整实现示例

```java
public class CircularArray {
    private int[] array;
    private int capacity;
    private int size;
    private int head; // 头部指针
    private int tail; // 尾部指针
    
    // 构造函数
    public CircularArray(int capacity) {
        this.capacity = capacity;
        this.array = new int[capacity];
        this.size = 0;
        this.head = 0;
        this.tail = -1; // 初始时为空
    }
    
    // 判断是否为空
    public boolean isEmpty() {
        return size == 0;
    }
    
    // 判断是否已满
    public boolean isFull() {
        return size == capacity;
    }
    
    // 添加元素到尾部
    public boolean enqueue(int value) {
        if (isFull()) {
            System.out.println("队列已满，无法添加");
            return false;
        }
        
        tail = (tail + 1) % capacity; // 循环计算新位置
        array[tail] = value;
        size++;
        return true;
    }
    
    // 从头部移除元素
    public Integer dequeue() {
        if (isEmpty()) {
            System.out.println("队列为空，无法移除");
            return null;
        }
        
        int value = array[head];
        head = (head + 1) % capacity; // 循环移动头部指针
        size--;
        return value;
    }
    
    // 获取头部元素（不移除）
    public Integer peek() {
        if (isEmpty()) {
            return null;
        }
        return array[head];
    }
    
    // 遍历环形数组
    public void display() {
        if (isEmpty()) {
            System.out.println("队列为空");
            return;
        }
        
        System.out.print("环形数组内容: ");
        int current = head;
        for (int i = 0; i < size; i++) {
            System.out.print(array[current] + " ");
            current = (current + 1) % capacity;
        }
        System.out.println();
    }
    
    // 测试代码
    public static void main(String[] args) {
        CircularArray circularArray = new CircularArray(5);
        
        // 添加元素
        circularArray.enqueue(1);
        circularArray.enqueue(2);
        circularArray.enqueue(3);
        circularArray.enqueue(4);
        circularArray.enqueue(5);
        circularArray.display(); // 输出: 1 2 3 4 5
        
        // 队列已满，无法添加
        circularArray.enqueue(6); // 输出: 队列已满，无法添加
        
        // 移除元素
        System.out.println("移除: " + circularArray.dequeue()); // 输出: 移除: 1
        System.out.println("移除: " + circularArray.dequeue()); // 输出: 移除: 2
        circularArray.display(); // 输出: 3 4 5
        
        // 继续添加（利用释放的空间）
        circularArray.enqueue(6);
        circularArray.enqueue(7);
        circularArray.display(); // 输出: 3 4 5 6 7
        
        // 遍历展示循环特性
        System.out.println("头部元素: " + circularArray.peek()); // 输出: 3
    }
}
```

## 环形数组的应用场景

1. **循环队列**：最典型的应用，用于实现固定大小的队列
2. **缓冲区**：如网络数据包缓冲区、音频/视频缓冲区
3. **轮询调度**：循环分配任务给多个处理器
4. **游戏开发**：循环动画帧、循环地图等
5. **操作系统**：循环分配时间片给进程

## 环形数组 vs 普通数组

| 特性 | 普通数组 | 环形数组 |
|------|----------|----------|
| 空间利用率 | 可能浪费 | 高效利用 |
| 插入性能 | O(n) | O(1) |
| 删除性能 | O(n) | O(1) |
| 内存管理 | 简单 | 需要循环计算 |
| 动态扩容 | 支持 | 不支持 |

## 练习建议

1. **实现双向环形数组**：支持向前和向后遍历
2. **添加迭代器**：实现 `Iterator` 接口方便遍历
3. **处理边界情况**：如空数组、满数组的特殊处理
4. **扩展功能**：添加查找、更新等方法

通过这个详细的讲解和代码示例，你应该能够理解环形数组的概念和实现方式。环形数组是一种很实用的数据结构，特别适合需要循环利用固定大小空间的场景。