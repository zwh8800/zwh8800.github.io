---
title: "ubuntu server 12.04 搭建 pptp 服务器"
date: "2013-11-12 00:00:00"
updated: "2013-11-12 00:00:00"
tags:
-  Linux
-  运维
-  pptp
---


前几天把pptp服务器搭上了, xen的vps就这点好处, 想怎么搞就怎么搞, 虽说贵了点. 在国内的话用pptp连外国网站快多了, 本身校园网烂得掉渣自己电脑更新系统基本上得一晚上(特别是国外源), psv更新更是…呵呵..呵呵..呵呵呵. 搭起来pptp之后反而会比之前快很多, 今天把psv系统更新到了3.0, 只需要15分钟. 真是让我这个更新狂魔泪流满面.

[](/notename/ "archive 20131112")

好吧, 进正题

基本上是综合了网上的做法, 不过网上的教程总有些漏, 有的没法加密, 有的登陆不上.

首先, 安装pptpd

```
sudo apt-get install pptpd
```

安装pptpd的同时会安装上ppp, 因为pptp在握手时使用ppp协议, 通讯时使用ppp协议(通过GRE协议在ip层上使用ppp).

之后分别对pptp和ppp进行配置.

###### 1. 打开文件/etc/pptpd.conf
这个文件为Sample Poptop configuration file(简单Poptop配置文件), 可以看见里面有6个TAG不过需要我们改动的只有最后的那一组
```
# TAG: localip
# TAG: remoteip
```

用来设置连接之后的本机地址和对端地址(指pptp服务器在pptp子网中的ip地址, 不要填写真正分配的因特网地址), 可以看见注释里有个(Recommended)的localip和remoteip, 是192.168的那个, 这两个地址没被用过的话, 直接取消注释用它就好了.

###### 2. 打开文件/etc/ppp/pptpd-options

这个文件为PPP options文件, 其实这个文件在刚刚的pptpd.conf中的option tag指定了, 可以去看看, 还可以指定其他的文件当做PPP options. 首先看一下参数name(就是name xxx那一行), 看一下他后面的名字是什么, 一会儿要用, 我这里是name pptpd. 然后是一系列ppp协议的加密选项, pap和chap是明文传送密码的, mschap对内容不加密, mschap-v2配合上mppe可以进行对密码和内容的同时加密. 所以加密部分配置文件基本不用动:

```
# Encryption
# Debian: on systems with a kernel built with the package
# kernel-patch-mppe >= 2.4.2 and using ppp >= 2.4.2, …
# {{{
refuse-pap
refuse-chap
refuse-mschap
# Require the peer to authenticate itself using MS-CHAPv2 [Microsoft
# Challenge Handshake Authentication Protocol, Version 2] authentication.

require-mschap-v2
# Require MPPE 128-bit encryption
# (note that MPPE requires the use of MSCHAP-V2 during authentication)
require-mppe-128
# }}}
```

但对于不想加密的同学, 想直接用chap登陆可以这样写:

```
require-chap
```
下面还有一行ms-dns设置成你喜欢的dns服务器吧我设置的是:

```
ms-dns 114.114.114.114
ms-dns 8.8.8.8
```

还有最后, 至关重要的, 在文件最末尾加两行不明觉利的

```
novj
novjccomp
nologfd
```
我还不懂这个是干嘛的, google没google到, 谁知道的可以告诉我.

打开文件/etc/ppp/chap-secrets这里存放chap加密方式的密码, 打开之后分四列, 第一列为用户名, 第二列填写刚刚第一步里, 那个name参数就行了, 我的是pptpd, 第三列是密码, 第四列是允许接入的ip, 允许所有ip填写*, 没列用Tab隔开就好了.
基本上ok了, 直接sudo /etc/init.d/pptpd restart吧

更新:

刚刚查了man pppd, 终于弄懂了那三行不明觉利的代码什么意思了

```
 novj   Disable Van Jacobson style TCP/IP header compression in both the
        transmit and the receive direction.
novjccomp
      Disable the connection-ID compression  option  in  Van  Jacobson
      style  TCP/IP  header  compression.  With this option, pppd will
      not omit the connection-ID byte  from  Van  Jacobson  compressed
      TCP/IP headers, nor ask the peer to do so.
```

先看说明, 貌似就是有个叫Van Jacobson的, 他的压缩协议让我总上不了网, 只好把它关啦. 总之就是禁用TCP/IP头压缩和connection-ID压缩, 否则我的win7一直在登陆的最后一步断开连接.

