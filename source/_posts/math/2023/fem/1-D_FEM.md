---
title: 一维静电场有限元例子  
date: 2023-07-10  
tags:  
    - 电机  
    - 仿真  
    - CAE  
    - 有限元
    - 电磁学    
---    

> ![](1-D_element_question.png)  
<!-- more -->
> 已知条件：  
> $$\begin{array}{lll}
    \epsilon_r = 1 \\  
    V_0 = 1V \\  
    V_5 = 0V  \\
    d = 8cm  \\  
    l = 2cm \\  
    N_e = 4 \\
    \rho = 10^{-8}C/m^3 
\end{array}$$  

## 计算参数  
由于是均匀材质，且等距的分割，所以矩阵$K$ 前面的系数是定值：  
$$K^e=\frac{\epsilon_r\epsilon_0}{l} \begin{bmatrix}
    +1 & -1 \\
    -1 & +1
\end{bmatrix} \approx \frac{8.85\times10^{-12}}{x\times10^{-2}} \begin{bmatrix}
    +1 & -1 \\
    -1 & +1
\end{bmatrix} = 4.425\times10^{-10} \begin{bmatrix}
    +1 & -1 \\
    -1 & +1
\end{bmatrix} \tag{1.1}$$  

同样可以求得向量$\boldsymbol{b}$ 或者叫$\boldsymbol{f^e}$：  
$$\boldsymbol{f^e} = -\frac{l\rho}{2} \begin{bmatrix}
    1 \\
    1
\end{bmatrix} = -10^{-10} \begin{bmatrix}
    1 \\
    1
\end{bmatrix} \tag{1.2}$$    

## 边界条件  
在已知两端均为`Dirichlet` 条件时，可以忽略矩阵$\boldsymbol{d^e}$。于是可以构造下面的矩阵：  
$$4.425\times10^{-10} \begin{bmatrix}
    1 & -1 & 0 & 0 & 0 \\
    -1 & 1+1 & -1 & 0 & 0 \\
    0 & -1 & 1+1 & -1 & 0 \\
    0 & 0 & -1 & 1+1 & -1 \\
    0 & 0 & 0 & -1 & 1 
\end{bmatrix} \begin{bmatrix}
    V_1  \\
    V_2  \\
    V_3  \\
    V_4  \\
    V_5  \\
\end{bmatrix} = -10^{-10} \begin{bmatrix}
    1 \\
    2 \\
    2 \\
    2 \\
    1
\end{bmatrix} \tag{1.3}$$    
化简后得：  
$$\begin{bmatrix}
    1 & -1 & 0 & 0 & 0 \\
    -1 & 2 & -1 & 0 & 0 \\
    0 & -1 & 2 & -1 & 0 \\
    0 & 0 & -1 & 2 & -1 \\
    0 & 0 & 0 & -1 & 1 
\end{bmatrix} \begin{bmatrix}
    V_1  \\
    V_2  \\
    V_3  \\
    V_4  \\
    V_5  
\end{bmatrix} = \begin{bmatrix}
    -0.2259887 \\
    -0.4519774 \\
    -0.4519774 \\
    -0.4519774 \\
    -0.2259887 
\end{bmatrix} \tag{1.4}$$
在已知$V_0 = 1V$ 的情况下，可以将$(4)$ 左边的矩阵的首行首列取消掉，并且将$V_1$ 的值替换到方程$(4)$ 的左右两边：  
$$\begin{bmatrix}
    2 & -1 & 0 & 0 \\
    -1 & 2 & -1 & 0 \\
    0 & -1 & 2 & -1 \\
    0 & 0 & -1 & 1 
\end{bmatrix} \begin{bmatrix}
    V_2  \\
    V_3  \\
    V_4  \\
    V_5  
\end{bmatrix} = \begin{bmatrix}
    -0.4519774 +1 \\
    -0.4519774 \\
    -0.4519774 \\
    -0.2259887 
\end{bmatrix} \tag{1.5}$$    
同理，可以应用第二条边界条件$V_5=0V$：  
$$\begin{bmatrix}
    2 & -1 & 0  \\
    -1 & 2 & -1 \\
    0 & -1 & 2 
\end{bmatrix} \begin{bmatrix}
    V_2  \\
    V_3  \\
    V_4  \\
\end{bmatrix} = \begin{bmatrix}
    -0.5480226 \\
    -0.4519774 \\
    -0.4519774 + 0 
\end{bmatrix} \tag{1.6}$$    
则根据方程$(6)$，则可以求解：  
$$\begin{bmatrix}
    V_2 \\
    V_3 \\  
    V_4
\end{bmatrix} = \begin{bmatrix}
    0.0720339  \\  
    -0.4039548 \\  
    -0.4279661  
\end{bmatrix} \tag{1.7}$$  

