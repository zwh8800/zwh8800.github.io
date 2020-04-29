---
title: "linux设备驱动程序(3) – 字符设备驱动(设备号 注册设备)"
date: "2014-01-29 00:00:00"
updated: "2014-01-29 00:00:00"
tags:
-  linux
-  驱动开发
---


这次我们学习最简单的一种设备, 字符设备驱动的开发. 最终写出一个字符设备, 用户可以进行打开和关闭, 并向他写入数据, 它会始终保存着最后一次写入的数据, 对它进行读取会读出最后一次写入的数据.

[](/notename/ "archive 20140129")

### 1.设备号
在linux中执行ls -l命令, 在日期之前可以看到两个用逗号隔开的数, 这个便是设备号, 逗号之前的是主设备号(major)后面的是次设备号(minor).

在内核中, 设备号使用dev_t来表示(`<linux/types.h>`). dev_t可以同时保存主设备号和次设备号, 当需要从dev_t中获取主设备号或次设备号时, 可以使用以下:

```
MAJOR(dev_t dev);
MINOR(dev_t dev);
```

相反, 如果需要用设备号构造出dev_t则使用:

```
MKDEV(int major, int minor);
```

### 2.分配设备号
建立字符设备前, 驱动程序首先应该分配设备号, 有三个函数用来分配(注册)设备号和释放设备号(在`<linux/fs.h>`中):

```
int register_chrdev_region(dev_t first, unsigned int count, 
				char *name);
int alloc_chrdev_region(dev_t *dev, unsigned int firstminor, 
				unsigned int count, char *name);
void unregister_chrdev_region(dev_t first, unsigned int count);
```

register_chrdev_region函数用在已知设备号的情况下向内核进行注册, alloc用在设备号不确定的情况下, 向内核动态分配设备号. first是申请的设备号的第一个, count是要连续申请的个数(次设备号的个数, 比如first是[10, 102], count是4, 则会申请[10,102][10,103][10,104][10,105]这四个). name是设备的名称, 将出现在/proc/devices和sysfs中. **如果出错返回负的错误号**.

alloc函数成功后通过dev返回第一个设备号.

例子:

```
DEBUG_LOG("", "allocating device number\n");
/* 申请设备号 */
if (chr_major != 0)		/* 如果用户提供了设备号 */
{
	dev = MKDEV(chr_major, chr_minor);
	ret = register_chrdev_region(dev, 1, DEV_NAME);
}
else
{
	ret = alloc_chrdev_region(&dev, chr_minor, 1, DEV_NAME);
	chr_major = MAJOR(dev);
}
if (ret < 0)
{
	DEBUG_LOG(KERN_WARNING, "cannot get major%d\n", chr_major);
	goto err;
}
DEBUG_LOG("", "success\n");
DEBUG_LOG("", "chr_major=%d, chr_minor=%d\n", chr_major, chr_minor);
```

### 3.重要的数据结构
关于字符设备驱动, 有三个重要的数据结构, 他们都在`<linux/fs.h>`中.分别是:

- struct file_operations
- struct file
- struct inode

```c
struct file_operations {
	struct module *owner;
	loff_t (*llseek) (struct file *, loff_t, int);
	ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
	ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
	ssize_t (*aio_read) (struct kiocb *, const struct iovec *, unsigned long, loff_t);
	ssize_t (*aio_write) (struct kiocb *, const struct iovec *, unsigned long, loff_t);
	int (*iterate) (struct file *, struct dir_context *);
	unsigned int (*poll) (struct file *, struct poll_table_struct *);
	long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
	long (*compat_ioctl) (struct file *, unsigned int, unsigned long);
	int (*mmap) (struct file *, struct vm_area_struct *);
	int (*open) (struct inode *, struct file *);
	int (*flush) (struct file *, fl_owner_t id);
	int (*release) (struct inode *, struct file *);
	int (*fsync) (struct file *, loff_t, loff_t, int datasync);
	int (*aio_fsync) (struct kiocb *, int datasync);
	int (*fasync) (int, struct file *, int);
	int (*lock) (struct file *, int, struct file_lock *);
	ssize_t (*sendpage) (struct file *, struct page *, int, size_t, loff_t *, int);
	unsigned long (*get_unmapped_area)(struct file *, unsigned long, unsigned long, unsigned long, unsigned long);
	int (*check_flags)(int);
	int (*flock) (struct file *, int, struct file_lock *);
	ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, size_t, unsigned int);
	ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, size_t, unsigned int);
	int (*setlease)(struct file *, long, struct file_lock **);
	long (*fallocate)(struct file *file, int mode, loff_t offset,
			  loff_t len);
	int (*show_fdinfo)(struct seq_file *m, struct file *f);
};
```

