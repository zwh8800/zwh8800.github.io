---
title: "linux 设备驱动程序 (4) – 并发"
date: "2014-02-17 00:00:00"
updated: "2014-02-17 00:00:00"
tags:
-  linux
-  驱动开发
---


linux 设备驱动程序 (4) – 并发

[](/notename/ "archive 20140217")

进行 linux 驱动开发不得不考虑的问题就是并发问题. 因为在内核态, 代码是可抢占的, 你不知道什么时候内核会抢占你对 CPU 的使用权来执行另一段代码 (这段代码可能会修改掉你的数据). 而且现在大多使用 SMP(对称多处理器), 代码甚至可以同时执行. 性能得到了很大提升但是编程的复杂程度也高了很多. 特别是在如何防止数据被其他执行线程修改上. 幸运的是, linux 已经提供了很多设施来完成这个功能.

### 1. 信号量 & 互斥体
这个在多线程编程中太常见了, 就不赘述了. 另外记一下 semaphore 这个单词, 总是拼错.

列一下函数原型:
```
#include <linux/semaphore.h> /* 不像书中所写
				并没有<asm/semaphore.h> */
void sema_init(struct semaphore *sem, int val);
void down(struct semaphore *sem);
int down_interruptible(struct semaphore *sem);
int down_trylock(struct semaphore *sem);
void up(struct semaphore *sem);
 
void init_rwsem(struct rw_semaphore *sem);
void down_read(struct rw_semaphore *sem);
int down_read_trylock(struct rw_semaphore *sem);
void up_read(struct rw_semaphore *sem);
void down_write(struct rw_semaphore *sem);
int down_write_trylock(struct rw_semaphore *sem);
void up_write(struct rw_semaphore *sem);
void downgrade_write(struct rw_semaphore *sem);
```
<<linux 设备驱动程序>> 上所说的 init_MUTEX 函数貌似在新版本中已经删掉了, 可以用 sema_init(&sem, 1); 来代替.
down_interruptible 函数当被中断时会返回非零值, down_trylock 当信号量不可获得时会返回非零值.

### 2. 自旋锁
当对信号量执行 down 函数时, 如果当前无法获取信号量, 会阻塞当前执行线程, 但是并非 CPU 空转不工作. 而是” 进入休眠”. 进入休眠是一个有明确定义的术语. 当” 进入休眠” 时, 执行线程会进入休眠状态, 这时会把 CPU 让给其他执行线程知道将来它能获取信号量为止.

但是自旋锁不一样, 当线程对自旋锁进行” 锁定” 动作时, 如果自旋锁已经被其他线程锁定, 那么当前线程将进行” 自旋”. 所谓自旋, 其实就是一个 while 循环 [它循环重复检查这个锁直到锁可用为止]. 所以说可见自旋锁当锁定时不会让出 CPU.

所以自旋锁简单, 而且也比信号量快 (因为不用设计到 CPU 调度). 但是使用却有一些限制:

<ul>
<li>考虑当前系统是单处理器非抢占系统, 那么如果一个线程进入自旋状态, 那么因为没有抢占其他线程得不到执行, 所以无法解锁自旋锁. 那么这个线程会一直循环下去. 整个系统会被卡死. <span style="color: #0000ff;"><strong>所以在非抢占式单处理器系统上自旋锁被优化为不做任何事.</strong></span></li>
<li> 考虑在一个单处理器抢占式系统上. 一个线程获得了一个自旋锁, 然后再临界区执行时丢掉了 CPU(可能被抢占, 可能调用了进入休眠的函数). 如果获得 CPU 的线程也想获取那个自旋锁, 那么整个系统会死锁下去. <strong><span style="color: #0000ff;">所以为了避免这个, 当一个线程获得自旋锁之后<span style="color: #ff0000;">此线程所在的 CPU</span> 的抢占会被禁止.</span></strong> 另外,<strong><span style="color: #ff0000;"> 人们要注意不要再获得自旋锁之后执行会丢掉 CPU 的函数.</span></strong></li>
<li> 另外, 当线程获得自旋锁之后, 发生了中断, 中断例程也请求获取自旋锁, 这时整个系统也会进入死锁. <strong><span style="color: #0000ff;">可以在获取锁时关闭当前 CPU 中断来解决.</span></strong></li>
<li> 最后, 自旋锁的重要准则是: “<strong>自旋锁必须在可能的最短时间内拥有</strong> “</li>
</ul>

```
#include <linux/spinlock.h>
 
spinlock_t lock = SPIN_LOCK_UNLOCKED;
void spin_lock_init(spinlock_t *lock);
 
void spin_lock(spinlock_t *lock);
void spin_lock_irqsave(spinlock_t *lock, unsigned long flags);
void spin_lock_irq(spinlock_t *lock);
void spin_lock_bh(spinlock_t *lock);
 
void spin_unlock(spinlock_t *lock);
void spin_unlock_irqsave(spinlock_t *lock, unsigned long flags);
void spin_unlock_irq(spinlock_t *lock);
void spin_unlock_bh(spinlock_t *lock);
 
int spin_trylock(spinlock_t *lock);
int spin_trylock_bh(spinlock_t *lock);
```
irqsave 会将中断状态保存在 flags 中, 当 unlock 时必须提供同一个 flags.

irq 函数会禁止本处理器的中断.

bh 会关闭软中断.

同样, 自旋锁有 rw 版本.

### 3. 使用锁的一些准则与陷阱

<ul>
<li>在编写函数时, 被调用的函数不能锁定此函数中一定锁定的锁否则会造成死锁. 所以当编写那些假定调用者已经获取锁的函数时,<span style="color: #0000ff;"><strong> 最好在注释中写明</strong></span>, 在此函数被调用之前调用者已经加锁. 防止几个月后重写时在函数中误加锁造成死锁. <strong><span style="color: #0000ff;">[最好养成习惯只在某一类函数中加锁 (如只在系统调用直接调用的函数中加锁)]</span></strong></li>
<li> 必须同时获取多个锁时, 最好都按照一定顺序获取.</li>
<li> 先获取局部的锁, 再获取全局的锁.</li>
<li> 先获取信号量, 再获取自旋锁.</li>
</ul>

### 4. 循环队列
使用循环队列是一种免锁算法. 生产者在队列的一端中写入, 消费者从另一端取走. 如果设计的好, 可以不必使用锁.

在 <linux/kfifo.h> 中有实现好的循环队列.

### 5. 原子变量
当对一个简单的整数进行加减的时候也加锁显得有些小题大做了. 但是很多整数运算确实不是原子的, 如 ++i;

所以 linux 内核实现了原子类型 atomic_t 来进行高效的原子的整形运算.

具体参见 <asm/atomic.h>

### 6. 原子位操作
除了原子的整数变量, 内核也提供了原子的位操作类型和函数. 集体参见 <asm/bitops.h>

### 7.seqlock

### 8. 读取 - 复制 - 更新 (RCU)
