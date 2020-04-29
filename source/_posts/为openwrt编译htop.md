---
title: "为 openwrt 编译 htop"
date: "2014-06-23 00:00:00"
updated: "2014-06-23 00:00:00"
tags:
-  openwrt
---


为 openwrt 编译 htop

[](/notename/ "archive 20140623")

其实就和原来给电视棒交叉编译一样, 不过这次交叉编译器可让我好找…

路由器用的是华为的 hg255d, mips 的芯片, 16M flash, 64M sdram.

一般嵌入式开发都把内核和 app 分开的… 这个 openwrt 却不单独提供 toolchain. 只给一个内核源码包 (也不只是内核,  是内核和软件包的混合体…)

不过最后还是找到一个单独的工具链:

下载地址:

有了工具链一切就好办了. htop 依赖与 ncurses 所以先下载 ncurses.
```
mkdir openwrt
cd openwrt
wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
wget http://downloads.sourceforge.net/project/htop/htop/1.0.2/htop-1.0.2.tar.gz
```
下载好之后, 在当前目录建一个文件夹 build, 编译后的文件就安装在这里, 然后分步解压
```
mkdir build
tar zxvf ncurses-5.9.tar.gz
tar zxvf htop-1.0.2.tar.gz
```
然后先编译 ncurses:
```
cd ncurses-5.9
./configure --prefix=/home/zzz/openwrt/build --host=mipsel-openwrt-linux --without-cxx --without-cxx-binding --without-ada --without-manpages --without-progs --without-tests 
make
make install
```
后面几个 without 是去除 c++ 和 ada 支持以及不编译 manpage 和测试程序
然后就能发现在 build/lib 里有编译好的 ncurses 库了

之后编译 htop:
```
cd htop-1.0.2
./configure --prefix=/home/zzz/openwrt/build --disable-unicode --host=mipsel-openwrt-linux LDFLAGS=-L/home/zzz/openwrt/build/lib
make 
make install
```
LDFLAGS=-L/home/zzz/openwrt/build/lib 选项是为了加上链接库的路径

短暂等待过后, 在 build/bin 里应该能看见 htop.

拿到 openwrt 上运行又发生点问题. 提示
Error opening terminal: xterm.
上网 Google 一下发现需要设置 TERMINFO 环境变量:
```
export TERMINFO=/usr/share/terminfo
```
[EOF]


