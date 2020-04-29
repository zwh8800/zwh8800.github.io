---
title: "cortex-m3 系统异常相关寄存器"
date: "2014-04-25 00:00:00"
updated: "2014-04-25 00:00:00"
tags:
-  stm32
-  单片机
---


enc28j60 驱动和 udp 协议栈移植到 stm32 成功

[](/notename/ "archive 20140425")

<h3 style="color: #080">1. 手动挂起、清除系统异常和中断挂起示意</h3>

软件挂起
<table>
    <thead>
        <tr>
            <td>类型</td>
            <td>NMI</td>
            <td>PendSV</td>
            <td>SysTick</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>寄存器位</td>
            <td>NMIPENDSET</td>
            <td>PENDSVSET</td>
            <td>PENDSTSET</td>
        </tr>
    </tbody>
</table>
软件清除
<table>
    <thead>
        <tr>
            <td>类型</td>
            <td>PendSV</td>
            <td>SysTick</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>寄存器位</td>
            <td>PENDSVCLR</td>
            <td>PENDSVCLR</td>
        </tr>
    </tbody>
</table>

中断挂起状态示意

<span style="color: red">ISRPENDING</span>

寄存器: <span style="color: red">SCB_ICSR</span>(Interrupt Control and state register)

![image_1bl04ftuo1f9ck9318ol1pqn195c9.png-148.6kB][1]
![image_1bl04gc7heidbq71ikbn99tanm.png-174.2kB][2]

<h3 style="color: #080">2. 设置系统异常优先级</h3>
寄存器: <span style="color: red">SCB_SHPRx</span>(System handler priority)

![image_1bl04hde214oj1i9i13iv194p1vam13.png-101.3kB][3]
![image_1bl04hodm70q11la19pkuuh1jhr1g.png-116.3kB][4]
![image_1bl04i123oasa21c94f1u1r01t.png-57.5kB][5]

<h3 style="color: #080">3. 使能 fault，和挂起状态、活动状态示意</h3>
使能
<table>
    <thead>
        <tr>
            <td>类型</td>
            <td>Usage fault</td>
            <td>Bus fault</td>
            <td>mem fault</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>寄存器位</td>
            <td>USGFAULTENA</td>
            <td>BUSFAULTENA</td>
            <td>MEMFAULTENA</td>
        </tr>
    </tbody>
</table>
挂起状态
<table>
    <thead>
        <tr>
            <td>类型</td>
            <td>SVC</td>
            <td>Bus fault</td>
            <td>mem fault</td>
            <td>Usage fault</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>寄存器位</td>
            <td>SVCALLPENDED</td>
            <td>BUSFAULTPENDED</td>
            <td>MEMFAULTPENDED</td>
            <td>USGFAULTPENDED</td>
        </tr>
    </tbody>
</table>
活动状态
<table>
    <thead>
        <tr>
            <td>类型</td>
            <td>SysTick</td>
            <td>PendSV</td>
            <td>Debug Monitor</td>
            <td>SVC</td>
            <td>Usage fault</td>
            <td>Bus fault</td>
            <td>Mem fault</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>寄存器位</td>
            <td>SYSTICKACT</td>
            <td>PENDSVACT</td>
            <td>MONITORACT</td>
            <td>SVCALLACT</td>
            <td>USGFAULTACT</td>
            <td>BUSFAULTACT</td>
            <td>MEMFAULTACT</td>
        </tr>
    </tbody>
</table>

寄存器: <span style="color: red">SCB_SHCSR</span>(System handler control and state register)

![image_1bl04u1pi1o0v9cc19ugj11c672a.png-177.9kB][6]

一个 dump 出 scb(System control block 系统控制块) 的函数, 调试的时候有时很有用

