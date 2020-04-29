---
title: "arm-linux 汇编(1) – Helloworld"
date: "2014-01-15 00:00:00"
updated: "2014-01-15 00:00:00"
tags:
-  arm-linux
-  汇编
-  系统编程
---


linux下一般使用c语言编程，但其实也可以直接使用汇编语言。谈谈在 Linux 下使用汇编编写应用程序。

[](/notename/ "archive 20140115")

linux下一般使用c语言编程，但其实也可以直接使用汇编语言。

linux下的汇编工具也是由GNU提供的，叫做as（汇编器）和ld（连接器，c语言也要用它）

在写第一个汇编程序之前我们先看看工具的使用：

假如我们的汇编源码文件叫做hello.s，我们需要先将其汇编成hello.o，再将hello.o连接成hello

```bash
as hello.s -o hello.o
ld hello.o -o hello
```

简单吧，和上文说的一样，需要两步。

然后让我们先写第一个小程序，功能很简单，就是退出程序，并返回状态码1：

```asm
.section .text		@伪指令.section, 说明下面代码在text段
.global _start			@伪指令.global或.globl, 向外部暴露出_start符号
_start:				
	mov r0, #1		@将立即数1存入寄存器r0, 作为_exit系统调用的参数
	mov r7, #1		@将系统调用号存入r7
	swi #0			@软中断, 陷入内核来调用系统调用
```

在arm-linux汇编中 **`.` 开头的表示伪指令**, **`@` 表示单行注释**. 代码的注释里已经把每一句的功能写的很清楚了, 现在说一些没说清楚的.

在汇编中 `_start` 是一个**程序的开始**(貌似x86和arm都是从_start开始执行)所以不能像c语言中写main函数了, 要写_start标号.

然后将我们要调用的系统调用的参数存入寄存器, 因为arm体系架构中, 寄存器的数量相当多, 所以当参数的个数不多时, **一般使用寄存器来传递**. 我们要调用的_exit只有一个参数, 就是程序的返回值, 所以我们把1存入r0中.

第二步, 我们必须告知内核我们要调用哪个系统调用, **每个系统调用都有一个系统调用号**, 在arm-linux中, 系统调用号保存在/usr/include/arm-linux-gnueabifh/asm/unistd.h中可以看到有很多__NR开头的宏, 后面写着系统调用的名字, 然后就是我们要的系统调用号. 经过寻找, 我们发现_exit调用的调用号是1.所以我们把1存入`r7`中.

最后一步, **swi指令发起软中断(中断号为0)**, 使程序陷入内核, 然后内核进行系统调用.

这里要说一些arm-linux系统调用的历史, 在cortex之前吧(大概是), arm-linux系统调用的方式一直是这样, swi #(0x900000 + 系统调用号), 既在中断号中传递系统调用号(0x900000是一个magic number), 这种方式现在称作oabi(old ABI), 现在的方式就是在r7中传递系统调用号, 称作eabi. 现在的系统大多都是采用eabi的方式.

好的, 现在汇编, 连接程序, 然后运行. 发现程序结束了, 然后使用*echo $?*可以查看刚刚结束的程序的返回值, 可以发现返回值为1. 说明程序没有问题.

现在来看第二个例子, helloworld.

```asm
.section .data		@data段
hello:
	.ascii "hello world\n"	@ascii伪指令,以ascii码格式来存储
	.equ len, . - hello	@equ伪指令,令len=.-hello .代表当前地址
				@.-hello就代表hello字符串的长度
 
.section .text
.global _start
 
_start:
	mov r0, #1		@stdout
	ldr r1, =hello		@将hello的地址保存在r1
	mov r2, #len		@将长度保存在r2
	mov r7, #4		@系统调用号
	swi #0			@发起系统调用
 
exit:
	mov r0, #0
	mov r7, #1
	swi #0
```

这个的注释也比较清楚就不说明了, 汇编连接执行后会在屏幕上看见helloworld的大字.

EOF

