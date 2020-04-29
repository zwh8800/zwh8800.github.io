---
title: "keil C51数据类型和存储器类型"
date: "2013-11-20 00:00:00"
updated: "2013-11-20 00:00:00"
tags:
-  keil
-  c51
-  单片机
---


总结了 keil C51数据类型和存储器类型

[](/notename/ "archive 20131120")

![image_1bl03j66u1lv51rila2p1ref6jp9.png-71.3kB][1]

转的别处的, int是16位

    存储器类型         说　明
    
    data                  直接访问内部数据存储器（128字节),访问速度最快
    对应图中RAM中的的低128字节, 使用直接访问(0x00 – 0x7F)
    
    bdata                可位寻址内部数据存储器（16字节），允许位与字节混合访问
    对应图中RAM中的位寻址空间(0x20 – 0x2F)
    
    idata                 间接访问内部数据存储器（256字节），允许访问全部内部地址
    对应整个RAM, 但是用间接访问(0x00 – 0xFF)
    
    pdata                分页访问外部数据存储器（256字节），用MOVX @Ri指令访问
    对应图中外部存储器(0x0000 – 0x0FFF, C8051F340只有4K外部XRAM)
    
    xdata                外部数据存储器(64KB)，用MOVX @DPTR指令访问
    对应图中外部存储器(0x0000 – 0x0FFF, C8051F340只有4K外部XRAM)
    
    code                 程序存储器（64KB），用MOVC @A+DPTR指令访问
    对应图中FLASH(0x0000 – 0xFBFF

直接寻址是使用指令MOV A,direct
间接寻址是使用指令MOV a,@Ri

对于C8051F34x, 直接寻址与间接寻址速度都为2个时钟周期. 访问外部存储器(MOVC, MOVX)则需要3个时钟周期

![image_1bl03j66u1lv51rila2p1ref6jp9.png-71.3kB][2]

  [1]: /images/d6b938f5426aa61b879062ea20023cdf.png
  [2]: /images/1ed8417da90effaee1475ce507c40be6.png