```c
struct file {
	/*
	 * fu_list becomes invalid after file_free is called and queued via
	 * fu_rcuhead for RCU freeing
	 */
	union {
		struct list_head	fu_list;
		struct llist_node	fu_llist;
		struct rcu_head 	fu_rcuhead;
	} f_u;
	struct path		f_path;
#define f_dentry	f_path.dentry
	struct inode		*f_inode;	/* cached value */
	const struct file_operations	*f_op;
 
	/*
	 * Protects f_ep_links, f_flags, f_pos vs i_size in lseek SEEK_CUR.
	 * Must not be taken from IRQ context.
	 */
	spinlock_t		f_lock;
#ifdef CONFIG_SMP
	int			f_sb_list_cpu;
#endif
	atomic_long_t		f_count;
	unsigned int 		f_flags;
	fmode_t			f_mode;
	loff_t			f_pos;
	struct fown_struct	f_owner;
	const struct cred	*f_cred;
	struct file_ra_state	f_ra;
 
	u64			f_version;
#ifdef CONFIG_SECURITY
	void			*f_security;
#endif
	/* needed for tty driver, and maybe others */
	void			*private_data;
 
#ifdef CONFIG_EPOLL
	/* Used by fs/eventpoll.c to link all the hooks to this file */
	struct list_head	f_ep_links;
	struct list_head	f_tfile_llink;
#endif /* #ifdef CONFIG_EPOLL */
	struct address_space	*f_mapping;
#ifdef CONFIG_DEBUG_WRITECOUNT
	unsigned long f_mnt_write_state;
#endif
};
```

```c
struct inode {
...
	dev_t			i_rdev;
	union {
		struct pipe_inode_info	*i_pipe;
		struct block_device	*i_bdev;
		struct cdev		*i_cdev;
	};
...
};
```

对于一个字符设备, 应当满足linux对于字符设备的定义(既它可以进行字符设备的操作, 如打开,读取,写入,ioctl,关闭), 所以他应当自己定义这些操作的函数, 然后把函数指针保存在**struct file_operations**结构中传递给内核. 这样内核就可以在用户对设备调用这些函数时调用适当的驱动程序. 所以在**struct file_operations**中可以看到, 大部分的都是函数指针, 而有一个成员例外, struct module *owner成员应给它赋值THIS_MODULE.

例如:

```c
struct file_operations chr_fops = 
{
	.owner = THIS_MODULE,
	.open = open,
	.release = release,
	.read = read,
	.write = write,
};
```

对于file和inode, 我的理解是, 用户每打开一个文件, 将产生一个file结构, 但是一个文件只有一个inode(硬盘上也保存着inode, 用户打开时将会读入内存). 所以看open和release函数的签名都有一个file和inode, 而其他函数只有file. 因为当打开文件时, 应当让file和inode建立联系, 关闭时应当解除联系. 所以内核的接口是这样设计的.

### 4.注册字符设备
刚刚只是分配了设备号了, 内核其实连你的设备是什么类型都不知道. 所以第二步应该注册设备. 字符设备的注册用到的结构体为**struct cdev**(`<linux/cdev.h>`, 刚刚在inode结构体中也看见这个结构了i_cdev)

cdev结构体的分配有两个函数:

```c
struct cdev *cdev_alloc(void);
void cdev_init(struct cdev *cdev, struct file_operations *fops);
```

第一个函数会分配内存空间, 并进行初始化cdev, 第二个只是会初始化cdev.

cdev有两个重要的字段, owner和ops, owner应该设置成THIS_MODULE, ops应当设置成一个指向struct file_operations的指针.

cdev结构构造好之后通过这两个函数注册和移除字符设备:

```c
int cdev_add(struct cdev *dev, dev_t num, unsigned int count);
void cdev_del(struct cdev *dev);
```

看看通过cdev_add我们传递给内核什么信息:

- 通过num和count传递了设备号
- 通过cdev内的ops传递了文件操作的函数指针

这样, 当有用户请求对num指定的设备号的设备进行操作时, 就会通过ops中的指针调用相应的函数了. 这就完成了字符设备的注册.cdev_add会返回错误代码

例:

