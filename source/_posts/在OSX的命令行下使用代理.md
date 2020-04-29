---
title: "在 OS X 的命令行下使用代理"
date: "2016-04-27 03:39:43"
updated: "2017-08-03 05:57:18"
tags:
-  mac技巧
-  bash
-  terminal
-  代理
---


相信程序员们工作中必不可少的就是一个趁手的代理。但是 Mac 客户端只提供了系统代理（供 app 调用的）和一个裸的 socks5 代理。都不方便在命令行工具中使用。下面介绍一种方法可以方便的在命令行中使用代理的方法。

[](/notename/ "using proxy in osx terminal")

首先介绍一个常识，大多数 gnu unix 程序都会访问一个环境变量 `http_proxy` ，比如 curl 在执行时会先访问一下 http_proxy ， 如果有这个变量的话，会使用这个变量给出的地址作为 proxy 。这相当于是 gnu 给我们带来的一个福利[^proxysetting]。

但是这个方式只支持 http、https、ftp 和 rsync 协议，不过大多数情况下也够用了，因为在命令行下大多是执行 `npm`，`go get` 才会用到代理，而这些程序打多使用 http 协议。

那么，具体思路就是使用一个转换器，把 socks5 代理转换成 http 代理，然后使用 `http_proxy` 环境变量。

polipo 可以做代理转换器：

```bash
# 安装polipo
brew install polipo
```

为了方便我们使用它，可以在 `~/.bash_profile` 里加一个 alias：

```bash
# ~/.bash_profile

alias startPolipo='polipo socksParentProxy=localhost:1080 proxyAddress=0.0.0.0'
```

这样，在使用之前，需要先开一个新的 term 窗口，执行一下 `startPolipo` 开启一个代理转换器。可以看到 polipo 监听了 8123 端口。

之后，在需要代理的程序前面加上 `http_proxy=http://localhost:8123 https_proxy=http://localhost:8123` 就可以让程序使用代理了。

另外，为了更加方便，我们可以再搞一个 alise：

```bash
alias proxy='env http_proxy=http://localhost:8123 https_proxy=http://localhost:8123'
```

只需要每次在需要使用 proxy 的命令前面加上 `proxy` 就可以使用代理了。例如：

```bash 
proxy curl https://google.com/
```

可以看见 curl 打印了 Google 首页出来

[^proxysetting]: 具体参考[这里](https://wiki.archlinux.org/index.php/proxy_settings)
