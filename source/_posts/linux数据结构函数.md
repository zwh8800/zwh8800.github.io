---
title: "linux 数据结构函数"
date: "2014-02-09 00:00:00"
updated: "2014-02-09 00:00:00"
tags:
-  linux
-  内核
-  kernel
---


linux 数据结构函数

[](/notename/ "archive 20140209")

今天翻 man page, 发现 linux 下的 libc 比标准库要丰富很多, 除了提供了一些系统相关的包装函数 (fdopen popen dprintf 之类) 来降低编程难度以外, 还提供了一组数据结构相关的函数. 粗略看了一下, 提供了以下数据结构:

- 哈希表
- 队列
- 二叉查找树

还提供了简单的线性查找算法.
哈希表:
```
#include <search.h>
int    hcreate(size_t);
void   hdestroy(void);
ENTRY *hsearch(ENTRY, ACTION);
#define _GNU_SOURCE
int hcreate_r(size_t nel, struct hsearch_data *htab);
int hsearch_r(ENTRY item, ACTION action, ENTRY **retval,
              struct hsearch_data *htab);
void hdestroy_r(struct hsearch_data *htab);
```

队列:
```
#include <search.h>
void   insque(void *, void *);
void   remque(void *);
```

线性查找:
```
#include <search.h>
void  *lfind(const void *, const void *, size_t *,
          size_t, int (*)(const void *, const void *));
void  *lsearch(const void *, void *, size_t *,
          size_t, int (*)(const void *, const void *));
```

查找树:
```
#include <search.h>
void  *tdelete(const void *restrict, void **restrict,
          int(*)(const void *, const void *));
void  *tfind(const void *, void *const *,
          int(*)(const void *, const void *));
void  *tsearch(const void *, void **,
          int(*)(const void *, const void *));
void   twalk(const void *,
          void (*)(const void *, VISIT, int ));
#define _GNU_SOURCE
void tdestroy(void *root, void (*free_node)(void *nodep));
```


