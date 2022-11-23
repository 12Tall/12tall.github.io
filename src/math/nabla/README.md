---  
title: Nabla算子与梯度、散度、旋度  
date: 2022-08-10
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学    
tag:   
    - 微积分  
    - 算子  
    - 微分方程  
---  


> 摘于：[【Nabla 算子】与梯度、散度、旋度-BiliBili](https://www.bilibili.com/video/BV1a541127cX)  
> $\nabla$：读作`nabla`，是希腊语中的一种竖琴。也被称作`atled` 因为它是$\Delta$(`delta`) 倒过来的形状。也有被称作`Del`，因此$\nabla$ 算子也被称作`Del` 算子

## 数量值函数与向量值函数  
一个函数的自变量可以是n 多个，对应着一个n 维空间的向量，其值域可以是一个数值，也可以是一个线性空间或线性空间的子集：  
1. $f:\mathbb{R}^n \rightarrow \mathbb{R}$：数量值函数（数量场）  
2. $f:\mathbb{R}^n \rightarrow \mathbb{R}^m$：向量值函数（向量场）  

### 数量值函数
$$f(x,y)=x^2+y^2$$  

### 向量值函数  
$$\vec{f}(x,y) = \left[ 
    \begin{matrix}
        x \\
        y        
    \end{matrix}
\right] $$  

## $\nabla$ 算子  
算子可以将函数转化为另一个函数，而$\nabla$ 算子可以实现数量值函数与向量值函数的互相转化、以及向量值函数间的互相转化，其定义式如下：  
$$\begin{array}{lll}
    \nabla & = & \left[ 
    \begin{matrix}
        \frac{\partial}{\partial{x_1}}, \frac{\partial}{\partial{x_2}}, \dots, \frac{\partial}{\partial{x_n}}
    \end{matrix}    
\right]^T \\  
&=&  \left[ 
    \begin{matrix}
        \frac{\partial}{\partial{x_1}} \\
        \frac{\partial}{\partial{x_2}} \\
        \vdots \\
        \frac{\partial}{\partial{x_n}}
    \end{matrix}    
\right]
\end{array}
$$  

### 数量值函数到向量值函数  
通过数量乘法，$\nabla$ 算子可以将数量值函数转化为向量值函数，表示函数值在各个自变量方向上变化的速度，也被称为梯度（Gradient）：  
$$\begin{array}{lll}
    \nabla f & = &  \left[ 
    \begin{matrix}
        \frac{\partial{f}}{\partial{x_1}} \\
        \frac{\partial{f}}{\partial{x_2}} \\
        \vdots \\
        \frac{\partial{f}}{\partial{x_n}}
    \end{matrix}    
\right]
\end{array}
$$  

### 向量值函数到数量值函数  
通过内积（点乘），$\nabla$ 算子可以将同维度的向量值函数转化为数量值函数，表示函数值在某个点上的发散程度，也被称为散（$s\grave{a}n$）度（Divergence）：  
$$\begin{array}{lll}
    \nabla \cdot \vec{f} & = &  \left[ 
    \begin{matrix}
        \frac{\partial{}}{\partial{x_1}} \\
        \frac{\partial{}}{\partial{x_2}} \\
        \vdots \\
        \frac{\partial{}}{\partial{x_n}}
    \end{matrix}    
\right] \cdot \left[ 
    \begin{matrix}
        f_1 \\
        f_2 \\
        \vdots \\
        f_n
    \end{matrix}    
\right] \\
& = & \frac{\partial{f_1}}{\partial{x_1}} + \frac{\partial{f_2}}{\partial{x_2}} + \dots + \frac{\partial{f_n}}{\partial{x_n}}
\end{array}$$  

可以理解为一个点上流入与流出的量的差。散度是通量的体密度。  

#### 电场的散度   
> 此例牵扯到球坐标与直角坐标间的转换问题，具体可参考：[电场的高斯定律证明](https://wuli.wiki/online/EGausP.html)

假设有点电荷在原点处，有电场强度$\vec{f}(\vec{x}) = \frac{\vec{x} }{ {||\vec{x}||}^2}$，可得：  
$$\nabla \cdot \vec{f} = 0, (\vec{x} \neq \vec{0})$$  

所以除原点外，电场的散度处处为0

### 向量值函数到向量值函数  
通过向量积（叉乘），$\nabla$ 算子可以将同维度的向量值函数转化为另一个向量值函数，表示函数值在某个点上的旋转程度，也被称为旋度（Curl）：  
$$\begin{array}{lll}
    \nabla \times \vec{f} & = &  \left[ 
    \begin{matrix}
        \frac{\partial{}}{\partial{x_1}} \\
        \frac{\partial{}}{\partial{x_2}} \\
        \vdots \\
        \frac{\partial{}}{\partial{x_n}}
    \end{matrix}    
\right] \times \left[ 
    \begin{matrix}
        f_1 \\
        f_2 \\
        \vdots \\
        f_n
    \end{matrix}    
\right] \\
& = & \begin{vmatrix}
\vec{i} & \vec{j} &\vec{k}  \\
\frac{\partial{}}{\partial{x}} & \frac{\partial{}}{\partial{y}} & \frac{\partial{}}{\partial{z}}  \\
f_1 & f_2 & f_3   
\end{vmatrix} \\
& = & \begin{bmatrix}
\frac{\partial{f_3}}{\partial{y}} - \frac{\partial{f_2}}{\partial{z}} \\
\frac{\partial{f_1}}{\partial{z}} - \frac{\partial{f_3}}{\partial{x}} \\ 
\frac{\partial{f_2}}{\partial{x}} - \frac{\partial{f_1}}{\partial{y}}
\end{bmatrix}
\end{array}$$  

可以理解为一个点附近的流速差。旋度是环量的面密度。需要注意的是旋度一般不超过三维空降。  

-----  
📅 2022-08-10 Aachen  