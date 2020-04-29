---
title: "linux 共享库搜索路径"
date: "2016-04-02 08:02:31"
updated: "2016-04-23 12:26:39"
tags:
-  linux
---


linux 中, 在执行一个可执行文件时，搜索动态库路径一共有 5 种，有优先级，会从上到下依次进行搜索。当执行一个程序上发现报错 `No such file or directory` 可以由此顺序来查错。

[](/notename/ "linux so search path")

- 在 ELF 文件的动态段 DT_RPATH 所指定的路径，可以在编译本文件时通过 “-Wl,rpath” 来指定 
```bash
gcc -Wl,-rpath,/usr/local/lib,-rpath,/home/zzz/opensource/lib test.c
```
- 环境变量 LD_LIBRARY_PATH
- /etc/ld.so.cache 中缓存的路径，可以通过修改配置文件 / etc/ld.so.conf 并执行 ldconf 命令来修改
- 默认路径 /lib
- 默认路径 /usr/lib

