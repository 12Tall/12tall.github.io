---
title: 机械臂笔记（四）通过雅可比矩阵实现逆运动学运算 
date: 2026-01-15 16:00:46  
description: 通过雅可比矩阵实现逆运动学运算 
tags:
    - python
    - 矩阵  
    - 机器人


prev: 
    text: 机械臂笔记（三）通过PyTorch 梯度下降进行逆运动学计算
    link: '../robot-arm-3/'
next: 
    text: 机械臂笔记（五）机械臂的动力学模型（欧拉-拉格朗日方程）
    link: '../robot-arm-5/'
---  

# 机械臂笔记（四）通过雅可比矩阵实现逆运动学运算 

通过雅可比矩阵可以较快的完成逆运动学运算，但是全程是通过计算当前位置与目标位置的差距（向量），来进行一步步迭代修正。可以理解为**走一步看一步**。  

假如有向量函数$Z=F(X)$，如下式所示：
$$\begin{matrix} z_1 = f_1(x_1,x_2) \\  z_2 = f_2(x_1,x_2)\end{matrix} \tag{1}$$


已知当前状态：$z_{1curr},z_{2curr}$、目标状态$z_{1target},z_{2target}$以及当前的输入变量$x_{1curr},x_{2curr}$，求$x_{1target},x_{2target}$ 应该为多少。  
既然有目标状态和函数式$(1)$，可以通过解析法或者梯度下降法算出应该给出的输入，但是依据上面给出的条件，通过计算当前位置与目标位置的差距（向量），也可以得到各输入变量的需要变化的梯度：

$$
\begin{matrix}
    dz_1 = \frac{\partial f_1}{\partial x_1}dx_{1} + \frac{\partial f_1}{\partial x_2}dx_{2}  \\ 
    dz_2 = \frac{\partial f_2}{\partial x_1}dx_{1} + \frac{\partial f_2}{\partial x_2}dx_{2}
\end{matrix} 
\tag{2}
$$

写成向量的方式如下：
$$
\begin{bmatrix} 
    dz_1 \\ 
    dz_2 
\end{bmatrix} = 
\begin{bmatrix} 
    \frac{\partial f_1}{\partial x_1}& \frac{\partial f_1}{\partial x_2} \\
    \frac{\partial f_2}{\partial x_1}& \frac{\partial f_2}{\partial x_2}
\end{bmatrix}
\begin{bmatrix} 
    dx_1 \\ 
    dx_2 
\end{bmatrix} = 
J 
\begin{bmatrix} 
    dx_1 \\ 
    dx_2 
\end{bmatrix} 
$$  

其中矩阵$J$ 就是雅可比(Jacobian) 矩阵，看起来也是一组梯度向量组成的矩阵。  
反过来根据$dZ$ 和$J$求$dX$：  
$$
dX=J^{-1}dZ
$$  

根据实际情况$dZ$ 取值如果太大的话可能会引起较大的误差，但是我们可以根据$dZ$ 求得$dX$， 然后将$dX$ 缩放到一个实际可接受的范围，得到新的输入$x_{1n},x_{2n}$，计算下一步的位置$z_{1n},z_{2n}$。根据下一步的位置状态信息重新规划新的$dX_n$，一直循环值距离目标$z_{1target},z_{2target}$ 的误差足够小：  
1. 计算机械臂末端距离目标的向量方向和大小。如果小于一定阈值则停止计算；  
2. 根据当前关节角度计算雅可比矩阵；  
3. 计算雅可比矩阵的逆矩阵；  
4. 根据逆矩阵计算每个关节需要旋转的角度；   
5. 完成旋转操作；  
6. 返回步骤1，直到精度满足需要或达到循环次数限制。  

## 程序设计（仅做位置IK）  

