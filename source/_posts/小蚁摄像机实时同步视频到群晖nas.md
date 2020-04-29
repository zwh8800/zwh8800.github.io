---
title: "小蚁摄像机实时同步视频到群晖 nas"
date: "2017-01-02 14:28:14"
updated: "2017-01-04 07:33:01"
tags:
-  linux
-  交叉编译
-  嵌入式
-  折腾
---


之前买了个小蚁智能摄像机，原生只支持向小米路由器里同步视频，我只有一个群晖 nas 做网络存储，所以元旦放假在家研究了下怎么样“破解”小蚁摄像头使它能同步视频到 nas 上。本质上，小蚁摄像头也是一个 Linux 服务器，只不过是运行在 arm 上的嵌入式 Linux，所以 Linux 的整个生态环境都可以利用的上。我这次的解决方案是使用 Linux 上著名的 [rsync](https://rsync.samba.org/) 做同步工具，但是必须编译出一个在 arm 上能用使用的 rsync。所以这篇文章的重点是 **交叉编译**。

[](/notename/ "sync video from Yi Camera to Synology nas")

<!-- more -->

## 拿到小蚁摄像头的 shell

据说某些系统版本的小蚁摄像头默认没关闭 telnet 服务，那么在做以下事情之前可以先试试你的摄像头是不是已经开启了 telnet 。在终端里运行 `telnet xxx.xxx.xxx.xxx` xxx.xxx.xxx.xxx 是你摄像头的 ip 地址，可以在路由器管理界面中查到。如果出现 `(none) login:` 字样，说明你已经拿到了 shell，就不用做下面的操作了，直接跳到[这里](#jumpto-1)。

- 把小蚁摄像头里的内存卡取出来，在内存卡根目录建立一个文件夹 test
- 在 test 目录下创建文件 `equip_test.sh` 粘贴以下内容。

```sh
#!/bin/sh
# Telnet
if [ ! -f "/etc/init.d/S88telnet" ]; then
    echo "#!/bin/sh" > /etc/init.d/S88telnet
    echo "telnetd &" >> /etc/init.d/S88telnet
    chmod 755 /etc/init.d/S88telnet
fi
dr=`dirname $0`
# fix bootcycle
mv $dr/equip_test.sh $dr/equip_test.sh.moved
reboot
```

根据网上的说法，`equip_test.sh` 会在开机的时候自动运行。

这个脚本的内容很简单，第一步创建 `/etc/init.d/S88telnet` 这个文件，内容如下：

```sh
#!/bin/sh
telnetd &
```

这个文件相当于创建了一个 busybox-init 的 `服务` [^ref3]，和 ubuntu、CentOS 的服务类似，不过功能更简单一些，直接就是一个 shell 脚本。这个 shell 脚本开启了 telnetd 后台程序。

第二步是把自身重命名并且重启，避免每次摄像头开机重复运行。

<div id="jumpto-1"></div>

现在，可以把内存卡查到摄像头中开机，不出意外的话现在再次在终端里输入 `telnet xxx.xxx.xxx.xxx` 就可以看到 `(none) login:` 了，现在输入用户名 `root` 按回车，再输入密码 `1234qwer` 就可以进入小蚁摄像头的 shell 界面了。

## 交叉编译 rsync

拿到 shell 之后先进去看了看系统信息，没想到这个小蚁摄像头的配置这么寒酸。。。? cpu 是 N 年前的 arm9 ，内存只有 32MiB ，你没看错，就是 32MiB，一点都不夸张，root 文件系统只有 3.5MiB 的空间，毛都放不了，只能想办法把东西放内存卡上。

```
$ uname -a
Linux (none) 3.0.8 #1 Wed Apr 30 16:56:49 CST 2014 armv5tejl GNU/Linux
$ cat /proc/cpuinfo
Processor       : ARM926EJ-S rev 5 (v5l)
BogoMIPS        : 218.72
Features        : swp half thumb fastmult edsp java
CPU implementer : 0x41
CPU architecture: 5TEJ
CPU variant     : 0x0
CPU part        : 0x926
CPU revision    : 5

Hardware        : hi3518
Revision        : 0000
Serial          : 0000000000000000
$ cat /proc/meminfo
MemTotal:          35212 kB
MemFree:            1044 kB
Buffers:             268 kB
Cached:            10016 kB
SwapCached:            0 kB
Active:            11536 kB
Inactive:           5432 kB
Active(anon):       6996 kB
Inactive(anon):     2944 kB
Active(file):       4540 kB
Inactive(file):     2488 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:               600 kB
Writeback:             0 kB
AnonPages:          6708 kB
Mapped:             5344 kB
Shmem:              3256 kB
Slab:               8152 kB
SReclaimable:       1192 kB
SUnreclaim:         6960 kB
KernelStack:         808 kB
PageTables:          692 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:       17604 kB
Committed_AS:     312508 kB
VmallocTotal:     966656 kB
VmallocUsed:       23856 kB
VmallocChunk:     935280 kB
$ df -h
Filesystem                Size      Used Available Use% Mounted on
/dev/root                 3.5M      2.7M    844.0K  76% /
tmpfs                    17.2M     16.0K     17.2M   0% /dev
/dev/mtdblock5            8.9M      8.1M    784.0K  91% /home
tmpfs                    32.0M    164.0K     31.8M   1% /tmp
/dev/hd1                 14.8G      4.1G     10.8G  27% /tmp/hd1
tmpfs                   512.0K     16.0K    496.0K   3% /home/mmap_tmpfs
tmpfs                    16.0M     36.0K     16.0M   0% /home/tmpfs
tmpfs                    16.0M      3.0M     13.0M  19% /home/jrview

```

soc 用的好像是屁眼公司的 hi3518，小米在手机行业和华为干架那么厉害，芯片还是得用菊花厂的啊。

回归正题，我们开始交叉编译 rsync。一开始我用的是 ubuntu 上自带的交叉工具链 `gcc-arm-linux-gnueabi` 折腾半天编译出来的东西没法用，这才发现这个摄像头用的 libc 是 uClibc， 这种低端错误都犯了，之前自己做嵌入式的时候最常用的就是 uClibc 都忘记了?。

后来想办法下载一个 `arm-linux-uclibc-gcc` ubuntu 上好像没有现成的源可以下，Google 一下发现了这个 maillist http://lists.busybox.net/pipermail/buildroot/2010-January/031634.html。

这个帖子讨论的是一个叫 [buildroot](https://buildroot.org/) 的东西。我研究了一下这个项目，它竟然可以一键 build 出整个嵌入式系统，包括 host 上运行的交叉工具链、bootloader、kernel、root filesystem甚至是各种软件包，其中就包括 rsync。那我还费心找什么工具链啊，直接用它就好了。

现在要做的就是找一台 Linux 机器，在上面运行以下命令，编译出 rsync。

```bash
wget https://buildroot.org/downloads/buildroot-2016.11.1.tar.gz
tar xvf buildroot-2016.11.1.tar.gz
cd buildroot-2016.11.1
make menuconfig
make
```

执行 `make menuconfig` 之后会出现一个菜单（和编译内核的菜单用的同一个）。

- 进入 `Target options` 再进入 `Target Architecture` 菜单，选择 `ARM (little endian)`
- 进入 `Target Architecture Variant` 选择 `arm926t` 其他选项不用动，按两下 esc 退出来
- 进入 `Toolchain` 菜单，`C library` 选择 `uClibc-ng`
- 进入 `Kernel Headers`，貌似没有 `3.0.8` 选个最低的 `Linux 3.2.x kernel headers` 吧
- 退出来进入 `Target packages`，在 `Networking applications` 里找到 `rsync` 按空格键打上勾
- 退出来进入 `Shell and utilities` 把 `inotify-tools` 打上勾，这个我们也要用到
- 按 tab 键，使光标移动到 `Save`，回车存盘退出。

之后执行 make，经过漫长的等待，终于编译好了。进入到 buildroot-2016.11.1/output/target 文件夹可以看到整个根目录，在 `/usr/bin` 可以看到编译好的 rsync 。不过只把这个文件放到摄像头是不行的，因为还有 rsync 的动态链接库 so 文件也得放进去。

我直接 `tar zxcf target.tgz ./target` 把根目录打包，放到摄像头内。然后摄像头开机进入 shell，执行 `tar xvf target.tgz` 解包到内存卡里。然饿。。。现在也不能运行，因为必须把链接库的目录设置好，在 shell 里再执行一下 

```sh
export PATH=$PATH:/tmp/hd1/target/bin:/tmp/hd1/target/usr/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tmp/hd1/target/lib:/tmp/hd1/target/usr/lib
```

这个是把动态库的搜索路径设置好，具体可以看我[这篇文章](https://lengzzz.com/note/linux-so-search-path)，现在，执行 rsync，竟然报错 `libz.so.1 not found` 。我进入发现只有 `libz.so.1.2.8` 并没有 `libz.so.1` 原来是因为内存卡是 fat32，不支持软连接，只好复制一份了?。`cp libz.so.1.2.8 libz.so.1` 这也是没有办法的事。

最后，执行一下 rsync，可以看到久违的帮助信息了，真不容易。

## 自动同步脚本

rsync 只能同步一次文件，当文件保持同步之后就会退出，怎么样想个方法能让两端文件实时同步呢？答案是利用 [inotify-tool](https://github.com/rvoicilas/inotify-tools)。这个工具利用了内核的通知系统，当文件进行改动之后，就会发出一个通知，此时再调用 rsync 进行同步就可以了。

所以把它写成了一个脚本[^ref4]：

```sh
#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tmp/hd1/target/lib:/tmp/hd1/target/usr/lib
export PATH=$PATH:/tmp/hd1/target/bin:/tmp/hd1/target/usr/bin
export RSYNC_PASSWORD="xxxxx"

SRC=/tmp/hd1/record/
DST=rsync://YiCamera@10.0.0.222/YiCamera/
nowtime=$(date +%s)
inotifywait -mrq --timefmt '%s' --format '%T' -e modify,delete,create,attrib,move $SRC | while
read timestamp
do  
    diffnow=$(($nowtime - $timestamp))
    echo $nowtime $timestamp $diffnow

    if [ $diffnow -lt 5 ]
    then
        echo 'start rsync'
        rsync -vzrtopg --delete $SRC $DST
        nowtime=$(date +%s)
    fi
done

```

解释一下这个脚本。前两句不用说了，第三局是导出一个系统变量，rsync 会读取这个变量拿到 rsync 的密码[^ref2]。之后是调用 inotifywait，当他发现文件的修改、删除、创建、修改属性时，会输出到标准输出中。

标准输出被重定向到管道中，`read files` 当接不到数据时会 block，当接收到数据之后会向下执行 rsync。

rsync 的参数 `-vzrtopg` 里的v是verbose，z是压缩，r是recursive，topg都是保持文件原有属性如属主、时间的参数，--delete参数会把原有getfile目录下的文件删除以保持客户端和服务器端文件系统完全一致[^ref1]。

然后，在 `/etc/init.d` 创建一个服务：

```sh
cat /etc/init.d/S90nasync
#!/bin/sh
/tmp/hd1/nasync.sh >> /tmp/hd1/nasync.log &
```

重启摄像头，你会发现，nas 里有自动同步过来的视频了。

[^ref1]: [Rsync安全配置](http://wps2015.org/drops/drops/Rsync%E5%AE%89%E5%85%A8%E9%85%8D%E7%BD%AE.html)

[^ref2]: [rsync without prompt for password](http://unix.stackexchange.com/questions/111526/rsync-without-prompt-for-password)

[^ref3]: [Create and control start up scripts in BusyBox](http://unix.stackexchange.com/questions/59018/create-and-control-start-up-scripts-in-busybox)

[^ref4]: [Linux-rsync+inotify 文件实时同步](http://miaocbin.blog.51cto.com/689091/1662466)


