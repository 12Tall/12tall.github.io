---
title: 有限元计算电磁场  
date: 2023-06-15  
timeLine: true
icon: notebook
category:  
    - 笔记  
tag:  
    - 电机  
    - 仿真  
    - CAE  
    - 有限元
    - 电磁学    
---   

> 笔记中涉及公式推导的部分并不严谨，仅为了便于理解而记录。如果需要严谨的推导过程，则需要参考专业书籍。笔记中的例子取自[《INTRODUCTION TO THE FINITE ELEMENT METHOD IN ELECTROMAGNETICS》](https://de.mathworks.com/academia/books/introduction-to-the-finite-element-method-in-electromagnetics-polycarpou.html) 

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
所以基地的选择还是蛮重要的，但是无论怎么选，只要选取的阶数足够多，那么精确度肯定可以保证。即使是多项式也能取得很好的效果。  

假如实验函数$w_h(x)=\alpha_1x^2+\alpha_2x$，这个时候我们肯定第一想法就是有两个基底，按照上面的步骤计算发现只能算出来$\alpha_1 = -0.5$。这是为什么呢？  
仔细观察我们的边界条件可以看到$w_h'(1)=0$，即可得到$\alpha_2=-2\alpha_1$。表面上有两组基底但实际上只有一组。所以在选取基底时，一定要先注意基地间的耦合关系。

## 一维有限元  
> todo  


