---
title: "CodeVisionAVR C 编译器数据类型"
date: "2014-03-21 00:00:00"
updated: "2014-03-21 00:00:00"
tags:
-  AVR
-  单片机
---


CodeVisionAVR C 编译器数据类型

[](/notename/ "archive 20140321")

| 类型        |关键字   |  大小 (位)  | 	范围|
|    | | : |:|
| 位型     | bit |   1    | 	0, 1|
| 字符型     | char |   8     | -128, 127|
| 无符号字符型     | unsigned char |   8  | 0, 255|
| 有符号字符型    | signed char |   8   | -128, 127 |
| 整型     | int |   `16`   | -32767, 32768|
| 无符号整型     | unsigned int |   `16`    | 0, 65536|
| 短整型        |   short int  |   16   | -32767, 32768 |
| 无符号短整型 |  unsigned short int    |  16  | 0, 65536 |
| 长整形 |  long int    |  32  |-2147483648, 2147483647|
| 无符号长整形 |  unsigned long int   |  32  |0, 4294967295|
| 浮点型 |  float  |  32|
| 双精度浮点型 |  double  | `32`|

avr 是小端模式

<h1>麻痹的! 傻逼 CodeVisionAVR 改什么语言, 把 const 和 flash 等价. 艹, 移植麻烦死</h1>
