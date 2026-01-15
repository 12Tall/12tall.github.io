---
title: 机械臂笔记（二）运动学正逆过程
date: 2026-01-15 15:08:19  
description: 通过D-H 参数表实现机器人运动学的正逆过程
tags:
    - python
    - 矩阵  
    - 机器人
    - sympy

prev: 
    text: 机械臂笔记（一）D-H 参数表建立
    link: '../robot-arm-1/'

next: 
    text: 机械臂笔记（三）通过PyTorch 梯度下降进行逆运动学计算
    link: '../robot-arm-3/'
---  

在[机械臂笔记（一）D-H 参数表建立](../robot-arm-1/index.md)中，我们学犀利建立D-H 表的一般步骤。本文将通过`sympy` 库，计算机械臂运动学的正逆过程。  

## 准备工作  

根据[机械臂笔记（一）D-H 参数表建立](../robot-arm-1/index.md)中公式$(4),\,(5)$。可以构建以下函数：  
:::code-group

```python [trans.py]
from trans_x impot RotX, TransX
from trans_z impot RotZ, TransZ

def D_H(alpha, a, d, theta ):
    return RotX(alpha)*TransX(a)*TransZ(d)*RotZ(theta)
    # 下面写法与上面等价（数学结果上）
    # return RotX(alpha)*TransX(a)*RotZ(theta)*TransZ(d)
```

```python [trans_x.py]
import sympy as sp

# 按X 轴旋转
def RotX( alpha: sp.Expr):
    return sp.Matrix([
        [1, 0, 0, 0],
        [0, sp.cos(alpha), -sp.sin(alpha), 0],
        [0, sp.sin(alpha), sp.cos(alpha), 0],
        [0, 0, 0, 1]
    ])


# 沿X 轴平移
def TransX(a: sp.Expr):
     return sp.Matrix([
        [1, 0, 0, a],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
```

```python [trans_z.py]
import sympy as sp

# 按Z 轴旋转
def RotZ(theta: sp.Expr):
    return sp.Matrix([
        [sp.cos(theta), -sp.sin(theta), 0, 0],
        [sp.sin(theta), sp.cos(theta), 0, 0],
        [0, 0,1, 0],
        [0, 0, 0, 1]
    ])

# 沿Z 轴平移
def TransZ(d: sp.Expr):
    return sp.Matrix([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, d],
        [0, 0, 0, 1]
    ])
```
:::

## 正过程（Forward Kinematics）
依据上篇笔记中的改进D-H 参数表，可以构建正向过程的变换矩阵，将$\theta_{1-6}$ 的数值代入，就得到了机械臂末端的姿态和位置信息。  
:::code-group
```python [构建最终变换矩阵]
# 批量定义符号，前面补None 是为了从1 序号对齐
a  = (None,) + sp.symbols("a_1:7")
theta = (None,) + sp.symbols("theta_1:7")
d = (None,) + sp.symbols("d_1:7")
alpha = (None,) + sp.symbols("alpha_1:7")

T1=D_H(0,0,0, theta[1])
T2=D_H(-sp.pi/2,0,0, theta[2])
T3=D_H(0,a[2],d[3], theta[3])
T4=D_H(0-sp.pi/2,a[3],d[4], theta[4])
T5=D_H(sp.pi/2,0,0, theta[5])
T6=D_H(-sp.pi/2,0,0, theta[6])

T = sp.simplify(T1*T2*T3*T4*T5*T6)
```

```python [传入实际参数]
subs_dict = {
    # 各关节转动角度
    theta[1]: 0
    theta[2]: 0,
    theta[3]: 0,
    theta[4]: 0,
    theta[5]: 0,
    theta[6]: 0,

    # a 和d 都是机械臂的固有参数，是常量
    a[2]: 0.431,  
    a[3]: 0.020,

    d[3]: 0.149,
    d[4]: 0.433,
}

T_num = T.subs(subs_dict)
T_num
```
:::

最终转换矩阵形式如下：
$$T=T_1T_2T_3T_4T_5T_6=\left[\begin{matrix} n_x & o_x & a_x & p_x \\ n_y & o_y & a_y & p_y \\ n_z & o_z & a_z & p_z \\0 & 0 & 0 & 1\end{matrix}\right] \tag{1}$$

> 参考各变量意义如下：
> - n（normal）：末端坐标系 X 轴 在基坐标系下的方向
> - o（orientation）：末端坐标系 Y 轴 在基坐标系下的方向
> - a（approach）：末端坐标系 Z 轴 在基坐标系下的方向
> - p（position）：末端坐标系原点在基坐标系下的位置  

