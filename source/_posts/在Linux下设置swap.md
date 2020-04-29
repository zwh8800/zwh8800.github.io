---
title: "在Linux下设置swap"
date: "2016-04-10 07:31:11"
updated: "2016-04-23 12:18:17"
tags:
-  linux
---


今早起来发现博客的数据库挂了，赶紧用手机上的ConnectBot连上去把mysql启动。看了下日志大概是因为内存不够用且没设置swap，所以mysql进程申请不到内存挂了（小内存服务器桑不起）所以赶紧把swap搞上，这样至少能让服务不轻易挂掉。

这里记录一下，以备遗忘。

[](/notename/ "add swap on linux")

大概分三步

- 生成一个空文件
- 把文件格式化成swap格式
- 挂载

```bash
# create swap file
sudo dd if=/dev/zero of=/swapfile bs=128M count=4

# adjust permission
sudo chmod 600 /swapfile

# format swap
sudo mkswap /swapfile

# mount swap
sudo swapon /swapfile

# see if ok
sudo swapon -s

```

没问题的话，最后一个命令会显示
```
Filename				Type		Size	Used	Priority
/swapfile               file		524284	0	    -1
```

另外，dd程序花的时间比较长，因为它确实写入东西了。但其实Linux的文件系统有个功能，它可以忽略（合并？）文件中的0，比如一个1G的文件，只有前面3个字节和后面3个字节写字了，其余都是0，那么在硬盘上只会记录几个字节，而不会把上G的0写到硬盘中，这样就能加快性能。

所以可以使用 `fallocate` 程序。
```bash 
sudo fallocate -l 512M /swapfile
```

这个应该会很快。

最后，修改一下fstab，保证开机自动挂载：
```
sudo vim /etc/fstab

# write this to fstab
/swapfile   none    swap    sw    0   0
```

