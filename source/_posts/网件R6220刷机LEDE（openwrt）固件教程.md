---
title: "网件 R6220 刷机 LEDE（openwrt）固件教程"
date: "2017-08-20 07:22:39"
updated: "2017-09-18 08:41:52"
tags:
-  折腾
-  路由器
-  openwrt
-  lede
---


家里一直用的是网件的 R6220 路由器，之前一直用的是原厂固件，因为本人不太喜欢在主路由器上装奇奇怪怪的东西，另外是因为 R6220 一直都没有好用的固件可以刷，前几天逛论坛发现竟然已经有人破解了 R6220 可以刷 LEDE 和 pandora 了，忍不住手痒又去刷了一波固件。此文记录一下过程。

[](/notename/ "install lede on netgear r6220")

<!-- more -->

[toc]

> **请全程使用网线连接进行操作，操作时千万不要断电，因为 R6220 使用 NAND flash，刷坏后无法使用普通编程器修复，刷机有风险，请扶稳方向盘谨慎驾驶**

## 1. 开启路由器telnet

在浏览器打开 http://192.168.1.1/setup.cgi?todo=debug 这个网址，记着把 192.168.1.1 替换成你路由器的 ip 地址，成功后会显示 `Debug Enabled !` 说明已经成功。

使用 Mac 或 Linux 的用户，打开终端，执行 `telnet 192.168.1.1` ，可以登录到路由器的管理shell里，使用 windows 的用户，可以[点这里](https://the.earth.li/~sgtatham/putty/latest/w32/putty.exe)下载 putty，然后如下图，Host Name填路由器ip，port写23，connection type 选 telnet：

![image_1bnv9ksf91joebhc5uvi451l14p.png-84.3kB][1]

点击 open 之后，会出现一个黑屏窗口，显示 `R6220 login:` ，输入 `root` 按回车，会显示一个大的 logo 和一个 `#` 号（如下），此时说明已经登录成功了。

```
Welcome to
    _______  _______  ___     __  ____   _  _   ___
    |  ___  \|   __  ||   |   |__||    \ | || | /  /
    | |___| ||  |__| ||   |__  __ |     \| || |/  /
    |   _   /|   _   ||      ||  || |\     ||     \
    |__| \__\|__| |__||______||__||_| \____||_|\___\
                     =System Architecture Department=
#
```

## 2. 备份eeprom

> 此步骤可跳过，但有一定几率无法使用 Wi-Fi

准备一个格式化成 fat32 的U盘（最好重新格式化，卷标写成U），插入 R6220 的USB口中，然后在刚才的黑窗口里输入命令：`ls /mnt/shares`

会显示出你刚才优盘的卷标名，如果重新格式化成 U 了，那么就会显示一个 U。

下一步，执行 `cd /mnt/shares/优盘的卷标名` ，同理如果刚才显示 U 这里就应该执行 `cd /mnt/shares/U`。

如果没有报错的话就进行下一步：

```
dd if=/dev/mtd10 of=./mtd10.bin
```

这是为了把 eeprom 备份到U盘中。如果执行之后，显示一个 `#` 说明成功了。现在把U盘拔下来插到电脑上，可以看到一个 mtd10.bin 文件，把它复制到电脑上备份。

## 3. 刷写不死 bootloader pb-boot

从这里下载 pb-boot：

> 链接: https://pan.baidu.com/s/1jIONs6i 密码: nyn9

把这个文件放到U盘里，插入到路由器中。

使用 telnet 登陆到路由器，和第二步一样，执行 `cd /mnt/shares/U` 进入到U盘文件夹。执行下面的命令：

```
mtd_write write pb-boot-r6220-20170801.img Bootloader
```

成功后会显示：

```
Unlocking Bootloader ...
Writing from pb-boot-r6220.bin to Bootloader ...  [w]
```

接下来路由器关机，然后用针扎着reset键开机，开机后发现电源灯和wan口灯呼吸闪烁，说明进入了 bootloader，在浏览器中输入 192.168.1.1 会看到 pb-boot 的界面：

![image_1bnvblmm81d0t1hgfpfu1h0ft4116.png-107.3kB][2]

现在说明不死 bootloader 已经刷好了，可以随意折腾路由器而不怕刷坏了，无论何时感觉刷坏了，都可以用针扎着reset键开机，来反复刷机重置系统。

> 小知识：bootloader 是在操作系统运行之前先运行的一个小程序，类似电脑的 bios，折腾路由器时就算把系统搞坏了，只要 bootloader 没被破坏，都可以刷回出厂设置的。

### 3.1 mac 用户会遇到的坑

使用 mac 的用户再刷写了 pb-boot 之后，会发现无法获取到 IP 地址，可以这样操作：

在**系统偏好设置**中点网络，把网卡设置成下图所示：

![image_1bnvc6apsorr15en13he1l7s1mei1j.png-107.3kB][3]

打开**终端**反复执行如下命令：

```
sudo arp -ad
sudo arp -s 192.168.1.1 ff:ff:ff:ff:ff:ff
```

第一次可能会要求你输密码，输入即可

每执行一遍就再浏览器中刷新一次 192.168.1.1 ，直到浏览器能打开网页后停止执行命令。

## 4. 刷 LEDE 官方固件

一开始我是在 [恩山无限论坛](http://www.right.com.cn/forum/thread-208580-1-1.html) 下载的网友编译的固件，他的固件本身集成了好多功能，比如 广告屏蔽大师和s-s，不爱折腾的人刷他的固件用自带的功能就够用了，但是他的固件有个问题，固件的内核版本不是官方的版本，没办法安装官方软件仓库里的 kmod 软件包（可以强制安装，但是会大几率无限重启），另外固件的 opkg 好像也没有配置好，安装软件包会比较折腾。所以我建议还是先刷网友版，然后升级成官方版。

先从这里下载恩山网友版固件

> 链接: https://pan.baidu.com/s/1c1YSCLy 密码: 36vm

然后在 192.168.1.1 里，点击 browse 选择刚才下载的网友版固件，再点击 Firmware update，等 1 分钟就刷好了。

再次刷新 192.168.1.1 网页，发现已经进入 lede 的界面了。

![image_1bnvcca3pf6dfb6177rr9b70o20.png-23.1kB][4]

用户名填 root，密码输admin，进入到管理界面中。

然后左侧点击**网络**、**接口**，把 WAN 口配置好，尝试一下能不能上去网。

对于不想折腾的朋友到此为止就可以了，恩山网友版的固件足够好用，喜欢折腾的朋友继续看下面（如果发现Wi-Fi无法正常使用的请看[最下面](#8-找不到-wi-fi或wi-fi信号很差)）。

点击左侧的**系统**，然后点击**备份/升级**。现在咱们要升级成 lede 官方版。

从这里下载官方版：https://downloads.lede-project.org/snapshots/targets/ramips/mt7621/lede-ramips-mt7621-r6220-squashfs-sysupgrade.tar

或者从中科大的镜像里下载：http://mirrors.ustc.edu.cn/lede/snapshots/targets/ramips/mt7621/lede-ramips-mt7621-r6220-squashfs-sysupgrade.tar

在刷写新的固件那一栏，选择刚下载的固件，然后点击刷写固件。

等 1 分钟后，路由器自动重启，此时官方固件已经刷好了。

## 5. 配置官方固件

官方固件默认不开启Wi-Fi，默认不安装web管理界面，所以我们需要先使用命令行进行配置。

使用 `ssh root@192.168.1.1` 登陆，windows的朋友还使用 putty，但是 port 需填写 22，connection type 选 SSH。

然后输入 root 回车，再输入 admin 回车。

![image_1bnvd5mqeofhlp61sa51q0c11fm2d.png-22.6kB][5]

接着会看到一个 LEDE 的 logo，说明登陆成功了，下一步安装web管理界面。

> 以下内容选作

因为 lede 默认的软件仓库可能会比较慢，所以我们可以换成中科大的源，先执行vim：

```
vim /etc/opkg/distfeeds.conf
```

用 vim 打开 opkg 配置文件，然后多按几次键盘上的 `dd` 会发现之前的内容被删除了。之后按一下 键盘上的 `I` ，然后复制下面的内容，在终端里粘贴（putty用户直接在黑窗口里右键就可以了）

```
src/gz reboot_core http://mirrors.ustc.edu.cn/lede/snapshots/targets/ramips/mt7621/packages
src/gz reboot_base http://mirrors.ustc.edu.cn/lede/snapshots/packages/mipsel_24kc/base
src/gz reboot_luci http://mirrors.ustc.edu.cn/lede/snapshots/packages/mipsel_24kc/luci
src/gz reboot_packages http://mirrors.ustc.edu.cn/lede/snapshots/packages/mipsel_24kc/packages
src/gz reboot_routing http://mirrors.ustc.edu.cn/lede/snapshots/packages/mipsel_24kc/routing
src/gz reboot_telephony http://mirrors.ustc.edu.cn/lede/snapshots/packages/mipsel_24kc/telephony
```

然后按一下键盘上的 ESC 键，然后依次输入 `冒号`、`w`、`q`、`回车键`，退出到 shell 界面，现在中科大源就配置好了。

> 以上内容选作

接下来执行opkg来安装web管理界面，中文翻译和material皮肤：

```
opkg update
opkg install luci
opkg install luci-i18n-base-zh-cn
opkg install luci-theme-material
```

短暂等待后就安装好了，在浏览器打开 192.168.1.1 就能看到路由器管理界面了。

> 注意，此处有个小坑，如果在刚才升级到原版系统时，把 **保留配置** 的勾给去掉了，那么此时路由器是无法上网的，也就无法从软件仓库安装，所以如果你和我一样手贱去掉了那个勾，你现在可以把 R6220 接到一个已经配置好能上网的路由器的 LAN 口上，然后再进行 opkg install 操作。

## 6. 安装upnp

官方版固件默认没有 upnp，需要ssh登陆到路由器执行下面命令安装：

```
opkg update
opkg install luci-app-upnp
```

或者也可以在**系统**、**软件包**里安装 `luci-app-upnp`

然后在 **服务**、**UPNP**里勾选 Start UPnP and NAT-PMP service，点击保存&应用

## 7. 编译广告屏蔽大师（adbyby）

[广告屏蔽大师（英文名adbyby）](https://github.com/kuoruan/luci-app-adbyby)是一个很好用的 lede 应用，能屏蔽爱奇艺、优酷等一系列广告而且不用等待。

### 7.1 下载SDK

中科大源：http://mirrors.ustc.edu.cn/lede/snapshots/targets/ramips/mt7621/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64.tar.xz

```
wget http://mirrors.ustc.edu.cn/lede/snapshots/targets/ramips/mt7621/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64.tar.xz
tar xvf lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64.tar.xz
```

### 7.2 下载adbyby

```
git clone https://github.com/kuoruan/luci-app-adbyby.git
```

### 7.3 更新feeds

```
cd ~/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64
./scripts/feeds update -a
```

### 7.4 把 adbyby 放进 SDK

```
cd ~/luci-app-adbyby
cp ./adbyby ~/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64/package -r
cp ./luci-app-adbyby ~/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64/feeds/luci/applications -r
```

把 adbyby 放到 package 里，把 luci-app-adbyby 放到 feeds/luci/applications 里。

### 7.5 再更新 feeds

```
cd ~/lede-sdk-ramips-mt7621_gcc-5.4.0_musl.Linux-x86_64
./scripts/feeds update -a
./scripts/feeds install luci-app-adbyby
```

### 7.6 编译

```
make menuconfig
```

会打开一个界面，在里面用上下键移动光标，用回车键选择，先选 LuCI，再选 Appications，然后找到 luci-app-adbyby 按两下空格使前面变成 `[*]` ，然后一直按 ESC 退出，退出前会询问是否保存，选 YES。

然后执行 

```
make V=99
```

最后会在 bin 文件夹编译出 luci-app-adbyby.ipk 文件，上传到路由器的/tmp 文件夹，执行 `opkg install luci-app-adbyby.ipk` 进行安装。

## 8. 找不到 Wi-Fi，或Wi-Fi信号很差

如果刷了 lede 之后找不到Wi-Fi，可以把 eeprom 还原成原厂。

### 8.1 把之前备份的 `mtd10.bin` 放到路由器中

在终端里执行：

```
scp mtd10.bin root@10.0.0.1:/tmp
```

使用 windows 的用户可以下载一个 [WinScp](https://sourceforge.net/projects/winscp/files/WinSCP/5.9.6/WinSCP-5.9.6-Portable.zip/download) 来远程复制文件：

File protocol 选择 scp，hostname输入路由器IP，port写22，username写root，password写密码。

![image_1bnvf7v6un84c0v11qm1vku1sd37.png-39.8kB][7]

点击login，然后再右侧窗口双击一下 `..` ，然后再双击 tmp 文件夹。然后再左侧窗口找到刚才备份的 mtd10.bin 文件，直接拖到右侧窗口的空白区域。

![image_1bnvfagtt1k5f105kcgr7r132a3k.png-193.8kB][8]

### 8.2 还原 eeprom

使用 putty 或 ssh 登陆路由器，然后执行下面命令：

```
mtd -r write /tmp/mtd10.bin factory
```

成功后会自动重启。

然后在**系统**、**备份/升级**里重新上传sysupgrade.tar，并且不勾选**保留设置**。

  [1]: /images/1a797a80091c5a2290a090407be0801f.png
  [2]: /images/6f4b994612ac748b39bf5768d96db680.png
  [3]: /images/3e9a5f6d55c07d805533d03e2d3b8a24.png
  [4]: /images/772ab39a5aa6a5091dc7111ab7983f0f.png
  [5]: /images/6450c2de39907259390b2e4f293b4ec4.png
  [6]: /images/bd8cad4893f595c6e743cdd80dc143c2.png
  [7]: /images/b2fc85fcbac6955b1c2fc2c68fa01d89.png
  [8]: /images/38b4a52764c74bf82b95b87032f00a2f.png
