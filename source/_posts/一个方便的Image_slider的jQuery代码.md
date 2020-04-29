---
title: "一个方便的 Image_slider 的 jQuery 代码"
date: "2014-04-14 00:00:00"
updated: "2014-04-14 00:00:00"
tags:
-  JS
-  jquery
-  前端
---


UDP, ICMP, IP 协议校验和的计算

[](/notename/ "archive 20140414")

```JS
<html>
<head>
<script src="script/jquery-1.11.0.min.js"></script>
</head>
 
<body>
 
<div id="slider">
	<img style="position:absolute" src="images/sliser_bg_img_1.jpg" />
	<img style="position:absolute;display:none" src="images/sliser_bg_img_2.jpg" />
	<img style="position:absolute;display:none" src="images/sliser_bg_img_3.jpg" />
</div>
 
<script>
	var slider = $("#slider");
	var img_list = slider.children();
	var current = 0;
 
	setInterval("change()", 3000);
 
	function change()
	{
		$(img_list[current]).fadeOut(800);
		current++;
		if (current >= img_list.length)
		{
			current = 0;
		}
		$(img_list[current]).fadeIn(800);
	}
 
</script>
 
</body>
</html>

```


