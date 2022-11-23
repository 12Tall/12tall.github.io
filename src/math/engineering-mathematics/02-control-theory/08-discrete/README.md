---  
title: 连续系统的离散化  
date: 2022-08-25   
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学    
tag:   
    - 控制理论    
    - 线性定常系统  
---   
 
> 无论是现根据连续系统设计出相应的控制器，然后再对控制器进行离散化；还是先对连续的系统进行离散化，再设计相应的控制器。从结果上看差别并不大。  

- 采样频率一般选取为信号最高频率的五到十倍  
- 输出量一般使用零阶保持器。若输出信号频率足够高，各种保持器的输出量应该是极为接近的  
- 采样周期$T$ 不能小于系统的计算所需时间  

## 连续系统离散化  
对于空间状态方程：  
$$\dot{X(t)} = AX(t)+BU(t) \tag{1}$$  
其解的形式为：  
$$X(t)=e^{A(t-t_0)X_{t_0}}+\int_{t_0}^te^{A(t-tau)}BU(\tau)d\tau \tag{2}$$  
当使用零阶保持器时，$U(t)=U(kT),kT\leq t\leq(k+1)T$，则$2$ 式可写为：  
$$X(t_{k+1})=e^{A(t_{k+1}-t_k)}X(t_k)+\int_{t_0}^te^{A(t-tau)}BU(t_k)d\tau \tag{3}$$  
因为$U(\tau)$ 在一个采样周期内可以看作是一个常数，则$3$ 式可以化简为：  
$$X(k+1)=e^{AT}X(k)+\int_{0}^T e^{A(T-\tau)}d\tau BU(k)$$  
考虑积分变限，最终结果为：  
$$X(k+1)=e^{AT}X(k)+\int_{0}^T e^{A\tau}d\tau BU(k) \tag{4}$$  

在Matlab 或Octave 中，可以通过`sys=ss(A,B,C)` 生成连续系统的空间状态方程。然后通过`sys_d=c2d(sys, simple_time)` 将连续系统离散化。


## 参考  
- [一文书尽离散化——连续系统离散化原理及应用](https://zhuanlan.zhihu.com/p/438475328)

<iframe src="//player.bilibili.com/player.html?aid=984708072&bvid=BV1Dt4y1J7tk&cid=809839051&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>  
