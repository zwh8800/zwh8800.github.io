---
title: "用 thttpd+lua+cgi+jQuery mobile 搭建自动关机服务器"
date: "2014-06-30 00:00:00"
updated: "2014-06-30 00:00:00"
tags:
-  服务器
---


最近猎豹 wifi 共享精灵推出了一个 wifi 控制关机的功能. 我因为没有笔记本一直都用台式机 + linux nat + 无线 ap 来实现 wifi 共享 (见上次用虚拟机建立 NAT 曲线共享上网的经历忘了记录了). 所以看到这个功能之后一直眼红的不行, 在床上看视频到两三点再下去关电脑实在是破坏幸福感的事情. 所以嘛, 就又到了自己造轮子的时间.

[](/notename/ "archive 20140630")

首先分析一下需求, 很简单就是在手机上打开一个网页可以远程控制我的台式机关机.

所以必须要有一个 web 服务器, 另外一门 web 脚本语言也是必不可少的, 而且前端网页应该尽量漂亮, 并且适配手机.

首先 web 服务器应当尽量小巧, 一开始我用 shttpd 来做, 用了一天之后发现它对 http 验证支持的不很好. 所以便放弃他选择 thttpd 了. thttpd 也很小巧而且功能更多, 并且自称性能上不弱于 Apache.

然后脚本语言, 脚本语言的话我只会 lua 和 javascript, 如果用 javascript 的话需要用到 nodejs, 可是我有点不习惯 nodejs 的异步模型和一层一层的函数嵌套. 所以还是选 lua 吧. 而且 thttpd 支持 cgi, 可以和 lua 很好的适配

ok, 下面开始搭建环境. 因为对性能的要求不高, 所以决定在 Cygwin 下运行. 下载编译 thttpd, 直接 wget->./configure –prefix/usr->make->make install 就 ok 了.

中间可能在编译 htpasswd.c 文件时提示 getline 重定义. 直接把 htpasswd.c 文件里的所有 getline 改名成_getline 即可.

安装的时候会提示没有 / usr/man/man1 文件夹, 直接 mkdir /usr/man/man1 就 ok

thttpd 支持命令行启动同时也支持配置文件. 具体可以 man thttpd 来查看. 在源码包里的./contrib/redhat-rpm 文件夹有一个例子的配置文件. 我们把它改一下放到用户目录里:
```
# This section overrides defaults
dir=/home/Administrator/webroot
#chroot
user=Administrator# default = nobody
logfile=/var/log/thttpd.log
pidfile=/var/run/thttpd.pid
# This section _documents_ defaults in effect
# port=80
# nosymlink# default = !chroot
# novhost
cgipat=/*.cgi
# nothrottles
# host=0.0.0.0
# charset=iso-8859-1
```

然后就是安装 lua 了, Cygwin 源里直接就有, 装上即可.

在用户目录里建立一个 webroot 文件夹, 网站放这里.

建立两个文件, 一个叫 index.cgi, 一个叫 shutdown.cgi 内容如下:

```
#!/bin/lua
 
local Z_SHUTDOWN_FILE = "/tmp/zshutdown"
 
print("Content-type: text/html")
print()
 
local is_shutting_down
local time_to_shutdown
local file = io.open(Z_SHUTDOWN_FILE, "r")	--read模式, 可查看文件是否存在
if file == nil then
	is_shutting_down = false
 
else
	is_shutting_down = true
	local t1 = assert(file:read("*n"))
	time_to_shutdown = 30 - os.difftime(os.time(), t1)
	if time_to_shutdown < 0 then
		is_shutting_down = false
		os.remove(Z_SHUTDOWN_FILE)
	end
end

print[=[
<!Doctype html>
<html xmlns=https://www.w3.org/1999/xhtml>
<head>
<meta charset="utf-8">
<title>zzZ的自动关机</title>
 
<meta name="viewport" content="user-scalable=no, width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta http-equiv="mobile-agent" content="format=html5;">
 
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css">
<script src="https://code.jquery.com/jquery-1.8.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js"></script>
 
</head>
<body>
 
<div data-role="page" id="main">
 
	<div data-role="header" data-position="fixed">
		<h1>zzZ的自动关机</h1>
	</div>
 
	<div style="text-align:center;" data-role="content">
 
]=]
	if is_shutting_down then
	print[=[
		<p>您的电脑将在<span id="time" style="color:red">]=] print(time_to_shutdown); print[=[</span>秒后自动关机</p>
		<script>
			var t = ]=] print(time_to_shutdown); print[=[;
			function decrease()
			{ if (t > 0)$("#time").text(--t); }
			setInterval("decrease()", 1000);
		</script>
		<p>按动按钮来取消关机：</p>
		<a href="shutdown.cgi" data-rel="dialog" data-role="button" data-inline="true" data-icon="info">取消关机</a>
	]=]
	else
	print[=[
		<p>按动按钮来进行关机：</p>
		<a href="#shutdown_confirm" data-rel="dialog" data-role="button" data-inline="true" data-icon="info">关机</a>
	]=]
	end
print[=[
 
	</div>
 
	<div data-role="footer" data-position="fixed">
	<h1>Powered by zzZ</h1>
	</div>
 
</div>
 
<div data-role="page" id="shutdown_confirm">
	<div data-role="header">
		<h1>真的要进行关机?</h1>
	</div>
 
	<div data-role="content">
	<center>
		<a href="shutdown.cgi" data-rel="dialog" data-role="button" data-inline="true" data-icon="info">确认</a>
		<a href="#main" data-role="button" data-inline="true" data-icon="delete">取消</a>
	</center>
	</div>
 
	<div data-role="footer">
	<h1>Powered by zzZ</h1>
	</div>
 
</div>
 
</body>
</html>
]=]
```

