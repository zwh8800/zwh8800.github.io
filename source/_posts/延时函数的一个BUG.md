---
title: "延时函数的一个BUG"
date: "2013-12-18 00:00:00"
updated: "2013-12-18 00:00:00"
tags:
-  BUG
-  错题本
---


延时函数的一个BUG

[](/notename/ "archive 20131218")

```
void Delay_us (unsigned char time_us)
{
   TR2   = 0;                          // Stop timer
   TF2H  = 0;                          // Clear timer overflow flag
   TMR2  = -( (unsigned int)(SYSCLK * time_us / 1000000) );
   TR2   = 1;                          // Start timer
   while (!TF2H);                      // Wait till timer overflow occurs
   TR2   = 0;                          // Stop timer
}
 
void Delay_ms (unsigned char time_ms)
{
   unsigned char i;
 
   while(time_ms--)
      for(i = 0; i< 10; i++)           // 10 * 100 microsecond delay
         Delay_us(100);
}
```

先贴代码

这是silicon lab里自带的例子(其实不是, 本身第五行是这样写的

```
TMR2  = -( (UINT)(SYSCLK/1000000) * (UINT)(time_us) );
```

不论现在两种方法怎么写都有BUG.

先看silicon原版的吧, SYSCLK为24500000时除以1000000等于24.5, 转为整数, 近似成24, 这样还好, 差别不大.

假如没有开那么高的频率呢, 一般情况下, 我测试时用默认的8分频, 也就是SYSCLK = 12000000 / 8 = 1500000= 1.5MHZ  (用F340说吧, 比较明显)

SYSCLK / 1000000 = 1 < 1.5

一下子比1.5小了三分之一

导致我每次演示都会快那么三分之一.

然后我就把代码改成了上面贴的那样.

没想到, 当时以为改对了的, 还是有BUG.

当时的想法是, 既然除以1000000之后把小数部分消去了, 那就先乘上time_us(当时也意识到了, 这样会比之前慢一些, 因为SYSCLK / 1000000会在编译时优化求值, 而先做乘法, 再做除法的话两个工作都会在运行时进行)

如果当时的想法能向前再走一步的话就会找到这个BUG了. 既然要在运行时进行, 那么SYSCLK>32768, 会被认为是为signed int, 然后乘以time_us, time_us是unsigned char类型. 所以提升成signed int, 可是在Delay_ms函数中调用的是Delay_us(100), 24500000 * 100 = 2’450’000’000而232 / 2 – 1 = 2’147’483’647, 比2’450’000’000要小!, signed int的最大值竟然比2’450’000’000还小…之后的事情大家知道了吧, 2’450’000’000会被截断成一个负数!(对, 就是负数…)

![image_1bl05485217g51fci1kl2i1g19809.png-74.2kB][1]

原谅我才疏学浅, 这是第一次遇见超整数上限的事情(貌似原来写PSP程序的时候也遇见过一次, 取随机数超过signed int上限, psp平台的随机数最大是SIGNED_INT_MAX, 再进行加法的话就变成负的了)

一定记住教训!

  [1]: http://static.zybuluo.com/zwh8800/8qz85rwvubngw6a4i33hr5w8/image_1bl05485217g51fci1kl2i1g19809.png
