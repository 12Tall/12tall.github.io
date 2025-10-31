---
title: 协方差矩阵与三维重建
date: 2025-10-30 17:01:39
tags:
    - python
    - 3d  
    - 建模  
    - ransac
---

最近在搞点云重建圆柱体，通过[ransac3d](https://leomariga.github.io/pyRANSAC-3D/)发现在点云部分缺失的情况下结果并不理想。但是其中有些知识点还是蛮有用的，算是复习了。  
![fit-bad](fit-bad.png)

<!-- more -->  

## RANSAC 算法  
随机采样一致性算法的核心流程：  
1. 随机取点；
2. 根据采样点拟合一个空间方程；
3. 判断所有在该方程附近点的数量；
4. 循环1-3，直到发现一组点，其拟合的方程包含最多的点

RANSAC 可以排除掉离群的点，但既然是随机采样，那就可能出现不准确的问题。于是RANSAC 之后通过最小二乘法重新拟合一遍所有的接近的点就是一个比较好的方案。  
然而在最小二乘法拟合圆柱方程时，需要给一个轴向的向量，在点云数据较为完整的情况下可以通过协方差矩阵求出。但是如果**点云不完整**，则会出现较大问题。


## 协方差矩阵  
假设有以下数据：  
name|height|weight|age
---|---|---|---  
p1|179|74|33
p2|187|80|31  
p3|175|71|28  
AVR|180.3|75|30.7  

则可计算方差：  
$$\sigma^2_H=\frac{1}{n}\sum^{n}_{i=1}(H_i-\bar{H})^2, \quad \text{where } n=3 \tag{1}$$
其中统计数据可以有很多个，所以`n>=1`。其他两个变量的方差计算方式相同，得到：  
$$\begin{array}{c|ccc}
 & \sigma_H & \sigma_W & \sigma_A \\
\hline
\sigma_H & 24.89 & & \\
\sigma_W & & 14 & \\
\sigma_A & & & 4.22
\end{array} \tag{2}$$  

上表中的横纵坐标只表示关系，不代表实际运算，虽然看起来像是乘法运算。  

类似地，`height`和`weight` 之间也存在着某些关系：
$$\sigma_H\sigma_W=\frac{1}{n}\sum^{n}_{i=1}[(H_i-\bar{H})(W_i-\bar{W})], \quad \text{where } n=3 \tag{3}$$
继续填入表（2）：
$$\begin{array}{c|ccc}
 & \sigma_H & \sigma_W & \sigma_A \\
\hline
\sigma_H & 24.89 & 18.7 &  4.4\\
\sigma_W & 18.7 & 14 & 3.3 \\
\sigma_A & 4.4 & 3.3 & 4.22
\end{array} \tag{4}$$
表（4）就表示协方差矩阵。协方差矩阵是对称矩阵。
## 矩阵的特征向量与特征值  
假设有
$$\mathbf{A}\vec{v}=\lambda\vec{v} \tag{5}$$
我们就叫$lambda$ 为矩阵$\mathbf{A}$的特征值，$\vec{v}$是与之对应的特征向量。一般来说，矩阵是多少维的，就会有多少对特征值和特征向量。

特征值和特征向量的求解步骤如下：  
$$\mathbf{A}\vec{v}=\lambda\vec{v} \rightarrow |(\mathbf{A}-\lambda\mathbf{I})|=0 \tag{6}$$
假设$\mathbf{A}=\begin{vmatrix}
4 & 1 & 1 \\
1 & 2 & 1 \\
3 & 2 & 3
\end{vmatrix}$，则有：
$$\mathbf{A}-\lambda\mathbf{I}=\begin{vmatrix}
4-\lambda & 1 & 1 \\
1 & 2-\lambda  & 1 \\
3 & 2 & 3-\lambda 
\end{vmatrix} \tag{7}$$

### 行列式的值
行列式的几何意义：
1. 缩放因数：行列式可以衡量一个线性变换对空间体积的缩放程度；
2. 有向体积：行列式可以表示由矩阵向量张成的平行多面体的**有向**体积。

求解行列式的值：
1. 高斯消元：复杂度$O(n^3)$ 更适合大规模运算  
2. 拉普拉斯展开：复杂度$O(n!)$ 适合小规模矩阵，更直观  

对于$n \times n$ 的行列式，可以以第$i_0$行展开，其值为：
$$det(\mathbf{A}) = \sum^n_{j=1}(-1)^{i_0+j}a_{i_0j}det(\mathbf{M}_{ij}) \tag{8}$$
之所以会出现正负系数，是因为行列式任意交换两行都会引起符号的变化。整体规律如下：
$$\begin{bmatrix}
+ & - & + & - \\
- & + & - & + \\
+ & - & + & - \\
- & + & - & +
\end{bmatrix}$$

结合式$(7)(8)$进行运算，得到：
$$\lambda^3-9\lambda^2+20\lambda-12=0 \tag{9}$$

### 有理根定理  
假设多项式方程所有系数都是整数，且存在有理根$\frac{p}{q}$：
$$a_nx^n+a_{n-1}x^{n-1}+\dots+a_0x^0=0, \quad \text{where }a_n\ne 0, a_0\ne 0 \tag{10}$$
则$p,q$必须分别是$a_0,a_n$的因子。

要求解式$(9)$，则可以逐个代入$-12$的所有因子，尝试$\lambda=1,2$发现满足后，可以待定系数法求出最后一个解$\lambda=6$。

### 由特征值求特征向量
由式$(7)$求特征向量，即是求方程组$(\mathbf{A}-\lambda\mathbf{I})\vec{v}=0$的解。**特征向量是两两正交的**

## 协方差矩阵的特征向量  

在主成份分析/PCA 中的意义，假设三维空间中所有的点存在于一个扁椭圆中：
1. 最大特征值对应的特征向量对应该扁椭圆最长轴的方向；
2. 第二大特征值对应的特征向量对应扁椭圆中与最长轴垂直的次长轴的方向；
3. 第三大特征值对应的特征向量对应扁椭圆中同时与最长轴和次长轴垂直的轴的方向；
4. 更高维度以此类推。。。  

![eigenvalues-and-eigenvectors](eigenvalues-and-eigenvectors.jpeg)

但是显而易见，如果采样数据不完整，有缺失，就会有很大的麻烦。

## 参考资料  
1. [2_数学基础_数据融合_协方差矩阵_状态空间方程_观测器问题 （06:30开始）](https://www.bilibili.com/video/BV12D4y1S7fU)  
2. [协方差矩阵的特征向量指的是什么](https://blog.csdn.net/weixin_43772166/article/details/106731233)  
3. [【深度学习数学基础 04】行列式与体积计算](https://zhuanlan.zhihu.com/p/28428594519)
4. [特征值和特征向量](https://zh.wikipedia.org/zh-hans/%E7%89%B9%E5%BE%81%E5%80%BC%E5%92%8C%E7%89%B9%E5%BE%81%E5%90%91%E9%87%8F)