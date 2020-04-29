---
title: "小蚁摄像头实时同步视频到群晖 nas（2）—— 使用 rtsp 协议同步"
date: "2017-01-04 07:27:55"
updated: "2017-01-04 08:13:37"
tags:
-  linux
-  嵌入式
-  折腾
---


[上一篇 blog](https://lengzzz.com/note/sync-video-from-yi-camera-to-synology-nas "小蚁摄像头实时同步视频到群晖 nas") 我利用 inotify-tools 和 rsync 两个工具实现了自动同步小蚁摄像机里拍摄的视频。不过今天翻网络又发现了另一种自动同步的解决方案，这个可以利用到群晖 nas 的 Surveillance Station 功能，使用效果更佳一些。这篇博客记录一下这次折腾过程。

[](/notename/ "sync video from yi camera to synology nas 2")

Surveillance Station 是群晖上的一个功能套件，可以管理网络摄像机，功能十分强大，而且原生支持很多品牌的网络摄像机，但是不支持小蚁摄像机。不过还好的是 Surveillance Station 支持 rtsp 协议，只要能在小蚁上开启 rtsp 服务就可以了。

<center width="80%">
![QQ20170104-1@2x.png-4220.7kB][1]
<small>功能很强的Surveillance Station</small>
</center>

这次没有自己编译 rtsp 服务，一是因为没有找到一个好用又轻量的，二是因为刚好找到一个俄罗斯的国际友人做的 [“小蚁Hack”项目](https://github.com/fritz-smh/yi-hack) 里面正好有我想要的 rtsp 服务，我就直接拿来用了。

我们只需要用到他项目里的一个文件，叫做 rtspsvrM 可以在 https://raw.githubusercontent.com/fritz-smh/yi-hack/master/sd/test/rtspsvrM 下载到。如果小蚁的系统版本比较老，可能需要 rtspsvrK 或者 rtspsvrI。我用的最新的 1.8.6.1 所以使用 M 版本的。具体的规则可以在 https://github.com/fritz-smh/yi-hack/blob/master/sd/test/equip_test.sh#L216 这个脚本里找到，我就不赘述了。

下载好 rtspsvrM 文件后，放到 sd 卡根目录，然后再创建一个服务。

```sh
#!/bin/sh
/tmp/hd1/rtspsvrM >> /tmp/hd1/rtspsvrM.log 2>&1 &
```

然后重启，执行下 `netstat -tuanp` ，可以看到 rtspsvrM 已经监听 554 端口了。

```sh
# netstat -tuanp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:38888           0.0.0.0:*               LISTEN      1266/goolink
tcp        0      0 0.0.0.0:8554            0.0.0.0:*               LISTEN      1214/rtspsvrM
tcp        0      0 0.0.0.0:554             0.0.0.0:*               LISTEN      1214/rtspsvrM
tcp        0      0 0.0.0.0:21              0.0.0.0:*               LISTEN      1197/tcpsvd
tcp        0      0 0.0.0.0:18554           0.0.0.0:*               LISTEN      1214/rtspsvrM
tcp        0      0 10.0.0.224:49016        120.25.66.121:28622     ESTABLISHED 1266/goolink
tcp        0      1 10.0.0.224:53621        10.0.0.1:56688          LAST_ACK    -
tcp        0  36200 10.0.0.224:35958        10.0.0.222:873          ESTABLISHED 1837/rsync
tcp        0      0 10.0.0.224:554          10.0.0.222:53007        ESTABLISHED 1214/rtspsvrM
tcp        0      0 10.0.0.224:42065        42.62.94.185:80         ESTABLISHED 1629/cloud
tcp        0      0 :::80                   :::*                    LISTEN      1141/server
tcp        0      0 :::23                   :::*                    LISTEN      1204/telnetd
tcp        0   1087 ::ffff:10.0.0.224:23    ::ffff:10.0.0.220:46884 ESTABLISHED 1204/telnetd
udp        0      0 0.0.0.0:6970            0.0.0.0:*                           1214/rtspsvrM
udp        0      0 0.0.0.0:6972            0.0.0.0:*                           1214/rtspsvrM
udp        0      0 0.0.0.0:23887           0.0.0.0:*                           2596/p2p_tnp
udp        0      0 0.0.0.0:32108           0.0.0.0:*                           2596/p2p_tnp
udp        0      0 0.0.0.0:56944           0.0.0.0:*                           1266/goolink
udp        0      0 0.0.0.0:56501           0.0.0.0:*                           1266/goolink
udp        0      0 0.0.0.0:1500            0.0.0.0:*                           1266/goolink
```

说明服务已经起来了。另外这个 rtspsvrM 虽然没有开源，但是他好像没有建立什么乱七八糟的网络连接，姑且认为它不会泄漏用户信息。

现在回到 nas 的管理界面中，打开 Surveillance Station，点击网络摄像机点新增。

![image_1b5k8dc0o19jf8bt1fe1abrtjr17.png-48.3kB][2]

之后把 IP、端口号填写上，品牌选择最上面的用户自定义。最后一个视频原路径很关键，需要填写成 `rtsp://10.0.0.224:554/ch0_0.h264` 把其中的 IP 地址替换成你摄像机的 IP 就可以了。

之后，就可以好好享受 Surveillance Station 的强大功能了。

  [1]: http://static.zybuluo.com/zwh8800/obh6frw0djqaum7ibwkg8kfi/QQ20170104-1@2x.png
  [2]: http://static.zybuluo.com/zwh8800/fdsn1kae71w3krm42sn58ede/image_1b5k8dc0o19jf8bt1fe1abrtjr17.png
