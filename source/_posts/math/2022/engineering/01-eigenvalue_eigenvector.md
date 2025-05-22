---
title: 特征值与特征向量  
date: 2022-08-25   
tags:   
    - 线性代数   
    - 工程数学 
---    

> 看[【工程数学基础】1_特征值与特征向量](https://www.bilibili.com/video/BV1fx41137Zm)的笔记。  

<!-- more -->
对于特定的线性变换$A$，它的特征向量$\vec{v}$，在经过这个变换后的新向量$\vec{v'}$，仍然与$\vec{v}$ 在同一直线上，仅长度或符号发生变化，即：  
$$A\vec{v} = \lambda \vec{v}$$  
其中，$\lambda$ 是标量，被称为$A$ 的特征值；$\vec{v}$ 被称为特征向量。  

例题：  
对于矩阵$A = \begin{bmatrix}
    1 & 1  \\  
    4 & -2
\end{bmatrix}$  
1. 有向量$\vec{v_1} = \begin{bmatrix}
    1 \\
    2
\end{bmatrix}$：  
$$A \vec{v_1} = \begin{bmatrix}
    1 \times 1 + 1 \times 2 \\
    4 \times 1 + (-2) \times 2
\end{bmatrix} = \begin{bmatrix}
    3 \\
    0
\end{bmatrix} $$  
不是特征向量。  
2. 有向量$\vec{v_2} = \begin{bmatrix}
    1 \\
    1
\end{bmatrix}$：  
$$A \vec{v_2} = \begin{bmatrix}
    1 \times 1 + 1 \times 1 \\
    4 \times 1 + (-2) \times 1
\end{bmatrix} = \begin{bmatrix}
    2 \\
    2
\end{bmatrix} = 2 \vec{v_2}$$  
是特征向量，特征值是`2`。  

## 如何求特征值和特征向量  
根据$A\vec{v} = \lambda \vec{v}$，可以写作$(A - \lambda I) \vec{v} = 0$，若使方程有非零解，则要求：  
$$|A - \lambda I| = 0$$  
以$A = \begin{bmatrix}
    1 & 1  \\  
    4 & -2
\end{bmatrix}$ 为例，应有$\begin{vmatrix}
    1-\lambda & 1  \\  
    4 & -2-\lambda
\end{vmatrix} = 0$  
得：$-(1-\lambda)(2+\lambda)-4 = 0$  
求得特征值：$\lambda_1 = 2, \lambda_2 = -3$    

### 根据特征值求特征向量  
把上面求得的特征向量分别代入$(A - \lambda I) \vec{v} = 0$:  
1. 对于$\lambda_1 = 2$，有$(A - \lambda I) \vec{v} = \begin{bmatrix}
    -1 & 1  \\
    4 & -4
\end{bmatrix}\begin{bmatrix}
    v_{11} \\
    v_{12}
\end{bmatrix} = 0$，求得关系$v_{11} = v_{12}$。  
2. 同理，对于$\lambda_2 = -3$，求得关系$-4v_{21} = v_{22}$  

因为特征向量的长度不会影响其性质，这里可以取$\vec{v_1} = \begin{bmatrix}
    1 \\
    1
\end{bmatrix}, \vec{v_2} = \begin{bmatrix}
    1 \\
    -4
\end{bmatrix}$

## 特征向量的应用  
特征向量可以用来化对角矩阵。  
设$P=\begin{bmatrix}  
    \vec{v_1} & \vec{v_2}
\end{bmatrix}$，$P$ 被称为过渡矩阵。则有：  
$$AP = A\begin{bmatrix}
    \vec{v_1} & \vec{v_2}
\end{bmatrix} = \begin{bmatrix}
    A \vec{v_1} & A \vec{v_2}
\end{bmatrix} = \begin{bmatrix}
    \lambda_1 \vec{v_1} & \lambda_2 \vec{v_2}
\end{bmatrix} \\  
= \begin{bmatrix}
    \lambda_1 v_{11} & \lambda_2 v_{21}  \\  
    \lambda_1 v_{12} & \lambda_2 v_{22}
\end{bmatrix}=\begin{bmatrix}
    v_{11} & v_{12}  \\  
    v_{12} & v_{22}
\end{bmatrix}\begin{bmatrix}
    \lambda_1 & 0 \\  
    0 & \lambda_2
\end{bmatrix} = P \Lambda$$  
如果在左边乘以$P^{-1}$，则有：  
$$P^{-1} A P = P^{-1} P \Lambda = \Lambda$$  

### 求解微分方程组  
特征向量和特征值还可以用来解微分方程组，例如：  
$$\begin{bmatrix}
    \dot{x_1} \\
    \dot{x_2}
\end{bmatrix} = \begin{bmatrix}
    1 & 1 \\
    4 & -2
\end{bmatrix}\begin{bmatrix}
    x_1 \\
    x_2
\end{bmatrix}$$  
可以简写为$\dot{X} = A X$，令$X = P Y$，则$\dot{X} = P \dot{Y}$。  
结合$A X = A P Y$，可得$P \dot{Y} = A P Y$，两边同时乘以$P^{-1}$ 可得：  
$$\dot{Y} = \Lambda Y$$  
即$\dot{Y} = \begin{bmatrix}
    2 & 0 \\
    0 & -3
\end{bmatrix} Y$，可得：$\left\{\begin{matrix}  
    \dot{y_1} = 2y_1  \\
    \dot{y_2} = 2y_2
\end{matrix}\right.$    
  
  
即：$\left\{\begin{matrix}  
    y_1 = C_1e^{2t}  \\
    y_2 = C_2e^{-3t}  
\end{matrix}\right.$  

$$X = PY = \begin{bmatrix}
    1 & 1 \\
    1 & -4
\end{bmatrix}\begin{bmatrix}
    C_1e^{2t}  \\
    C_2e^{-3t} 
\end{bmatrix} = \begin{bmatrix}
    C_1e^{2t} + C_2e^{-3t}  \\
    C_1e^{2t} - 4C_2e^{-3t} 
\end{bmatrix}$$


## 参考资料 
1. [如何用latex编写矩阵（包括各类复杂、大型矩阵）？](https://zhuanlan.zhihu.com/p/266267223)