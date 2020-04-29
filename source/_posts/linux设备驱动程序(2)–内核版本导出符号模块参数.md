---
title: "linux设备驱动程序(2) – 内核版本 导出符号 模块参数"
date: "2014-01-28 00:00:00"
updated: "2014-01-28 00:00:00"
tags:
-  linux
-  驱动开发
---


关于 内核版本 导出符号 模块参数 的内容

[](/notename/ "archive 20140128")

### 1.内核版本

有时模块会针对多个不同版本的内核进行编译, 这时就应该用到预处理命令来实现条件编译. 主要通过测试`<linux/version.h>`中的宏来完成.

UTS_RELEASE: 内核版本的字符串, 如”2.6.10″

LINUX_VERSION_CODE: 内核版本的二进制表示, 每个版本号对应一个字节, 如2.6.10版的LINUX_VERSION_CODE为0x02060a

KERNEL_VERSION(major, minor, release): 这个宏将major, minor和release扩展成LINUX_VERSION_CODE的形式, 可以直观的进行测试

### 2.导出模块符号

有时, 模块可能需要被其他模块来调用, 所以需要导出自己模块的符合供别人使用. Linux内核头文件提供了一个方便的方法来到处内核符号:

```
EXPORT_SYMBOL(name);		//导出name
EXPORT_SYMBOL_GPL(name);	//导出的符号只能被GPL代码使用
```

### 3.许可证

通过MODULE_LECENSE(license)宏来声明当前模块的许可证, license是一个字符串, 支持的许可证如下:

“GPL”, “GPL v2”, “GPL and additional rights”, “Dual BSD/GPL”, “Dual MPL/GPL”, “Proprietary”(专用)

如果不声明, 默认为”Proprietary”

### 4.模块参数
linux内核模块可以声明全局变量为模块参数, 从而可以在加载时赋值.

```
static char* whom = "nobody";
static int howmany = 1;
module_param(howmany, int, S_IRUGO);
module_param(whom, charp, S_IRUGO);
```

通过module_param宏可以导出whom和howmany两个模块参数. 这个宏在<linux/moduleparam.h>中定义.
当插入模块时, 使用以下指令来设置模块参数:

```
insmod hello howmany=10 whom="zzZ"
```

对于module_param宏的第二个参数, 可以取以下值:

    bool
    invbool
        布尔值, 应关联int型, invbool会翻转布尔值.
    charp
        字符指针, 也就是字符串
    int, long, short, uint, ulong, ushort

还有一个姐妹宏module_param_array(name, type, num, perm);来设置数组参数.

再来说说第三个参数perm, 这个是成员访问许可, 在`<linux/stat.h>`中定义可选值. 这个用来控制谁能访问sysfs中对模块参数的表述. 如果perm为0, 则在sysfs中没有对用的入口项(entry), 否则会在/sys/module中出现. 如果使用S_IRUGO, 任何人都可读取, 但不能修改. S_IRUGO | S_IWUSR允许root修改.

