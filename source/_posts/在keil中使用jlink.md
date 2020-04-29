---
title: "在 keil 中使用 jlink"
date: "2014-03-22 00:00:00"
updated: "2014-03-22 00:00:00"
tags:
-  jlink
-  单片机
---


在 keil 中使用 jlink

[](/notename/ "archive 20140322")

先安装 jlink 的工具包. 在官网下载需要输序列号, 鉴于国内大多使用盗版. 在本站放一个镜像供大家下载: https://lengzzz.com/download/Setup_JLinkARM_V480.zip

下载后安装

安装好之后插上 jlink. 打开 keil

点击 Target Option 按钮:
![image_1bl07o71mk7i521141i1rbr6nj9.png-17kB][1]

然后打开 Debug 选项卡, 选择右边的 use jlink
![image_1bl07om2r1ecb7vtphf4bdpnjm.png-24.1kB][2]

然后点击 Utilities 选项卡, 也选择 jlink:
![image_1bl07p8up16eg8n53951jbvk4s13.png-18.1kB][3]

接着点击 Settings 选择 add 然后在列表中选择我们的器件:
![image_1bl07pm2ni37imc1vsi5tt9s61g.png-30.3kB][4]

之后勾选上 Reset and run:
![image_1bl07q50dkns1flb1hid1ffn19ot1t.png-20.2kB][5]
一路 ok 后, 应该可以下载和调试程序了

  [1]: http://static.zybuluo.com/zwh8800/7jgd86b8v29dssmfeya7paxn/image_1bl07o71mk7i521141i1rbr6nj9.png
  [2]: http://static.zybuluo.com/zwh8800/pbkcy680p6wxoi54xk8gip7e/image_1bl07om2r1ecb7vtphf4bdpnjm.png
  [3]: http://static.zybuluo.com/zwh8800/s353yhzpofjn0l6la6cpj862/image_1bl07p8up16eg8n53951jbvk4s13.png
  [4]: http://static.zybuluo.com/zwh8800/p47bb6vw9z3eivk7mzjx2sy0/image_1bl07pm2ni37imc1vsi5tt9s61g.png
  [5]: http://static.zybuluo.com/zwh8800/poxp24jgkqvkypwbo3w597mz/image_1bl07q50dkns1flb1hid1ffn19ot1t.png
