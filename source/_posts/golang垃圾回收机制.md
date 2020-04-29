---
title: "golang 垃圾回收机制"
date: "2016-06-22 07:22:16"
updated: "2019-07-20 09:14:32"
tags:
-  golang
-  GC
-  垃圾回收
---


用任何带 GC 的语言最后都要直面 GC 问题。在以前学习 C# 的时候就被迫读了一大堆 .NET Garbage Collection 的文档。最近也学习了一番 golang 的垃圾回收机制，在这里记录一下。

[](/notename/ "gc in golang")

## 常见 GC 算法

趁着这个机会我总结了一下常见的 GC 算法。分别是：**引用计数法**、**Mark-Sweep法**、**三色标记法**、**分代收集法**。

### 1. 引用计数法

原理是在每个对象内部维护一个整数值，叫做这个对象的**引用计数**，当对象被引用时引用计数加一，当对象不被引用时引用计数减一。当引用计数为 0 时，自动销毁对象。

目前引用计数法主要用在 c++ 标准库的 std::shared_ptr 、微软的 COM 、Objective-C 和 PHP 中。

但是引用计数法有个缺陷就是不能解决循环引用的问题。循环引用是指对象 A 和对象 B 互相持有对方的引用。这样两个对象的引用计数都不是 0 ，因此永远不能被收集。

另外的缺陷是，每次对象的赋值都要将引用计数加一，增加了消耗。

### 2. Mark-Sweep法（标记清除法）

这个算法分为两步，标记和清除。

- 标记：从程序的根节点开始， **递归地** 遍历所有对象，将能遍历到的对象打上标记。
- 清除：讲所有未标记的的对象当作垃圾销毁。

<center>
![Animation_of_the_Naive_Mark_and_Sweep_Garbage_Collector_Algorithm.gif-143.9kB][1]
<small>图片来自 https://en.wikipedia.org/wiki/Tracing_garbage_collection </small>
</center>

如图所示。

但是这个算法也有一个缺陷，就是人们常常说的 STW 问题（Stop The World）。因为算法在标记时必须暂停整个程序，否则其他线程的代码可能会改变对象状态，从而可能把不应该回收的对象当做垃圾收集掉。

当程序中的对象逐渐增多时，递归遍历整个对象树会消耗很多的时间，在大型程序中这个时间可能会是毫秒级别的。让所有的用户等待几百毫秒的 GC 时间这是不能容忍的。

golang 1.5以前使用的这个算法。

### 3. 三色标记法

三色标记法是传统 Mark-Sweep 的一个改进，它是一个并发的 GC 算法。

原理如下，

1. 首先创建三个集合：白、灰、黑。
2. 将所有对象放入白色集合中。
3. 然后从根节点开始遍历所有对象（注意这里**并不递归遍历**），把遍历到的对象从白色集合放入灰色集合。
4. 之后遍历灰色集合，将灰色对象引用的对象从白色集合放入灰色集合，之后将此灰色对象放入黑色集合
5. 重复 4 直到灰色中无任何对象
6. 通过write-barrier检测对象有变化，重复以上操作
7. 收集所有白色对象（垃圾）

<center>
![Animation_of_tri-color_garbage_collection.gif-94kB][2]
<small>图片来自 https://en.wikipedia.org/wiki/Tracing_garbage_collection </small>
</center>

过程如上图所示。

这个算法可以实现 "on-the-fly"，也就是在程序执行的同时进行收集，并不需要暂停整个程序。

但是也会有一个缺陷，可能程序中的垃圾产生的速度会大于垃圾收集的速度，这样会导致程序中的垃圾越来越多无法被收集掉。

使用这种算法的是 Go 1.5、Go 1.6。

### 4. 分代收集

分代收集也是传统 Mark-Sweep 的一个改进。这个算法是基于一个经验：绝大多数对象的生命周期都很短。所以按照对象的生命周期长短来进行分代。

一般 GC 都会分三代，在 java 中称之为新生代（Young Generation）、年老代（Tenured Generation）和永久代（Permanent Generation）；在 .NET 中称之为第 0 代、第 1 代和第2代。

原理如下：

- 新对象放入第 0 代
- 当内存用量超过一个较小的阈值时，触发 0 代收集
- 第 0 代幸存的对象（未被收集）放入第 1 代
- 只有当内存用量超过一个较高的阈值时，才会触发 1 代收集
- 2 代同理

因为 0 代中的对象十分少，所以每次收集时遍历都会非常快（比 1 代收集快几个数量级）。只有内存消耗过于大的时候才会触发较慢的 1 代和 2 代收集。

因此，分代收集是目前比较好的垃圾回收方式。使用的语言（平台）有 jvm、.NET 。

## golang 的 GC

go 语言在 1.3 以前，使用的是比较蠢的传统 Mark-Sweep 算法。

1.3 版本进行了一下改进，把 Sweep 改为了并行操作。

1.5 版本进行了较大改进，使用了三色标记算法。go 1.5 在源码中的解释是“非分代的、非移动的、并发的、三色的标记清除垃圾收集器”

go 除了标准的三色收集以外，还有一个辅助回收功能，防止垃圾产生过快手机不过来的情况。这部分代码在 [`runtime.gcAssistAlloc`](https://golang.org/src/runtime/mgcmark.go#L316) 中。

但是 golang 并没有分代收集，所以对于巨量的小对象还是很苦手的，会导致整个 mark 过程十分长，在某些极端情况下，甚至会导致 GC 线程占据 50% 以上的 CPU。

因此，当程序由于高并发等原因造成大量小对象的gc问题时，最好可以使用 [`sync.Pool`](https://golang.org/pkg/sync/#Pool) 等对象池技术，避免大量小对象加大 GC 压力。

  [1]: http://static.zybuluo.com/zwh8800/m4mhohyyesdbb15repsbu12t/Animation_of_the_Naive_Mark_and_Sweep_Garbage_Collector_Algorithm.gif
  [2]: http://static.zybuluo.com/zwh8800/h1yckkjd1az3q64y55z8bvbx/Animation_of_tri-color_garbage_collection.gif
