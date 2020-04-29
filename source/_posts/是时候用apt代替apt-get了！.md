---
title: "是时候用 apt 代替 apt-get 了！"
date: "2016-05-28 01:51:48"
updated: "2016-05-28 02:18:59"
tags:
-  linux
-  ubuntu
-  运维
---


最近无痛升级了 ubuntu 16.04 ，软件包和数据一点没丢。比上次 12.04 升级 14.04 舒服多了，直接 ssh 就搞定升级了。不得不说 ubuntu 已经成熟很多了。升级后我才发现多了个 `apt` 命令，用起来很符合我的审美，不过这个东西好像也存在比较久的一段时间了，实在是后知后觉了。

[](/notename/ "it is time to replace apt-get with apt")

apt 这个命令行工具在功能上基本涵盖了以前 apt-get 和 apt-cache 的功能，在他们之上提供了一个 high-level 的命令行界面，而且也更有交互性。

![image_1ajqh3qkm1kf81vb81kmtjldlipg.png-416.8kB][1]

在命令行下敲击 apt 后会打印出一些常见命令：

```
zzz@ubuntu-server ~ $ apt
apt 1.2.10 (amd64)
用法： apt [选项] 命令

命令行软件包管理器 apt 提供软件包搜索，管理和信息查询等功能。
它提供的功能与其他 APT 工具相同（像 apt-get 和 apt-cache），
但是默认情况下被设置得更适合交互。

常用命令：
  list - 根据名称列出软件包
  search - 搜索软件包描述
  show - 显示软件包细节
  install - 安装软件包
  remove - 移除软件包
  autoremove - 卸载所有自动安装且不再使用的软件包
  update - 更新可用软件包列表
  upgrade - 通过 安装/升级 软件来更新系统
  full-upgrade - 通过 卸载/安装/升级 来更新系统
  edit-sources - 编辑软件源信息文件

参见 apt(8) 以获取更多关于可用命令的信息。
程序配置选项及语法都已经在 apt.conf(5) 中阐明。
欲知如何配置软件源，请参阅 sources.list(5)。
软件包及其版本偏好可以通过 apt_preferences(5) 来设置。
关于安全方面的细节可以参考 apt-secure(8).
                                         本 APT 具有超级牛力。
```

虽然这个 `超级牛力` 是什么鬼我也不明白了。。。（莫非是 powered by GNU？）但是基本的使用介绍还是很清晰的。对于咱们普通用户来说，最明显的就是把 search 功能合并过来了。

另外，比较好用的一点是 list 命令。可以使用 `apt list --upgradable` 来查看需要升级的软件包，有点类似 `brew outdated` 。

还有一个 `apt show` 可以打印出软件包的基本信息。

```
zzz@ubuntu-server ~ $ apt show zsh
Package: zsh
Version: 5.1.1-1ubuntu2
Priority: optional
Section: shells
Origin: Ubuntu
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Original-Maintainer: Debian Zsh Maintainers <pkg-zsh-devel@lists.alioth.debian.org>
Bugs: https://bugs.launchpad.net/ubuntu/+filebug
Installed-Size: 2,023 kB
Pre-Depends: dpkg (>= 1.17.14)
Depends: zsh-common (= 5.1.1-1ubuntu2), libc6 (>= 2.15), libcap2 (>= 1:2.10), libtinfo5 (>= 6)
Recommends: libncursesw5 (>= 6), libpcre3
Suggests: zsh-doc
Homepage: http://www.zsh.org/
Supported: 5y
Download-Size: 651 kB
APT-Sources: http://cn.archive.ubuntu.com/ubuntu xenial/main amd64 Packages
Description: 具有很多特性的 Shell
 Zsh 是一个既可用作登录 Shell，又可用于执行脚本的命令解析器。 在标准 Shell 中 Zsh 与 Ksh
 最相近，同时又带有许多改进。Zsh 支持命令行编辑，内置拼写纠正，支持可编程命令补全、带自动加载的 Shell 函数、历史功能和大量其他特性。

```

总之就是各种命令清晰漂亮了很多，个人用起来很舒服。

  [1]: /images/78febf75a690a0a0b38c17a8c046defe.png
