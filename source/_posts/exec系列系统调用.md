---
title: "exec系列系统调用"
date: "2014-01-12 00:00:00"
updated: "2014-01-12 00:00:00"
tags:
-  unix
-  系统编程
---


exec系列系统调用有六个，本文讲解了它们之间的区别

[](/notename/ "archive 20140112")

exec系列系统调用有六个，通过后缀字母的含义很好记忆：

- execl
- execlp
- execle
- execv
- execvp
- execve

`l` 代表参数是一个list（用NULL结尾的可变参数），`v` 代表参数是一个vector（char* const argv[]）。
`p` 代表调用时可以只提供文件名，只要该文件在系统变量PATH中
`e` 代表为新进程提供了一个新的环境

原型如下：

```c
#include <unistd.h>
 
extern char **environ;
 
int execl(const char *path, const char *arg, ...);
int execlp(const char *file, const char *arg, ...);
int execle(const char *path, const char *arg,
           ..., char * const envp[]);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[],
           char *const envp[]);

```

上面的都是c函数，只有execve是系统调用。另外多出的一个execvpe是linux特有的，只有glibc库才有

```c
#include <unistd.h>
 
int execve(const char *filename, char *const argv[],
           char *const envp[]);
```

unix网络编程中的图给出了他们之间的关系：

![image_1bl0edi351pei15d8vba25occg9.png-96.5kB][1]

  [1]: http://static.zybuluo.com/zwh8800/3smuv4z4no4ddywavs5iegoq/image_1bl0edi351pei15d8vba25occg9.png
