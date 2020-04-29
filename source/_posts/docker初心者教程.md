---
title: "docker 初心者教程"
date: "2016-04-02 12:03:06"
updated: "2016-04-26 05:40:17"
tags:
-  docker
-  DevOps
-  运维
---


换了博客系统之后，好有写博客的欲望。先来一篇docker的。

[](/notename/ "docker for beginners")

[toc]

## 微服务

先谈一下我对docker的理解吧。docker这个东西和微服务是离不来的，目前各大互联网企业都实践微服务，催生了docker的出现。我现在所在的公司也不例外，现在公司的技术大方向就是把老系统一步一步拆分成微服务，同时新系统直接做成微服务。身在其中，吃的屎多了，自然感到了微服务的种种优势。

对于微服务的优点我感觉最明显的有两点:

- **思维上**解耦了
- 团队的工作更具体明确了。

因为现在同时在做新系统（微服务）的同时还需要在老系统上加功能，对第一点感觉就十分明显。在老系统那40万行屎山一样的代码上改东西时，整个人的心智负担就会很重，生怕哪一行把整个app拖慢了。新系统因为它足够微，所以理解整体业务逻辑就比较容易，应用做了什么事情大家都心知肚明，所以写代码的时候就可以随意一些啦wwww

第二点感觉也很明显是因为几个月前公司才做了一次调整，由之前的按照技术栈分团队改为了按产品线分团队。这样一个团队中既有做web的也有iOS、android的还有懂运维的，大家组成一个团队共同来开发一个（或几个）产品，这样大家对一个产品会理解的更深刻，不会出现之前那种每部分都摸过，但是哪部分业务都不熟的情况。而且现在大家职责更分明，出了问题也能第一时间找到人来处理。

## docker 解决的问题

但是，微服务也会带来很多部署上的问题。以前发布只用build、deploy一个项目，现在需要搞10+个项目。这不把运维给累死啦？最麻烦的是每个项目依赖的东西不一样，可能项目A用的库是1.5.0，但项目B用的是1.6.0。这部署到一台机器还是两台机器呢，一台出错两台费钱。出问题的更多的是两个项目的依赖的依赖的依赖有冲突（不是直接冲突，两个项目的依赖树上有冲突）。另外程序员们总喜欢用最新的库，天天催运维升级系统。这样运维老爷们就会很头疼，大喊`老子不干啦！你们程序员事真多，自己搭环境自己玩吧！`。

因此，docker就腾空出世了。由上面可见，docker解决的最大的问题就是`定制的运行环境持久化，使应用或服务无论最终在哪里运行都有同样可预测的行为，尽量减少环境导致问题的可能性`。

另外，docker统一了由于操作系统不同而带来的服务接口不一致，比如应用部署上线后通常配合系统的initctl或upstart之类的写一个服务脚本。但是不同的系统甚至不同版本的系统都不互相兼容。用docker的话大家都统一`docker restart`了。爽歪歪。

## docker 使用

第一次用docker给人的感觉像用一个速度超快的虚拟机，但是比虚拟机牛逼在没有开机关机过程。docker中也有两个概念：**image**、**container**。container就相当于VBox里的一个虚拟机了，而image可以认为是container的一个备份（系统快照）。

基本的helloworld咱们就不跑了，就拿今天写好的博客系统来讲吧。这个和纯的微服务不一样，并不以接口形式向外提供服务，而是使用了模版引擎提供页面服务，以及向下访问数据库，和抓取cmd markdown的数据（类似于服务间调用接口啦233）。

### 准备

首先你需要把你的项目编译打包，这一步一般会在持续集成里去做。但是我们就手动搞啦。我这里的项目是golang的所以是一些go的编译命令
```bash
# golang交叉编译
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build
tar zcvf 
```

### 安装 docker

