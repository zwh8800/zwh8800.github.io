---
title: "setuid和seteuid"
date: "2014-01-17 00:00:00"
updated: "2014-01-17 00:00:00"
tags:
-  系统编程
-  linux
-  unix
---


linux下有4种uid, 真实uid(real user id), 有效uid(effective user id), 被保存的uid(saved user id)和文件系统的uid. 本文详细讲解一下相关内容。

[](/notename/ "archive 20140117")

linux下有4种uid, 真实uid(*real user id*), 有效uid(*effective user id*), 被保存的uid(*saved user id*)和文件系统的uid.

先说下这两个系统调用, 再说这几种uid:

- setuid(uid)首先请求内核将本进程的[真实uid],[有效uid]和[被保存的uid]**都**设置成函数指定的uid, 若权限不够则请求**只**将effective uid设置成uid, 再不行则调用失败.
- seteuid(uid)仅请求内核将本进程的[有效uid]设置成函数指定的uid.

再具体来说setuid函数的话是这样的规则:

- 当用户**具有超级用户权限**的时候,setuid 函数设置的id对**三者都**起效.【规则一】
- 否则,**仅当该id为real user ID 或者saved user ID时,该id对effective user ID起效**.【规则二】
- 否则,setuid函数调用失败.

现在说下前三种uid

real uid表示进程的实际执行者, **只有root才能更改real uid**, effective uid用于检测进程在执行时所获得的访问文件的权限(既 但进程访问文件时, 检测effective uid有没有权限访问这个文件), saved uid用于保存effective uid, **以便当effective uid设置成其他id时可以再设置回来**(下面着重讲).

一般情况下, 当一个程序执行时(既调用exec), **进程的effective uid会和real uid一致**, 但是可执行文件有一个set-user-ID位, 如果这个set-user-ID位被设置了, 那么执行exec后, **进程的effective uid会设置成可执行文件的属主uid, 同时saved uid也会被设置成effective uid**.

举例说明: 用户zzz执行了文件a.out, a.out的属主为hzzz且设置了set-user-ID位. 现在本进程的real uid为zzz, effective uid = saved uid = hzzz.

进程执行了一会之后, 突然想用zzz的权限访问一个文件, 于是进程可能会调用setuid(zzz), 此时检测进程的权限, 进程的effective uid是hzzz, 不是root, 所以不能更改real uid(只有root才能更改real uid[setuid规则一不满足]), 所以只能设置effective uid, 发现effective uid可以被设置为zzz(因为real uid是zzz[规则二满足]), 所以函数调用成功, 只将effective uid设置成zzz.

现在进程访问完zzz的文件了, 又想回到hzzz的环境中执行, 所以有可能会调用setuid(hzzz), 这次saved uid的作用就表现出来了, 因为刚刚只是改变了effective uid, 而saved uid还保存着之前的effective uid, 所以可以调用setuid(hzzz)来要回原来的权限([规则二满足]).

代码:

```c
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
 
int main()
{
	printf("real uid is %d\n", getuid());
	printf("effective uid is %d\n", geteuid());
	getchar();
 
	if (seteuid(1001) == -1)	/* zzz = 1001 */
	{
		perror("seteuid");
		return -1;
	}
 
	printf("real uid is %d\n", getuid());
	printf("effective uid is %d\n", geteuid());
	getchar();
 
	if (seteuid(0) == -1)		/* root = 1001 */
	{
		perror("seteuid");
		return -1;
	}
 
	printf("real uid is %d\n", getuid());
	printf("effective uid is %d\n", geteuid());
	getchar();
}
```

然后编译代码, 并把可执行文件的属主改为root, 然后添加上set-user-ID位:

```bash
gcc uid.c -o uid
sudo chown root:root uid
sudo chmod u+s uid
```

执行uid之后会打印出如下:

> real uid is 1001
> effective uid is 0
> real uid is 1001
> effective uid is 1001
> real uid is 1001
> effective uid is 0

可以看出, 我们先把effective uid改成了zzz. 之后又可以改回root.这就是saved uid的作用.
另外这个程序中使用的是seteuid而不是setuid, 这是因为如果改成setuid的话, 执行第一个setuid时, 因为当前effective uid为root, 第一个规则就满足, 所以把real uid, effective uid和saved uid都改成hzzz了, 因为这样更改了saved uid, 我们就回不去root了.

所以, 从这里也可以看出来setuid和seteuid的区别, 分清什么时候用哪个.

参考:

https://www.cppblog.com/converse/archive/2007/12/20/39166.html
https://blog.csdn.net/buaalei/article/details/5344647
https://www.dutor.net/index.php/2010/08/cmd-chmod-set-user-id-set-group-id/
https://hi.baidu.com/zhujian0805/item/cf54470f0bec70c02f4c6b4e

![image_1bl0fnhvhft51tdk8q87491gkj9.png-268.8kB][1]

  [1]: http://static.zybuluo.com/zwh8800/z5vfopj00g0q8qt6dcme95yx/image_1bl0fnhvhft51tdk8q87491gkj9.png
  
  
