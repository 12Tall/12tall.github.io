---
title: Nabla算子与梯度、散度、旋度  
date: 2022-08-10 00:00:01
tags:   
    - 微积分  
    - 算子  
    - 微分方程  
---


> 摘于：[【Nabla 算子】与梯度、散度、旋度-BiliBili](https://www.bilibili.com/video/BV1a541127cX)  
> $\nabla$：读作`nabla`，是希腊语中的一种竖琴。也被称作`atled` 因为它是$\Delta$(`delta`) 倒过来的形状。也有被称作`Del`，因此$\nabla$ 算子也被称作`Del` 算子

<!-- more -->
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
\right] \left[\hat{i} , \hat{j} \right] $$  

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
在[Sympy](https://docs.sympy.org/latest/modules/vector/fields.html) 中，有一个`vector` 模块，可以向量的计算。我们首先定义示例函数：$f(x,y)=cos(x)+sin(y)$  
```python
import numpy as np  
import sympy as sp # 导入符号运算库
from sympy.vector import CoordSys3D, Del # 导入坐标系，Nabla 算子
from sympy.utilities.lambdify import lambdify # 此函数可以将sympy 函数转化为可执行的numpy 函数
import matplotlib.pyplot as plt

C = CoordSys3D('C')  # 定义坐标系  
f = sp.cos(C.x) + sp.sin(C.y) # 定义函数  

fZ = lambdify((C.x, C.y), f, "numpy")  # 可执行的numpy 函数

# 函数定义域
x_vals = np.linspace(-5, 5, 100)
y_vals = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x_vals, y_vals)
Z = fZ(X, Y)

# 绘制函数图像  
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()
```
![](fn.png)

## 梯度——数量值函数到向量值函数  
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
\end{array} \begin{bmatrix}
    \hat{i} & \hat{j} & \dots
\end{bmatrix}
$$  

通过运行以下代码观察结果：   
```python
delop = Del()  # 定义Nabla 算子

grad = delop.gradient(f)  # 求函数的梯度

# 梯度是一组函数，所以要分别对每个坐标转化为numpy 函数进行求解
gradX = grad.dot(C.i).simplify()  # for i
fX = lambdify((C.x, C.y), gradX, "numpy")

gradY = grad.dot(C.j).simplify()  # for j
fY = lambdify((C.x, C.y), gradY, "numpy")

dX = fX(X, Y)
dY = fY(X,Y)

plt.quiver(X,Y,dX,dY)
plt.show()
```
因为上面的代码坐标点过于密集，可以手工稀疏之后，显示结果如下：  
![](grad.png)

## 散度——向量值函数到数量值函数  
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
上面的例子中，我们已经有了向量场`grad`，可以对于这个向量场求散度：  
```python  
diver = delop.dot(grad)  # 求散度公式

diverz = diver.simplify()   # 因为散度是一个数量场，没有许多坐标转化
fZ = lambdify((C.x, C.y), diverz, "numpy")

Z = fZ(X, Y)


# 绘制热力图像
plt.pcolormesh(X, Y, Z, cmap='jet')

# 设置标题和轴标签
plt.title('Sin Function')
plt.xlabel('x')
plt.ylabel('y')

# 添加颜色条
plt.colorbar()

# 显示图像
plt.show()
```
![](divergence.png)

从上面的图像中可以看到，温度越高的地方，对应函数梯度是向外发散的，证明此处函数是凹进去的。  


### 电场的散度   
> 此例牵扯到球坐标与直角坐标间的转换问题，具体可参考：[电场的高斯定律证明](https://wuli.wiki/online/EGausP.html)

假设有点电荷在原点处，有电场强度$\vec{f}(\vec{x}) = \frac{\vec{x} }{ {||\vec{x}||}^2}$，可得：  
$$\nabla \cdot \vec{f} = 0, (\vec{x} \neq \vec{0})$$  

所以除原点外，电场的散度处处为0

### 拉普拉斯算子  
$\vec{\nabla}^2 \cdot f = \nabla \cdot \nabla \cdot f$ 表示求一个函数的梯度的散度，这里的$f$ 的梯度在物理上一般可以是场强或者其他表示`势（驱动力）`的物理量，例如电场强度$\vec{E}$。如果在某一处的值为正，则表示该处存在着一个`源`，为负则表示此处存在着`漏`。  

## 旋度——向量值函数到向量值函数  
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
对于上面梯度的旋度，可以通过代码计算：  
```python
curl = delop.cross(grad)  

# 梯度是一组函数，所以要分别对每个坐标转化为numpy 函数进行求解
curlZ = curl.dot(C.k).simplify()  
fZ = lambdify((C.x, C.y), curlZ, "numpy")

Z = fZ(X, Y)

print(Z)
```
结果发现其旋度处处为0。

-----
📅 2022-08-10 Aachen  