```
#!/bin/lua
 
local Z_SHUTDOWN_FILE = "/tmp/zshutdown"
 
print("Content-type: text/html")
print()
 
local is_shutting_down
local file = io.open(Z_SHUTDOWN_FILE, "r")	--read模式, 可查看文件是否存在
if file == nil then
	is_shutting_down = false
	file = io.open(Z_SHUTDOWN_FILE, "w")	--write模式, 打开文件并写入
	file:write(os.time())
	file:close()
 
	os.execute('shutdown -s 30')
else
	is_shutting_down = true
	os.remove(Z_SHUTDOWN_FILE)
 
	os.execute('shutdown -a')
end

print[=[
<!Doctype html>
<html xmlns=https://www.w3.org/1999/xhtml>
<head>
<meta charset="utf-8">
<title>关机命令已接受</title>
 
<meta name="viewport" content="user-scalable=no, width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta http-equiv="mobile-agent" content="format=html5;">
 
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css">
<script src="https://code.jquery.com/jquery-1.8.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js"></script>
 
</head>
<body>
 
<div data-role="page" id="main">
 
	<div data-role="header" data-position="fixed">
		<h1>
]=]
 
if is_shutting_down then
	print "关机已取消"
else
	print "关机命令已接受"
end
 
print[=[
		</h1>
	</div>
 
	<div data-role="content">
	<center>
]=]
 
if is_shutting_down then
print[=[
		<p>关机命令已取消</p>
		<a href="javascript:location.reload(true)" data-role="button" data-inline="true" data-icon="info">返回</a>
]=]
else
print[=[
		<p>您的电脑将在<span id="time" style="color:red">30</span>秒后自动关机</p>
		<script>
			var t = 30;
			function decrease()
			{ if (t > 0)$("#time").text(--t); }
			setInterval("decrease()", 1000);
		</script>
		<a href="javascript:location.reload(true)" data-role="button" data-inline="true" data-icon="info">返回</a>
]=]
end
 
print[=[
	</center>
	</div>
 
	<div data-role="footer" data-position="fixed">
	<h1>Powered by zzZ</h1>
	</div>
 
</div>
 
</body>
</html>
 
]=]
```

ok 了, 效果如图:
![image_1bl0277mi94vhuh2v11d3gar49.png-219.7kB][1]
![image_1bl028649hrj10b9p66155e14jtm.png-153.8kB][2]
![image_1bl028n31qgj1ikq13e81ktcqam13.png-130kB][3]
![image_1bl029cp41lakb6l1f1m1tfmrf91g.png-136.7kB][4]
![image_1bl02a0ek97d1m54foe9suips1t.png-177.8kB][5]
![image_1bl02ajhhg2v1vqc1kmbmrm1ilh2a.png-124.4kB][6]

  [1]: http://static.zybuluo.com/zwh8800/f9e5nxrsul19mal0edw8p4c2/image_1bl0277mi94vhuh2v11d3gar49.png
  [2]: http://static.zybuluo.com/zwh8800/7lfovihp8gzsvxasli8e21ce/image_1bl028649hrj10b9p66155e14jtm.png
  [3]: http://static.zybuluo.com/zwh8800/0i0piuanimshib8yylomlau4/image_1bl028n31qgj1ikq13e81ktcqam13.png
  [4]: http://static.zybuluo.com/zwh8800/b4nzpv6egxd8v02ar2pryqz1/image_1bl029cp41lakb6l1f1m1tfmrf91g.png
  [5]: http://static.zybuluo.com/zwh8800/yesdko4og6c4izj08lc24o65/image_1bl02a0ek97d1m54foe9suips1t.png
  [6]: http://static.zybuluo.com/zwh8800/4g3vx68fnyc5jqvkmtwehqjr/image_1bl02ajhhg2v1vqc1kmbmrm1ilh2a.png