当前坐标系$i-1$|下一个关节$i$|$\boldsymbol{R}_x/\alpha_i$|$d_x/a_i$|$\boldsymbol{R}_z/\theta_i$|$d_z/d_i$  
:---:|:---:|---:|---:|---:|---:
$0$|$1$|$0$|$0$|$\theta_1$|$0$
$1$|$2$|$-\frac{\pi}{2}$|$0$|$\theta_2$|$0$
$2$|$3$|$0$|$a_2$|$\theta_3$|$d_3$
$3$|$4$|$-\frac{\pi}{2}$|$a_3$|$\theta_4$|$d_4$
$4$|$5$|$\frac{\pi}{2}$|$0$|$\theta_5$|$0$
$5$|$6$|$-\frac{\pi}{2}$|$0$|$\theta_6$|$0$  

参照之前的参数表，首先我们需要Sympy 能够将推导的公式固化下来。  
```python
import jax
import jax.numpy as jnp
from typing import List, Sequence,Tuple
jax.config.update("jax_enable_x64", True)  # jax 默认不支持64位浮点数运算，需要手动启用  

# 某一个MDH 关节的MDH 参数矩阵构建
def mdh(alpha: float, a: float, theta: float, d: float) -> jnp.ndarray:
    cos_alpha = jnp.cos(alpha)
    sin_alpha = jnp.sin(alpha)
    cos_theta = jnp.cos(theta)
    sin_theta = jnp.sin(theta)
    return jnp.array([
        [cos_theta,             -sin_theta,             0,          a],
        [sin_theta*cos_alpha,   cos_alpha*cos_theta,    -sin_alpha, -d*sin_alpha],
        [sin_alpha*sin_theta,   sin_alpha*cos_theta,    cos_alpha,  d * cos_alpha],
        [0,                     0,                      0,          1]
    ],dtype=jnp.float64)

# 根据MDH 表都构建参数矩阵
def mdhs(params: List[Tuple[float, float, float, float]])->jnp.ndarray:
    t = jnp.eye(4)
    for param in params:
        (alpha, a, theta, d) = param
        t = t @ mdh(alpha, a, theta, d) 
    return t

# 指定机型（固化了某些参数）
def mdh_puma_560(theta:List[float]):
    alpha = [0, -jnp.pi/2,  0,      -jnp.pi/2,  jnp.pi/2,   -jnp.pi/2]
    a =     [0, 0,          0.431,  0.020,      0,          0] 
    d =     [0, 0,          0.149,  0.433,      0,          0]    
    return mdhs(zip(alpha,a,theta,d))[:3,3]
### 之所以取[:3, 3] 是只计算最终位置，加上姿态难度有些太大了
jac_puma_560 = jax.jacobian(mdh_puma_560)  # 推导puma 560 的雅可比矩阵
target_pos = jnp.array([                    # 目标位置
    [-0.344,	0.923,	-0.170,	0.213],
    [0.398,	0.307,	0.864,	0.847],
    [0.850,	0.230,	-0.474,	-0.078],
    [0.000,	0.000,	0.000,	1.000]
])[:3,3]


theta0 = jnp.zeros(6)  
init_pos = mdh_puma_560(theta0)     # 初始位置
step = 0.5          # 每次角度变换的步长系数 

for i in range(0, 1000):
    d_pose = target_pos-init_pos    # 计算位置查（向量）
    jac_pose = jac_puma_560(theta0) # 计算雅可比矩阵
    jac_pose_pinv = jnp.linalg.pinv(jac_pose) # 计算雅可比矩阵的逆矩阵
    d_theta = jac_pose_pinv@d_pose  # 计算角度变化
    
    theta0 = theta0 + d_theta*step  # 更新角度
    init_pos = mdh_puma_560(theta0) # 更新末端位置

    if jnp.linalg.norm(d_pose) < 1e-4:  # 当误差值小于允许之后就退出循环
        deg = jnp.rad2deg(theta0)
        print(deg)
        break
# 没有结果，失败
```

一般循环20次左右就能得到结果。比前面神经网络要快得多。     

| 方法    | 更新公式                     |
| ----- | ------------------------ |
| 梯度下降  | `Δθ = −α Jᵀ e`           |
| 伪逆 IK | `Δθ = J⁺ e`              |
| DLS   | `Δθ = Jᵀ (JJᵀ + λI)⁻¹ e` |

