---
title: "做了个 golang 安装包的镜像"
date: "2016-05-25 07:57:16"
updated: "2016-05-25 08:07:30"
tags:
-  闲扯
-  golang
---


鉴于国情，国内下载 golang 安装包还是挺蛋疼的，就算使用代理速度也比较感人。虽然现在 docker 镜像是个比较好的选择，但还是有很多场景需要原始的 golang 环境的。所以抽空做了个 mirror ，定时拉取 golang 官网的安装包到我的服务器上。

[](/notename/ "golang china download mirror")

地址在这里：https://lengzzz.com/download/golang/

包含了 golang 1.5 之后的所有版本，所有平台的安装包和源码包都放在里面，自行 `control + f` 搜一下吧。新版本的 golang release 之后，应该在一两天内可以拉取过来。

欢迎使用。

![屏幕快照 2016-05-25 下午4.06.56.png-311.7kB][1]

  [1]: /images/1f5556f01de37fc838e02d1c4d7a6682.png