:::details 点击查看每一步的变换矩阵  
$$
\begin{array}{l}
    T_1 = \left[\begin{matrix}\cos{\left(\theta_{1} \right)} & - \sin{\left(\theta_{1} \right)} & 0 & 0\\\sin{\left(\theta_{1} \right)} & \cos{\left(\theta_{1} \right)} & 0 & 0\\0 & 0 & 1 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \\ 
    T_2 = \left[\begin{matrix}\cos{\left(\theta_{2} \right)} & - \sin{\left(\theta_{2} \right)} & 0 & 0\\0 & 0 & 1 & 0\\- \sin{\left(\theta_{2} \right)} & - \cos{\left(\theta_{2} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \\
    T_3 = \left[\begin{matrix}\cos{\left(\theta_{3} \right)} & - \sin{\left(\theta_{3} \right)} & 0 & a_{2}\\sin{\left(\theta_{3} \right)} & \cos{\left(\theta_{3} \right)} & 0 & 0\\0 & 0 & 1 & d_{3}\\0 & 0 & 0 & 1\end{matrix}\right] \\
    T_4 = \left[\begin{matrix}\cos{\left(\theta_{4} \right)} & - \sin{\left(\theta_{4} \right)} & 0 & a_{3}\\0 & 0 & 1 & d_{4}\\- \sin{\left(\theta_{4} \right)} & - \cos{\left(\theta_{4} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \\
    T_5 = \left[\begin{matrix}\cos{\left(\theta_{5} \right)} & - \sin{\left(\theta_{5} \right)} & 0 & 0\\0 & 0 & -1 & 0\\\sin{\left(\theta_{5} \right)} & \cos{\left(\theta_{5} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \\
    T_6 = \left[\begin{matrix}\cos{\left(\theta_{6} \right)} & - \sin{\left(\theta_{6} \right)} & 0 & 0\\0 & 0 & 1 & 0\\- \sin{\left(\theta_{6} \right)} & - \cos{\left(\theta_{6} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right]
\end{array}
$$
:::

替换实际数值得到初始状态：
$$
T_{num} = \left[\begin{matrix}0 & 1 & 0 & -0.149\\1 & 0 & 0 & 0.451\\0 & 0 & -1 & -0.433\\0 & 0 & 0 & 1\end{matrix}\right] \tag{2}
$$


点击[链接](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/simulation.html)可以查看在线的仿真。  

## 逆过程（Inverse Kinematics）  
对于大多数 6 自由度串联工业机器人（前三轴定位、后三轴定向）：
- 关节 1–3：主要决定 末端位置 P
- 关节 4–6：主要决定 末端姿态 N,O,A

于是，对于给定$T_{num}$ 可以根据式$(1)$ 求逆，得到各个关节转动的角度。一般过程如下：
1. 根据位移$P$，求得一些变量值  
2. 根据姿态$N,O,A$，求得剩余变量值
3. 姿态矩阵是单位正交矩阵，**正交矩阵的转置就是该矩阵的逆矩阵**  


但是解析解并不总是容易计算，于是我们还可以引入数值解，在后两篇笔记中实现。  

:::details 点击可以展开一个失败的数值计算案例

直接通过sympy 求逆：  
```python
# 给定姿态和位置信息
T_num = sp.Matrix([
    [ 0.966,	0.257	,0.022	,0.069],
    [-0.069,	0.174,	0.982,	0.626],
    [0.249	,-0.951	,0.186	,0.587],
    [0.000	,0.000,	0.000	,1.000],
])

# 替换掉机械臂的常量参数
T = sp.simplify(T.subs({
    a[2]: 0.431,
    a[3]: 0.020,

    d[3]: 0.149,
    d[4]: 0.433,
}))

# 取部分方程用于求解
eqs = [
    # --- 位置 ---
    T_n[0, 3] - T_num[0, 3],
    T_n[1, 3] - T_num[1, 3],
    T_n[2, 3] - T_num[2, 3],

    # --- X 轴方向 ---
    # T_n[0, 0] - T_num[0, 0],
    # T_n[1, 0] - T_num[1, 0],
    T_n[2, 0] - T_num[2, 0],

    # --- Y 轴方向 ---
    # T_n[0, 1] - T_num[0, 1],
    # T_n[1, 1] - T_num[1, 1],
    T_n[2, 1] - T_num[2, 1],

    # --- Z 轴方向 ---
    # T_n[0, 2] - T_num[0, 2],
    # T_n[1, 2] - T_num[1, 2],
    T_n[2, 2] - T_num[2, 2],
]

# 尝试多个初始值（初值的选择对于求解非常重要）
init_values = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],

    # [1.22173,-0.95993,-1.13446,0.80285,0.45379,0.62832]  # 实际值
]

variables = [theta[1], theta[2], theta[3], theta[4], theta[5], theta[6]]

# 尝试求解
for i, init in enumerate(init_values):
    try:
        print(f"尝试初始值 {i+1}...")
        sol = sp.nsolve(eqs, variables, init, tol=0.001, maxsteps=1000)
        print(f"成功! 解为:\n{sol}")
        break
    except Exception as e:
        print(f"失败: {e}")
        if i == len(init_values) - 1:
            print("\n所有初始值都失败了,建议:")
            print("1. 检查 T 矩阵定义是否正确")
            print("2. 检查目标位姿是否在工作空间内")
            print("3. 尝试更多不同的初始值")
```

因为没有条件约束，所以得到解不一定符合实际：  
```python
# Matrix([[-7.72491731805477], [-14.7422003906631], [4.35746204512255], [-3.50411915670601], [13.0101345948651], [7.90147643899537]])
# -82.708, -124.731, -110.340, 159.202, 25.729, 92.807
```
但是如果初始值取得贴近实际值，也会得到较好的效果，假如上面取消实际初始值的注释：
```python
# Matrix([[1.22173000000000], [-0.959930000000000], [-1.13446000000000], [0.782773875704379], [0.446574970116345], [0.644213908491614]])
```

### 验算方法  
位置误差比较容易得到，计算姿态误差：  
$$θ=arccos(\frac{trace(R_1^T​R_2​)−1}{2}​)\approx1\degree$$
**得到误差较大，不具备实际工程意义，失败**

:::


## 参考资料  
1. [从零手搓人形机器人之逆运动学解算](https://www.bilibili.com/video/BV1pJCDB9E3D/)  
2. [Sympy](https://www.sympy.org/en/index.html)
3. [Click to open the Simulator Tab ](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/simulation.html)