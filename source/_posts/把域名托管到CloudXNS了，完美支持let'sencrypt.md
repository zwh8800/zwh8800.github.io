---
title: "把域名托管到 CloudXNS 了，完美支持 let's encrypt"
date: "2016-05-01 08:41:51"
updated: "2016-05-01 09:07:25"
tags:
-  闲扯
-  DNS
-  CloudXNS
---


[lengzzz.com](https://lengzzz.com) 这个域名我已经用了6年了，当年年少无知用了 oray 的服务，就为了一个花生壳的功能（tplink自带花生壳）。现在越发感觉 oray 的服务质量不很好。各省解析速度不一，国外就更慢了。尤其是不支持 `let's encrypt` 让我好生郁闷。所以赶紧换上了 CloudXNS 。

CloudXNS 的页面就看着比较顺眼。据说 DNSPod 也不错，但是我感觉网页太丑了，就没有使用它，哈哈，所以证明一句话 **你的颜值决定了别人会不会去发现你的内心** 。

![QQ20160501-0@2x.png-321.5kB][1]

注册了之后发现使用超级方便，只给你显示了一个超大的输入框，让你输入自己的域名。

![QQ20160501-1@2x.png-43.7kB][2]

输入之后，就进入了控制台节目了，好像你的域名已经托管在 CloudXNS 上了一样，当你设置好解析之后，只需要把之前域名的 NS 地址设置到 CloudXNS 上就好了。整个用户体验相当舒服。

设置好之后，控制台上会实时显示接管状态。不过5分钟，就可以用了。立即用 let's encrypt 更新一下 ssl 证书。果然可以用了。

![QQ20160501-2@2x.png-70.3kB][3]

最后来张测速图吧。

![QQ20160501-3@2x.png-138.9kB][4]

  [1]: http://static.zybuluo.com/zwh8800/gmz55dfpsc6k07y0ctrcf80y/QQ20160501-0@2x.png
  [2]: http://static.zybuluo.com/zwh8800/cpgnk0wkgntpg08az7heqecr/QQ20160501-1@2x.png
  [3]: http://static.zybuluo.com/zwh8800/a3cvhjcpf7v0d965cnxeceqo/QQ20160501-2@2x.png
  [4]: http://static.zybuluo.com/zwh8800/nh72858jdjk7fwt42x1us6rp/QQ20160501-3@2x.png
