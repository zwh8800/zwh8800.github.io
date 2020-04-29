---
title: "linux下整数尺寸"
date: "2014-01-14 00:00:00"
updated: "2014-01-14 00:00:00"
tags:
-  系统编程
-  linux
-  体系架构
---


linux 分为 ILP32 和 LP64 两种

[](/notename/ "archive 20140114")

ILP32体系：int = long = pointer = 32
LP64体系：long = pointer = 64

在我的电脑上（64位ubuntu，Xeon E3处理器）是LP64体系

结果如下:

![image_1bl0ehvba19urh6r19i8df11mjc9.png-45.3kB][1]

  [1]: /images/c078e202803909b2cf459f62c0d5485c.png
