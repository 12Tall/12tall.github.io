---
title: 机械臂笔记（一）—— D-H 参数表的建立
date: 2025-11-18 16:27:30
tags:
    - 机械臂 
---

记录下机械臂D-H建模的基本过程，基本不牵扯公式推导，只记录直观解释。「还不是特别清晰」  

<!-- more -->

## 基础知识  
一般我们计算机械臂末端的位置和姿态，位置信息可以用一个三维向量表示：  
$$\vec{P} = \begin{bmatrix} x & y & z\end{bmatrix}^T \tag{1}$$

姿态信息可以通过一个正交矩阵表示：  
$$\boldsymbol{T_0} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1\end{bmatrix} \tag{2}$$
列向量表示$x,y,z$ 轴的朝向。  

### 旋转变换  
将三维向量左乘一个旋转矩阵即可，有三个基本形式的旋转矩阵（分别绕$x,y,z$轴）：
$$\boldsymbol{R}_x(\theta) =  \begin{bmatrix} 1 & 0 & 0 \\ 0 & cos(\theta) & -sin(\theta) \\ 0 & sin(\theta) & cos(\theta)\end{bmatrix}\tag{3}$$
$$\boldsymbol{R}_y(\theta) =  \begin{bmatrix} cos(\theta) & 0 & sin(\theta) \\ 0 & 1 & 0 \\ -sin(\theta)& 0 & cos(\theta)\end{bmatrix}\tag{4}$$
$$\boldsymbol{R}_z(\theta) =  \begin{bmatrix} cos(\theta) & -sin(\theta) & 0 \\ sin(\theta) & cos(\theta) & 0 \\ 0 & 0 & 1\end{bmatrix}\tag{5}$$
空间中的旋转可以通过上边两两组合得到，机械臂中一般组合$\boldsymbol{R}_z, \boldsymbol{R}_x$。

### 平移变换  
如果需要将向量$\vec{P}$分别沿$x,y,z$轴平移$x_0,y_0,z_0$，则可以左乘下面矩阵：  
$$\boldsymbol{T} = \begin{bmatrix} 1 & 0 & 0 &x_0\\ 0 & 1 & 0 &y_0 \\ 0 & 0 & 1 &z_0 \\ 0&0&0&1\end{bmatrix} \tag{6}$$

将旋转矩阵扩展进来，则的到齐次变换矩阵（以绕$x$ 轴旋转后再平移为例）：
$$\boldsymbol{T} = \begin{bmatrix} 1 & 0 & 0 &x_0\\ 0 & cos(\theta) & -sin(\theta)  &0 \\ 0 & sin(\theta) & cos(\theta) &0 \\ 0&0&0&1\end{bmatrix} = \begin{bmatrix} \boldsymbol{R} & \vec{P} \\ 0 &1 \end{bmatrix}\tag{7}$$
> 实际上，<u>在机械臂中，一般也用齐次矩阵的形式表示末端的状态</u>。在机械臂中如果有多个关节，知道**每个关节相对于前一个关节的齐次变换矩阵**，依次相乘就能计算出末端相对于起始位置的坐标：
> $$
> \vec{P}_{new} =  (\boldsymbol{T}_n\boldsymbol{T}_{n-1}\cdots\boldsymbol{T}_1)\vec{P}_{local} \tag{8}
> $$
> ![](r_l_multiply.svg)
> 变换算子左乘：表示该变换是相对固定坐标系变换：  
> - 把物体在世界坐标系下旋转$90\degree$，$\boldsymbol{T}' = \boldsymbol{R}_z(90\degree)\boldsymbol{T}$；  
>
> 变换算子右乘：表示该变换是相对动的坐标系（新坐标系）变换,多个关节的变换是“粘在”前一个姿态后面:  
> - 夹爪坐标系下向前走$1cm$，$\boldsymbol{T}' = \boldsymbol{T}\boldsymbol{Trans}_x(1)$  

## 标准D-H 参数表
关节坐标系间的变换无非是平移和旋转，但是无论平移还是旋转，都是以$z,x$ 轴为基准的，当然也可以用$z, y$ 轴，只是不常见而已。  

### 建表步骤
1. 确定每个关节的$z$ 轴，尽量不要改变$z$ 轴方向：     
    - 转动关节$z$ 轴沿转动轴方向；
    - 平动关节$z$ 轴沿伸缩方向；
2. 确定每个关节的$x$ 轴，尽量不要改变$x$ 轴方向：
    - 选择当前关节与上一个关节$z$ 轴的公垂线方向；
    - 如果当前关节与上一个关节平行，则选择两个关节连线的方向；
