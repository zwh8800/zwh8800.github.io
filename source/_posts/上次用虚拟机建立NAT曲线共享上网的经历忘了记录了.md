---
title: "上次用虚拟机建立NAT 曲线共享上网的经历忘了记录了"
date: "2013-10-25 00:00:00"
updated: "2013-10-25 00:00:00"
tags:
-  Linux
-  运维
-  NAT
---


上次用虚拟机建立NAT 曲线共享上网的经历忘了记录了

[](/notename/ "archive 20131025")

首先主机连上学校的2B校园网

然后ubuntu server虚拟机装两个网卡, 一个是正常nat上网, 另一个为桥接网卡

/etc/network/interfaces 大概这样写

![image_1bl00gri2a201k807s01gk016t99.png-13.1kB][1]

一个为上网的出口, 一个桥接到校园网的局域网内, 做NAT服务器

之后修改/etc/sysctl.conf文件

将net.ipv4.ip_forward= 1的注释删掉

否则内核如果读取的目的地址不是本机ip但目的mac地址为本机的数据包(路由数据包)将会直接丢弃

然后加载iptables和nat模块

```bash
sudo modprobe ip_tables
sudo modprobe ip_nat_ftp
```

如果没安装iptables先执行

```bash
sudo apt-get install iptables
```

之后执行

```bash
sudo iptables -F -t nat    #清空所有规则
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE    #建立nat 以eth0为出口
```

然后调用

```bash
sudo iptables-save -c /home/zzz/iptables.save
```

把刚刚配置的写入一个文件中, 下次开机只需调用

```bash
sudo iptables-restore -c /home/zzz/iptables.save
```

就ok了, 可以把modprobe那两句 和restore放到rc.local里 每次开机自动执行

https://www.cnblogs.com/JemBai/archive/2009/03/19/1416364.html
https://oa.jmu.edu.cn/netoa/libq/pubdisc.nsf/66175841be38919248256e35005f4497/7762e8e1056be98f48256e88001ef71d?OpenDocument

参考两篇文章

  [1]: http://static.zybuluo.com/zwh8800/hk6o73lt9mqidvp371w7mff0/image_1bl00gri2a201k807s01gk016t99.png
