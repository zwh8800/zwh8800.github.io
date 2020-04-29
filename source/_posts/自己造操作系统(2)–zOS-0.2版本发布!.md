---
title: "自己造操作系统 (2) – zOS-0.2 版本发布!"
date: "2014-05-23 00:00:00"
updated: "2014-05-23 00:00:00"
tags:
-  操作系统
---


自己造操作系统系列之 0.2 版

[](/notename/ "archive 20140523")

新增了信号量功能, 实现进程间同步.

zOS 暂时分成两条线, 一条是上文说的那些功能 (类似于宏内核, 加载执行)

另一条是今天发布的 zOS-mini, 只包含调度, 同步设施. 而且只需要三个文件

还是只能在 stm32 上运行

链接: [https://lengzzz.com/zOS/zOS_mini-0.2.zip](https://lengzzz.com/zOS/zOS_mini-0.2.zip)

下面是一个测试用例
四个线程, 以不同的时间闪烁 led, 线程间通过 sem 信号量同步:
```c
#include <stm32f10x.h>
#include <stm32f10x_rcc.h>
#include <stm32f10x_gpio.h>
#include "zOS.h"
 
void init();
 
#define BitP(addr, n) (*(volatile unsigned int *)(0x42000000 + (((unsigned)(addr) - 0x40000000) * 8 + (n)) * 4))
#define BitM(addr, n) (*(volatile unsigned int *)(0x22000000 + (((unsigned)(addr) - 0x20000000) * 8 + (n)) * 4))
 
#define STACK_SIZE 32
 
semaphore sem;
 
uint32_t stack0[STACK_SIZE];
void process0()
{
	while (1)
	{
		BitP(&GPIOA->ODR, 4) = 1;
		delay_ms(1000);
		BitP(&GPIOA->ODR, 4) = 0;
		delay_ms(1000);
	}
}
 
uint32_t stack1[STACK_SIZE];
void process1()
{
	while (1/*SYS_TICK < 10 * 1000 * 1000*/)
	{
		down_sem(&sem);
		BitP(&GPIOA->ODR, 0) = 1;
		delay_ms(125);
		BitP(&GPIOA->ODR, 0) = 0;
		delay_ms(125);
	}
	//create_process(&stack0[STACK_SIZE], process0);
	//kill_process();
}
uint32_t stack2[STACK_SIZE];
void process2()
{
	while (1)
	{
		down_sem(&sem);
		BitP(&GPIOA->ODR, 1) = 1;
		delay_ms(250);
		BitP(&GPIOA->ODR, 1) = 0;
		delay_ms(250);
	}
}
uint32_t stack3[STACK_SIZE];
void process3()
{
	while (1)
	{
		down_sem(&sem);
		BitP(&GPIOA->ODR, 2) = 1;
		delay_ms(500);
		BitP(&GPIOA->ODR, 2) = 0;
		delay_ms(500);
	}
}
uint32_t stack4[STACK_SIZE];
void process4()
{
	while (1)
	{
		up_sem(&sem);
		up_sem(&sem);
		BitP(&GPIOA->ODR, 3) = 1;
		delay_ms(1000);
		BitP(&GPIOA->ODR, 3) = 0;
		delay_ms(1000);
	}
}
 
int main(void)
{
	init();
	init_zos();
 
	init_sem(&sem, 0);
 
	create_process(&stack1[STACK_SIZE], process1);
	create_process(&stack2[STACK_SIZE], process2);
	create_process(&stack3[STACK_SIZE], process3);
	create_process(&stack4[STACK_SIZE], process4);
 
	schedule();
 
	while (1);
}
 
void init()
{
	GPIO_InitTypeDef gpio;
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
 
	gpio.GPIO_Pin =
		GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3 | GPIO_Pin_4;
	gpio.GPIO_Mode = GPIO_Mode_Out_PP;
	gpio.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &gpio);
}
```