```
#define PRIORITY_Msk 0xF0
#define PRIORITY_Pos 4
void dump_scb()
{
	uint32_t icsr = SCB->ICSR;
	uint32_t shcsr = SCB->SHCSR;
 
	printf("ICSR:\r\n");
	printf("\t there %s interrupt pending\r\n", 
		(icsr & SCB_ICSR_ISRPENDING_Msk) ? "is" : "isn't");
	printf("\t pending exception number:%u\r\n", 
		(icsr & SCB_ICSR_VECTPENDING_Msk) >> SCB_ICSR_VECTPENDING_Pos);
	printf("\t active exception number:%u\r\n", 
		(icsr & SCB_ICSR_VECTACTIVE_Msk) >> SCB_ICSR_VECTACTIVE_Pos);
 
	printf("SHPRx:\r\n");
	printf("\t Mem Manage:%hhd\r\n", (SCB->SHP[0] & PRIORITY_Msk) >> PRIORITY_Pos);
	printf("\t Bus Fault:%hhd\r\n", (SCB->SHP[1] & PRIORITY_Msk) >> PRIORITY_Pos);
	printf("\t Usage Fault:%hhd\r\n", (SCB->SHP[2] & PRIORITY_Msk) >> PRIORITY_Pos);
 
	printf("\t SVC:%hhd\r\n", (SCB->SHP[7] & PRIORITY_Msk) >> PRIORITY_Pos);
	printf("\t Debug Monitor:%hhd\r\n", (SCB->SHP[8] & PRIORITY_Msk) >> PRIORITY_Pos);
 
	printf("\t PendSV:%hhd\r\n", (SCB->SHP[10] & PRIORITY_Msk) >> PRIORITY_Pos);
	printf("\t SysTick:%hhd\r\n", (SCB->SHP[11] & PRIORITY_Msk) >> PRIORITY_Pos);
 
	printf("SHCSR:\r\n");
	printf("\t Usage Fault enable:%u\r\n",
		(shcsr & SCB_SHCSR_USGFAULTENA_Msk) >> SCB_SHCSR_USGFAULTENA_Pos);
	printf("\t Bus Fault enable:%u\r\n",
		(shcsr & SCB_SHCSR_BUSFAULTENA_Msk) >> SCB_SHCSR_BUSFAULTENA_Pos);
	printf("\t Mem Fault enable:%u\r\n",
		(shcsr & SCB_SHCSR_MEMFAULTENA_Msk) >> SCB_SHCSR_MEMFAULTENA_Pos);
 
	printf("\r\n");
 
	printf("\t SVCall pended:%u\r\n",
		(shcsr & SCB_SHCSR_SVCALLPENDED_Msk) >> SCB_SHCSR_SVCALLPENDED_Pos);
	printf("\t Bus Fault pended:%u\r\n",
		(shcsr & SCB_SHCSR_BUSFAULTPENDED_Msk) >> SCB_SHCSR_BUSFAULTPENDED_Pos);
	printf("\t Mem Fault pended:%u\r\n",
		(shcsr & SCB_SHCSR_MEMFAULTPENDED_Msk) >> SCB_SHCSR_MEMFAULTPENDED_Pos);
	printf("\t Usage Fault pended:%u\r\n",
		(shcsr & SCB_SHCSR_USGFAULTPENDED_Msk) >> SCB_SHCSR_USGFAULTPENDED_Pos);
 
	printf("\r\n");
 
	printf("\t SysTick active:%u\r\n",
		(shcsr & SCB_SHCSR_SYSTICKACT_Msk) >> SCB_SHCSR_SYSTICKACT_Pos);
	printf("\t PendSV active:%u\r\n",
		(shcsr & SCB_SHCSR_PENDSVACT_Msk) >> SCB_SHCSR_PENDSVACT_Pos);
	printf("\t Monitor active:%u\r\n",
		(shcsr & SCB_SHCSR_MONITORACT_Msk) >> SCB_SHCSR_MONITORACT_Pos);
	printf("\t SVCall active:%u\r\n",
		(shcsr & SCB_SHCSR_SVCALLACT_Msk) >> SCB_SHCSR_SVCALLACT_Pos);
	printf("\t Usage Fault active:%u\r\n",
		(shcsr & SCB_SHCSR_USGFAULTACT_Msk) >> SCB_SHCSR_USGFAULTACT_Pos);
	printf("\t Bus Fault active:%u\r\n",
		(shcsr & SCB_SHCSR_BUSFAULTACT_Msk) >> SCB_SHCSR_BUSFAULTACT_Pos);
	printf("\t Mem Fault active:%u\r\n",
		(shcsr & SCB_SHCSR_MEMFAULTACT_Msk) >> SCB_SHCSR_MEMFAULTACT_Pos);
}
 
#define DIVBYZERO_Pos 9
#define DIVBYZERO_Msk (1ul << DIVBYZERO_Pos)
#define UNALIGNED_Pos 8
#define UNALIGNED_Msk (1ul << UNALIGNED_Pos)
#define NOCP_Pos 3
#define NOCP_Msk (1ul << NOCP_Pos)
#define INVPC_Pos 2
#define INVPC_Msk (1ul << INVPC_Pos)
#define INVSTATE_Pos 1
#define INVSTATE_Msk (1ul << INVSTATE_Pos)
#define UNDEFINSTR_Pos 0
#define UNDEFINSTR_Msk (1ul << UNDEFINSTR_Pos)
void dump_ufsr()
{
	uint16_t ufsr = (SCB->CFSR & SCB_CFSR_USGFAULTSR_Msk) >> SCB_CFSR_USGFAULTSR_Pos;
	printf("UFSR:\r\n");
	printf("\t Divide by zero: %d\r\n", 
		(ufsr & DIVBYZERO_Msk) >> DIVBYZERO_Pos);
	printf("\t Unaligned access: %d\r\n", 
		(ufsr & UNALIGNED_Msk) >> UNALIGNED_Pos);
	printf("\t No coprocessor: %d\r\n", 
		(ufsr & NOCP_Msk) >> NOCP_Pos);
	printf("\t Invaild PC load: %d\r\n", 
		(ufsr & INVPC_Msk) >> INVPC_Pos);
	printf("\t Invaild state(attempt to entry ARM state): %d\r\n", 
		(ufsr & INVSTATE_Msk) >> INVSTATE_Pos);
	printf("\t Undefined instruction: %d\r\n", 
		(ufsr & UNDEFINSTR_Msk) >> UNDEFINSTR_Pos);
}
```

  [1]: http://static.zybuluo.com/zwh8800/1191dgqrfw76d139d4omlu1n/image_1bl04ftuo1f9ck9318ol1pqn195c9.png
  [2]: http://static.zybuluo.com/zwh8800/6f6kib4vfu4gk2c15b7j8lb1/image_1bl04gc7heidbq71ikbn99tanm.png
  [3]: http://static.zybuluo.com/zwh8800/8qp2dq1oke7qkd28ew17j5wn/image_1bl04hde214oj1i9i13iv194p1vam13.png
  [4]: http://static.zybuluo.com/zwh8800/20pp7nw51faremehckt1mqt5/image_1bl04hodm70q11la19pkuuh1jhr1g.png
  [5]: http://static.zybuluo.com/zwh8800/zvi2cg6p0okw2wm9pss3roam/image_1bl04i123oasa21c94f1u1r01t.png
  [6]: http://static.zybuluo.com/zwh8800/61h1c9pz2dfw4lhcjgy54xpz/image_1bl04u1pi1o0v9cc19ugj11c672a.png
