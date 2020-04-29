---
title: "Linux Shell 编程中的 trap 的小坑"
date: "2016-05-24 10:58:33"
updated: "2016-05-24 11:25:19"
tags:
-  linux
-  bash
-  shell
-  trap
---


在 Shell 编程中，为了脚本的健壮性，一般会用到 `trap` 这个 builtin command。trap 命令类似 c 语言中的 `signal` 函数，可以注册一个函数，当程序收到信号时执行函数。但是 trap 命令也有一些比较坑的小细节，比如 trap 的执行时机。

[](/notename/ "trap's trap in linux shell programing")

在 c 语言中，程序收到信号之后会立即执行 signal 注册的信号处理函数。那么在 shell 程序中呢，信号究竟什么时候被 trap 处理？是像 c 程序一样停下程序立即执行，还是等待当前程序执行之后再执行？

```bash
#!/bin/bash
trap 'echo "signal received!"; exit' INT
sleep 100
```

我们先写一段程序做个实验。在 bash 中执行它，然后按 `control + c` 发现程序立即停止了，然后打印了 signal received，似乎 trap 是类似 c 程序一样立即处理信号的。但其实是被表面现象蒙骗了。

我们再次执行这个 shell 程序，然后打开另一个 shell，在里面执行 `kill -SIGINT xxx` 发现 shell 程序并没有退出，等待了 100 秒之后才打印 signal received 退出。

因为第一次在键盘上按 `control + c` 后，sleep 程序和 shell 程序同属一个进程组，所以也接到了 int 信号退出了，而第二次只有 shell 程序收到信号，所以造成了两者的差异。我第一次也被蒙骗了，傻乎乎的以为 trap 能在 sleep 时也处理信号。

那么问题来了，我们如果需要在 sleep 时处理信号，并且及时退出怎么办呢？国外一篇文章给了例子[^sample]，我就负责搬运一下了。

```bash
pid=
trap '[[ $pid ]] && kill $pid' EXIT
sleep 10000 & pid=$!
wait
pid=
```

利用了 bash 的 builtin 命令 wait。wait 是一个 shell 内部的命令，而不是一个外部程序，所以它没有前面的限制。另外，要记得退出时 kill 掉 sleep 进程，擦好屁股。

[^sample]: http://mywiki.wooledge.org/SignalTrap

