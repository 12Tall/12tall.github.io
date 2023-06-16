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

## 一维有限元  
> todo  


