---
title: "netstat命令help翻译"
date: "2014-01-13 00:00:00"
updated: "2014-01-13 00:00:00"
tags:
-  unix
-  系统编程
---


翻译了一下 netstat --help 的提示信息

[](/notename/ "archive 20140113")

```
zzz@lengzzz:~$ netstat --help
usage: netstat [-vWeenNcCF] [<Af>] -r         netstat {-V|--version|-h|--help}
       netstat [-vWnNcaeol] [<Socket> ...]
       netstat { [-vWeenNac] -i | [-cWnNe] -M | -s }

        -r, --route			显示路由表
        -i, --interfaces		显示接口列表
        -g, --groups		显示组播组成员
        -s, --statistics		显示网络统计数据（类似SNMP）
        -M, --masquerade	显示伪装连接

        -v, --verbose		显示详细信息
        -W, --wide			不截断IP地址
        -n, --numeric		不解析名字
        --numeric-hosts		不解析主机名
        --numeric-ports		不解析端口名
        --numeric-users		不解析用户名
        -N, --symbolic		解析硬件名
        -e, --extend		显示更多信息
        -p, --programs		显示套接字的PID/程序名
        -c, --continuous		刷屏显示

        -l, --listening		显示监听套接字
        -a, --all, --listening	显示所有套接字（默认：只显示连接套接字）
        -o, --timers		显示套接字定时器状态
        -F, --fib			显示前导路由信息（默认启用）
        -C, --cache			显示路由cache中的前导路由信息

  <Socket>={-t|--tcp} {-u|--udp} {-w|--raw} {-x|--unix} --ax25 --ipx --netrom
  <AF>=Use '-6|-4' or '-A <af>' or '--<af>'; default: inet
  可以使用的地址族列表 (支持路由的):
    inet (DARPA Internet) inet6 (IPv6) ax25 (AMPR AX.25) 
    netrom (AMPR NET/ROM) ipx (Novell IPX) ddp (Appletalk DDP) 
    x25 (CCITT X.25) 
```