## 后处理阶段  
在已知每条线段的电压$V^e_1,V^e_2$ 的情况下，则可以通过插值函数（形函数）获取每一点的电压：  
$$V(\xi) = V^e_1N_1(\xi)+V^e_2N_2(\xi) \tag{1.8}$$  
又因为$\xi = \frac{2(x-x^e_1)}{x^e_2-x^e_1}-1$，所以：  
$$V(\xi) = V^e_1\frac{x^e_2-x}{x^e_2-x^e_1}+V^e_2\frac{x-x^e_1}{x^e_2-x^e_1} \tag{1.9}$$  

## 二阶有限元  
![](1-D_element_quadratic.png)  
二阶有限元中，每个元素应包含三个节点。那么在重置坐标系时，应取：  
$$\xi = \frac{2(x-x^e_3)}{x^e_2 - x^e_1} \tag{2.1}$$  
其中$x^e_3=\frac{x^e_2 + x^e_1}{2}$。  
对应的，新坐标系下的插值函数应有如下形式：  
$$V(\xi) = V^e_1N_1(\xi) + V^e_2N_2(\xi) + V^e_3N_3(\xi) \tag{2.2}$$  
以插值函数$N_1(\xi)$ 为例，要求：  
$$\begin{array}{l}
    N_1(-1) = 1  \\  
    N_1(0) = 0  \\  
    N_1(1) = 0  
\end{array}$$  
假设$N_1(\xi) = c\xi(\xi-1)$，则根据上面的条件可以确定系数$c=\frac{1}{2}$。同理可得：  
$$\begin{cases}
    N_1(\xi) = \frac{\xi(\xi-1)}{2}  \\
    N_2(\xi) = \frac{\xi(\xi+1)}{2}  \\
    N_3(\xi) = (1+\xi)(1-\xi)
\end{cases} \tag{2.3}$$  

### 确定系数  
$$K^e_{ij} = \epsilon^e\int^{x^e_2}_{x^e_1}(\frac{dN_i}{dx})(\frac{dN_j}{dx})dx = \epsilon^e\int^{+1}_{-1}(\frac{dN_i}{d\xi}\frac{d\xi}{dx})(\frac{dN_j}{d\xi}\frac{d\xi}{dx})\frac{l_e}{2}d\xi = \frac{2\epsilon^e}{l_e}\int^{+1}_{-1}\frac{dN_i}{d\xi}\frac{dN_j}{d\xi}d\xi \tag{2.4}$$  

根据上式，可以计算：  
$$K^e = \frac{\epsilon^e}{3l^e} \begin{bmatrix}
    7 & 1 & -8  \\
    1 & 7 & -8  \\
    -8 & -8 & 16  
\end{bmatrix} \tag{2.5}$$  
同样可以知道，这是一个对称矩阵。    

$$f^e_i=-\frac{l^e\rho^e_v}{2}\int^{+1}_{-1}N_i{\xi}d\xi = -\frac{l^e\rho_0}{6}\begin{bmatrix}
    1 \\
    1 \\
    4
\end{bmatrix} \tag{2.6}$$  
而$D^e_x(x) = -\epsilon^e\frac{dV(x)}{dx}$ 保持不变。  

### 二阶有限元中中组装元素  
组装元素与上面例题中的步骤一样。刚开始最好还是使用循环去完成而不是直接用矩阵，否则容易出错。  


### 二阶有限元中的后处理  
同上面的例题。  

## 三阶有限元   
![](1-D_element_cubic.png)  

于是在更高阶的有限元处理中，我们需要做的也就是更新$K^e, \boldsymbol{f^e}$。其余的处理步骤一样：  
$$K^e=\frac{\epsilon^e}{40l^e}\begin{bmatrix}
    148 & -13 & -189 & 54 \\
    -13 & 148 & 54 & -189 \\
    -189 & 54 & 432 & -297 \\
    54 & -189 & -297 & 432
\end{bmatrix} \tag{3.1}$$  

$$\boldsymbol{f^e} = -\frac{l^e\rho_0}{8} \begin{bmatrix}
    1 \\
    1 \\
    3 \\
    3
\end{bmatrix} \tag{3.2}$$  
$\boldsymbol{d}$ 矩阵不变。  
$$\boldsymbol{d} = \begin{bmatrix}
    -\epsilon^{(1)}\frac{dV}{dx}|_{x=x^{(1)}_1}  \\
    0 \\
    \vdots \\ 
    0 \\ 
    -\epsilon^{(N_e)}\frac{dV}{dx}|_{x=x^{(N_e)}_2}
\end{bmatrix}$$  

-----  

看完[一维有限元基础](./README.md)之后，还是有一种囫囵吞枣的感觉，估计再用Python 写一遍就好了吧。多看两遍总是能理解的！