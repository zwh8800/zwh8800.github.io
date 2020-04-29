---
title: "Quartus II开发工具的基本操作"
date: "2014-01-05 00:00:00"
updated: "2014-01-05 00:00:00"
tags:
-  FPGA
-  Quartus
---


Quartus II开发工具的基本操作

[](/notename/ "archive 20140105")

1 新建工程 New project wizard

2 file-new 编写源码,保存源文件.选择Processing->start->start analysis&synthesis 或者单击对应图标![image_1bl0cvqbj1cp8m9miju13lffdg9.png-0.3kB][1]

3 Tools-Netlist Viewers – RTL Viewer 查看生成综合后的电路结构图

4功能仿真: Processing->Generate Functional Simulation Netlist产生功能网络表;

File->new 新建VWF向量波形文件. 右击 Insert ->Insert Node or Bus 加入结点或总线,进行结点或总线信号的查找,选择

需要仿真观察的信号,进行信号设置;

保存文件;

单击菜单选项![image_1bl0d0ep0v0r1tfg1ddhh5ev2m.png-0.2kB][2]进行仿真设置,如

![image_1bl0d0r7u1nb31f0v1kl719vgic213.png-27kB][3]

单击工具按钮![image_1bl0d1p0hbqh11anq6k9u717io2g.png-0.3kB][4]进行功能仿真.

5时序仿真  需要对整个工程进行全编译,![image_1bl0d28ne1pp711i3gj2toc10ba2t.png-0.3kB][5],编译无误后

修改![image_1bl0d2o351ca6qcp1b7hkkq41e3a.png-26.9kB][6]为timing模式

单击![image_1bl0d33qb1upr1836mr01br11umg3n.png-0.3kB][7],进行时序仿真.

Quartus II 与ModelSim联合开发

源文件 测试文件编写完毕;

单击https://hzzz.lengzzz.com/blog/wp-content/uploads/2014/01/QQ%E6%88%AA%E5%9B%BE20140105164431.png![image_1bl0d44n11p6r1aob1guvj9gp44.png-0.2kB][8],选择EDA Tools Setting -> Simulation进行相关仿真设置.

设置完毕后,进行工程编译,无误后选择Tools ->Run EDA Simulation tool ->EDA RTL simulation 调用modelsim进行仿真.

  [1]: /images/7eaf49a4ca86aed1594b17f2e50c99e9.png
  [2]: /images/398b4b18f9458e2b73a3a076650f8935.png
  [3]: /images/f29e7afe9d3c69600e51e369ae8bf3a3.png
  [4]: /images/fe67cb460aa38c4a9ecb6fc17b2b79a8.png
  [5]: /images/de4269738854f31936d4a83eb5683771.png
  [6]: /images/80a945aa2bb2664e98bde7f55469f709.png
  [7]: /images/280fdedb63e565f594ad7ade46e0fbd3.png
  [8]: /images/c83b76a623082408c3abe6760bb0e0e4.png
