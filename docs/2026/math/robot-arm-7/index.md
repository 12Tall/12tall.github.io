---
title: 机械臂笔记（七）机械臂动力学参数辨识
date: 2026-01-21 09:08:52  
description: 简单梳理机械臂动力学方程参数辨识
tags:
    - python
    - 矩阵  
    - 机器人

prev: 
    text: 机械臂笔记（六）机械臂的动力学模型（牛顿-欧拉方程）
    link: '../robot-arm-6/'
next: 
    text: todo
    link: '.'
---  

在前面的文章中，我们得到了机械臂动力学模型的理想方程：  
$$
\tau = M(q)q'' + C(q,q')q'+G(q) 
\tag{1}
$$

但是实际上，伴随着制造误差、运动摩擦、磨损、负载变化等，这个理想模型很难直接应用到工业生产中，我们还需要通过后期实验数据，来计算机器人/机械臂的整体辨识参数。这些参数主要包含机械臂关节的质量、转动惯量、摩擦力等各种固有属性。  

虽然**动力学方程对于$q,q',q''$ 是非线性的，但是对于上述固有属性确是线性的**，因此，上述$(1)$式可以写作：  
$$
\vec{\tau} = Y(q,q',q'')\vec{\theta}  
\tag{2}
$$

然后： 
$$
\vec{\theta} = (Y^TY)^{-1}Y^T\vec{\tau}  
\tag{3}
$$


## 以1R 机械臂为例  
一个关节转动时，其力矩主要有以下四个来源：  
$$
\begin{array}{lllll}
\tau_J & = & Jq'' & \dots & _{惯量（转得快、加速大 → 费力）} \\
\tau_b & = & bq' & \dots & _{粘性摩擦（转得越快阻力越大）} \\
\tau_f & = & f sign(q') & \dots & _{库仑摩擦（正转一股力，反转一股力）} \\
\tau_g & = & k_g \cos (q) & \dots & _{重力（姿态不同 → 要托住）} 
\end{array}
\tag{4}
$$

合在一起即可得到一个可辨识的模型：  
$$
\begin{array}{lllll}
\tau & = & Jq'' + bq' + f sign(q') + k_g \cos (q) \\
 & = &  \underbrace{\begin{bmatrix} q'' & q' & sign(q') & \cos(q)\end{bmatrix}}_{非线性部分 Y}  
 \underbrace{\begin{bmatrix} J \\ b \\ f \\ k_g\end{bmatrix}}_{固有属性 \vec{\theta}}  
\end{array}
\tag{5}
$$
实验中，上式左边的力矩，右边的非线性部分，都可以通过测量或者简单地计算得出。根据实验数据，我们可以得出一批关于$\vec{\theta}$ 的方程组，之后通过最小二乘法等统计学分析工具，就可以得出所需的$\vec{\theta}$。  

## 以2R 机械臂为例（忽略耦合）
先假设两个关节互不影响，对系统进行建模：  
$$
\begin{array}{lllll}
\begin{bmatrix} \tau_1 \\ \tau_2 \end{bmatrix}
 & = & 
 \begin{bmatrix} 
 J_1q''_1+b_1q'_1+f_1 sign(q'_1) + k_{g_1}\cos(q_1)  \\ 
 J_2q''_2+b_2q'_2+f_2 sign(q'_2) + k_{g_2}\cos(q_1+q_2)  \\ 
\end{bmatrix} \\
 & = & 
 \begin{bmatrix} 
 q''_1 & q'_1 & sign(q'_1) & \cos(q_1) &0&0&0&0  \\ 
 0&0&0&0   & q''_2 & q'_2 & sign(q'_2) & \cos(q_1+q_2)  \\ 
\end{bmatrix}
 \begin{bmatrix} 
 J_1 \\ b_1 \\ f_1 \\k_{g_1} \\ J_2 \\ b_2 \\ f_2 \\k_{g_2} 
\end{bmatrix}
\end{array}
\tag{6}
$$

### 加入最低阶的耦合  

$$
\begin{array}{lllll}
\tau_1 
 & = & 
 \begin{bmatrix} 
 q''_1 & q''_2 & \cos(q_2)q''_1 & q'_1 & sign(q'_1) & \cos(q_1) & \cos(q_1+q_2) \\ 
\end{bmatrix}
 \begin{bmatrix} 
 J_{11} \\ J_{12} \\ k_{12} \\ b_1 \\ f_1 \\k_{g_1} \\ k_{g_2} 
\end{bmatrix} \\  
\tau_2 
 & = & 
 \begin{bmatrix} 
 q''_1 & q''_2 & \cos(q_2)q''_2 & q'_2 & sign(q'_2) & \cos(q_1+q_2) \\ 
\end{bmatrix}
 \begin{bmatrix} 
 J_{21} \\ J_{22} \\ k_{21} \\ b_2 \\ f_2 \\ k_{g_3} 
\end{bmatrix} \\  
\end{array}
\tag{7}
$$

## 矩阵分解  
实际测量中，对于矩阵$Y$ 经常存在以下情况：  
- 列之间线性相关  
- 或者某列全是0  
- 或者某些列是其他列的倍数  

例如，机械臂的参数：  
- 质量$m_1,m_2$  
- 质心$c_1,c_2$  
- 转动惯量$I_1, I_2$  


它们几乎永远以组合的形式出现，例如：  
- $a_1 = I_1 + m_1c^2_1$  
- $a_2 = I_2 + m_2c^2_2 + m_2l^2_1$  
- $a_3 = m_2l_1c_2$  

例如：  
$$
\tau = \begin{bmatrix}3 \\ 6 \\ 9 \end{bmatrix} = \begin{bmatrix}1 &1 \\ 2&2 \\3&3 \end{bmatrix}\begin{bmatrix}a \\ b\end{bmatrix}
\tag{8.1}
$$
会发现$(a,b)$ 有无穷多个解。则需要对矩阵进行奇异值分解、提取可辨识子空间、构造基参数、压缩回归矩阵（看不懂了）  

简单理解就是合并有线性关系的参数。减少回归矩阵的维度（把$a+b$ 看作一个变量）：  
$$
\tau = \begin{bmatrix}3 \\ 6 \\ 9 \end{bmatrix} = \begin{bmatrix}1 \\ 2 \\3 \end{bmatrix}\begin{bmatrix}(a + b)\end{bmatrix}
\tag{8.2}
$$
之后就可解了。  

> 最好是：每学一层理论，都配上一个最小可运行的实验！不然根本不知所云~

## 参考资料  
1. [奇异值分解](https://zh.wikipedia.org/zh-hans/%E5%A5%87%E5%BC%82%E5%80%BC%E5%88%86%E8%A7%A3)