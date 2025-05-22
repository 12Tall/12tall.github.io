---
title: 倒立摆状态反馈控制    
date: 2022-08-25      
tags:   
    - 控制理论    
    - 线性定常系统  
---  

> 摘抄自[倒立摆状态反馈控制——分析、建模与仿真(matlab)](https://blog.csdn.net/qq_41342525/article/details/106193258)，物理模型如下：   
<!-- more -->

![](model.svg) 

## 建立状态空间方程  
假设外力为$F$，小车质量为$M$、向右的位移为$s$，摆杆质量为$m$、长度为$2l$。要求使摆杆保持垂直，即$\theta = 0$。则可以对白干进行受力分析：  
1. 摆杆（质心）的加速度与受力的关系（向右、向上为正）：  
$$m\frac{d^2}{dt^2}(s+l\sin{\theta}) = F_H  \tag{1}$$  
$$\frac{d^2}{dt^2}(l\cos{\theta})=F_V - mg \tag{2}$$  
2. 摆杆转动惯量与受力的分析（顺时针为正）：  
$$T\ddot{\theta} = F_Vl\sin{\theta}-F_Hl\cos{\theta} \tag{3}$$  
3. 假设$d$ 为地面与小车的阻尼系数，则小车的受力情况分析：  
$$M\ddot{s} = F-F_V-d\dot{s} \tag{4}$$  
4. 摆杆的转动惯量$T=\frac{4}{3}ml^2$，联立以上$4$ 个方程，然后忽略阻尼系数$d=0$，因为$\theta \rightarrow 0$， 则$\sin{\theta}=\theta, \cos{\theta}=1$。可以得到以下方程：  
$$\frac{4}{3}ml^2\ddot{\theta}=mgl\theta-ml^2\ddot{\theta}-ml\ddot{s} \tag{5}$$  
$$M\ddot{s} = F - m\ddot{s} - ml\ddot{\theta}-k\dot{s} \tag{6}$$  
可以化简为：  
$$\frac{7}{3}l\ddot{\theta} + \ddot{s} = g\theta \tag{7}$$  
$$(M+m)\ddot{s} + ml\ddot{\theta}=F \tag{8}$$  
定义系统状态$x_1=\theta, x_2=\dot{\theta}, x_3=s, x_4=\dot{s}$，得到系统的状态方程：  
$$\begin{array}{lll}
    \dot{x_1} & = & x_2 \\
    \dot{x_2} & = & \frac{3(M+m)}{(4M+m)l}gx_1-\frac{3}{(4M+m)l}F\\
    \dot{x_3} & = & x_4 \\
    \dot{x_4} & = & -\frac{3mg}{4M+m}x_1 + \frac{4}{4M+m}F  \\
    y &=& x_1 
\end{array}$$  
代入数据，后得到：$\dot{X} = AX +BU, Y = CX+DU$，其中$y_1=\theta,y_2 = \dot{\theta}$：  
$$A=\begin{bmatrix}
    0 & 1 &0 & 0\\
    15.244 & 0 &0 & 0\\
    0 & 0 &0 & 1\\
    -0.363 & 0 &0 & 0
\end{bmatrix},B=\begin{bmatrix}
    0\\
    -0.741\\
    0\\
    0.494
\end{bmatrix},C=\begin{bmatrix}
    1 & 0 & 0 & 0 \\ 
    0 & 1 & 0 & 0 
\end{bmatrix}, D=\begin{bmatrix}
    0  \\
    0
\end{bmatrix}$$  

## 控制器设计  

首先判断系统的能控性` CONT=ctrb(A,B)；rank(CONT)`，结果为`4`，证明系统是可控的。**系统的特征多项式为：$\alpha(s)=det(sI-A)=s^4-20.601s^2$**发现特征值存在大于0 的情况，系统是不稳定的。  

### 配置极点  
这是一个四阶系统，我们可以配置两个**靠近虚轴的闭环主导极点**，另外两个远离虚轴得得极点，既可以将系统近似简化成一个二阶系统。根据二阶系统的调节时间、超调量等参数确定闭环主导极点：  
$$\lambda_1^*=-2+j2\sqrt{3}, \lambda_2^*=-2-j2\sqrt{3} \, (t_s \approx 2s, \zeta=0.5)$$  
然后再选两个远离虚轴的极点：$\lambda_3^*=\lambda_4^*=-10$，可以计算状态反馈增益矩阵：$K=\begin{bmatrix}
    -545.54 & -110.16 & -380.39 & -116.88
\end{bmatrix}$

或者也可以根据[LQR控制理论的应用之一阶倒立摆](https://zhuanlan.zhihu.com/p/353697932) 确定状态反馈增益矩阵。  

## （降维）观测器的设计  
假设我们只能测量到摆杆的角度、小车的位移两个状态，我们可以重新排序状态空间方程：  
$$x_1=\theta, x_2=s, x_3=\dot{\theta}, x_4=\dot{s} \tag{9}$$  
状态矩阵变为：  
$$A=\begin{bmatrix}
    0 & 1 &0 & 0\\
    0 & 0 &0 & 1\\
    15.244 & 0 &0 & 0\\
    -0.363 & 0 &0 & 0
\end{bmatrix},B=\begin{bmatrix}
    0\\
    0\\
    -0.741\\
    0.494
\end{bmatrix},C=\begin{bmatrix}
    1 & 0 & 0 & 0 \\ 
    0 & 1 & 0 & 0 
\end{bmatrix}, D=\begin{bmatrix}
    0  \\
    0
\end{bmatrix}$$   

1. 首先判断系统是能观的  
2. 设原系统的输出矩阵为$C=\begin{bmatrix}
    C_1 &\vdots& C_2
\end{bmatrix}$，其中$C_1$非奇异（满秩）：  
    2.1 构造状态变换矩阵$P=\begin{bmatrix}
    C_1^{-1} & -C_1^{-1}C_2 \\
    0 & I_{n-m}
\end{bmatrix}$  
    2.2 将原系统的状态矩阵变为  
$$\bar{A} = P^{-1}AP = \begin{bmatrix}
    \bar{A_{11}} & \bar{A_{12}} \\
    \bar{A_{21}} & \bar{A_{22}} 
\end{bmatrix}$$  
$$\bar{B} = P^{-1}B = \begin{bmatrix}
    \bar{B_{1}} \\
    \bar{B_{2}} 
\end{bmatrix}$$  
$$\bar{C} = CP = \begin{bmatrix}
    I & 0 
\end{bmatrix}$$  
3. 设计反馈增益矩阵$\hat{H}$，使得$\hat{A_{22}}-\hat{H}\hat{A_{12}}$ 的特征值在复平面的左半边指定位置上，一般观测器的极点为系统主导极点的三到五倍，可以确定$\bar{H}=\begin{bmatrix}
    H_{11} & H_{12}  \\
    H_{21} & H_{22}
\end{bmatrix}$    
4. 子系统$X_2$ 的观测器如下，而$Y=\begin{bmatrix}
    x_1 \\
    x_2
\end{bmatrix}$：  
$$\left\{\begin{array}{l}
    \dot{Z} = (\bar{A_{22}}-\bar{H}\bar{A_{12}})\hat{X_2} + (\bar{B_2}-\bar{H}\bar{B_1})U +(\bar{A_{21}}-\bar{H}\bar{A_{11}})Y  \\
    \hat{X_2} = Z + \bar{H}Y
\end{array} \right.$$  
5. 原系统的观测量为：  
$$\hat{X}=P\begin{bmatrix}
    x_1 \\
    \hat{x_2}
\end{bmatrix}$$  

虽然目前还没完全掌握降维观测器的知识，但是下面的连接却让我看到了有人实现了我想做的事情。念念不忘，必有回响吧！现在想想，应该好好地学习如何写代码了！

## 参看资料  
- [降维状态观测器的直观理解与仿真](https://blog.csdn.net/qq_34288751/article/details/123061451)  
- [simucpp：C++搭建微分方程求解器框架(重写simulink)](https://blog.csdn.net/qq_34288751/article/details/117740605)  
- [番外篇(1)模块次序表、代数环及其检测算法](https://blog.csdn.net/qq_34288751/article/details/122648967?spm=1001.2014.3001.5502)  
- [petercorke/bdsim](https://github.com/petercorke/bdsim)  

