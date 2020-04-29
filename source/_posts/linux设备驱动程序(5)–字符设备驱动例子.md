---
title: "linux 设备驱动程序 (5) – 字符设备驱动例子"
date: "2014-03-03 00:00:00"
updated: "2014-03-03 00:00:00"
tags:
-  linux
-  驱动开发
---


 linux 设备驱动程序 (5) – 字符设备驱动例子

[](/notename/ "archive 20140303")

这次给出一个例子, 比 (3) 中的例子稍微复杂一些. 在 (3) 中, 给出了一个字符设备的例子, 会保存最后一个写入的字节. 这次的例子使用一个链表保存写入的数据, 读取时从链表中移出数据:
![image_1bl0atutt1kn7iv5t3b18q8fr49.png-5.9kB][1]

因此这个驱动和 FIFO 和管道非常相似, 当用户写入数据时, write point 后移, 并且写入数据 (如果当前链表 node 空间用尽则创建新 node). 当用户读取数据时, read pointer 也后移 (如果 read pointer 指向后一个 node 则删除前一个 node)

所以首先写一个简单的单向链表:
```
#define BYTE_PER_NODE 4096	/* 每个节点的数据size */
struct linked_node
{
	char *data;	/* 指向一个数组, 数据保存在这里 */
	struct linked_node* next;	/* 指向下一个节点 */
};
/* 创建一个新node */
struct linked_node* create_node(void)	
{
	struct linked_node* ret;
	if ((ret = kmalloc(sizeof(struct linked_node), GFP_KERNEL)) == NULL)
	{
		DEBUG_LOG(KERN_WARNING, "no memory\n");
		goto err;
	}
	if ((ret->data = kmalloc(BYTE_PER_NODE, GFP_KERNEL)) == NULL)
	{
		DEBUG_LOG(KERN_WARNING, "no memory\n");
		goto err1;
	}
	return ret;
 
err1:
	kfree(ret);
err:
	return NULL;
}
/* 删除一个node */
void free_node(struct linked_node* node)
{
	kfree(node->data);
	kfree(node);
}
```
因为我们的读写指针 (read pointer/write pointer) 需要保存指向哪个节点, 以及在节点中的哪个位置. 所以用一个结构体来保存这个指针:
```
struct pos_pointer
{
	struct linked_node* node;
	size_t pos;
};
struct chr_dev
{
	struct pos_pointer read_ptr;
	struct pos_pointer write_ptr;
	struct semaphore sem;
	wait_queue_head_t queue;
 
	struct cdev cdev;
};
```
在我们的设备结构体中使用 pos_pointer 保存读写指针.

另外发现多了一个 sem 成员, 这个是上篇中学习的信号量. queue 成员是一个” 等待队列头”, 用于当无数据可读时进行休眠 [下一篇讲述].

