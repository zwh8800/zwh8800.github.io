---
title: rclone挂载Google群友盘 + OverlayFS + tmm + kodi打造家庭媒体中心
date: "2021-08-17 10:54:00"
tags:
- rclone
- OverlayFS
- kodi
- 多媒体
---

之前我的家庭媒体中心一直是使用本地 nas 存高清片源 + tmm（TinyMediaManager）做媒体搜刮器 + 电视上安装 kodi 做播放器的方案，但是这种方式的缺点是总得自己花时间下载片源。后来白嫖了一段时间别人的 gayufan emby，然鹅现在也用不了了，自己又懒着去签到+考试。索性去tg群里买了个群友盘权限，56元不限时间，可以说是很良心了。现在持续更新的片源有了，于是这周末折腾了下媒体管理中心，踩坑各种不同的方案之后选择了一个网上不太常见但个人感觉很好用的方案，于是记录一下。

![kodi 截图][1]

<!-- more -->

## 方案对比

|  方案   | 是否能播放原始文件  | 搜刮 | 硬件解码 |
|  ----  | ----  | ---- | ---- |
| plex | 需付费直接放弃 | | |
| emby  | 大多数ok，因字幕等原因会触发转码 | 速度一般，无法手动搜索 | 需付费开启 |
| jellyfin | 大多数ok，因字幕等原因会触发转码 | 速度一般，准确性一般，无法手动搜索 | 可开启 |
| tmm + kodi | 可以 | 速度较快，可手动搜索，提升准确性 | 取决于电视 | 

我的需求其实比较简单，观影设备只有客厅和卧室的电视，没有在移动端、web端看剧的需求。需要支持多端能同步观影记录。需要能尽可能播放原始文件，一方面是对画质的要求，另一方面是考虑家庭服务器的负载。

一开始尝试了 emby ，搜刮直接花了一个白天的时间，然后发现海报怎么都加载不出来，另外很多视频都会走转码（我就很奇怪为啥，我电视端明明支持这种格式，服务端仍然会转码），emby 的硬件解码需要收费，尝试了下破解也不太好用，遂放弃。然后尝试了 jellyfin，这个转码倒是比较完美的支持硬件解码了，然鹅搜刮还是难用，一是慢，二是不好进行微调。最后还是用回了 kodi。下面是 kodi 方案的教程。

## rclone 配置

rclone 的作用是把各种网盘挂载到 Linux 服务器上，这样访问网盘的文件就像是访问本地的文件夹一样方便。

#### 安装
安装的话直接按照官方的方法，一条命令完事：

```bash
curl https://rclone.org/install.sh | sudo bash
```

#### 初始化
安装好了之后首先需要配置下，在终端执行 `rclone config` 命令后是一个交互式的命令行界面，能看懂英文的话照着提示一步一步来就行了，主要就是中间会给你一个url，在浏览器里用你的Google账号打开然后进行授权，得到一个授权码填到 rclone 里就行了，很简单就不赘述了，详细可以参考这个教程： https://ley.best/rclone/ 

#### 挂载
挂载同样是一条命令

```bash
rclone mount g: /home/gdrive-lower -copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000 --daemon
```

- g: 代表初始化的时候给网盘起的名字
- /home/gdrive-lower：代表要挂载的位置，需要先创建出这个目录
- 其他参数暂时不用管
- 这个命令会阻塞，为了开机自启动，可以创建一个systemd服务，或者更简单的放在rc.local文件里也行

挂载好了之后，可以发现 /home/gdrive-lower 目录里已经是网盘上的文件了。不过都是只读的，我们搜刮到额外的信息海报等信息是无法存储到这个目录的，所以就需要 Linux 上另一个神器 OverlayFS 来解决这个问题。

## OverlayFS 配置

OverlayFS 是 Linux 的一个文件系统，用途很广泛，比如 openwrt、docker 的文件系统就基于这个。简单讲一下他的作用。

OverlayFS 可以多个目录进行合并成一个新的目录，比如a、b两个目录里分别有 1.mp4 和 1.nfo 文件，那么他们合并成的新目录就同时包含了1.mp4和1.nfo两个文件。另外 OverlayFS 也有层级的概念，如果a、b目录有同名的文件，那么更高层级的目录的文件会优先被访问。

由于 OverlayFS 这么好用的特性，很适合用在我这个场景，能方便的把只读的目录变成可读写的。

![overlayfs 原理][2]

#### 创建必要目录

首先创建两个目录：

```bash
mkdir ~/gdrive-upper ~/gdrive-work /home/gdrive
```

- ~/gdrive-upper：作为上层目录，对谷歌云的读写都会保存到这里，而不会真正写入谷歌云的挂载点
- ~/gdrive-work：存储临时文件
- /home/gdrive：合并出的新目录


#### 挂载 OverlayFS

同样是一条命令

```bash
sudo mount -t overlay overlay -o lowerdir=/home/gdrive-lower,upperdir=～/gdrive-upper,workdir=～/gdrive-work /home/gdrive
```

