---
title: 有限元计算电磁场  
date: 2023-06-15  
tags:  
    - 电机  
    - 仿真  
    - CAE  
    - 有限元
    - 电磁学    
---   

> 笔记中涉及公式推导的部分并不严谨，仅为了便于理解而记录。如果需要严谨的推导过程，则需要参考专业书籍。笔记中的例子取自[《INTRODUCTION TO THE FINITE ELEMENT METHOD IN ELECTROMAGNETICS》](https://de.mathworks.com/academia/books/introduction-to-the-finite-element-method-in-electromagnetics-polycarpou.html) 
<!-- more -->
## 静电场与泊松方程  

> 关于梯度、散度和旋度的问题，可以参考[这篇笔记](../nabla/README.md)  

从能量的角度考虑，电势$\phi(x,y,z) \cdot q = W(x,y,z)$；从电场力的角度来看，电场强度$\vec{E}(x,y,z) \cdot \vec{d} \cdot q = W(x,y,z)$。容易得出空间上某一点的场强与该点的电势的关系：$\vec{E}(x,y,z) = -\lim\limits_{\vec{d} \rarr \vec{0}}( \frac{\partial \phi(x,y,z)}{\partial \vec{d}})$，即**电场强度是电势梯度的负值**。  
$$\vec{E}(x,y,z) = -\nabla\cdot\phi(x,y,z) \tag{1.1.1}$$  

而对于空间上的某一点来说，其电场强度的散度等于这一点的电荷密度比上这一点的介电常数$\epsilon = \epsilon_r(x,y,z)\cdot\epsilon_0$，其中$\epsilon_r$ 是一个与材料有关的相对介电常数，无量纲。一般而言，材料的介电常数越大，导电能力越弱。  
$$\nabla\cdot\vec{E}(x,y,z) = \frac{\rho(x,y,z)}{\epsilon_r(x,y,z)\cdot\epsilon_0} \tag{1.1.2}$$  

那么联立$(1.1.1),(1.1.2)$ 可得：  
$$\nabla^2\cdot\phi(x,y,z) = -\frac{\rho(x,y,z)}{\epsilon_r(x,y,z)\cdot\epsilon_0} \tag{1.1.3}$$  

其中，$\phi(x,y,z)$ 一般是要求的空间中的电势分布；$\rho(x,y,z),\epsilon_r(x,y,z)$ 表示空间中电荷的密度与材料的相对介电常数，是已知的函数或者常数。  

### 代数解   
以$(1.1.3)$ 式为例，取一维情况，假设$\phi(x=0) = V_0, \phi(x=d)=0,\rho=\rho_0,\epsilon_r$ 为常数。则得到方程：  
$$\nabla^2\cdot\phi(x) =\frac{d^2\phi(x)}{dx^2} = -\frac{\rho_0}{\epsilon_r\cdot\epsilon_0} \tag{1.2.1}$$  
两边同时积分两次得：  
$$\phi(x) = \frac{\rho_0}{2\epsilon_r\epsilon_0}x^2+c_1x+c_0 \tag{1.2.2}$$  
代入边界条件，可得：  
$$\phi(x) = \frac{\rho_0}{2\epsilon_r\epsilon_0}x^2 - (\frac{\rho_0d}{2\epsilon_r\epsilon_0}+\frac{\phi_0}{d})x+\phi_0 \tag{1.2.3}$$  
当空间上没有电荷分布，即$\rho=0$时，式$(1.2.3)$ 简化为：  
$$\phi(x) = \phi_0 \cdot (1-\frac{x}{d}) \tag{1.2.4}$$  
表示在$0<x<d$ 时，区域内的电压随距离递减。符合预期。  

在数值分析或仿真计算中，求解如$(3)$ 的微分方程时，一般会给区域和对应的定边界条件。在有限元分析中，用户将空间划分为许多小网格，通过不断迭代计算网格节点的$\phi_i$，然后通过某种插值算法最后才组合出来任意点上的电势$\phi$。  

> 在这篇笔记中，重点只关注偏微分方程的求解与结果的插值，至于网格划分，一般可以通过现成的工具完成。    

### 加权余量法  
> [有限元之加权残值法初探](https://zhuanlan.zhihu.com/p/432639622) 这是一个求解二阶边值问题的十分清晰的例子。这里只记录简单的过程。  

假设有二阶微分方程：  
$$w'' + 1 = 0 \tag{1.3.1}$$  
并且给定边界条件：  
$$w(0)=0, w'(1)=0 \tag{1.3.2}$$  

可以先任意猜一个函数作为方程$(1.3.1)$ 的解，称作**实验函数(trial func)**。假设为：  
$$w_h = sin(\frac{\pi}{2}x) \tag{1.3.3}$$  
代入方程$(1.3.1)$ 可以求得假设的解与真实解之间的误差函数，即**残差(residual)**：  
$$r(x) = w_n'' + 1 = -(\frac{\pi}{2})^2sin(\frac{\pi}{2}x)+1 \tag{1.3.4}$$  

如果残差处处为0，那么$w_h(x)$ 就是我们需要的精确解。但是靠一次猜中概率未免太低，所以残差往往不会为0。其实这里还有一个问题：如何判断残差处处为0？即**加权残值测试**：  
如果残差函数$r(x)$ 处处为0，则对于任意的可积的**测试函数(test func)**，$v(x)$，他们积的积分必然也为0。即：  
$$\int_0^1v(x)r(x)dx = 0? \tag{1.3.5}$$  
将式$(1.3.5)$拆分，可以写作以下形式：  
$$\int_0^1v(x)r(x)dx = \int_0^1v(x)[w_h(x)''+1]dx = \underbrace{\int_0^1v(x)w_h''(x)dx }_{part 1}+ \underbrace{\int_0^1v(x)dx}_{part 2} \tag{1.3.6}$$  
将$part 1$分部积分为：  
$$\int_0^1v(x)w_h''(x)dx = [v(x)w_h'(x)]|^1_0 - \int_0^1v'(x)w_h'(x)dx \tag{1.3.7}$$  
所以式$(1.3.5)$ 最终就变成下面的形式：  
$$\int_0^1v(x)r(x)dx = [v(x)w_h'(x)]|^1_0 - \int_0^1v'(x)w_h'(x)dx + \int_0^1v(x)dx \tag{1.3.8}$$

这么做的目的是为了简化我们寻找测试函数$v(x)$ 的难度，只要满足$v(x)$ 一阶可导即可。  
如果我们取测试函数$v(x)$和实验函数$w_h(x)$ 有相同的形式，这种方法被称作**伽辽金法(Galerkin method)**。  

现取$v(x)=w_h = sin(\frac{\pi}{2}x)$，代入方程$(1.3.5)$，可得残差不等于零。为了使残差等于0，我们可以采取下面两个策略：  
1. 为实验函数添加系数，也被称作**自由度(DOF)**，而原先的$sin(\frac{\pi}{2}x)$ 则被称为**基函数(basis func)**；  
2. 为实验函数添加高次项，类似于级数的思想，只要高次项足够多，总能拟合出优秀的曲线  

首先应用第一种策略，令$w_h(x) = \alpha sin(\frac{\pi}{2}x)$，代入式$(1.3.5)$，$v(x)$ 系数不变，要使得结果为0，可以求得$\alpha=\frac{16}{\pi^2}$。添加上一个系数之后的拟合效果要好很多。  

继续应用第二种策略，为实验函数添加一组高阶的基函数和自由度：  
$$w_h(x) = \alpha_1sin(\frac{\pi}{2}x) +  \alpha_2sin(\frac{3\pi}{2}x) \tag{1.3.9}$$  
因为有了两个自由度，所以在验证加权残差时需要两个试函数：  
$$\begin{cases}
    v_1(x) = sin(\frac{\pi}{2}x)  \\
    v_2(x) = sin(\frac{3\pi}{2}x)
\end{cases} \tag{1.3.10}$$  
联立式$(1.3.5),(1.3.9),(1.3.10)$ 可以求解得到两个自由度。将使得我们的结果函数更接近与精确解。    
> 原笔记上没有，这里我也没算  

#### 基底的选择  
抱着试试看的态度，自己选择了一个多项式的基底，满足边界条件和二阶微分方程，则基底可以选择如下形式：  
$$w_h(x) = (x^2-2x) \tag{1.3.11}$$  
同样试函数$v(x)=w_h(x)=x^2-2x$，代入式$(1.3.5)$ 可以求解自由度$\alpha=-0.5$。歪打正着刚好式精确解。  
所以基底的选择还是蛮重要的，但是无论怎么选，只要选取的阶数足够多，那么精确度肯定可以保证。即使是多项是也能取得很好的效果。  

假如实验函数$w_h(x)=\alpha_1x^2+\alpha_2x$，这个时候我们肯定第一想法就是有两个基底，按照上面的步骤计算发现只能算出来$\alpha_1 = -0.5$。这是为什么呢？  
仔细观察我们的边界条件可以看到$w_h'(1)=0$，即可得到$\alpha_2=-2\alpha_1$。表面上有两组基底但实际上只有一组。所以在选取基底时，一定要先注意基底间的耦合关系。并且要能满足边界条件。  

## 一维有限元  
同样取$(1.2.1)$ 作为示例，假设一维场景，令$V(x=0) = V_0, V(x=d)=0,\rho=\rho_0,\epsilon_r$ 为常数。则有：  
$$\nabla^2\cdot V(x) =\frac{d^2V(x)}{dx^2} = -\frac{\rho_0}{\epsilon_r\cdot\epsilon_0} \tag{2.1.1}$$    

### 划分网格  
![](discrerization_of_the_1-D_domain.png)

划分网格在一维条件下就表现为划分线段。假设在$x \in [0,d]$ 划分了$N_e$ 个小的线段，则我们可以先求得每个小线段上的电势，最后再将结果组合起来，得到最终解。  

### 插值函数  
插值函数，也称作形函数，也是上文中的[实验函数](#加权余量法)。对于插值函数得选择，我们往往会做一些优化：  
![](interpolation_functions_and_xi_axis.png)  

上图$(a)$ 表示从网格中任意取一个线段$e$，并且假定其起止位置分别为$x^e_1,x^e_2$，**但是由于根据起止点求积分不太方便，这里我们考虑将其转化到新的$\xi$ 坐标系下**。令：  
$$\xi = \frac{2(x-x^e_1)}{x^e_2 - x^e_1}-1 \tag{2.2.1}$$  
可以得到$\xi\in [-1,1]$。这样在计算积分、最后组装结果时会相对简单一些。  

同样为了简化计算，我们取形函数为一次线性函数，并且只与起止点有关：  
$$V(\xi) = V^e_1N_1(\xi) + V^e_2N_2(\xi) \tag{2.2.2}$$  
这里$V^e_1,V^e_2$ 表示线段端点的电压，是未知量。要式上式成立则要求**形函数**：  
$$\begin{cases}
    N_1(\xi) = \frac{1-\xi}{2}  \\
    N_2(\xi) = \frac{1+\xi}{2}
\end{cases} \tag{2.2.3}$$  
![](interpolation_functions_and_xi_axis_2.png)

提一嘴，形函数的数量表示自由度，一般来说自由度越多，最后的解也就越精确。  

### 伽辽金法  
![](1-D_element.png)
在[加权余量法](#加权余量法) 中，我们提到了伽辽金法是一种特殊的加权余量法，其权重函数等于形函数。对于一维静电场的问题，我们的形函数只有两个自由度，在任意一条线段上，其电压的函数应如下式：  
$$V(x) = \sum\limits^n_{j=1}v^e_jN_j(x) \tag{2.3.1}$$  

其中$j$ 表示自由度，那么结合式$(2.1.1)$，其加权残差可以表示为：  
$$r^e = \int^{x^e_2}_{x^e_1}w [\frac{d}{dx}(\epsilon^e\frac{dV}{dx})+\rho^e_v]dx \tag{2.3.2}$$  
其中$\epsilon^e = \epsilon^e_r\epsilon_0$ 表示材料的固有属性，$\rho^e_v$ 表示材料中得电荷密度，为常数$0$。  
要令残差等于零，那么我们就需要寻找合适的$V(x)$，因为上面方程中唯一能调整的只有$V(x)$，也就是去发现接近于真实解得电压值。考虑分部积分法，式$(2.3.2)$ 可以化简为下面形式：  
$$\int^{x^e_2}_{x^e_1} (\frac{dw}{dx})\epsilon^e(\frac{dV}{dx})dx - \int^{x^e_2}_{x^e_1} w\rho^e_v dx - w\epsilon^e\frac{dV}{dx}|^{x^e_2}_{x^e_1} = 0 \tag{2.3.3}$$  

令$D^e_x(x) = -\epsilon^e\frac{dV(x)}{dx}$，则式$(2.3.3)$ 可以写作：  
$$\int^{x^e_2}_{x^e_1} (\frac{dw}{dx})\epsilon^e(\frac{dV}{dx})dx - \int^{x^e_2}_{x^e_1} w\rho^e_v dx + w(x^e_2)D^e_x(x^e_2) - w(x^e_1)D^e_x(x^e_1) = 0 \tag{2.3.4}$$

因为我们选取的自由度等于$2$，所以结合式$(2.3.1)$，可以构造出下面两个方程，用以求解线段两端得电压（电势）：  
$$\begin{cases}
    \int^{x^e_2}_{x^e_1} (\frac{dN_1}{dx})\epsilon^e(\sum\limits^n_{j=1}v^e_j\frac{dN_j}{dx})dx = \int^{x^e_2}_{x^e_1} N_1\rho^e_v dx - N_1(x^e_2)D^e_x(x^e_2) + N_1(x^e_1)D^e_x(x^e_1) \\    
    \int^{x^e_2}_{x^e_1} (\frac{dN_2}{dx})\epsilon^e(\sum\limits^n_{j=1}v^e_j\frac{dN_j}{dx})dx = \int^{x^e_2}_{x^e_1} N_2\rho^e_v dx - N_2(x^e_2)D^e_x(x^e_2) + N_2(x^e_1)D^e_x(x^e_1) \\
\end{cases} \tag{2.3.5}$$  
又因为：  
$$\begin{cases}
    N_1(x^e_1) = 1  \\ 
    N_2(x^e_1) = 0  \\ 
    N_1(x^e_1) = 0  \\ 
    N_2(x^e_1) = 1 
\end{cases}$$  
所以可以得到如下形式：  
$$\begin{cases}
    \int^{x^e_2}_{x^e_1} (\frac{dN_1}{dx})\epsilon^e\frac{dN_1}{dx}dx \cdot v^e_1 + \int^{x^e_2}_{x^e_1} (\frac{dN_1}{dx})\epsilon^e\frac{dN_2}{dx}dx \cdot v^e_2 = \int^{x^e_2}_{x^e_1} N_1\rho^e_v dx + D^e_x(x^e_1) \\    
    \int^{x^e_2}_{x^e_1} (\frac{dN_2}{dx})\epsilon^e\frac{dN_1}{dx}dx \cdot v^e_1 + \int^{x^e_2}_{x^e_1} (\frac{dN_2}{dx})\epsilon^e\frac{dN_2}{dx}dx \cdot v^e_2 = \int^{x^e_2}_{x^e_1} N_2\rho^e_v dx -D^e_x(x^e_2) \\
\end{cases} \tag{2.3.6}$$  
令$K^e_{ij} = \int^{x^e_2}_{x^e_1} (\frac{dN_i}{dx})\epsilon^e\frac{dN_j}{dx}dx, f^e_i= \int^{x^e_2}_{x^e_1} N_i\rho^e_v dx, \boldsymbol{d^e}=\begin{bmatrix}
    D^e_1  \\
    -D^e_2
\end{bmatrix}$，那么式$(2.3.6)$ 可以进一步精简为：  
$$\begin{bmatrix}
    K^e_{11} & K^e_{12} \\
    K^e_{21} & K^e_{22} 
\end{bmatrix}\begin{bmatrix}
    v^e_{1}  \\
    v^e_{2} 
\end{bmatrix} = \begin{bmatrix}
    f^e_{1}  \\
    f^e_{2} 
\end{bmatrix} + \begin{bmatrix}
    D^e_{1}  \\
    -D^e_{2} 
\end{bmatrix} \tag{2.3.7}$$  

回忆[插值函数](#插值函数) 中的坐标系变换部分，我们容易得到：  
$$d\xi = \frac{2}{x^e_2 - x^e_1}dx = \frac{2}{l^e}dx \tag{2.3.8}$$  
亦有：  
$$\frac{dN_i}{dx} = \frac{dN_i}{d\xi}\frac{d\xi}{dx} = \frac{2}{l^e}\frac{N_i}{d\xi} \tag{2.3.9}$$  
可以根据式$(2.3.9)$ 计算$K^e_{ij}$：  
$$K^e_{ij} = \int^{+1}_{-1}(\frac{2}{l^e}\frac{dN_i}{d\xi})\epsilon^e(\frac{2}{l^e}\frac{dN_j}{d\xi})\frac{l^e}{2}d\xi = \frac{2\epsilon^e}{l^e}\int^{+1}_{-1}\frac{dN_i}{d\xi}\frac{dN_j}{d\xi}d\xi \tag{2.3.10}$$  
有根据式$(2.2.3)$ 可得：  
$$\begin{cases}
    \frac{dN_1}{d\xi} = -\frac{1}{2}  \\
    \frac{dN_2}{d\xi} = \frac{1}{2}  
\end{cases} \tag{2.3.11}$$  
于是：  
$$K^e = \frac{\epsilon^e}{l^e}\begin{bmatrix}
    +1 & -1  \\
    -1 & +1
\end{bmatrix} \tag{2.3.12}$$    
同理，我们可以求$f^e_i=-\frac{l^e\rho^e_v}{2}\int^{+1}_{-1}N_i{\xi}d\xi$：  
$$f^e = -\frac{l^e\rho_0}{2}\begin{bmatrix}
    1 \\
    1
\end{bmatrix} \tag{2.3.13}$$  
这里的$\rho$ 取为常数。于是我们求节点电压（电势）的方程$(2.3.7)$ 可以进一步简写为：  
$$\frac{\epsilon^e}{l^e}\begin{bmatrix}
    +1 & -1  \\
    -1 & +1
\end{bmatrix} \begin{bmatrix}
    v^e_1  \\
    v^e_2
\end{bmatrix} = -\frac{l^e\rho_0}{2}\begin{bmatrix}
    1 \\
    1
\end{bmatrix} + \begin{bmatrix}
    D^e_1  \\
    -D^e_2
\end{bmatrix} \tag{2.3.14}$$  

现在可以看出来为什么切换坐标系可以简化计算了。  

## 组装结果   

我们在划分网格，也就是线段的时候，线段是彼此首尾相连的，也就是说一个线段尾端的各种参数应该是等于下一条线段首端的参数。由式$(2.3.7)$，可以写出所有线段的方程：  
$$\begin{cases}
    \begin{rcases}
        K^{(1)}_{11}v^{(1)}_{1} + K^{(1)}_{12}v^{(1)}_{2} & = & f^{(1)}_{1} + D^{(1)}_{1} \\
        K^{(1)}_{21}v^{(1)}_{1} + K^{(1)}_{22}v^{(1)}_{2} & = &  f^{(1)}_{2} - D^{(1)}_{2} \\
    \end{rcases} & l1\\
    \begin{rcases}
        K^{(2)}_{11}v^{(2)}_{1} + K^{(2)}_{12}v^{(2)}_{2} & = &  f^{(2)}_{1} + D^{(2)}_{1} \\
        K^{(2)}_{21}v^{(2)}_{1} + K^{(2)}_{22}v^{(2)}_{2} & = & f^{(2)}_{2} - D^{(2)}_{2} \\
    \end{rcases} & l2 \\
    \vdots  \\
    \begin{rcases}
        K^{(n)}_{11}v^{(n)}_{1} + K^{(n)}_{12}v^{(n)}_{2} & = &  f^{(n)}_{1} + D^{(n)}_{1} \\
        K^{(n)}_{21}v^{(n)}_{1} + K^{(n)}_{22}v^{(n)}_{2} & = & f^{(n)}_{2} - D^{(n)}_{2} \\
    \end{rcases} & ln\\
\end{cases} \tag{2.4.1}$$

并且有$v^{e}_2 = v^{e+1}_1$，令$v^{(1)}_i = v^{(2)}_{i-1} =V_i$，则上式可写作：  
$$\begin{cases}
    \begin{rcases}
        K^{(1)}_{11}V_1 + K^{(1)}_{12}V_2 & = & f^{(1)}_{1} + D^{(1)}_{1} \\
        K^{(1)}_{21}V_1 + K^{(1)}_{22}V_2 & = &  f^{(1)}_{2} - D^{(1)}_{2} \\
    \end{rcases} & l1\\
    \begin{rcases}
        K^{(2)}_{11}V_2 + K^{(2)}_{12}V_3 & = &  f^{(2)}_{1} + D^{(2)}_{1} \\
        K^{(2)}_{21}V_2 + K^{(2)}_{22}V_3 & = & f^{(2)}_{2} - D^{(2)}_{2} \\
    \end{rcases} & l2 \\
    \vdots  \\
    \begin{rcases}
        K^{(n)}_{11}V_{n} + K^{(n)}_{12}V_{n+1} & = &  f^{(n)}_{1} + D^{(n)}_{1} \\
        K^{(n)}_{21}V_{n} + K^{(n)}_{22}V_{n+1} & = & f^{(n)}_{2} - D^{(n)}_{2} \\
    \end{rcases} & ln\\
\end{cases} \tag{2.4.2}$$  

考虑线段首尾相连，故将$l1.(2), l2.(1)$ 式相加可得：  
$$K^{(1)}_{21}V_1 + (K^{(1)}_{22} + K^{(2)}_{11})V_2 + K^{(2)}_{12}V_3 = f^{(1)}_{2} - D^{(1)}_{2} + f^{(2)}_{1} + D^{(2)}_{1} \tag{2.4.3}$$  

如此类推，可以将式$(2.4.2)$ 写作矩阵的形式：  
$$\begin{bmatrix}
    K^{(1)}_{11} & K^{(1)}_{12} \\  
    K^{(1)}_{21} & (K^{(1)}_{22} + K^{(2)}_{11}) & K^{(2)}_{12} \\  
    & K^{(2)}_{21} & (K^{(2)}_{22} + K^{(3)}_{11}) & K^{(3)}_{12} \\  
    & & K^{(3)}_{21} & (K^{(3)}_{22} + K^{(4)}_{11}) & K^{(4)}_{12} \\  
    \vdots & \vdots & \vdots & \vdots & \vdots & \vdots  \\
    & & & K^{(N_e-1)}_{21} & (K^{(N_e-1)}_{22} + K^{(N_e)}_{11}) & K^{(N_e)}_{12} \\  
    & & & & K^{(N_e)}_{21} & K^{(N_e)}_{22}  \\  
\end{bmatrix} \begin{bmatrix}
    V_1 \\ 
    V_2 \\ 
    V_3 \\ 
    V_4 \\ 
    \vdots \\  
    V_{N_e} \\
    V_{N_e+1}
\end{bmatrix} = \begin{bmatrix}
    f^{(1)}_1 \\ 
    f^{(1)}_2 + f^{(2)}_1 \\ 
    f^{(2)}_2 + f^{(3)}_1 \\ 
    f^{(3)}_2 + f^{(4)}_1 \\ 
    \vdots \\  
    f^{(N_e-1)}_2 + f^{(N_e)}_1 \\
    f^{(N_e)}_2
\end{bmatrix} + \begin{bmatrix}
    D^{(1)}_1 \\ 
    -D^{(1)}_2 + D^{(2)}_1 \\ 
    -D^{(2)}_2 + D^{(3)}_1 \\ 
    -D^{(3)}_2 + D^{(4)}_1 \\ 
    \vdots \\  
    -D^{(N_e-1)}_2 + D^{(N_e)}_1 \\
    -D^{(N_e)}_2
\end{bmatrix} \tag{2.4.4}$$  

上式中的最右边一项表示电通量的密度，以第二行为例：  
$$ -D^{(1)}_2 + D^{(2)}_1 = \epsilon^{(1)}\frac{dV}{dx}|_{x=x^{(1)}_2} -  \epsilon^{(2)}\frac{dV}{dx}|_{x=x^{(2)}_1} \tag{2.4.5}$$  

如果是介质、电场变化连续，则式$(2.4.5)$ 应当近似等于$0$，这也是矩阵中最多的情况。  
$$\boldsymbol{d} = \begin{bmatrix}
    D^{(1)}_1 \\ 
    0 \\ 
    0 \\ 
    0 \\ 
    \vdots \\  
    0 \\
    -D^{(N_e)}_2
\end{bmatrix} \tag{2.4.6}$$
由此也可以看出，这一项一般用来表示边界条件。  

考虑式$(2.3.12), (2.3.13)$，则矩阵也可以写作如下形式：  
$$KV=\boldsymbol{b}+\boldsymbol{d} \tag{2.4.7}$$  
其中：  
$$K=\begin{bmatrix}
    \frac{\epsilon^{(1)}}{l^{(1)}} & -\frac{\epsilon^{(1)}}{l^{(1)}} \\
    -\frac{\epsilon^{(1)}}{l^{(1)}} & \frac{\epsilon^{(1)}}{l^{(1)}} + \frac{\epsilon^{(2)}}{l^{(2)}} &  -\frac{\epsilon^{(2)}}{l^{(2)}}  \\ 
    & -\frac{\epsilon^{(2)}}{l^{(2)}} & \frac{\epsilon^{(2)}}{l^{(2)}} + \frac{\epsilon^{(3)}}{l^{(3)}}  &  -\frac{\epsilon^{(3)}}{l^{(3)}} \\ 
    & & -\frac{\epsilon^{(3)}}{l^{(3)}} & \frac{\epsilon^{(3)}}{l^{(3)}} + \frac{\epsilon^{(4)}}{l^{(4)}}  &  -\frac{\epsilon^{(4)}}{l^{(4)}} \\ 
    \vdots & \vdots & \vdots & \vdots & \vdots & \vdots  \\
    & & & -\frac{\epsilon^{(N_e-1)}}{l^{(N_e-1)}} & \frac{\epsilon^{(N_e-1)}}{l^{(N_e-1)}} + \frac{\epsilon^{(N_e)}}{l^{(N_e)}}  &  -\frac{\epsilon^{(N_e)}}{l^{(N_e)}} \\ 
    & & & & -\frac{\epsilon^{(N_e)}}{l^{(N_e)}} & \frac{\epsilon^{(N_e)}}{l^{(N_e)}} \\ 
\end{bmatrix} \tag{2.4.8}$$  
$$\boldsymbol{b} = -\frac{\rho_0}{2}\begin{bmatrix}
    l^{(1)}  \\ 
    l^{(1)}+l^{(2)}  \\ 
    l^{(2)}+l^{(3)}  \\ 
    l^{(1)}+l^{(4)}  \\ 
    \vdots  \\
    l^{(N_e-1)}+l^{(N_e)}  \\ 
    l^{(N_e)}  \\ 
\end{bmatrix}$$  
> 这里是照着书上抄的，假设有$N_e$ 条线段。组装结果矩阵需要多次循环完成  
```matlab   
% 伪代码
% Initialize the global matrix
K=sparse(Nn,Nn);
b=zeros(Nn,1);
% Loop through the elements
for e=1:Ne
    % Double loop through the local nodes of each element
    for i=1:2
        for j=1:2
            K(elmconn(e,i),elmconn(e,j))=K(elmconn(e,i),elmconn(e,j))+Ke(i,j);
        end
    b(elmconn(e,i))=b(elmconn(e,i))+fe(i);
    end
end
```

## 边界条件  

在式$(2.4.4)$ 中，存在着$N_e$ 个方程和$N_e+2$ 个变量，因为$\boldsymbol{d}$ 中有两个微分是未知的，如果要求解的话，需要再知道两个变量值：  
- `Dirichlet` 边界条件：知道端点的函数值$v_1, v_{N_e+1}$。每知道一个，则可以消去一行，忽略掉未知的$\boldsymbol{d}$    
- `Neumann` 边界条件：知道端点的微分$-\epsilon^{(1)}\frac{dV}{dx}|_{x=x^{(1)}_1}, -\epsilon^{(N_e)}\frac{dV}{dx}|_{x=x^{(N_e)}_2}$  
- 混合边界条件，这个比较难以理解。如果已知一个端点的值和微分，那么可以求解其相邻节点的值。就不要以矩阵的想法去思考，而是以顺序求解方程的思路去求解就好了。  


-----  

这篇笔记中的公式很多，并且公式与节点的数量也很多。需要有一个[例子](./1-D_FEM.md) 来复习一遍就更好了。  
