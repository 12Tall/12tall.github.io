---
title: 线性时不变系统的可控性  
date: 2022-08-25   
tags:   
    - 控制理论    
    - 线性定常系统  
---  
  
> 观看[系统的可控性_Controllability](https://www.bilibili.com/video/BV1vx411j7ah)的笔记  
 
<!-- more -->
系统可控性的定义：对于系统$\dot{X} = AX +BU$，在$t_0$ 时刻处于$X_0$ 状态，存在一组输入$U$，可以将系统的状态转移到$X_1$。  
![](controllability.png)

以离散型的系统进行推导，假设系统方程为：  
$$X_{k+1} = AX_k + BU_k \tag{1}$$    

令$X_0 = 0$那么，从$k=0$ 时开始：  
- $X_1 = AX_0 + BU_0 = BU_0$  
- $X_2 = AX_1 + BU_1 = ABU_0 + BU_1$  
- $X_3 = AX_2 + BU_2 = A^2BU_0 + ABU_1 + BU_2$  
- ... = ...  
- $X_n = AX_{n-1} + BU_{n-1} =A^{n-1}BU_0 + A^{n-2}BU_1 + ... + ABU_{n-2} + BU_{n-1}$  

最后，$X_n$ 可以写作：  
$$X_n = \begin{bmatrix}
    B & AB & \dots & A^{n-2}B & A^{n-1}B
\end{bmatrix}\begin{bmatrix}
    U_{n-1}  \\
    U_{n-2}  \\
    \dots  \\
    U_{1}  \\
    U_{0}  
\end{bmatrix} \tag{2}$$  
即，经过$n$ 步之后，我们把系统的状态从$X_0$ 变成了$X_n$，这时定义$\begin{bmatrix}
    B & AB & \dots & A^{n-2}B & A^{n-1}B
\end{bmatrix}$ 叫做$C_o$ 矩阵，$\begin{bmatrix}
    U_{n-1}  \\
    U_{n-2}  \\
    \dots  \\
    U_{1}  \\
    U_{0}  
\end{bmatrix}$ 叫做矩阵$U$，要使矩阵$U$ 有解，则要求$C_o$ 满秩，即$|C_o| = n$。对于连续系统也是一样的。  
> 对于$C_o$ 来说，它和 $\begin{bmatrix}
    B & AB
\end{bmatrix}$ 同秩。$A^n$及以上可以由$A^0, A^1, ···, A^{n-1}$线性组合得到，不会影响秩的变化，所以只需要写到$A^{n-1}*B$ 也就是前$n$ 项

所以对于形如式$(1)$ 的线性定常系统来说，$|C_o|=n$ 就是系统可控的依据。  

**这里的可控是指状态的可控，而不是过程的可控**，在现实系统中，可能有其他的因素影响可控性。


<iframe src="//player.bilibili.com/player.html?aid=16067367&bvid=BV1vx411j7ah&cid=26214133&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>