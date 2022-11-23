---  
title: 状态观测器设计 
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

> 在控制器设计中，$U$ 是根据系统状态确定的，但实际系统中，某个状态可能是不可测的。于是我们需要通过根据系统的输入和输出来估算某个状态的值。这就是系统的观测器。  


## Luenberger Observer  
实际系统的状态空间方程为：  
$$\begin{array}{l}
    \dot{X}=AX + BU   \\  
    Y = CX + DU 
\end{array} \tag{1}$$

假设$\hat{X}$ 为状态的估计值，$\hat{Y}$ 为输出的估计值，则有：  
$$\begin{array}{l}
    \dot{\hat{X}}=A\hat{X} + BU + L(Y-\hat{Y})  \\  
    \hat{Y} = C\hat{X} + DU 
\end{array} \tag{2}$$

我们需要寻找合适的矩阵$L$，使得估计值趋近于实际值。
首先整合式$(2)$，得：  
$$\dot{\hat{X}}=(A-LC)\hat{X} + (B-LD)U+LY \tag{3}$$  

然后整合式$(1),(3)$ 得：  
$$\dot{X}-\dot{\hat{X}}=(A-LC)(X-\hat{X}) \tag{4}$$

令误差$E_x=X-\hat{X}$，则有：  
$$\dot{E_x} = (A-LC)E_x \tag{5}$$  
要使误差$E_x \rightarrow 0$，则$A-LC$ 的特征值应小于$0$。  

> 从另一个角度理解，建立观测器相当于建立了一个新的反馈系统，使得误差趋近于0。  
> 而$L(Y-\hat{Y})$ 就相当于把实际输出和估计输出的误差反馈给了状态的估计值。  

## 可观测性  
假设矩阵$O=\begin{bmatrix}
    C\\
    CA\\
    \vdots \\
    CA^{n-1}
\end{bmatrix}$，若$Rank(O) = n$，则系统是可观测的。具体推导过程参考[系统的可控性](../03-controllability/README.md)。  

## 分离原理  
假设系统如式$(1)$ 所示，且满足可控可观的条件，但是无法通过直接手段测量系统状态。那么：  
1. 我们可以设计观测器$\hat{X}$ 去估算系统状态   
2. 然后根据观测结果，设计控制器$U=-K\hat{X}$   
3. 令$E=X-\hat{X}$将状态反馈$U$ 带入式$(1)$ 可得： 
$$\dot{X} = AX - BK\hat{X} = (A-BK)X +BKE \tag{6}$$  

合并式$(5),(6)$，可得：  
$$\begin{bmatrix}
    \dot{E_x}  \\
    \dot{X}
\end{bmatrix}=\begin{bmatrix}
    A-LC & 0\\
    BK & A-BK
\end{bmatrix}\begin{bmatrix}
    E_x  \\
    X
\end{bmatrix}=M\begin{bmatrix}
    E_x  \\
    X
\end{bmatrix} \tag{7}$$  
而我们的目标就是让$E_x,X$ 都趋近于$0$，即令矩阵$M$ 的特征值有负实部。因为矩阵$M$ 是三角矩阵，所以其特征值也是其主对角元素的特征值。
> 需要注意的是:  
> - 观测器的收敛速度应大于控制器的收敛速度  
> - 观测器可以是纯软件实现，可以简化控制系统的硬件设计  


至此，现代控制理论的基本概念就已经全部涉及到了，之后可以再去看书或者实践一些练手项目了。    


-----  

<iframe src="//player.bilibili.com/player.html?aid=18088018&bvid=BV1bW411i7j7&cid=29531718&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe><br/>  

<iframe src="//player.bilibili.com/player.html?aid=18088047&bvid=BV1bW411i77w&cid=29531759&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe><br/>  

<iframe src="//player.bilibili.com/player.html?aid=18363622&bvid=BV13W411v76t&cid=29974626&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>
