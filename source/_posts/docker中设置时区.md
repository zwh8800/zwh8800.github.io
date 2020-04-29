---
title: "docker 中设置时区"
date: "2016-04-07 05:15:31"
updated: "2016-04-23 12:19:46"
tags:
-  docker
---


昨天使用 docker 时遇到一个问题，应用输出的时间永远是utc时间，一开始我检查了服务器的时区，发现没问题。然后我就以为是代码中的bug，寻找了很久bug后突然想起docker中的时区应该和宿主机不一致。修改了一下果然好了。

[](/notename/ "timezone in docker")

修改docker镜像时区的方法和修改普通Linux系统时区的方法一致。具体方法要看使用的是什么发行版。

比如我使用的alpine方法如下：
```bash
apk add tzdata 
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime 
echo "Asia/Shanghai" > /etc/timezone
```
写到Dockerfile里就是：
```Dockerfile
RUN apk update && apk add ca-certificates && \
    apk add tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

```

update: 

在ubuntu中，设置好时区之后需要执行一下
```bash
dpkg-reconfigure -f noninteractive tzdata
```
否则不会生效

