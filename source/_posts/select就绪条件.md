---
title: "select就绪条件"
date: "2014-01-10 00:00:00"
updated: "2014-01-10 00:00:00"
tags:
-  unix
-  网络编程
-  系统编程
---


select函数当被检测的文件描述符可读或可写或异常时返回. 可是究竟什么可以称作可读什么叫可写什么叫异常? 到达EOF算是哪一种? 

[](/notename/ "archive 20140110")

unix网络编程中给出了详细解释:

![image_1bl0e2qg7f8r1he3n4p1lh510ec9.png-406.5kB][1]

![image_1bl0e35vmqrg1oie1bohovt16qdm.png-158.1kB][2]

简言之, 描述符可读就是以下情况:

- **有数据传过来**
- **对端关闭连接(到达EOF)**
- **监听套接字收到连接请求**
- **发生套接字错误**

描述符可写是以下情况

- **缓冲区空闲可写**
- **写半部关闭**
- **connect建立连接完成**
- **发生套接字错误**

描述符异常只有一种情况: **有带外数据到达**.

表格6.7更加清晰

  [1]: http://static.zybuluo.com/zwh8800/xvnf7dr7n0o9sykpcmglpgnp/image_1bl0e2qg7f8r1he3n4p1lh510ec9.png
  [2]: http://static.zybuluo.com/zwh8800/ym29f11vmo4t5l8dpc6eepda/image_1bl0e35vmqrg1oie1bohovt16qdm.png
