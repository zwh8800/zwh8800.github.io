---
title: "基本上找到问题了 Connection refused"
date: "2014-01-22 00:00:00"
updated: "2014-01-22 00:00:00"
tags:
-  Linux
-  网络编程
-  错题本
---


对udp套接字执行read时一直报错: connection refused. 关键是udp还会报connection就太不正常了, udp可是无连接的.

[](/notename/ "archive 20140122")

对**udp套接字**执行read时一直报错: **connection** refused. 关键是udp还会报connection就太不正常了, udp可是无连接的.

刚刚查到了这篇博文: [UDP怎么会返回Connection refused](https://blog.csdn.net/dog250/article/details/9569855)  原来是因为对端传来了一个ICMP包(传来一个port unreachable), 结果某些内核会把这个包为**已连接**(执行过connect函数)的udp套接字保存起来, 并在下一次操作时(读取, 写入)返回一个connection refused错误.

但是到底为什么会有一个ICMP包, 刚刚做了些实验, 原因是 一台客户机和stun服务器建立udp连接之后, nat路由器会记录下这条路线[既保存下这个四元组], 如果有非stun服务器的主机向客户机端口发来udp包, 会返回一个ICMP错误. (想想你这路由器真够没事找事呢, 可能是为了安全性考虑?)

现在的想法是, 客户机另开一个端口和另一台客户进行p2p通讯, 不再用和stun通讯的端口, 应该可以解决问题.

具体做法是在向stun服务器登陆时, 报出另一条线路的端口.

