---
title: "c 标准库字符输入输出"
date: "2014-03-01 00:00:00"
updated: "2014-03-01 00:00:00"
tags:
-  C
-  标准库
---


c 标准库字符输入输出

[](/notename/ "archive 20140301")

## 按功能分类

<h3 style="color: #080">读取一个字符</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/getchar/" data-slimstat="5">getchar</a></b></td>
<td>Get character from stdin&nbsp;(function)</td>
</tr>
<tr>
<td><a href="https://www.cplusplus.com/reference/cstdio/getc/" data-slimstat="5"><b>getc</b></a></td>
<td>Get character from stream&nbsp;(function)</td>
</tr>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/fgetc/" data-slimstat="5">fgetc</a></b></td>
<td>Get character from stream&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
int getchar ( void );
int getc ( FILE * stream );
int fgetc ( FILE * stream );
```
第一个是从 stdin 中读取, 后两个都是从 FILE * 中读取但是 getc 可能被实现为宏, 返回值都为 int.

当成功时, 返回被读取的字符 (会被提升为 int); `当读取失败时返回 EOF, 需检测 feof 和 ferror 函数来检测是读到文件尾或是发生错误`.

<h3 style="color: #080">写入一个字符</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/putchar/" data-slimstat="5">putchar</a></b></td>
<td>Write character to stdout&nbsp;(function)</td>
</tr>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/putc/" data-slimstat="5">putc</a></b></td>
<td>Write character to stream&nbsp;(function)</td>
</tr>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/fputc/" data-slimstat="5">fputc</a></b></td>
<td>Write character to stream&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
int putchar ( int character );
int putc ( int character, FILE * stream );
int fputc ( int character, FILE * stream );
```
当写入时 character 会被强制为 unsigned int.

成功时返回写入的字符, `失败时返回 EOF, 应检测 ferror.`

<h3 style="color: #080">读取一行</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/gets/" data-slimstat="5">gets</a></b></td>
<td>Get string from stdin&nbsp;(function)</td>
</tr>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/fgets/" data-slimstat="5">fgets</a></b></td>
<td>Get string from stream&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
char * gets ( char * str );
char * fgets ( char * str, int num, FILE * stream );
```
分别从 stdin 和 stream 中读取一行字符保存到 str 中, 使用 gets 比较危险可能会造成缓冲区溢出. `当使用 fgets 时最多会读取 num 个字符`.

当成功读取时, 返回参数 str. `当第一个字符就为 EOF 时, 返回 NULL. 当遇到错误时返回 NULL. 所以应检测 feof 和 ferror.`

<h3 style="color: #080">写入一行</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/puts/" data-slimstat="5">puts</a></b></td>
<td>Write string to stdout&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
int puts ( const char * str );
```
将 str 写到 stdout, 并且在后面加一个 \ n

成功时返回`非零值, 出错时返回 EOF`.

<h3 style="color: #080">写入字符串</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/fputs/" data-slimstat="5">fputs</a></b></td>
<td>Write string to stream&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
int fputs ( const char * str, FILE * stream );
```
和 puts 不同, 这个不在 str 后添加 \ n 字符

成功时返回非零值, `出错时返回 EOF`.

<h3 style="color: #080">读回</h3>
<table>
<tbody>
<tr>
<td><b><a href="https://www.cplusplus.com/reference/cstdio/ungetc/" data-slimstat="5">ungetc</a></b></td>
<td>Unget character from stream&nbsp;(function)</td>
</tr>
</tbody>
</table>
```
int ungetc ( int character, FILE * stream );
```

将 character 写回 stream 中

成功时返回 character, `失败时返回 EOF`

[EOF]