```c
DEBUG_LOG("", "register char device\n");
/* 注册字符设备 */
chr_dev = kmalloc(sizeof(chr_dev), GFP_KERNEL);
if (chr_dev == NULL)
{
	DEBUG_LOG(KERN_WARNING, "no memory\n");
	ret = -ENOMEM;
	goto err1;
}
memset(chr_dev, 0, sizeof(*chr_dev));
cdev_init(&chr_dev->cdev, &chr_fops);
chr_dev->cdev.owner = THIS_MODULE;
chr_dev->cdev.ops = &chr_fops;
if ((ret = cdev_add(&chr_dev->cdev, dev, 1)) != 0)
{
	DEBUG_LOG(KERN_WARNING, "Error %d adding chr\n", ret);
	goto err2;
}
DEBUG_LOG("", "success\n");
```

我们使用一个自己的结构来保存cdev和相关的信息chr_dev.

### 5.具体的驱动程序如何写
前面的所有操作讲的都是驱动程序的初始化操作, 都是应当写到module_init函数中的. 下面将驱动真正的事件处理函数应当怎么写.

我们的功能是这个设备可以打开,关闭,读取,写入. 所以我们只需实现这几个函数, 如果用户对设备调用其他的函数, 内核会有相应的默认操作.

##### 1)打开

前面说了, 打开操作就是将inode和file结构体建立联系, 这两个结构体内核都会在用户打开/关闭文件时自动创建/销毁, 驱动程序不用照看他们的生命周期.

open函数会用参数传来inode和file, inode是内核根据用户打开的文件创建的, 因为文件系统保存着设备文件的设备号, 而刚刚我们通过cdev_add函数将设备号和cdev建立了联系所以这个inode中会有一个指向对应cdev的指针. 但是file中没有, 我们要做的就是让每个打开的file也保存起这个指针(通过保存在**filp->private_data**中).

但是我们的cdev保存在chr_dev结构中, 而且这个结构中还有另外一些我们感兴趣的东西, 所以不如直接保存chr_dev结构.

```c
int open(struct inode *inode, struct file *filp)
{	
	struct chr_dev *dev;
	DEBUG_LOG("", "open from user\n");
 
	dev = container_of(inode->i_cdev, struct chr_dev, cdev);
	filp->private_data = dev;
 
	if ((filp->f_flags & O_ACCMODE) == O_WRONLY)
	{
		dev->last_char = 0;
	}
 
	DEBUG_LOG("", "open success\n");
	return 0;
}
```

##### 2)关闭

当用户关闭文件时, 我们应当:

- 释放filp->private_data中我们分配的数据(如果不再使用)
- 如果是最后一个文件被关闭, 关闭硬件(如果需要的话[硬件可能会费电])

我们这两个工作都不用做.

##### 3)读写

这个很简单了没什么要说的. 注意一点, 传来的buf指针是用户空间的指针(用__user修饰), 我们不能对这个指针进行解引用, 因为它根本不指向我们这个空间(内核空间)的数据. 而对它进行读写只能通过函数copy_from_user/copy_to_user进行(`<linux/uaccess>`).

另外, 如果在内核空间需要分配内存, 应使用kmalloc和kfree(`<linux/stab.h>`)

直接看最终代码吧

### 6.最终代码

