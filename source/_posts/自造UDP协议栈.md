---
title: "自造 UDP 协议栈"
date: "2014-04-18 00:00:00"
updated: "2014-04-18 00:00:00"
tags:
-  UDP
-  网络编程
-  协议栈
---


自造 UDP 协议栈

[](/notename/ "archive 20140418")

这一个星期一直在自造一个 UDP 协议栈.

今天是周五, 屁屁和室友逛街去了, 我就在寝室敲代码搞了一下午, 终于是搞定了.

这个是老师的项目里要用的, 实现 avr 的单片机和 PC 机通讯. 中间通过以太网进行连接, avr 上用的是 enc28j60 芯片. 这个芯片原来我在 C8051F 上写过一个驱动. 移植过来倒是不麻烦, 半天搞定.

麻烦的是协议栈!

原来在 51 上用的是一个我精简了的 uIP 协议栈, 因为 C8051F 系列 FLASH 足够大, 而且 ram 也大 (f340 有 4096 字节). 足够移植 uIP 过去了.

在 avr 上遇了不少麻烦.

首先就是蛋疼的 codevision 编译器乱改 C 语言, 不按标准来. const 修饰的变量没法直接访问. 移植起来很麻烦. 然后就是 uIP 的 ram 占用一直下不去. 我已经把以太网最大帧长度调成 512 了还是费了 1100 多个字节. 然后很不幸, ATMega16 只有 1024 字节的 RAM. 可恶的 uIP 竟然用去了 512 个字节… 知道 RAM 有多宝贵嘛你!

想想算了, 还是换个内存大点的吧. 周一给老师要了 ATMEGA32, 想着鸟枪换炮! 不料, 老师给了我张板子, 说” 自己焊吧”……

贴片的本身就不容易焊, 况且我烙铁吃灰 n 久了脏死了完全不想动呀! (我这个死洁癖!)

切! 想想我也是立志成为驱动工程师的男人, 这种小事应该交给硬件工程师来做嘛, 哼╭(╯^╰)╮(无任何冒犯…)

所以嘛这点困难完全难不倒我! 开源的不行我就自己写一个嘛.

自己动手丰衣足食.

↑一点都不华丽的分割线

自己造轮子的话最大的好处就是可以<span style="color: red">紧密把握需求</span>, 只写需要的功能, 不需要的一概不写! 另外因为对内存需求比较严格, 所以这个协议栈<span style="color: red">几乎是不占内存</span>, 除了 6 个 ip 地址 7 个 mac 地址常驻内存以外, 全部使用栈内存.

这个协议栈最大的特点就是简洁, 只有两个文件构成: udp.c, 和 udp.h
而且接口设计的也比较简洁, 只向外部提供三个函数:
```
void init_udp(unsigned char* mac_addr, ip_t ip_addr, ip_t netmask, ip_t gateway,
	INCOMING_CALLBACK incoming, SENDBUF_CALLBACK sendbuf, DELAY_CALLBACK delay);
void process(unsigned char* buf,  unsigned short len);
void send_udp(struct address* addr, void* buf,  unsigned short len);
```

顾名思义

1. init_udp 是初始化函数, 需要提供 ip 地址和 mac 地址. 另外需要提供三个回调函数.
2. process 函数是当主程序接收到数据帧时需要调用的函数, 直接将以太网数据帧和 size 传入即可. 协议栈会进行处理 (现在可处理 arp 请求, icmp ping 请求, 和 udp 数据)
3. send_udp 函数是主程序发送 udp 数据的函数, 需要把对端 ip 和端口以及本地端口存入 struct address 结构体中.

另外在 init_udp 函数中的三个回调函数:
```
typedef void (*INCOMING_CALLBACK)(struct address* addr, unsigned char* buf,  unsigned short len);
typedef void (*SENDBUF_CALLBACK)(void* buf,  unsigned short len);
typedef void (*DELAY_CALLBACK)(int ms);
```

分别是
1. 当有 UDP 数据到达时被调用
2. 当需要发送数据时被调用
3. 当需要 sleep 时调用

**INCOMING_CALLBACK** 函数的 addr 参数传来对端的 ip 端口和本地端口号, buf 中的是 <span style="color: red">UDP 数据</span>, 不包含任何报头

SENDBUF_CALLBACK 函数传来 buf, <span style="color: red">SENDBUF_CALLBACK </span>`需要将 buf 中的数据写入一个缓冲区` (可以是`硬件缓冲区`中). SENDBUF_CALLBACK 函数会被`多次`调用, 应当`依次将 buf 中数据写入缓冲`.

当 SENDBUF_CALLBACK <span style="color: red">最后一次被调用时, buf 会传入 </span>`NULL`. 此时, <span style="color: red">SENDBUF_CALLBACK 函数</span>`应当将缓冲区中数据发送到以太网上`.

DELAY_CALLBACK 函数需要休眠指定的毫秒数, 如果程序运行在一个 RTOS 上的话可以调用 SLEEP 来让出处理器. 如果是裸板程序的话… 那就用循环吧 (这个协议栈在通过 arp 协议查找 mac 地址时会等待, 但最多不超过 1000 毫秒 [这个数值可以改]).

如果不能忍受等待的话, 可以将要紧任务放到中断中处理 (这个常识应该都用吧)

大致就是这样. 下午就是在板子上简单的测试了一下, 基本可用, 能收发 udp 包, 能 ping 通.

源码如下: (不做任何担保, 用了出事不怪我, 逃…

[https://lengzzz.com/udp/udp-0.3.zip](https://lengzzz.com/udp/udp-0.3.zip)

最后上图:
![image_1bl057v6q5uq1rbf1b5ejk311q9.png-579.9kB][1]
![image_1bl058hv31jct1gsd4slnej20dm.png-68.2kB][2]

  [1]: /images/13880d8baedd7994327526f1a8aa7556.png
  [2]: /images/27fff57e412e0967ec53c768c9485894.png
