---
title: "ppp协议"
date: "2014-01-01 00:00:00"
updated: "2014-01-01 00:00:00"
tags:
-  网络协议
-  ppp协议
---


ppp协议详解

[](/notename/ "archive 20140101")

## 1.概述

ppp协议分为几个部分：LCP（链路控制协议）、NCP（网络控制协议）、认证协议（包括PAP协议和CHAP协议）、另外还有CCP（压缩控制协议）。

如下图所示：

![image_1bl05ebacvgpurr6fpo7neq79.png-186.3kB][1]

ppp是一个分层结构。在底层，它能使用同步媒介（如ISDNH或同步DDN专线），也能使用异步媒介（如基于Modem拨号的PSTN网络）。

在数据链路层，PPP在链路层建立方面提供了丰富的服务，这些服务以LCP协商选项的形式提供。

在上层，PPP通过NCPs提供对多种网络层协议的支持。PPP对于每一种网络层协议都有一种封装格式来区别它们的报文。

2.帧结构

基本的ppp帧如下：

![image_1bl05fa3u39duuo146u5bl194em.png-27.9kB][2]

标记用于标记一个ppp帧的开始和结束。

地址域和控制域为固定值（0xff，0x03）

协议的可选值如下：

```
协议代码          对应协议

0XC021            LCP协议

0XC023            PAP协议

0XC223            CHAP协议

0X8021            IPCP协议

0X0021            IP协议
```

3.建立连接
PPP协商过程分为几个阶段:Dead阶段,Establish阶段,Authenticate阶段,Network阶段和Termintate阶段,在不同的阶段进行不同协议的协商.只有前面的协商出现结果后,才能转到下一个阶段,进行下一个协议的协商.

![image_1bl05h1551vu94i197egm118ie13.png-196.8kB][3]

1. 当物理层不可用时,PPP链路处于dead阶段,链路必须从这个阶段开始和结束.当物理层可用时,PPP在建立链路之前首先进行LCP协商,协商内容包括工作方式是SP还是MP,验证方式和最大传输单元等.
1. LCP协商过后就进入Establish阶段,此时LCP状态为Opened,表示链路已经建立.
1. 如果培植了验证(远端验证本地或者本地验证远端)就进入Authenticate阶段,开始CHAP或PAP验证.
1. 如果验证失败进入Terminate阶段,拆除链路,LCP状态转为Down;如果验证成功就进入Network协商阶段(NCP),此时LCP状态仍为Opened,而IPCP状态从Initial转到Request.
1. NCP协商支持IPCP协商,IPCP协商主要包括双方的IP地址.通过NCP协商来选择和配置一个网络层协议.当选中的网络层协议配置成功后,该网络层协议就可以通过这条链路发送报文了.
1. PPP链路将一直保持通信,直至有明确的LCP或NCP帧关闭这条链路,或发生了某些外部事件.(例如,用户的干预).

在建立连接时需要用到LCP和NCP协议（IPCP）。

这些协议都会用到编码和ID字段（其实也可以这样分，地址、协议、控制三个字段属于ppp协议，后面的属于LCP或NCP或IP自己的协议）

编码字段的含义如下：

```
编码值	        对应含义

1             配置请求（Req）

2             接受配置（Ack）

3             配置请求接受，其他拒绝（Nak）

4             配置请求不认识或不被接受（Rej）

5             终止链接

6             终止确认
```

传输IP报文时，没有编码和ID字段，在协议字段之后直接就是IP报文。

4.验证

PAP验证，没啥好说的，客户端向服务器发送明文用户名和密码，服务器发回Acknowledge或Not Acknowledge

![image_1bl05jtp3qs1148f13051c0d18491g.png-187.3kB][4]

CHAP验证，比PAP验证安全，不明文发送密码。具体流程是这样：

1. 服务器向客户端发送一个随机生成的质询字符串（challenge string）和自己的主机名。
2. 客户端用自己的密码作为秘钥，通过单向加密算法（HASH）对服务器发来的质询字符串进行加密，之后将自己的用户名（明文）和加密后的质询字符串发送到服务器。
3. 服务器通过收到的用户名查询该用户的密码，用这个密码作为秘钥，也对刚刚的质询字符串进行单向加密，如果和用户发来的加密质询字符串一致的话，返回ACK，否则返回NAK。

![image_1bl05kjrq19ln1tdg9fb1k4h159a1t.png-205.7kB][5]

更明了的图如下：

![image_1bl05krd67doh1ujmh5kkga72a.png-131.7kB][6]

  [1]: http://static.zybuluo.com/zwh8800/a6hlyfbtpz4boecszdsyxzx3/image_1bl05ebacvgpurr6fpo7neq79.png
  [2]: http://static.zybuluo.com/zwh8800/r3biqwsowcpafr5ecs8neoeq/image_1bl05fa3u39duuo146u5bl194em.png
  [3]: http://static.zybuluo.com/zwh8800/7wzboy6euy4kf8va6pprg1u1/image_1bl05h1551vu94i197egm118ie13.png
  [4]: http://static.zybuluo.com/zwh8800/gwucrscztqpdjg9s762gdu14/image_1bl05jtp3qs1148f13051c0d18491g.png
  [5]: http://static.zybuluo.com/zwh8800/xnl0u041txsy909p91bwigvd/image_1bl05kjrq19ln1tdg9fb1k4h159a1t.png
  [6]: http://static.zybuluo.com/zwh8800/3a6w8fs79dilcdzuberagmpt/image_1bl05krd67doh1ujmh5kkga72a.png
