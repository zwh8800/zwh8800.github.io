---
title: "记录一下开发过程的小插曲minimad"
date: "2014-01-27 00:00:00"
updated: "2014-01-27 00:00:00"
tags:
-  linux
-  minimad
---


libmad是一个开源mp3软件解码库(很久以前的东西了, 原来曾用过, 突然有想法把它放我mk808上试试), c+汇编写的, 本身对arm平台有汇编优化, 可是因为年代久远而且是针对armv4优化的, 优化了还不如不优化(优化了反而有杂音, 关了之后很好).

[](/notename/ "archive 20140127")

源代码目录里有一个示例用的minimad.c, 是基于这个库的一个简单的mp3播放器. 插上我的号称7.1channel的usb外置声卡(20块淘宝货), 和aplay连用, 就能听歌了!(geek就是爱折腾, 没办法)

首先, 从sourceforge.net上找到libmad并wget到mk808上, cd入目录, ./configure –disable-fpm关掉平台优化.

然后需要改一下Makefile, 打开Makefile查找-fforce-mem, 删掉它(这是gcc老版本才有的选项)

然后make(编译libmad), make minimad(编译minimad).

没什么错误的话就会在当前目录看见一个绿色的minimad了.

这个minimad说是播放器, 不如说是解码器…因为它只会从stdin读入mp3文件, 然后把解码后的pcm数据输出到stdout, 所以还得借助aplay来控制硬件播放.

这是命令:

```
sudo bash -c "minimad <1.mp3 | aplay -f cd"
```

这个是让1.mp3作为minimad的输入, 然后输出通过管道给aplay. -f是format, 使用CD格式的format, 也就是16 bit little endian, 44100, stereo, 正好是minimad的输出格式. 然后带上耳机, 就能听到美妙的歌声了.


