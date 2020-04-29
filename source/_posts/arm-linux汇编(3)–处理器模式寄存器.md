---
title: "arm-linux 汇编(3) – 处理器模式 寄存器"
date: "2014-01-18 00:00:00"
updated: "2014-01-18 00:00:00"
tags:
-  系统编程
-  arm-linux
-  汇编
---


上一篇中给出了在arm体系架构中[用户态]的寄存器, 共有16个通用寄存器r0-r15和一个通用程序状态寄存器(cpsr).

[](/notename/ "archive 20140118")

上一篇中给出了在arm体系架构中[用户态]的寄存器, 共有16个通用寄存器r0-r15和一个通用程序状态寄存器(cpsr).

###### 1.这次接着说通用程序状态寄存器

先看图:

![image_1bl0ld0ga1lkn16khh2rvg1j3a9.png-116.9kB][1]

cpsr分为4个域, 每个域8位, 分别是**标志域**, **状态域**, **扩展域**和**控制域**.(图上画的有点错误, 扩展域画大了, mode和I,F,T都是控制域的)

其中标志域表示运算结果的标志. 控制域中, I为1表示屏蔽掉普通中断, F为1表示屏蔽掉快速中断, T为1表示当前为thumb模式.

Mode域表示了当前CPU的处理器模式.

###### 2.处理器模式

不算上最新安全扩展和虚拟化扩展新加上的模式的话, arm架构共有7个处理器模式:

<table>
<tbody>
<tr>
<td>User mode</td>
<td>FIQ mode</td>
<td>IRQ mode</td>
<td>Supervisor (svc) mode</td>
</tr>
<tr>
<td>Abort mode</td>
<td>Undefined mode</td>
<td>System mode</td>
</tr>
</tbody>
</table>

其中User mode为非特权模式以外, 剩下6个都为特权模式.

当快速中断产生时进入FIQ模式.

当中断产生时进入IRQ模式.

当系统reset或swi(又称svc, 软中断)命令执行时进入svc模式.

当访问内存失败时(分为prefetch abort和data abort)进入Abort模式.

当执行的指令未定义时进入Undefined模式.

是否为特权模式决定了那些寄存器是可用的, 以及cpsr本身的访问权限. 对于特权模式, 对cpsr有完全的访问权限(MSR和MRS指令), 对以非特权模式, 只能读控制域但可读写条件标志域.

###### 3.寄存器

arm架构共有37个寄存器但在不同时刻有20个寄存器是隐藏的(图中阴影部分), 只有当寄存器处于某种特定模式时, 才能访问特定的寄存器(如在abort模式才能访问r13_abt), 另外, 在不同的模式访问cpsr都是同一个, 而spsr_mode用来保存进入特权模式之前的cpsr以便保存异常之前的现场.

![image_1bl0lfomu104c13dd161112p81p89m.png-178.8kB][2]

<table class="wikitable">
<caption>Registers across CPU modes</caption>
<tbody>
<tr>
<th>usr</th>
<th>sys</th>
<th>svc</th>
<th>abt</th>
<th>und</th>
<th>irq</th>
<th>fiq</th>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R0</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R1</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R2</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R3</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R4</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R5</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R6</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R7</td>
</tr>
<tr align="center">
<td colspan="6">R8</td>
<td>R8_fiq</td>
</tr>
<tr align="center">
<td colspan="6">R9</td>
<td>R9_fiq</td>
</tr>
<tr align="center">
<td colspan="6">R10</td>
<td>R10_fiq</td>
</tr>
<tr align="center">
<td colspan="6">R11</td>
<td>R11_fiq</td>
</tr>
<tr align="center">
<td colspan="6">R12</td>
<td>R12_fiq</td>
</tr>
<tr align="center">
<td colspan="2">R13</td>
<td>R13_svc</td>
<td>R13_abt</td>
<td>R13_und</td>
<td>R13_irq</td>
<td>R13_fiq</td>
</tr>
<tr align="center">
<td colspan="2">R14</td>
<td>R14_svc</td>
<td>R14_abt</td>
<td>R14_und</td>
<td>R14_irq</td>
<td>R14_fiq</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">R15</td>
</tr>
<tr>
<td style="text-align: center;" colspan="7">CPSR</td>
</tr>
<tr align="center">
<td colspan="2"></td>
<td>SPSR_svc</td>
<td>SPSR_abt</td>
<td>SPSR_und</td>
<td>SPSR_irq</td>
<td>SPSR_fiq</td>
</tr>
</tbody>
</table>

从wiki上copy的一个寄存器的表格

其实这些东西对于写用户程序的话都是透明的了, 但是有利于理解arm体系架构和看懂一些系统级的代码.

下面想要学一学eabi相关的东西了除了指令集就是这个最重要了.

  [1]: /images/28991ebc5db7944a343f3ed4838bf94b.png
  [2]: /images/c60cfa84042bad9d13e432b0b7436873.png
