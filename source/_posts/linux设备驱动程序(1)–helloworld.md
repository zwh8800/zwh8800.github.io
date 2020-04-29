---
title: "linux设备驱动程序(1) – helloworld"
date: "2014-01-26 00:00:00"
updated: "2014-01-26 00:00:00"
tags:
-  linux
-  驱动开发
---


经过这几天痛苦debug，ztun终于是勉强能用了。（bug应该还不少，但不想改了呀wwww

[](/notename/ "archive 20140126")

然后，昨天看完了《linux系统编程》今天开始正式学习《linux设备驱动程序》，自然先从helloworld开始。

对于驱动开发，首先你得有内核源代码树。如果你是ubuntu之类的发行版，一般软件仓库里会有linux-kernel-header包，下载一个适合自己的版本就可以了，它会安装在/scr中，但一般使用/lib/module/`uname -r`/build这个路径（这是个连接，连接到/src中）

如果你是使用开发板做嵌入式，那么就麻烦一些，因为没有人给你做好内核树让你用，你必须自己从kernel.org或者你的零售商那里获取合适版本的内核源代码。然后cd到源代码目录执行以下操作：

```bash
make oldconfig
make prepare
make scripts #不一定需要, 我这里就不用
```

如果是交叉编译还应该在make前加上ARCH=XXX CROSS_COMPILE=XXX，比如：

```bash
ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- make
```

好的，这样准备工作就完成了，可以写helloworld了：

```c
/* file: hello.c */
#include "linux/init.h"
#include "linux/module.h"
 
MODULE_LICENSE("Dual BSD/GPL");
 
static int hello_init(void)
{
	printk("Hello world\n");
	return 0;
}
 
static void hello_exit(void)
{
	printk("Goodbye\n");
}
 
module_init(hello_init);
module_exit(hello_exit);
```

而一向让人头疼的Makefile却很好写：

```Makefile
obj-m := hello.o
```

什么？你TM在逗我？只有一行？对，只有一行，但是命令行需要麻烦点：

```bash
make -C /lib/module/`uname -r`/build M=`pwd` modules
```

obj-m的意思是需要编译的模块，因为使用:=所以表示覆盖前面的值，所以只会编译hello.c而不会编译内核中的其他模块。命令行中/lib/module/`uname -r`/build是内核源代码树的路径，你可以改成你自己的。-C指令表示make执行时先chdir到内核源代码树，调用那里的Makefile，M=`pwd`代表模块代码在当前目录。

执行成功后会在当前目录下生成一个hello.ko文件，这就是刚编译好的内核模块了。执行

```bash
sudo insmod ./hello.ko
dmesg
sudo remod ./hello.ko
dmesg
```

可以在两次dmesg中看到Hello world和Goodbye。

但是每次都打那么长的命令行是不能接受的，特别是交叉编译时命令行更长。这个稍复杂点的Makefile可以解救你：

```Makefile
ifneq ($(KERNELRELEASE),)
	obj-m := hello.o
else
	KERNELDIR ?= /lib/modules/$(shell uname -r)/build
	PWD := $(shell pwd)
 
all:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules
 
clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean
 
endif
```

只需要在模块目录打一个make就可以编译。

下面分析一下这个Makefile。这个其实有点像递归，执行make时，KERNELRELEASE变量还没有被设置，所以执行else里的。首先吧KERNELDIR设置成内核源代码树路径。PWD变量设置成当前目录。然后执行\$(MAKE) -C \$(KERNELDIR) M=\$(PWD) modules。这句话被翻译成刚刚的那句命令行。于是又执行一次make（递归来了。。。）递归时会先读取内核源代码树里的Makefile，里面设置了KERNELRELEASE变量所以还是刚刚的那句代码obj-m := hello.o。于是，完成编译。

书上没写清楚的东西都说清楚了，希望对那些像我一样在看了书之后搞不出helloworld的人有帮助吧。