```c
#include <linux/module.h>
#include <linux/init.h>			/* module_*		*/
#include <linux/kernel.h>		/* printk		*/
#include <linux/moduleparam.h>	/* module_param */
#include <linux/types.h>		/* dev_t		*/
#include <linux/fs.h>			/* reg*_chrdev	*/
#include <linux/cdev.h>			/* cdev_add		*/
#include <asm/uaccess.h>		/* copy_*_user	*/
#include <linux/string.h>		/* memset		*/
#include <linux/slab.h>			/* kmalloc		*/
 
#define DEV_NAME "chr"
 
#define _DEBUG
 
#ifdef _DEBUG
 
#define DEBUG_LOG(lvl, fmt, ...) 		\
	printk(lvl "%s: %s:%d <%s>: " fmt,	\
	DEV_NAME, __FILE__, __LINE__, __func__, ##__VA_ARGS__)
 
#else
 
#define DEBUG_LOG(lvl, fmt, ...) 
 
#endif
 
MODULE_LICENSE("Dual BSD/GPL");
 
struct chr_dev
{
	char last_char;
	struct cdev cdev;
};
 
int open(struct inode *inode, struct file *filp)
{	
	struct chr_dev *dev;
	DEBUG_LOG("", "open from user\n");
 
	dev = container_of(inode->i_cdev, struct chr_dev, cdev);
	filp->private_data = dev;
 
	if ((filp->f_flags & O_ACCMODE) == O_WRONLY)
	{
		dev->last_char = 0;
	}
 
	DEBUG_LOG("", "open success\n");
	return 0;
}
 
int release(struct inode *inode, struct file *filp)
{
	DEBUG_LOG("", "release from user\n");
	DEBUG_LOG("", "release success\n");
	return 0;
}
 
ssize_t read(struct file *filp, char __user *buf, size_t count, loff_t *fpos)
{
	struct chr_dev *dev = filp->private_data;
	char* kbuf = kmalloc(count, GFP_KERNEL);
	DEBUG_LOG("", "read from user\n");
 
	if (kbuf == NULL)
	{
		DEBUG_LOG(KERN_WARNING, "no memory\n");
		goto err1;
	}
	memset(kbuf, dev->last_char, count);
 
	if (copy_to_user(buf, kbuf, count) != 0)
	{
		DEBUG_LOG(KERN_WARNING, "copy_to_user error\n");
		goto err;
	}
 
	kfree(kbuf);
 
	DEBUG_LOG("", "read success count=%d\n", count);
	return count;
 
err1:
	kfree(kbuf);
err:
	return -EFAULT;
}
 
ssize_t write(struct file *filp, const char __user *buf, size_t count, loff_t *fpos)
{
	struct chr_dev *dev = filp->private_data;
	DEBUG_LOG("", "write from user\n");
	if (copy_from_user(&dev->last_char, buf + count - 1, 1) != 0)
	{
		DEBUG_LOG(KERN_WARNING, "copy_from_user error\n");
		return -EFAULT;
	}
	DEBUG_LOG("", "write success count=%d\n", count);
	return count;
}
 
struct file_operations chr_fops = 
{
	.owner = THIS_MODULE,
	.open = open,
	.release = release,
	.read = read,
	.write = write,
};
 
int chr_major = 0;
int chr_minor = 0;
//module_param(chr_major, int, S_IRUGO);
 
struct chr_dev* chr_dev;
 
int chr_init(void)
{
	int ret;
	dev_t dev;
 
	DEBUG_LOG("", "allocating device number\n");
 
	/* 申请设备号 */
	if (chr_major != 0)		/* 如果用户提供了设备号 */
	{
		dev = MKDEV(chr_major, chr_minor);
		ret = register_chrdev_region(dev, 1, DEV_NAME);
	}
	else
	{
		ret = alloc_chrdev_region(&dev, chr_minor, 1, DEV_NAME);
		chr_major = MAJOR(dev);
	}
	if (ret < 0)
	{
		DEBUG_LOG(KERN_WARNING, "cannot get major%d\n", chr_major);
		goto err;
	}
	DEBUG_LOG("", "success\n");
	DEBUG_LOG("", "chr_major=%d, chr_minor=%d\n", chr_major, chr_minor);
 
	DEBUG_LOG("", "register char device\n");
	/* 注册字符设备 */
	chr_dev = kmalloc(sizeof(chr_dev), GFP_KERNEL);
	if (chr_dev == NULL)
	{
		DEBUG_LOG(KERN_WARNING, "no memory\n");
		ret = -ENOMEM;
		goto err1;
	}
	memset(chr_dev, 0, sizeof(*chr_dev));
	cdev_init(&chr_dev->cdev, &chr_fops);
	chr_dev->cdev.owner = THIS_MODULE;
	chr_dev->cdev.ops = &chr_fops;
	if ((ret = cdev_add(&chr_dev->cdev, dev, 1)) != 0)
	{
		DEBUG_LOG(KERN_WARNING, "Error %d adding chr\n", ret);
		goto err2;
	}
	DEBUG_LOG("", "success\n");
 
	return 0;
 
err2:
	kfree(chr_dev);
err1:
	unregister_chrdev_region(dev, 1);
err:
	return ret;
}
 
void chr_exit(void)
{
	DEBUG_LOG("", "unloading module\n");
 
	cdev_del(&chr_dev->cdev);
	kfree(chr_dev);
	unregister_chrdev_region(MKDEV(chr_major, chr_minor), 1);
 
	DEBUG_LOG("", "success\n");
}
 
module_init(chr_init);
module_exit(chr_exit);
```

