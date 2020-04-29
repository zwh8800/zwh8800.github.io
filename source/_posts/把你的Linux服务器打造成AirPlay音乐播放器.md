---
title: "把你的 Linux 服务器打造成 AirPlay 音乐播放器"
date: "2016-11-18 07:57:43"
updated: "2017-01-02 14:31:29"
tags:
-  AirPlay
-  
-  linux
---


AirPlay 是苹果设备上最方便的播放技术，可以很方便的把音频、视频串流到你的电视或音箱上。现在大部分智能电视都支持 AirPlay 投屏了，但是支持 AirPlay 的音响设备还是比较少见（and 贵）。那么，有没有比较廉价的搭建 AirPlay 音乐播放器的方式呢？那就是今天的主角 shairport-sync。

[](/notename/ "make your linux server a airplay player")

shairport 是一个音频 AirPlay receiver 服务器。但是不幸的是 shairport 的作者两年前停止更新了，就有了另一个开发者 fork 了 shairport 做出了 shairport-sync。

shairport-sync 基于 shairport，在此基础上还改进了音视频的同步的问题，这样使用 shairport-sync 播放视频时不会出现影音不同步的问题了。

## 在 ubuntu 16.04 上安装 shairport-sync

ubuntu 16.04 的软件仓库里已经集成了 shairport-sync，这样只需要执行 `apt install` 就可以安装了。

但是 shairport 还需要 avahi-daemon 这个服务，avahi-daemon 是开源的，它实现了苹果的 mDNS 协议（在苹果的设备上对应的服务是 Banjour）。shairport 需要在 avahi 上注册自己。

```bash
sudo apt install avahi-daemon
sudo apt install shairport-sync
```

## 配置 shairport-sync

shairport-sync 的配置非常简单，它的配置文件放在 `/etc/shairport-sync.conf` ，打开它之后会发现里面有很多配置项，我们只需要简单的配置下 name 就可以了，其他的选项不用动。

```
// General Settings
general =
{
    //	...
    name = "客厅的服务器";
    //	...
};

```

改完配置之后记得重启一下服务：

```bash
sudo systemctl restart shairport-sync.service
```

## 不出声音的故障

安装之后有可能会不出声音，这是因为 shairport 的用户不在 audio 组了，这样的话 shairport 没有音频设备的权限，执行下面语句可以解决。

```bash
sudo usermod -aG audio shairport-sync
```

## 最后来一张效果图

![IMG_1197.PNG-394.9kB][1]

  [1]: /images/1ee3cfdd2eb20f717381a3c95775dec8.PNG