在 chr_init() 函数中应该设置我们的读写指针和信号量设施:
```
/* in function chr_init() */
 
/* 设置私有数据 */
DEBUG_LOG(DEFAULT_LEVEL, "setup private data\n");
if ((node = create_node()) == NULL)
{
	goto err2;
}
chr_dev->read_ptr.node = node;
chr_dev->read_ptr.pos = 0;
chr_dev->write_ptr.node = node;
chr_dev->write_ptr.pos = 0;
DEBUG_LOG(DEFAULT_LEVEL, "success\n");
/* 初始化信号量 */
DEBUG_LOG(DEFAULT_LEVEL, "initialize semaphore\n");
sema_init(&chr_dev->sem, 1);
DEBUG_LOG(DEFAULT_LEVEL, "success\n");
/* 初始化等待队列 */
DEBUG_LOG(DEFAULT_LEVEL, "initialize wait queue\n");
init_waitqueue_head(&chr_dev->queue);
DEBUG_LOG(DEFAULT_LEVEL, "success\n");
```
在 chr_exit() 中也应该释放资源:
```
p = chr_dev->read_ptr.node;
chr_dev->read_ptr.node = NULL;
chr_dev->write_ptr.node = NULL;
while (p)
{
	q = p->next;
	free_node(p);
	p = q;
}
cdev_del(&chr_dev->cdev);
```
写入函数:
```
ssize_t write(struct file *filp, const char __user *buf, size_t count, loff_t *fpos)
{
	struct chr_dev *dev = filp->private_data;
	size_t this_write, total_write = 0;
	char* p;
 
	if (down_interruptible(&dev->sem) != 0)
		return -ERESTARTSYS;
 
	DEBUG_LOG(DEFAULT_LEVEL, "write from user,pid=%d [%s]\n", 
		current->pid, current->comm);
 
	while (count != 0)
	{
		this_write = MIN(BYTE_PER_NODE - dev->write_ptr.pos,
						count);
		p = &dev->write_ptr.node->data[dev->write_ptr.pos];
		if (copy_from_user(p, buf, this_write) != 0)
		{
			DEBUG_LOG(KERN_WARNING, "copy_from_user error\n");
			goto err;
		}
		count -= this_write;
		total_write += this_write;
		buf += this_write;
		dev->write_ptr.pos += this_write;
		if (dev->write_ptr.pos == BYTE_PER_NODE)
		{
			dev->write_ptr.node->next = create_node();
			dev->write_ptr.node = dev->write_ptr.node->next;
			dev->write_ptr.pos = 0;
		}
	}
 
	DEBUG_LOG(DEFAULT_LEVEL, "write success total_write=%d,pos=%d\n", 
		total_write, dev->write_ptr.pos);
 
	up(&dev->sem);
 
	wake_up_interruptible(&dev->queue);
	return total_write;
 
err:
	up(&dev->sem);
	return -EFAULT; 
}
```
我们使用循环将数据写入, 每次循环开始时检测当前 node 剩余空间 (BYTE_PER_NODE – dev->write_ptr.pos) 和用户要求写入的 count 谁更小, 取较小作为 this_write(这一次写入的数据). 写入 node 之后, 令 count-=this_write 和并且令写指针 +=this_write. 之后检测写指针是否到 node 的末尾, 如果是的话, create 一个新 node.

读取函数和写入很类似:
```
ssize_t read(struct file *filp, char __user *buf, size_t count, loff_t *fpos)
{
	struct chr_dev *dev = filp->private_data;
	size_t this_read, total_read = 0;
	char* p;
 
	if (down_interruptible(&dev->sem) != 0)
		return -ERESTARTSYS;
 
	DEBUG_LOG(DEFAULT_LEVEL, "read from user,pid=%d [%s]\n", 
		current->pid, current->comm);
 
	while (dev->read_ptr.node == dev->write_ptr.node &&
			dev->read_ptr.pos == dev->write_ptr.pos)
	{
		up(&dev->sem);
		if (filp->f_flags & O_NONBLOCK)
			return -EAGAIN;
 
		DEBUG_LOG(DEFAULT_LEVEL, "[%s] going to sleep\n", current->comm);
 
		if (wait_event_interruptible(dev->queue, (dev->read_ptr.node != dev->write_ptr.node ||
				dev->read_ptr.pos != dev->write_ptr.pos) ) != 0)
			return -ERESTARTSYS;
 
		if (down_interruptible(&dev->sem) != 0)
			return -ERESTARTSYS;
	}
 
	while (count != 0)
	{
		if (dev->read_ptr.node == dev->write_ptr.node)
		{
			this_read = MIN(dev->write_ptr.pos - dev->read_ptr.pos,
						count);
		}
		else
		{
			this_read = MIN(BYTE_PER_NODE - dev->read_ptr.pos,
						count);
		}
		if (this_read == 0)
			break;
 
		p = &dev->read_ptr.node->data[dev->read_ptr.pos];
		if (copy_to_user(buf, p, this_read) != 0)
		{
			DEBUG_LOG(KERN_WARNING, "copy_to_user error\n");
			goto err;
		}
		count -= this_read;
		total_read += this_read;
		buf += this_read;
		dev->read_ptr.pos += this_read;
		if (dev->read_ptr.pos == BYTE_PER_NODE)
		{
			struct linked_node* node;
			node = dev->read_ptr.node;
			dev->read_ptr.node = dev->read_ptr.node->next;
			free_node(node);
			dev->read_ptr.pos = 0;
		}
	}
 
	DEBUG_LOG(DEFAULT_LEVEL, "read success total_read=%d,pos=%d\n", 
		total_read, dev->read_ptr.pos);
 
	up(&dev->sem);
	return total_read;
 
err:
	up(&dev->sem);
	return -EFAULT;
}
```
[EOF]
  [1]: /images/86e4c5cbc6dbb08baa8ba93e91a4fccd.png
