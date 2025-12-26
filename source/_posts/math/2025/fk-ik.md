---
title: D-H 参数表到正逆过程
date: 2025-12-26 13:47:54
tags:
    - 机械臂
    - sympy  
    - 数值分析
---
在[D-H 参数表的建立](/2025/11/18/d-h_table/) 中，记录了建立D-H 表的一般步骤。现在将通过sympy 来计算机械臂运动学的正逆过程。  

<!-- more -->

## 准备过程  
简单定义几个类和工具函数：  
```python
import sympy as sp
# /2025/11/18/d-h_table/ 方程3~5

# 按X 轴旋转
def RotX( alpha: sp.Expr):
    return sp.Matrix([
        [1, 0, 0, 0],
        [0, sp.cos(alpha), -sp.sin(alpha), 0],
        [0, sp.sin(alpha), sp.cos(alpha), 0],
        [0, 0, 0, 1]
    ])

# 按Z 轴旋转
def RotZ(theta: sp.Expr):
    return sp.Matrix([
        [sp.cos(theta), -sp.sin(theta), 0, 0],
        [sp.sin(theta), sp.cos(theta), 0, 0],
        [0, 0,1, 0],
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

# 沿Z 轴平移
def TransZ(d: sp.Expr):
    return sp.Matrix([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, d],
        [0, 0, 0, 1]
    ])

def D_H(alpha, a, d, theta ):
    return RotX(alpha)*TransX(a)*TransZ(d)*RotZ(theta)
    # 下面写法与上面等价（数学结果上）
    # return RotX(alpha)*TransX(a)*RotZ(theta)*TransZ(d)
```


## 正过程（Forward Kinematics）  
参照[D-H 参数表的建立](/2025/11/18/d-h_table/)，打印正向过程中的变换矩阵：
```python
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

$$T_1 = \left[\begin{matrix}\cos{\left(\theta_{1} \right)} & - \sin{\left(\theta_{1} \right)} & 0 & 0\\\sin{\left(\theta_{1} \right)} & \cos{\left(\theta_{1} \right)} & 0 & 0\\0 & 0 & 1 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \tag{1}$$

$$T_2 = \left[\begin{matrix}\cos{\left(\theta_{2} \right)} & - \sin{\left(\theta_{2} \right)} & 0 & 0\\0 & 0 & 1 & 0\\- \sin{\left(\theta_{2} \right)} & - \cos{\left(\theta_{2} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \tag{2}$$
$$T_3 = \left[\begin{matrix}\cos{\left(\theta_{3} \right)} & - \sin{\left(\theta_{3} \right)} & 0 & a_{2}\\sin{\left(\theta_{3} \right)} & \cos{\left(\theta_{3} \right)} & 0 & 0\\0 & 0 & 1 & d_{3}\\0 & 0 & 0 & 1\end{matrix}\right] \tag{3}$$
$$T_4 = \left[\begin{matrix}\cos{\left(\theta_{4} \right)} & - \sin{\left(\theta_{4} \right)} & 0 & a_{3}\\0 & 0 & 1 & d_{4}\\- \sin{\left(\theta_{4} \right)} & - \cos{\left(\theta_{4} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \tag{4}$$
$$T_5 = \left[\begin{matrix}\cos{\left(\theta_{5} \right)} & - \sin{\left(\theta_{5} \right)} & 0 & 0\\0 & 0 & -1 & 0\\\sin{\left(\theta_{5} \right)} & \cos{\left(\theta_{5} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \tag{5}$$
$$T_6 = \left[\begin{matrix}\cos{\left(\theta_{6} \right)} & - \sin{\left(\theta_{6} \right)} & 0 & 0\\0 & 0 & 1 & 0\\- \sin{\left(\theta_{6} \right)} & - \cos{\left(\theta_{6} \right)} & 0 & 0\\0 & 0 & 0 & 1\end{matrix}\right] \tag{6}$$

$$T=T_1T_2T_3T_4T_5T_6=\left[\begin{matrix} n_x & o_x & a_x & p_x \\ n_y & o_y & a_y & p_y \\ n_z & o_z & a_z & p_z \\0 & 0 & 0 & 1\end{matrix}\right] \tag{7}$$
参考各变量意义如下：
- n（normal）：末端坐标系 X 轴 在基坐标系下的方向
- o（orientation）：末端坐标系 Y 轴 在基坐标系下的方向
- a（approach）：末端坐标系 Z 轴 在基坐标系下的方向
- p（position）：末端坐标系原点在基坐标系下的位置

将$\theta_{1-6}$ 的数值代入，就得到了机械臂末端的姿态和位置信息。
```python
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
$$T_{num} = \left[\begin{matrix}0 & 1 & 0 & -0.149\\1 & 0 & 0 & 0.451\\0 & 0 & -1 & -0.433\\0 & 0 & 0 & 1\end{matrix}\right] \tag{8}$$
点击[链接](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/simulation.html)可以查看在线的仿真。  

## 逆过程（Inverse Kinematics）  
对于大多数 6 自由度串联工业机器人（前三轴定位、后三轴定向）：
- 关节 1–3：主要决定 末端位置 P
- 关节 4–6：主要决定 末端姿态 N,O,A

于是，对于给定$T_{num}$ 可以根据式$(7)$ 求得各个关节转动的角度。一般过程如下：
1. 根据位移$P$，求得一些变量值  
2. 根据姿态$N,O,A$，求得剩余变量值
3. 姿态矩阵是正交矩阵，**正交矩阵的转置就是该矩阵的逆矩阵**  

但是解析解并不总是容易计算，于是我们还可以引入数值解：  
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

# 取部分方程用于求解（下面是全取了，但实际上不用那么多）  
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
**不具备实际工程意义，失败**




## 参考资料  
1. [从零手搓人形机器人之逆运动学解算](https://www.bilibili.com/video/BV1pJCDB9E3D/)  
2. [Sympy](https://www.sympy.org/en/index.html)
3. [Click to open the Simulator Tab ](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/simulation.html)