- lowerdir=/home/gdrive-lower：代表底层目录，写操作不会实际写到这里，读操作优先读取上层目录，读不到的才会读这里（比如视频文件）
- upperdir=～/gdrive-upper：代表上层目录，读写优先对这里操作，会保存nfo、poster等文件
- workdir=～/gdrive-work：临时目录，系统需要的，我们不用管他的作用
- /home/gdrive：合并出的新目录，我们后续只对他进行访问


#### 后续使用


> 下面samba 的 docker 有点问题，会进行 chown 修改文件所有者，这会导致文件被写入到upper上层目录，会使服务器硬盘爆炸。我最后使用的 ssh 协议（sftp）来访问，kodi上需要安装下 sftp 插件

既然已经搞定了读写的问题了，那么后续无论是要通过 smb 协议还是 ftp 协议访问都是配置一下的事了，~~我这里使用的是 docker 启动一个 smb 服务器：~~

```bash
docker run -d \
    --name samba \
    -e TZ=Asia/Shanghai \
    --net host \
    -v /home/gdrive:/mount \
    dperson/samba -p \
    -u "xxx;xxx" \
    -s "gdrive;/mount;yes;no" \
    -S
```

- -v /home/gdrive:/mount：这里填写合并后的目录，改成你自己的
- -u "xxx;xxx"：samba的用户名密码，自己改一个


## TinyMediaManager

TinyMediaManager 是一个很好用的媒体搜刮器，能很方便的搜挂电影、电视剧的片名、介绍、海报、缩略图等等，并且存储成 kodi、emby 能读取的 nfo 文件。

![overlayfs 原理][3]

我们基本上只会用到左上角的两个按钮。

#### 更新源

在设置里首先配置下要搜刮的目录，然后点击左上角的更新源按钮，他就开始自动搜索媒体文件了。

#### 搜刮

等搜索结束后，点击筛选，在里面选择新增季或新增电影，能筛选出刚刚新搜刮到的媒体文件，然后全选他们，点击搜索&剐削按钮旁边的下拉菜单，点击自动匹配，它会自动一个一个下载 nfo 和海报文件，最后匹配度低于 75% （在设置里可以调整）的视频，会提示给你来手动进行搜索匹配，速度挺快的，300 部电影十几分钟就搞好了。

#### docker

每次使用电脑可能会有所不便，毕竟个人电脑不能24小时开机，而服务器可以，其实 tmm 也支持docker:

```bash
docker run \
    --name=tinyMediaManager \
    --add-host=api.themoviedb.org:13.224.161.90 \
    --add-host=image.tmdb.org:104.16.61.155 \
    --add-host=api.themoviedb.org:13.35.67.86 \
    --add-host=www.themoviedb.org:54.192.151.79 \
    -v /home/gdrive:/media \
    -p 5800:5800 \
    -p 5900:5900 \
    romancin/tinymediamanager:latest
```
启动后就可以通过浏览器打开 http://192.168.1.123:5800/ 访问 tmm 了，这样开启搜刮任务后个人电脑就可以关机了，等有时间了再用浏览器看结果。事实上 docker 内部启动了个 xorg 桌面服务，然后通过 http 来访问 vnc，还是稍微有点卡顿的。

## kodi

我有个特殊的需求是需要在客厅和卧室的不同电视里同步播放进度，kodi 默认是把媒体库存储到本地的 sqlite 里，但也支持存储到远端 mysql。mysql 服务器可以用docker启动，也可以用群晖 nas 里的 MariaDB 软件包。如果安装教程较多，不再赘述。

针对 kodi 需要写一个 advancedsettings.xml 配置文件：

```xml
<advancedsettings>
    <videodatabase>
        <type>mysql</type>
        <host>192.168.1.123</host>
        <port>3306</port>
        <user>kodi</user>
        <pass>kodi</pass>
    </videodatabase>
    <videolibrary>
        <importwatchedstate>true</importwatchedstate>
        <importresumepoint>true</importresumepoint>
    </videolibrary>
</advancedsettings>
```

上面的 ip 地址用户名密码改成你自己的 mysql 地址。

把这个文件存储到每个电视的 `Android/data/org.xbmc.kodi/files/.kodi/userdata/` 下面，重启 kodi 后他搜挂到的信息就存储到 mysql 了。

（访问电视的文件，可以安装一个 ES文件浏览器，然后开启 ftp 访问）

另外推荐一个很好看的 kodi 皮肤 `Arctic: Zephyr - Reloaded`，在系统自带的插件库里就能安装，个人感觉比 emby、jellyfin 的 android app 好用/好看多了 😂

![kodi 截图][4]

## 总结

当然这个方案也不是完美的，只是比较切合我个人的需求，比如搜刮不能自动进行，需要定期手工打开 TinyMediaManager 进行搜刮。另外对 iOS 移动端支持的不好，appstore 无法直接安装 kodi。

  [1]: /images/IMG_9433.PNG
  [2]: /images/20171029124743310.jpeg
  [3]: /images/WechatIMG4.png
  [4]: /images/IMG_9431.PNG
