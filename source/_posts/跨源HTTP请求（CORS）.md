---
title: "跨源 HTTP 请求（CORS）"
date: "2016-06-13 06:37:05"
updated: "2016-06-13 07:12:16"
tags:
-  HTTP
-  CORS
-  跨域
---


之前一直对跨域问题一知半解，今天看了些资料[^cors]总算把所有情况搞明白了。总的来说跨域请求分为两种：简单请求和复杂请求，下面来详细说明。

[](/notename/ "cross origin http request")

## 简单请求

简单请求是指：

- 只使用 GET, HEAD 或者 POST 请求方法。如果使用 POST 向服务器端传送数据，则数据类型 (Content-Type，**注意是 request 的 Content-Type**) 只能是 application/x-www-form-urlencoded, multipart/form-data 或 text/plain中的一种。
- 不会使用自定义请求头（类似于 X-Modified 这种）。

当浏览器遇到这种请求时，会直接向服务器发送请求，但是在把结果返回给JS代码前会做一次检查。浏览器会查看 response header 中是否有 `Access-Control-Allow-Origin` 这个 header 。如果有且允许当前 Origin 访问的话，才会真正将结果返回给 JS 程序。

## 复杂请求和预请求

如果一个 Ajax 请求不是上面所说的那种。比如使用 POST 方法并且 Content-Type 是 application/json。那么浏览器则不会直接发送这个 HTTP 请求，而是先发送一个预请求。

预请求使用 OPTION 方法发送，并且带上 `Access-Control-Request-Method`、`Access-Control-Request-Headers` 等 header。

举例说明：

在 a.com 下使用 POST 请求 b.com/user ，数据类型是 application/json ，并且使用了私有 header ：x-token

```
OPTIONS /user HTTP/1.1
Host: b.com
User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3pre) Gecko/20081130 Minefield/3.1b3pre
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-us,en;q=0.5
Accept-Encoding: gzip,deflate
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Connection: keep-alive
Origin: http://a.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: X-TOKEN

HTTP/1.1 200 OK
Date: Mon, 01 Dec 2008 01:15:39 GMT
Server: Apache/2.0.61 (Unix)
Access-Control-Allow-Origin: http://foo.example
Access-Control-Allow-Methods: POST, GET, PUT, OPTIONS
Access-Control-Allow-Headers: X-TOKEN
Access-Control-Max-Age: 1728000
Vary: Accept-Encoding, Origin
Content-Encoding: gzip
Content-Length: 0
Keep-Alive: timeout=2, max=100
Connection: Keep-Alive
Content-Type: text/plain

```

这个 OPTION 请求类似一个询问，他会询问服务器是否支持用户的请求，服务器应当返回他所支持的请求。当进行了 OPTION 请求之后，浏览器进行判断此次请求是否合法，如果合法的话才会发起真正的 HTTP 请求。

## Cookies

默认情况下跨域请求是不带 Cookies 的，如果需要 Cookies 的话，在客户端需要将 XMLHttpRequest 对象的 withCredentials 设置为 true 。同时，服务器也应当做相应调整。

```javascript
var xhr = new XMLHttpRequest();
xhr.open('GET', url, true);
xhr.withCredentials = true; // 设置 withCredentials 为 true
xhr.send();

```

服务器应当返回 `Access-Control-Allow-Credentials: true` ，否则浏览器不会将结果返回给 JS 程序。

## 总结

总的来说，为了实现安全的跨域 Ajax 请求。会对 ajax 做一下检查。对于简单的请求，浏览器会直接发送请求，然后对结果进行检查；对于复杂请求，会首先发送一个预请求进行检查，检查通过之后才发送真正的请求。

为了实现检查的目的，在 HTTP 协议中新增了如下几个请求头和响应头。

### 请求头（request header）

- Origin：用于表明此请求来自哪个源
- Access-Control-Request-Method：用于表明此次请求需要使用哪个方法
- Access-Control-Request-Headers：用于表明此次请求需要哪些自定义头

### 响应头（response header）

- Access-Control-Allow-Origin：用于表明此资源允许哪些源访问
- Access-Control-Expose-Headers：用于表明此资源会返回哪些自定义响应头
- Access-Control-Max-Age：用于表明此次预请求的有效期（秒）
- Access-Control-Allow-Credentials：用于表明此资源允许使用 Cookies
- Access-Control-Allow-Methods：用于表明此资源允许哪些方法
- Access-Control-Allow-Headers：用于表明此资源允许哪些自定义请求头

[^cors]: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS


