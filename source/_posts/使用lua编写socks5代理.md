---
title: "使用 lua 编写 socks5 代理"
date: "2016-04-16 18:43:47"
updated: "2017-08-03 05:58:27"
tags:
-  网络编程
-  lua
-  libuv
-  socks5
---


之前做过一个有趣的东西，把[一部分 NodeJS 的 API 移植到了 lua 上](https://lengzzz.com/note/archive-20151015)。让我可以在 lua 里使用异步网络 API 了，我把做的这个小东西叫做 [lua-libuv](https://github.com/zwh8800/lua-libuv)。今天去参加了一下 Gopher China 2016 中间听得无聊了，便打开电脑，基于自己的 lua-libuv 编写了一个 socks5 协议的 proxy。这篇博客，讲解一下 socks5 协议以及实现。

[](/notename/ "socks5 proxy in lua")

[toc]

## socks5 协议介绍

socks5 协议可能是中国网友见得最多的协议了。很多著名的工具 都就会在本机的 1080 端口开启一个 socks5 proxy 服务，供浏览器来调用。我们今天就来聊一聊 socks5 协议。

socks5 协议不只是在中国流行，它其实是最常见的代理协议之一，几乎所有浏览器都会原生支持 socks5 协议，而在 <i class="icon-apple"></i> Mac 上则是系统级别的支持，所以可见其流行程度仅次于 http 代理。由于 socks5 是工作在 tcp 层的协议，所以它又比 http 代理灵活很多。比如 http 代理只能用来看网页。但是使用 socks5 协议还可以上外网打游戏，也可以使用代理登陆 QQ 。但是 socks5 也有自己的短板，比如对 udp 支持的不好（socks5 把域名 resolve 的事都做了，就为了避免 client 调用 udp ）

## socks5 协议详解

socks5 协议非常简单，[rfc1928](https://www.ietf.org/rfc/rfc1928.txt) 整个只有 9 页，我大概用了 10 分钟粗略看了一下就明白 socks5 的设计了。

### 端口

socks5 一般回使用 1080 端口来提供服务。

### 握手

socks5 协议使用四次应答式的握手建立一个链接。分别会

- client：协商method
- server：选用method
- client：发起请求
- server：处理请求并回复

四次握手结束之后，client 会把代理服务器当作是自己真正想通讯的服务器一样对待。而代理则会转发真正的通讯信息。

### 流程

#### 1. 协商 method

当一个客户端需要建立一个 firewall 之外的连接时，首先向 socks5 服务器的 1080 端口发起一个 tcp 连接。

随后，客户端向服务器提供自己支持的 method 列表。数据的 payload 如下：

```
                   ++++
                   |VER | NMETHODS | METHODS  |
                   ++++
                   | 1  |    1     | 1 to 255 |
                   ++++

```

上面是字段名，下面是字段长度。

字段分别是：

- 版本号，对于 socks5 来说始终为5
- method 个数
- method 列表，个数需要和第二个字段相同，不能超过255

method 的选项有如下几项，不过我感觉最常用的也就是第一个了。

- 0x00: 无需授权
- 0x01: GSSAPI
- 0x02: 用户名／密码授权
- 0x03 - 0x7f: IANA ASSIGNED
- 0x80 - 0xfe: 私有 method
- 0xff: 用于服务器向客户端返回不支持此 method 的错误代码

#### 2. 选择 method

服务器接到请求之后，应当选用一种 method 返回给客户端：

```
                         +++
                         |VER | METHOD |
                         +++
                         | 1  |   1    |
                         +++
```

之后如果 method 是需要鉴权的，会进行相应的鉴权。这里不谈了。

#### 3. 请求

之后客户端把自己想要连接的信息封成一个请求发给 proxy 。格式如下：

```
        +++++++
        |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
        +++++++
        | 1  |  1  | X'00' |  1   | Variable |    2     |
        +++++++
```

其中，

- VER 还是代表版本，始终为 0x05
- CMD 代表命令，表示建立连接还是监听连接
    - 0x01: Connect，连接其他服务器
    - 0x02: Bind，监听端口
    - 0x03: 建立udp连接
- 保留
- 地址类型
    - 0x01: IPv4
    - 0x03: DomainName
    - 0x04: IPv6
- 目的地址
- 目的端口

这里面，命令又会有三种情况。如上，udp因为没有建立连接这一步，所以监听和连接是等同的。

地址类型也是，当地址类型不同时，目的地址的长度会不一样

- IPv4: 4 字节
- DomainName: 目的地址的第一个字节代表域名长度
- IPv6: 16 字节

所以需要按照 ATYP 来读取目的地址。

#### 4. 回复

服务器收到请求后，需要向目的地址建立连接，如果失败了，需要告诉客户端原因。如果成功了，也需要告诉客户端代理服务器使用的地址和端口信息。

```
        +++++++
        |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
        +++++++
        | 1  |  1  | X'00' |  1   | Variable |    2     |
        +++++++
```

- VER 还是代表版本，始终为 0x05
- REP 代表返回值
    - 0x00: 成功
    - 0x01: socks 服务器错误
    - 0x02: 不允许访问
    - 0x03: Network unreachable
    - 0x04: Host unreachable
    - 0x05: Connection refused
    - 0x06: TTL expired
    - 0x07: Command not supported
    - 0x08: Address type not supported
- 保留
- 地址类型

### 例子

假如浏览器访问 https://lengzzz.com 需要如下对话

> 05 01 00
>> 05 00

> 05 01 00 03(ATYP) 0b(LEN) 6c 65 6e 67 7a 7a 7a 2e 63 6f 6d(DOMAINNAME) 01 bb(PORT)
>> 05 00 00 01(ATYP) 0a 00 00 11(IP) e9 c7(PORT)

## Lua 实现

大概就是用了两个函数来 parse 出 client 的 payload ，分别 parse 协商 method 阶段的 payload 和请求阶段的 payload 。

```lua
function parseMethodPayload(payload)
    if payload:byte(1) ~= SocksVersion then
        return nil, Errors.VersionError
    end

    local method = {
        version = SocksVersion,
        methods = {},
    }

    local methodCount = payload:byte(2)
    method.methods = {payload:byte(3, 3 + methodCount - 1)}
    return method
end
```

```lua
function parseRequestPayload(payload)
    if payload:byte(1) ~= SocksVersion then
        return nil, Errors.VersionError
    end

    local request = {
        version = SocksVersion,
        command = CommandType.Connect,
        addressType = AddressType.IPv4,
        distAddress = '',
        distPort = 0,
    }

    if payload:byte(2) > CommandType.Udp then
        return nil, Errors.CommandTypeNotSupported
    else
        request.command = payload:byte(2)
    end

    local requestAddressType = payload:byte(4)
    if  requestAddressType ~= AddressType.IPv4 and
        requestAddressType ~= AddressType.DomainName and
        requestAddressType ~= AddressType.IPv6
    then
        return nil, Errors.AddressTypeNotSupported
    else
        request.addressType = requestAddressType
    end

    local portIndex
    if request.addressType == AddressType.IPv4 then
        local ipBytes = {payload:byte(5, 8)}
        request.distAddress = table.concat(ipBytes, '.')
        portIndex = 9
    elseif request.addressType == AddressType.DomainName then
        local len = payload:byte(5)
        request.distAddress = payload:sub(6, 6 + len - 1)
        portIndex = 5 + len + 1
    elseif request.addressType == AddressType.IPv6 then
        return nil, Errors.AddressTypeNotSupported
    end

    local portBytes = {payload:byte(portIndex, portIndex + 1) }
    request.distPort = portBytes[1] * 256 + portBytes[2]

    return request, nil
end
```

比较关键的就是这里，在会场写的，还是比较糙了。详细的代码看 [<i class="icon-github"></i> Github](https://github.com/zwh8800/lua-libuv/blob/master/test/socksProxy.lua) 就好啦：

https://github.com/zwh8800/lua-libuv/blob/master/test/socksProxy.lua


