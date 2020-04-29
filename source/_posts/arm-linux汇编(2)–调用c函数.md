---
title: "arm-linux 汇编(2) – 调用c函数"
date: "2014-01-16 00:00:00"
updated: "2014-01-16 00:00:00"
tags:
-  arm-linux
-  汇编
-  系统编程
---


上一篇学习了armlinux汇编的helloworld，用到了arm汇编的一些基本指令，如mov、ldr、swi，需要详细的arm体系架构的信息可以去arm官网下载arm_architecture_reference_manual.pdf文件，上面有很详细的信息。本文接着上次，继续讲一下如何用汇编调用c函数。

[](/notename/ "archive 20140116")

另外，如果觉得那个手册太冗长，或者是英文苦手的话，可以在本站下载这个短小精悍的reference card（中文版哦）：

https://lengzzz.com/download/QRC0001_UAL.pdf

现在进入正题：

上一篇中，重点讲述了在arm-linux下的**系统调用**的方法，但是更多时候，我们可能会与一些c库进行交互，今天学习了**汇编调用c库函数**的方法。

先上例子：

```asm
.section .rodata
fmt:
	.asciz "2 * 4 = %d\n"	@.asciz以NULL结尾的字符串
 
.section .text
.global _start
 
_start:
	mov r2, #2
	mov r3, #4
	mul r1, r2, r3		@乘法指令, r1=r2*r3
	ldr r0, =fmt
	bl printf		@bl为函数调用, 跳转到printf并将当前pc保存到lr寄存器
exit:
	mov r0, #1
	mov r7, #1
	swi #0
```

例子很简单, 功能就是计算2*4并输出2 * 4 = 8. 先使用mul指令计算出2*4的值放在r1寄存器中, 然后将printf的格式串fmt放到r0中, 然后调用printf函数.

要汇编这个程序不能用昨天简单的指令了. 因为, printf是libc库中的函数, 必须要和c库进行连接:

```bash
as mul.s -o mul.o
ld -dynamic-linker /lib/ld-linux-armhf.so.3 mul.o -o mul -lc
```

相比较上一篇中的连接指令, 多了两条, 一个是**-dynamic-linker /lib/ld-linux-armhf.so.3`**另一个是**-lc**

第一个是指令在man pages中的介绍是:

> –dynamic-linker=file
> Set the name of the dynamic linker.  This is only meaningful when
> generating dynamically linked ELF executables.  The default dynamic
> linker is normally correct; don’t use this unless you know what you
> are doing.

是用来设置**动态链接器**的, 在不同的设备上ld-linux-armhf.so.3的名字可能都不一样, 但一般都在lib文件夹中并且以ld开头. 如果没有这条指令的话, 运行程序的时候会提示file not found

第二条是-lc, 和gcc的用法一样, **表示连接libc库**. 如果不加这个指令的话连接时会提示undefined “printf”.

现在介绍一下bl指令. bl是*branch*(分支) *link*(连接)的缩写(和x86架构的call ret相比意思太含糊了), branch的意思就是**跳转(分支)到其他地方执行**, link的意思是**将当前的pc(Program Counter程序计数器, 保存着当前程序运行到哪里了)寄存器保存到lr(Link Register连接寄存器)**, 以便调用函数之后函数可以返回回来. 当printf函数运行结束时, 会调用**mov pc, lr**来返回.

再来说一说arm的寄存器吧. 在**用户态**, arm的寄存器一共有这几个:

<table>
<tbody>
<tr>
<td>r0</td>
<td>r1</td>
<td>r2</td>
<td>r3</td>
<td>r4</td>
<td>r5</td>
<td>r6</td>
<td>r7</td>
</tr>
<tr>
<td>r8</td>
<td>r9</td>
<td>r10</td>
<td>r11</td>
<td>r12</td>
<td>r13(sp)</td>
<td>r14(lr)</td>
<td>r15(pc)</td>
</tr>
<tr>
<td>CPSR</td>
</tr>
</tbody>
</table>

算是比较多的. 其中sp表示堆栈指针(Stack Pointer), lr代表连接寄存器(Link Register), pc表示程序计数器(Program Counter).

具体函数调用时参数传递和返回值用那些寄存器在eabi中都有介绍. 之后将会进行学习.


