---
title: "总结 golang 对于 stream 的抽象"
date: "2016-07-18 07:23:09"
updated: "2016-08-10 06:24:10"
tags:
-  golang
-  stream
-  io
-  标准库
---


本文对 golang 标准库中的 stream 进行了一些总结。

[](/notename/ "golang stream")

## Interfaces

在 golang 中，通过几个基本的 interface 对流操作进行了抽象。

### 读写

首先是最基本的Reader、Writer，定义了对于一个流来说最基本的操作：**读、写**。这两个 interface 定义在 `io` 包里。

```golang
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

```

<!-- more -->

### Seeker、ReaderAt、WriterAt、Closer

更进一步的，最常见的流就是文件了。对于文件来说，除了简单的读写操作之外，还有 **Seek、ReadAt、WriteAt、Close** 操作。标准库对这些操作也进行了抽象。

```golang
type Seeker interface {
    Seek(offset int64, whence int) (int64, error)
}

type ReaderAt interface {
    ReadAt(p []byte, off int64) (n int, err error)
}

type WriterAt interface {
    WriteAt(p []byte, off int64) (n int, err error)
}

type Closer interface {
    Close() error
}
```

### 组合

有了这些基础设施之后，就可以使用 golang 的**组合**大法了：

```golang
type ReadCloser interface {
    Reader
    Closer
}
type ReadSeeker interface {
    Reader
    Seeker
}

type WriteCloser interface {
    Writer
    Closer
}
type WriteSeeker interface {
    Writer
    Seeker
}

type ReadWriter interface {
    Reader
    Writer
}
type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
type ReadWriteSeeker interface {
    Reader
    Writer
    Seeker
}
```

### 杂项

其他还有一些不很常用的操作。

**写到一个Writer中**、**从一个Reader中读取**。这两个操作会自动判断EOF，如果没有把所有数据写完／读完，就会继续写／读。

```golang
type WriterTo interface {
    WriteTo(w Writer) (n int64, err error)
}
type ReaderFrom interface {
    ReadFrom(r Reader) (n int64, err error)
}
```

还有一些面向 `byte` 和 `rune` 的读写操作：

```golang
type ByteReader interface {
    ReadByte() (c byte, err error)
}
type ByteScanner interface {
    ByteReader
    UnreadByte() error
}
type ByteWriter interface {
    WriteByte(c byte) error
}

type RuneReader interface {
    ReadRune() (r rune, size int, err error)
}
type RuneScanner interface {
    RuneReader
    UnreadRune() error
}
```

`Scanner` 允许把一个读出的字节重新放回流中。这个操作有点类似 Peek 但是比 Peek 别扭一些。这种操作在做词法分析器的时候很有用。

下面是一些这些 interface 的实现。

## 文件

使用 `os.Open`、`os.OpenFile` 可以打开一个文件进行读写。它返回一个 `*os.File` 结构体，这个结构体实现了上面除了杂项外的接口。

## 管道

使用 `os.Pipe` 可以创建一个操作系统提供的管道（参见 unix 管道）。这个函数也是返回一个 `*os.File` 结构体。

## 网络

`net.Conn` 是个 interface，他也实现了 `io.Reader`、`io.Writer`、`io.Closer` 这三个接口。

## 内存流

有时候我们需要把一段内存当作流来处理，我们把这种设施叫做内存流。内存流在某些情况下非常有用。

### 不阻塞的内存流

在 `strings` 包中，`strings.Reader` 实现了 `io.Reader` 、 `io.Seeker`、`io.ReaderAt`、`io.WriterTo`、`io.ByteScanner`、`io.RuneScanner` 这些接口。

可以将一个字符串当作一个**只读流**来使用。

`bytes` 包中提供了一个比 `strings.Reader` 更高级的内存流－－ `bytes.Buffer`。它支持**读写**操作，同时还可以讲写入的数据转换成字符串来使用。这个结构体一般会被当做 golang 中的 StringBuilder 使用。

另外，如果需要将 []byte 转换为只读流，可以使用 `bytes.Reader` 它和 `strings.Reader` 类似。当数据只需要进行读操作时，使用这两个 Reader 会比 Buffer 要高效一些。

这些内存流都是非阻塞的，如果内存中没有数据了，会立即返回一个 EOF 错误。

### 阻塞的内存流

有时我们需要一个可以阻塞的内存流。当 buffer 中无数据的时候，Read 操作会被阻塞住；当 buffer 满时，Write 操作也会阻塞。

`io.Pipe` 提供了这个功能。

```golang
func Pipe() (*PipeReader, *PipeWriter)
```

使用 `io.Pipe` 函数创建一对 pipe，对 PipeReader 进行读操作，对 
PipeWriter 进行写操作。

## 杂七杂八的功能

`io.LimitReader` 函数可以限制一个 Reader 的读取字节数

`io.TeeReader` 可以在你读一个 Reader 的同时，将数据写入到一个 Writer 中：

```golang
func teeExample(input io.Reader) {
    backup := os.Create("xxx.log")
    r := io.TeeReader(input, backup)
    fmt.Println(io.ReadAll(r))
}
```

这个例子可以将 input 的内容同时写到 console 和 xxx.log 文件中。

`io.MultiReader`、`io.MultiWriter` 函数可以将多个 Reader 或 Writer 合并成一个 Reader 或 Writer。

