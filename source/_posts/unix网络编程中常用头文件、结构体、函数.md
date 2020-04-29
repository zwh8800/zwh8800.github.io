---
title: "unix网络编程中常用头文件、结构体、函数"
date: "2014-01-09 00:00:00"
updated: "2014-01-09 00:00:00"
tags:
-  unix
-  网络编程
-  笔记
---


unix网络编程中常用头文件、结构体、函数

[](/notename/ "archive 20140109")

## 1.常用头文件

`<sys/socket.h>`：

> socket, bind, connect等函数定义, 所有socket程序必须要包含, 另外定义了一些通用的套接字地址结构, 如struct sockaddr.

`<netinet/in.h>`：

> struct sockaddr_in, struct sockaddr_in6等结构体的定义, 定义了ip协议中的套接字地址结构. 另外有些基础类型定义in_addr_t, in_port定义. hton*, ntoh* 字节序转换函数.

`<arpa/inet.h>`：

> inet_pton, inet_ntop, ip地址转换函数.

## 2.部分函数原型与结构体定义

#### 1)ipv4套接字地址结构体定义:

```c
/* from <netinet/in.h> */
/* Internet address.  */
typedef uint32_t in_addr_t;
struct in_addr
  {
    in_addr_t s_addr;
  };
 
/* Structure describing an Internet socket address.  */
struct sockaddr_in
  {
    __SOCKADDR_COMMON (sin_);
    in_port_t sin_port;			/* Port number.  */
    struct in_addr sin_addr;		/* Internet address.  */
 
    /* Pad to size of `struct sockaddr'.  */
    unsigned char sin_zero[sizeof (struct sockaddr) -
			   __SOCKADDR_COMMON_SIZE -
			   sizeof (in_port_t) -
			   sizeof (struct in_addr)];
  };
```

《unix网络编程》上的定义:
```c
struct in_addr {
  in_addr_t s_addr;
};
 
struct sockaddr_in {
  uint8_t sin_len;
  sa_family_t sin_family;
  in_port_t sin_port;
  struct in_addr sin_addr;
  char sin_zero[8];
};
```

#### 2)POSIX规范定义的类型:

![image_1bl0dmjqfum819j74jn19na1ecv9.png-77.2kB][1]

#### 3)通用的套接字地址:

```c
struct sockaddr {
  uint_8 sa_len;
  sa_family_t sa_family;
  char sa_data[14];
};
```

#### 4)各种套接字地址结构体:

![image_1bl0dnjs71238jhiqo21omc17s5m.png-187.3kB][2]

#### 5)字节序函数:

```c
#include <netinet/in.h>
 
uint32_t htonl(uint32_t hostlong);
uint16_t htons(uint16_t hostshort);
uint32_t ntohl(uint32_t netlong);
uint16_t ntohs(uint16_t netshort);
```

#### 6)ip地址转换函数:

```c
#include <sys/types.h>
#include <sys/socket.h>;
#include <arpa/inet.h>
 
int inet_pton(int af, const char *src, void *dst);
const char *inet_ntop(int af, const void *src, char *dst, socklen_t cnt);
```

这两个函数传入(或传出)的ip地址结构体为struct in_addr等结构体

传出的字符串buffer大小在<netinet/in.h>中定义:

```c
#define INET_ADDRSTRLEN 16
#define INET6_ADDRSTRLEN 48
```

#### 7)套接字函数:

```c
#include <sys/types.h>
#include <sys/socket.h>
 
int socket(int domain, int type, int protocol);
int connect(int sockfd, const struct sockaddr *serv_addr, socklen_t addrlen);
int bind(int sockfd, struct sockaddr *my_addr, socklen_t addrlen);
int listen(int s, int backlog);
int accept(int s, struct sockaddr *addr, socklen_t *addrlen);
int getsockname(int s, struct sockaddr *name, socklen_t *namelen);
int getpeername(int s, struct sockaddr *name, socklen_t *namelen);
```

## 3.常见用法

#### 1)初始化套结字地址结构：

对于IPV4一般需要初始化三个字段：sin_family、sin_addr、sin_port。

```c
bzero(&svraddr, sizeof(svraddr));/* 注意清零 */
svraddr.sin_family = AF_INET;
svraddr.sin_port = htons(PORT);/* 注意大端小端的转换 */
svraddr.sin_addr.s_addr = htonl(INADDR_ANY);/* 设置ip地址为任意地址 */
if (inet_pton(AF_INET, "192.168.0.1", &addr.sin_addr) < 0)/* 使用inet_pton设置ip */
{
	perror("inet_pton");
	exit(errno);
}
```

#### 2)创建套结字：

```c
svrsock = socket(AF_INET, SOCK_STREAM, 0);/* 参数3可以推断得出 */
if (svrsock == -1)
{
	perror("socket");
	exit(errno);
}
```

#### 3)绑定套结字到套结字地址：

```c
if (bind(svrsock, (SA*)&svraddr, sizeof(svraddr)) == -1)
{
	perror("bind");
	exit(errno);
}
```

#### 4)连接套结字到对端：

```c
if (connect(svrsock, (SA*)peeraddr, sizeof(peeraddr)) == -1)
{
	perror("connect");
	exit(errno);
}
```

#### 5)设置套结字为监听模式：

```c
if (listen(svrsock, 64) == -1)
{
	perror("listen");
	exit(errno);
}
```

#### 6)从套结字上等待一个连接：

```c
int cltsock;
struct sockaddr_in cltaddr;
socklen_t cltaddrlen = sizeof(cltaddr);
if ((cltsock = accept(svrsock, &cltaddr, &cltaddrlen)) == -1)
{
	perror("accept");
	exit(errno);
}
```

#### 7)获取本端和对端套结字地址：

```c
struct sockaddr_in addr;
socklen_t addrlen = sizeof(addr);
if (getsockname(svrsock, &addr, &addrlen) == -1)
{
	perror("getsockname");
	exit(errno);
}
if (getpeername(svrsock, &addr, &addrlen) == -1)
{
	perror("getpeername");
	exit(errno);
}
```

#### 8)将ip地址转换为字符串形式

```c
char cltaddrstr[INET_ADDRSTRLEN];
if (inet_ntop(AF_INET, &cltaddr.sin_addr, cltaddrstr, INET_ADDRSTRLEN) == NULL)/* 注意为cltaddr.sin.addr */
{
	perror("inet_ntop");
	exit(errno);
}
```

#### 9)将字符串转成ip地址

```c
if (inet_pton(AF_INET, "192.168.1.1", &cltaddr.sin_addr) == -1)
{
	perror("inet_pton");
	exit(errno);
}
```

  [1]: /images/4ea58ed2d79ce2287587598283256931.png
  [2]: /images/b096dbb637e71cfe09740ba797dfbdcd.png
