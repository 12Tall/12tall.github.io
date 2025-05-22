---
title: 状态空间    
date: 2022-08-25   
tags:   
    - 控制理论    
    - 线性定常系统  
---  
> 看[状态空间](https://www.bilibili.com/video/BV1fx41137dA) 的笔记  
 
<!-- more -->
对于如下的“弹簧-质量-阻尼系统”，其中`k` 为弹簧弹性系数、`d` 为阻尼系数：  
![](mass-spring-damping.png)
定义质量`m` 向右为正方向，那么对于输入外力`f(t)`，则有输出`x`：$m \ddot{x} = f(t) - k x - d \dot{x}$  
对上式进行拉氏变换可以得到：$m s^2 X(s) + k X(s) + d s X(s) = F(s)$，则该系统的传递函数为：  
$$G(s) = \frac{1}{ms^2 + ds + k} \tag{1}$$  

## 构建空间状态方程组  
我们可以选择系统的两个状态$z_1=x,z_2=\dot{x}$，则有：  
$$\begin{bmatrix}
    \dot{z_1} \\
    \dot{z_2}
\end{bmatrix} = \begin{bmatrix}
    0 & 1 \\
    -\frac{k}{m} & -\frac{d}{m}
\end{bmatrix} \begin{bmatrix}
    z_1  \\
    z_2
\end{bmatrix} + \begin{bmatrix}
    0 \\
    \frac{1}{m}
\end{bmatrix}\begin{bmatrix}
    F(t)
\end{bmatrix}$$  
而系统的输出：  
$$X(t) = \begin{bmatrix}
    1 & 0
\end{bmatrix} \begin{bmatrix}
    z_1 \\
    z_2
\end{bmatrix} + \begin{bmatrix}
    0
\end{bmatrix} \begin{bmatrix}
    F(t)
\end{bmatrix}$$  

写作一般形式：  
$$\begin{matrix}
    \dot{Z} = AZ + BU \\  
    Y = CZ + DU
\end{matrix} \tag{2}$$  

### 状态空间方程与传递函数之间的关系  
对系统的状态空间方程左右两端进行拉氏变换，得到：  
$$sZ(s)  = AZ(s) + BU(s) \tag{3.1} $$  
$$Y(s) = CZ(s) + DU(s) \tag{3.2}$$
将`3.1`左右移项可得$(sI-A)Z(s) = BU(s$，左右同时左乘$(sI-A)^{-1}$，可得：  
$$Z(s) = (sI-A)^{-1}BU(s) \tag{3.3}$$  
将式`3.3` 带入`3.2` 可得：  
$$Y(s) = C(sI-A)^{-1}BU(s) + DU(s) \tag{3.4}$$  
则系统的传递函数为：  
$$G(s) = \frac{Y(s)}{U(s)} = C(sI-A)^{-1}B + D \tag{4}$$  

> 如何求矩阵的逆矩阵？  
> $$A^{-1} = \frac{A^*}{|A|}$$  
> 其中$A*$，是矩阵$A$ 的伴随矩阵，对于二阶矩阵来说有一口诀：主对调，副变号
> $|A|$ 即为行列式的值，对于二阶矩阵来说，等于：主对角线的积-副对角线的积


对于上面“弹簧-质量-阻尼”系统的模型来说：  
- $A = \begin{bmatrix}
    0 & -1 \\
    -\frac{k}{m} & -\frac{d}{m}
\end{bmatrix}$  
  

- $B = \begin{bmatrix}
    0 \\ 
    \frac{1}{m}
\end{bmatrix}$  
  

- $C = \begin{bmatrix}
    1 & 0
\end{bmatrix}$  

  
- $D = \begin{bmatrix}
    0
\end{bmatrix}$    


- $I = \begin{bmatrix}
    1 & 0\\ 
    0 & 1
\end{bmatrix}$    

于是求得传递函数为：  
$$G(s) = \frac{Y(s)}{U(s)} = \frac{\frac{1}{m} }{s^2 + \frac{d}{m}s + \frac{k}{m} } \tag{5}$$  
上下同时乘以$\frac{1}{m}$，即可得到式`1`。  

**$(sI-A)^{-1}$ 决定了传递函数的极点**，因为传递函数的分母是$|(sI-A)|$ 决定的，参照[特征值与特征向量](../../01-eigenvalue-eigenvector/README.md)一节，这里的`s` 就是矩阵$A$ 的特征值。所以**矩阵$A$的特征值决定了系统的稳定性！**  

<iframe src="//player.bilibili.com/player.html?aid=15201360&bvid=BV1fx41137dA&cid=24743431&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>