3. 确定（关节）坐标系原点，一般选在关节轴（的几何中心）上：
    - 选择当前关节与上一个关节$z$ 轴相交，则选择交点；
    - 选择当前关节与上一个关节$z$ 轴平行，常选择上一轴的投影或连杆长度起点，以保证 DH 参数唯一性；
    - 当前关节与上一个关节 $z$ 轴异位（既不平行也不相交）。选择公垂线与当前轴的交点作为坐标系原点。
### 旋转平移的顺序  
$$^{i-1}_i\boldsymbol{T}=\boldsymbol{Rot}_{z_i-1}(\theta_i)\boldsymbol{Trans}_{z_i-1}(d_i)\boldsymbol{Trans}_{x_i}(a_i) \boldsymbol{Rot}_{x_i}(\alpha_i)\tag{9}$$
1. 先按$z_{i-1}$ 轴（起始坐标系）旋转$\theta_i$，使得$x_i, x_{i-1}$轴指向一致；  
2. 再沿$z_{i-1}$ 轴（起始坐标系）平移$d_i$，使得$x_i, x_{i-1}$轴重合；  
3. 再沿$x_{i}$ 轴（目标坐标系）平移$a_i$，使得起始坐标系和目标坐标系原点重合；  
4. 最后$x_{i}$ 轴（目标坐标系）旋转$\alpha_i$，使得起始坐标系和目标坐标系完全一致；  


## 改进D-H 参数表  
$$^{i-1}_i\boldsymbol{T}=\boldsymbol{Rot}_{x_i-1}(\theta_i)\boldsymbol{Trans}_{x_i-1}(d_i)\boldsymbol{Trans}_{z_i}(a_i) \boldsymbol{Rot}_{z_i}(\alpha_i)\tag{10}$$
改进D-H 与标准D-H 算法相比，差异点主要在旋转平移的操作顺序，**并且$x$轴的选择是参考当前关节与下一个关节**：  
1. 先按$x_{i-1}$ 轴（起始坐标系）旋转$\alpha_i$，使得$z_i, z_{i-1}$轴指向一致；  
2. 再沿$x_{i-1}$ 轴（起始坐标系）平移$a_i$，使得$z_i, z_{i-1}$轴重合；   
3. 再按$z_{i}$ 轴（目标坐标系）旋转$\theta_i$，使得起始坐标系和目标坐标系姿态一致； 
4. 最后沿$z_{i}$ 轴（目标坐标系）平移$d_i$，使得起始坐标系和目标坐标系原点重合； 


## 示例 PUMA 560 改进D-H 参数表  
![](puma560-kM.jpg)
需要注意的是第三节机械臂的转动轴不是平行的：  
![](puma560-kM1.jpg)
### 1. 确定z 轴及方向    
![](xyzdistan.png)  
### 2. 根据z 轴方向确定x 轴的方向  
x 轴的指向尽量保持不变，z 轴也是，这样得到的参数表会比较简洁  
### 3. 填写参数表  

当前坐标系$i-1$|下一个关节$i$|$\boldsymbol{R}_x/\alpha_i$|$d_x/a_i$|$\boldsymbol{R}_z/\theta_i$|$d_z/d_i$  
:---:|:---:|---:|---:|---:|---:
$0$|$1$|$0$|$0$|$\theta_1$|$0$
$1$|$2$|$-\frac{\pi}{2}$|$0$|$\theta_2$|$0$
$2$|$3$|$0$|$a_2$|$\theta_3$|$d_3$
$3$|$4$|$-\frac{\pi}{2}$|$a_3$|$\theta_4$|$d_4$
$4$|$5$|$\frac{\pi}{2}$|$0$|$\theta_5$|$0$
$5$|$6$|$-\frac{\pi}{2}$|$0$|$\theta_6$|$0$

正向过程的矩阵计算过程见[参考资料[5-6]](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/theory.html)。需要注意的是，**这样建立的参数表的世界坐标系原点位于第1,2 轴的交点**。

## 参考资料  
1. [机械臂 运动学 D-H经典方法和改进D-H方法参数表建立](https://www.bilibili.com/video/BV1Pk4y1N71b)  
2. [从零手搓人形机械臂之运动学板块（一）](https://www.bilibili.com/video/BV1dp1wB5Ex5)  
3. [详解PUMA 560机械臂的改进D-H参数和标准D-H参数表示](https://zhuanlan.zhihu.com/p/392320782)
4. [在线机械臂（改进）D-H 参数表可视化](https://intelligentsystemslab.org.ntnu.no/course/DH/index.html)  
5. [Forward Kinematics of PUMA 560](https://mr-iitkgp.vlabs.ac.in/exp/forward-kinematics/theory.html)
6. [详解PUMA 560机械臂的改进D-H参数和标准D-H参数表示](https://zhuanlan.zhihu.com/p/392320782)