准备工作完成后，下面来安装docker。Mac下的安装过程比较蛋疼，我看了下就放弃了。手边的Linux机器不少，再不济的也能用virtual box。不过前几天据说发布了测试的原生Mac版 [Docker 终于有 Windows 和 Mac 版了](http://www.oschina.net/news/71885/docker-to-mac-windows) 喜大普奔。

Linux下安装就比较方便的，我用的ubuntu，直接用get.docker.com的安装脚本就能一键安装。
```bash
#!/usr/bin/env bash

apt-get update -y
apt-get install -y curl
curl -fsSL https://get.docker.com/ | sh

```

### 先拉个操作系统

装好之后现在可以做我们自己的镜像了。docker的特点是你的镜像可以基于已有的镜像构建。所以我们可以先从docker hub（类似github一样的东西）拉一个基础的操作系统镜像下来，然后在其之上来构建我们的镜像。
```bash
# 拉取alpine系统
docker pull alpine:3.3

# 或者习惯ubuntu的可以拉ubuntu
docker pull ubuntu:15.10
```
在进行docker pull命令的完整语法是 `docker pull [registry]/[username]/[image]:[version]` 分为四个部分，registry代表拉取的服务器地址，username是被拉取的镜像所有者的用户名，image是镜像名，version是版本tag。

其中，registry被省去代表拉取官方registry，username被省去代表拉去官方镜像，version被省去代表拉去latest镜像，也就是最新镜像。

所以上面的命令的意思是把官方的alpine3.3拉过来。docker官方的registry里维护了一些最基本的镜像和比较常用的镜像。官方维护的品质一般都是比较可以信赖的，所以制作镜像可以基于官方镜像来build。

pull好之后可以执行一下
```bash
zzz@ubuntu-server ~ $ docker images
REPOSITORY             TAG                 IMAGE ID            CREATED             SIZE
zwh8800/xware          latest              9426e8b48edc        4 days ago          176.8 MB
gogs/gogs              latest              40ce39eb7c4b        9 days ago          81.17 MB
zwh8800/starbucks      latest              15fbd0099e0c        12 days ago         17.22 MB
zwh8800/douyu-notify   latest              48ee382f41b8        2 weeks ago         12.01 MB
dperson/samba          latest              a09a77b57057        2 weeks ago         250.3 MB
nginx                  1.9.12              af4b3d7d5401        3 weeks ago         190.5 MB
ubuntu                 15.10               79cfbe2a4950        4 weeks ago         135.9 MB
jenkins                latest              c2cac236cd93        4 weeks ago         708.7 MB
golang                 1.6.0-alpine        c40da134e949        4 weeks ago         238 MB
alpine                 3.3                 70c557e50ed6        4 weeks ago         4.798 MB
golang                 1.6                 bb6cd5033ad2        4 weeks ago         744 MB
```
看一下所有本地的镜像

### 执行一下试试

既然已经拉下来镜像了，不玩一下就工作实在是可惜。所以我们先试着运行一下官方的镜像
```bash
zzz@ubuntu-server ~ $ docker run --rm -ti ubuntu:15.10 /bin/bash
root@8b94129944d0:/# 
```
你会发现你好像回到了命令行，但有一些不同，你的hostname好像变了。如果你像我一样配置了prompt的颜色的话，发现颜色没了。其实我们已经进入容器（**container**）了，但完全没想到会是这么快，就像运行一个程序一样根本不需要开机的时间。在这个bash里你可以尽情的 `apt-get install` 甚至 `rm / -rf` 完全不会影响你的宿主机。docker就像一个虚拟机一样，他有独立的文件系统，独立的网络。所以 `解开安全带吧` `大家一起飙车`

玩开心了要退出的话直接 `exit` 就好了。我们在运行的时候使用了 `--rm` 选项所以退出 container 的时候会自动删除 container。如果我们不加这个选项的话，可以在退出之后执行一下 `docker ps -a`
```bash
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                      PORTS               NAMES
2f9dd61f8a18        ubuntu:15.10        "/bin/bash"         40 seconds ago      Exited (0) 35 seconds ago                       desperate_bartik
```
会看到我们的容器还存在，你可以再次 `docker start` 它。

### 在容器中运行应用

下面，我们真正运行一下应用。
```bash
docker run --rm -ti -p 80:3336 -v ~/go/src/github.com/zwh8800/md-blog-gen:/app ubuntu:15.10 bash
root@8b94129944d0:/# cd /app
root@8b94129944d0:/# ./md-blog-gen -log_dir log
```
现在在浏览器里输入 `http://docker所在机器ip/` 看看是不是已经开始运行了？

在docker中，`-v` 是类似挂载的选项，可以把宿主机的目录挂载到容器中。可以看见，在使用docker时，大家都是很粗犷的，直接把app放到根目录下wwww。

### 把容器打上 tag

刚才执行过命令之后，我们可以把这个状态下的容器打一个tag，它就可以变成一个镜像（**image**）。
```bash
docker commit -m "Release md-blog-gen image" -a "zwh8800" 15b042d970c9 zwh8800/md-blog-gen:latest
```
现在执行一下 `docker images` 是不是多了一个镜像？

### Dockerfile

有了个直观认识之后大家又会感觉 `不给力啊老湿` 着我每次都得手动执行还不如我以前呢。
<center>
![坑爹呢这是][1]
</center>

所以docker还有法宝一件Dockerfile。这个东西不仅简化而且统一了大家的部署流程。

先看看md-blog-gen的Dockerfile
```Dockerfile
FROM alpine:3.3
MAINTAINER zwh8800 <496781108@qq.com>

WORKDIR /app

RUN apk update && apk add ca-certificates

ADD ./md-blog-gen /app
ADD ./template /app/template

VOLUME /app/log
VOLUME /app/config

EXPOSE 3336

CMD ["./md-blog-gen", "-log_dir", "log", "-config", "config/md-blog-gen.gcfg"]

```
非常之 `短小` 

所以逐句解释一下

- 以alpine:3.3为基础构建镜像
- 维护者是我
- 当前目录设置为/app
- 安装一下我需要的依赖
- 把需要的文件放到容器里（ADD命令可以直接ADD一个tar.gz，可以自动解压）
- 指明镜像的挂载点
- 指明镜像暴漏的端口
- 镜像的默认执行命令

把Dockerfile放到项目的目录下面，执行一下 `docker build -t zwh8800/md-blog-gen:latest .` 就开始构建
```bash
Step 1 : FROM alpine:3.3
d7a513a663c1
Step 2 : MAINTAINER zwh8800 <496781108@qq.com>
Using cache
dcf2dbbf66e2
Step 3 : WORKDIR /app
Using cache
d8aa8ad0b356
Step 4 : RUN apk update && apk add ca-certificates
Using cache
9260849655f9
Step 5 : ADD ./md-blog-gen /app
Using cache
1a21d6e13904
Step 6 : ADD ./template /app/template
Using cache
449e6a44d38b
Step 7 : VOLUME /app/log
Using cache
402f6b0dc5b3
Step 8 : VOLUME /app/config
Using cache
5d0b036a04d7
Step 9 : EXPOSE 3336
Using cache
87a65b9eff28
Step 10 : CMD ./md-blog-gen -log_dir log -config config/md-blog-gen.gcfg
Using cache
e43ef3612d6b
Successfully built e43ef3612d6b
```

成功了，赶紧的 `docker run --name blog -d -v log:/app/log -v config:/app/config zwh8800/md-blog-gen` 啊，这次我们加上了 `-d` 选项，这个可以让container后台运行，另外加上了一个 `--name` 可以给容器起个名字。现在，它真的像一个服务了。

### 管理容器

最常用的肯定是操作肯定是启停
```bash
# 使用容器名
docker start blog
# 使用容器id
docker stop e43ef3612d6b
# 容器id不用打全部，前几位就可以
docker restart e43e
```
其他要做的就是在 `/etc/rc.local` 里加一句 `docker star blog` 就好了，保证开机时服务启动。

## database

另外比较关心的是，我们的服务依赖的服务应当放在哪里。首当其冲的问题就是数据库怎么办。

具体有这三种方式吧。

### 应用＋数据库组成镜像

就是在镜像里安装上数据库，优势是部署方便，劣势就是不同应用无法共享数据库了。而且这样不很符合现在 **immutable server** 的概念。

### 应用数据库单独为镜像

这样保证了共享数据库，使用docker link或者其他工具来打通容器。

### 数据库独立出来

有些公司的数据库是单独部署的，或使用云服务，这样就没必要放在docker中了。

### 关于docker容器之间相互打通

docker默认有 `--link` 选项，但是现在已经不推荐了。目前有一些集群方案可供使用

- [kubernetes](http://kubernetes.io/)
- [docker swarm](https://github.com/docker/swarm)
- [docker compose](https://docs.docker.com/compose/)

具体的坑大家自己踩啦233

## 坑

上次同事的分享会上谈了一些使用docker过程中的大坑，有空再谈。

  [1]: https://ss0.bdstatic.com/94oJfD_bAAcT8t7mm9GUKT-xh_/timg?image&quality=100&size=b4000_4000&sec=1459619617&di=854e04f972bc3c5e6bddddb01ed6a637&src=http://i3.sinaimg.cn/gm/2015/0104/U7232P115DT20150104121600.png
  [2]: http://static.zybuluo.com/zwh8800/9eljwd5yrke20m5n2v34f02t/docker-distribute-shapes.001.png
  [3]: http://static.zybuluo.com/zwh8800/66q85iwi6l7t8v3ngmhsx8jl/docker-distribute-shapes.002.png
  [4]: http://static.zybuluo.com/zwh8800/ew6an4tfwra4eauo9yt7g9uq/docker-distribute-shapes.003.png