## 程序设计（包含姿态IK）  
如果要包含姿态的话，就需要在计算误差时将姿态误差也体现出来。最简单的就是把DMH 的输出展平，**事实上只要能将MDH 最终的结果辗成(nx1) 维**即可：  
```python
def mdh_puma_560(theta:List[float]):
    alpha = [0, -jnp.pi/2,  0,      -jnp.pi/2,  jnp.pi/2,   -jnp.pi/2]
    a =     [0, 0,          0.431,  0.020,      0,          0] 
    d =     [0, 0,          0.149,  0.433,      0,          0]    
    return mdhs(zip(alpha,a,theta,d)).flatten()
target_pos = jnp.array([
    [-0.344,	0.923,	-0.170,	0.213],
    [0.398,	0.307,	0.864,	0.847],
    [0.850,	0.230,	-0.474,	-0.078],
    [0.000,	0.000,	0.000,	1.000]
]).flatten()
# 这种试验结果是最好的
```

后面的代码不用做任何修改。基本10~20 次迭代也能达到不错的效果。如果剔除原矩阵的第四行也不错。
```python
def mdh_puma_560(theta:List[float]):
    alpha = [0, -jnp.pi/2,  0,      -jnp.pi/2,  jnp.pi/2,   -jnp.pi/2]
    a =     [0, 0,          0.431,  0.020,      0,          0] 
    d =     [0, 0,          0.149,  0.433,      0,          0]    
    return mdhs(zip(alpha,a,theta,d))[:4, :3].flatten()
target_pos = jnp.array([
    [-0.344,	0.923,	-0.170,	0.213],
    [0.398,	0.307,	0.864,	0.847],
    [0.850,	0.230,	-0.474,	-0.078],
    [0.000,	0.000,	0.000,	1.000]
])[:4, :3].flatten()
```

因为机械臂末端一般只有一个旋转的自由度（夹抓或焊枪），所以也可以只取末端的z 轴（或z+x 轴）和位置作为判断目标：
```python
def mdh_puma_560(theta:List[float]):
    alpha = [0, -jnp.pi/2,  0,      -jnp.pi/2,  jnp.pi/2,   -jnp.pi/2]
    a =     [0, 0,          0.431,  0.020,      0,          0] 
    d =     [0, 0,          0.149,  0.433,      0,          0]    

    T = mdhs(zip(alpha,a,theta,d))
    return jnp.concatenate([T[:3,3], T[:3,2]])
```

上面代码测试结果有时候会出现角度非常大的情况，基本上将其缩放至0~360 之内就还可以。

### 自适应步长  
自适应步长可以在非常接近目标值时依然能保持较好的收敛，但是结果就是收敛速度比较慢。
```python
prev_d_pose = target_pos-init_pos 
for i in range(0, 1000):
    # ...
    if jnp.linalg.norm(prev_d_pose) < jnp.linalg.norm(d_pose):
        step *= 1.05
    else:
        step *=0.95
    prev_d_pose = d_pose
    # ...
```
### 轴角  
通过SE3 据说也能算，但是我在测试是会遇到不收敛的的问题。以后再说吧  

## 避免角度过大的问题
1. 增加阻尼  
2. 添加物理限位  
```python
joint_min = jnp.array([
    -160, -225, -225, -110, -100, -266
]) * jnp.pi / 180.0

joint_max = jnp.array([
     160,  45,  45,  170,  100,  266
]) * jnp.pi / 180.0

for i in range(0, 1000):
    # ...
    theta0 = theta0 + d_theta*step  # 更新角度
    theta0 = jnp.clip(theta0, joint_min, joint_max)
```



## 参考资料  
1. [基于指数映射的机器人位姿表达—SO(3)与SE(3)](https://zhuanlan.zhihu.com/p/625421186)  
2. [[数学]罗德里格旋转公式（Rodrigues' rotation formula）](https://zhuanlan.zhihu.com/p/451579313)  
3. [雅克比矩阵（Jacobian Matrix）在正运动学中的应用](https://www.cnblogs.com/caster99/p/4725914.html)
4. [雅克比矩阵转置（Jacobian Transpose）在力和力矩中的应用](https://www.cnblogs.com/caster99/p/4733988.html)