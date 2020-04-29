---
title: "arm-linux 汇编 (4) – 函数调用规则"
date: "2014-03-12 00:00:00"
updated: "2014-03-12 00:00:00"
tags:
-  arm-linux
-  汇编
-  asm
---


arm-linux 汇编 (4) – 函数调用规则

[](/notename/ "archive 20140312")

本篇主要考虑整数 (更精确点是 32 位整数) 作为参数和函数返回值时的传递规则.

网上很多资料都在说 arm 汇编中如果参数小于四个 (整数) 的话, 使用 r0, r1, r2, r3 来传递. 当大于 4 个时使用栈来传递. 但是究竟放到 sp 的上面还是下面, 顺序如何. 这次就来试一试到底是怎么样的.

```
int a7(int a, int b, int c, int d, int e, int f, int g)
{
	return 100 + a + b + c + d + e + f + g;
}
 
int test()
{
	a7(1, 2, 3, 4, 5, 6, 7);
}
```

编译以上代码 arm-linux-gnueabi-gcc -c arg.c 生成 arg.o 文件. 然后使用 arm-linux-gnueabi-objdump -d 来反编译. o 文件.

```
000001b4 <a7>:
 1b4:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
 1b8:	e28db000 	add	fp, sp, #0
 1bc:	e24dd014 	sub	sp, sp, #20
 1c0:	e50b0008 	str	r0, [fp, #-8]
 1c4:	e50b100c 	str	r1, [fp, #-12]
 1c8:	e50b2010 	str	r2, [fp, #-16]
 1cc:	e50b3014 	str	r3, [fp, #-20]
 1d0:	e51b3008 	ldr	r3, [fp, #-8]
 1d4:	e2832064 	add	r2, r3, #100	; 0x64
 1d8:	e51b300c 	ldr	r3, [fp, #-12]
 1dc:	e0822003 	add	r2, r2, r3
 1e0:	e51b3010 	ldr	r3, [fp, #-16]
 1e4:	e0822003 	add	r2, r2, r3
 1e8:	e51b3014 	ldr	r3, [fp, #-20]
 1ec:	e0822003 	add	r2, r2, r3
 1f0:	e59b3004 	ldr	r3, [fp, #4]
 1f4:	e0822003 	add	r2, r2, r3
 1f8:	e59b3008 	ldr	r3, [fp, #8]
 1fc:	e0822003 	add	r2, r2, r3
 200:	e59b300c 	ldr	r3, [fp, #12]
 204:	e0823003 	add	r3, r2, r3
 208:	e1a00003 	mov	r0, r3
 20c:	e28bd000 	add	sp, fp, #0
 210:	e8bd0800 	ldmfd	sp!, {fp}
 214:	e12fff1e 	bx	lr
 
00000218 <test>:
 218:	e92d4800 	push	{fp, lr}
 21c:	e28db004 	add	fp, sp, #4
 220:	e24dd010 	sub	sp, sp, #16
 224:	e3a03005 	mov	r3, #5
 228:	e58d3000 	str	r3, [sp]
 22c:	e3a03006 	mov	r3, #6
 230:	e58d3004 	str	r3, [sp, #4]
 234:	e3a03007 	mov	r3, #7
 238:	e58d3008 	str	r3, [sp, #8]
 23c:	e3a00001 	mov	r0, #1
 240:	e3a01002 	mov	r1, #2
 244:	e3a02003 	mov	r2, #3
 248:	e3a03004 	mov	r3, #4
 24c:	ebfffffe 	bl	1b4 <a7>
 250:	e1a00003 	mov	r0, r3
 254:	e24bd004 	sub	sp, fp, #4
 258:	e8bd4800 	pop	{fp, lr}
 25c:	e12fff1e 	bx	lr
```

得到以上文件

下面来分析一下.

在 test 函数中. 我们先不管 fp 寄存器, 只看 sp 寄存器. sp 寄存器一上来就向下移了 16 个字节 (4 个 int). 我们知道, arm 的栈是 FD 的 (Full decrease, 既 sp 指向栈顶元素, 栈向低地址增长). 所以就是说明新开辟了 4 个 int 的空间.

然后 224 到 238 这段. 是将 5, 6, 7 这三个参数存到 sp 和 sp 上面. 使用了 3 个 int 的空间.

之后, 又将 1, 2, 3, 4 这四个参数分别保存到 r0, r1, r2, r3 中.

最后, bl 调用函数.

由上面分析可知, 当我们调用一个函数前, 应当:

前四个参数使用寄存器传递
后面的参数使用栈传递
使用栈传递时, 从后向前依次压入参数. 压栈完成后, sp 指向最后一个参数
sp 是 8 字节对齐的 [我猜想的]
刚刚的分析中, 我们只需要额外传递 3 个参数, 可是我们在栈上分配了 16 个字节, 另外我尝试传递 5 个参数时分配了 8 个字节 (也是多一个) 所以我猜想 sp 可能需要 8 字节对齐.

然后对于被调用的函数来说, 它知道的信息就是: “我的前四个参数在寄存器中, 我的 sp 指针指向最后一个参数, 依次向上可以得到全部参数.”

然后对于被调用函数来说, 它会将 fp 指向参数的后一个字. 让 sp 指向栈顶. fp 和 sp 之间保存断点信息 (保护上一函数的寄存器) 和自己的局部变量.

[EOF]


