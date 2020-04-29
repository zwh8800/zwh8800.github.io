---
title: "udp隧道(STUN)"
date: "2013-11-15 00:00:00"
updated: "2013-11-15 00:00:00"
tags:
-  Linux
-  网络编程
-  隧道
---


前两天稍微研究了下通过UDP建隧道穿过NAT路由器, 自己写了个实现, 中间因为考试等事宜耽误了几天, 今天终于能用了.

[](/notename/ "archive 20131115")

说起udp隧道, 不得不说下nat. nat现在在市面上再常见不过, 市面上几乎所有的家用路由器, 网吧, 企业, 学校, 手机wifi热点, 无一不使用nat. nat是当前共享上网的主要方式.

不过nat的弊端也是明显的, nat一般只有少数个外网端口, 但却为多数个内网主机提供网络服务. 大家想想, 家里宽带是不是只有一个口接WAN, 其余四个都接LAN. 这就造成了内网主机无法直接与外网主机进行点对点通讯. 首先, 外部主机对内部主机是无知的, 无法对其发出tcp连接, 这还好说, 可以让内部主机主动对外部主机发出连接, 但假如两天主机都在nat内, 就很苦恼了. udp隧道是通过一个在公共互联网的主机作为服务器, 扮演一个中介的角色, 让两台处于nat内部的主机接上线.

首先先要说一下nat的种类, 在stun的标准文档([RFC3489](https://tools.ietf.org/html/rfc3489))中定义了两大种nat类型: 1.对称型nat, 2.圆锥形nat, 对于第一种对称性nat, stun是无能为力的. 圆锥形又分三种, 完全圆锥型NAT、受限圆锥型NAT和端口受限圆锥型NAT, 这三种stun都可以穿过.

###### 对称型nat. 
 如下图所示:
 
![image_1bl02vap6ei5s7s112g1mbk14lc9.png-27.2kB][1]

对称型nat在转发**同一主机同一端口号**(ip和port都相同)发出的的数据时, 如果对端服务器不是**同一个**, 则选用**不同的端口号**进行转发, 这将导致无法进行nat穿越.
如图所示

- 在客户端: nat内主机192.168.1.100通过同一端口8000分别向5.6.7.8:56214和5.6.7.9:12540发出数据包. 地址对: { 192.168.1.100:8000 – 5.6.7.8:56214 }  { 192.168.1.100:8000 – 5.6.7.9:12540 }
- 在路由器: nat路由器1.2.3.4分别选用了两个不同的端口转发数据包(1.2.3.4:34594和1.2.3.4:34595 ), 地址对: { 1.2.3.4:34594 – 5.6.7.8:56214 }  { 1.2.3.4:34595 – 5.6.7.9:12540 }
- 在服务器端: 两个服务器分别接收到不同的端口发来的数据

###### 圆锥形nat. 

如下如所示:

![image_1bl03203113feqll1ha0nmr1mitm.png-27.4kB][2]

圆锥形nat在转发**同一主机同一端口号**(ip和port都相同)发出的的数据时, 选用**同一端口号**进行转发. 所以可以利用这一点进行nat穿越
如图所示:

- 在客户端: nat内主机192.168.1.100通过同一端口8000分别向5.6.7.8:56214和5.6.7.9:12540发出数据包. 地址对: { 192.168.1.100:8000 – 5.6.7.8:56214 }  { 192.168.1.100:8000 – 5.6.7.9:12540 }
- 在路由器: nat路由器1.2.3.4选用相同的的端口转发数据包(1.2.3.4:34594 ), 地址对: { 1.2.3.4:34594 – 5.6.7.8:56214 }  { 1.2.3.4:34594 – 5.6.7.9:12540 }
- 在服务器端: 两个服务器分别接收到相同的端口发来的数据

而圆锥形nat又分三种:

- 完全圆锥型NAT : 同一主机同一端口号的数据都映射到nat路由器的同一端口, **任意外部主机向1.2.3.4:34594发送数据192.168.1.100:8000都能收到.**
- 受限圆锥型NAT :同一主机同一端口号的数据都映射到nat路由器的同一端口, **但必须内部主机192.168.1.100用8000向外部主机1.2.3.4发送一个数据报之后才能接受外部主机发来的数据**
- 端口受限圆锥型NAT : 同一主机同一端口号的数据都映射到nat路由器的同一端口, **但必须内部主机192.168.1.100用8000向外部主机1.2.3.4的34594端口发送一个数据报之后才能接受外部主机发来的数据**

nat原理明白了, 接下来就可以设计如何nat穿越了.

![image_1bl033glufm211471ra5f481eh413.png-38.3kB][3]

分三步

- 内部主机分别向处于外网的一台公共STUN服务器发送login信息, 报告自己的ip和端口 (图中的黑色)
- 当服务器收到两台主机发来login后分别向两台主机发送对端的ip和端口 (图中的蓝色)
- 两台内部主机用原先想服务器发login信息的端口向对端ip和端口通讯 (图中的粉色)
原理明白了很简单

下面是我自己的一个实现

服务端:

```c
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
 
typedef struct sockaddr SA;
 
const unsigned short PORT = 38000;
 
const unsigned char LOGIN = 0x01;
const unsigned char PEER = 0x02;
 
void wait_login(int sock, struct sockaddr_in* remoteaddr, socklen_t* paddrlen)
{
	int index = 0;
 
	while (index < 2)
	{
		int n;
		char buf[16];
 
		if ((n = recvfrom(sock, buf, 16, 0, (SA*)&remoteaddr[index], paddrlen)) < 0)
		{
			perror("recvfrom");
			exit(errno);
		}
		if (n != 1 || buf[0] != LOGIN)
			continue;	/* ignore it */
		++index;
	}
}
 
void send_peer(int sock, struct sockaddr_in* remoteaddr, int from, int to)
{
	char ip[INET_ADDRSTRLEN];
	char buf[1024];
	buf[0] = PEER;
 
	if (inet_ntop(AF_INET, &remoteaddr[from].sin_addr, ip, INET_ADDRSTRLEN) == NULL)
	{
		perror("inet_ntop");
		exit(errno);
	}
	snprintf(buf + 1, 1023, "%s:%d", ip, ntohs(remoteaddr[from].sin_port));
	printf("sending message: %s\n", buf + 1);
	if (sendto(sock, buf, strlen(buf + 1) + 1, 0, (SA*)&remoteaddr[to], sizeof(remoteaddr[to])) < 0)
	{
		perror("sendto");
		exit(errno);
	}
}
 
int main()
{
	int sock;
	struct sockaddr_in localaddr;
	struct sockaddr_in remoteaddr[2];
	socklen_t addrlen = sizeof(remoteaddr[0]);
 
	sock = socket(AF_INET, SOCK_DGRAM, 0);
	if (sock < 0)
	{
		perror("socket");
		exit(errno);
	}
 
	bzero(&localaddr, sizeof(localaddr));
	localaddr.sin_family = AF_INET;
	localaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	localaddr.sin_port = htons(PORT);
	if (bind(sock, (SA*)&localaddr, sizeof(localaddr)) < 0)
	{
		perror("bind");
		exit(errno);
	}
 
	while (1)
	{
		wait_login(sock, remoteaddr, &addrlen);
		send_peer(sock, remoteaddr, 0, 1);
		send_peer(sock, remoteaddr, 1, 0);
	}
 
	return 0;
}
```
客户端:

```c
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
 
#define max(a, b) ((a) > (b)?(a):(b))
 
const unsigned short PORT = 38000;
 
const unsigned char LOGIN = 0x01;
const unsigned char PEER = 0x02;
const unsigned char HELLO = 0x03;
const unsigned char MSG = 0x04;
 
typedef struct sockaddr SA;
 
int init_svraddr(const char* server, struct sockaddr_in* svrAddr, socklen_t len)
{
	struct hostent* ent = gethostbyname(server);
	if (ent == NULL)
	{
		fprintf(stderr, "gethostbyname:%s\n", hstrerror(h_errno));
		return -1;
	}
 
	bzero(svrAddr, len);
	svrAddr->sin_family = AF_INET;
	svrAddr->sin_port = htons(PORT);
	svrAddr->sin_addr = *(in_addr*)*ent->h_addr_list;
	return 0;
}
 
int login(int sock, struct sockaddr_in* svrAddr, socklen_t len)
{
	if (connect(sock, (SA*)svrAddr, len) < 0)
		return -1;
	if (write(sock, &LOGIN, sizeof(LOGIN)) < 0)
		return -1;
	return 0;
}
 
int get_peer_info(int sock, char* addrport, int len)
{
	int i, j;
	if ((i = read(sock, addrport, len)) < 0)
		return -1;
	if (*addrport != PEER)
		return -1;
 
	for (j = 0; j < i - 1; ++j)
		addrport[j] = addrport[j + 1];
	addrport[j] = '\0';
	return 0;
}
 
int say_hello_peer(int sock, struct sockaddr* addr, socklen_t len)
{
	if (connect(sock, addr, len) < 0)
		return -1;
	if (write(sock, &HELLO, sizeof(HELLO)) < 0)
 		return -1;
 	return 0; 
} 
 
int ptoap(char* str, struct sockaddr_in* addr, socklen_t len) 
{
 	char* p;
 	bzero(addr, len);
 	addr->sin_family = AF_INET;
 
	p = strchr(str, ':');
	*p = '\0';
	if (inet_pton(AF_INET, str, &addr->sin_addr) < 0)
 		return -1;
 	addr->sin_port = htons(atoi(p + 1));
	return 0;
}
 
const char* SERVER = "198.56.248.214";
 
int main()
{
	int sock;
	char addrport[256];
	struct sockaddr_in svrAddr;
	struct sockaddr_in peeraddr;
 
	sock = socket(AF_INET, SOCK_DGRAM, 0);
	if (sock < 0)
	{
		perror("socket");
		exit(errno);
	}
 
	if (init_svraddr(SERVER, &svrAddr, sizeof(svrAddr)) == -1)
		exit(-1);
 
	printf("Sending login\n");
	if (login(sock, &svrAddr, sizeof(svrAddr)) == -1)
	{
		perror("login");
		exit(errno);
	}
 
	printf("Getting peer info\n");
	if (get_peer_info(sock, addrport, 256) == -1)
	{
		perror("get_peer_info");
		exit(errno);
	}
	printf("Peer info: %s\n", addrport);
 
	if (ptoap(addrport, &peeraddr, sizeof(peeraddr)) == -1)
	{
		perror("ptoap");
		exit(errno);
	}
 
	if (say_hello_peer(sock, (SA*)&peeraddr, sizeof(peeraddr)) == -1)
	{
		perror("say_hello_peer");
		exit(errno);
	}
 
	while (true)
	{
		fd_set sockstdin;
		int maxFd;
		int n;
		char buf[4096];
 
		FD_ZERO(&sockstdin);
		FD_SET(STDIN_FILENO, &sockstdin);
		FD_SET(sock, &sockstdin);
		maxFd = max(sock, STDIN_FILENO);
 
		if (select(maxFd + 1, &sockstdin, NULL, NULL, NULL) < 0)
		{
			perror("select");
			exit(errno);
		}
 
		if (FD_ISSET(STDIN_FILENO, &sockstdin))
		{
 
			if ((n = read(STDIN_FILENO, buf, 4096)) < 0)
			{
				perror("read");
				exit(errno);
			}
			else if (n == 0)
			{
				exit(0);	/* exit normally */
			}
			if (write(sock, buf, n) < 0)
			{
				perror("sendto");
				exit(errno);
			}
		}
		if (FD_ISSET(sock, &sockstdin))
		{
			if ((n = read(sock, buf, 4096)) < 0)
			{
				perror("read");
				exit(errno);
			}
			if (write(STDOUT_FILENO, buf, n) < 0)
			{
				perror("write");
				exit(errno);
			}
		}
	}
 
	return 0;
}
```

  [1]: http://static.zybuluo.com/zwh8800/yxzjw2003d933c3cqjw2booi/image_1bl02vap6ei5s7s112g1mbk14lc9.png
  [2]: http://static.zybuluo.com/zwh8800/t3ix9lub7frb8uyvgm5swdxx/image_1bl03203113feqll1ha0nmr1mitm.png
  [3]: http://static.zybuluo.com/zwh8800/1tillp0vpj5q5oms8kh9liz0/image_1bl033glufm211471ra5f481eh413.png
