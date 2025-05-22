---
title: 相轨迹图/Phase Portrait  
date: 2022-08-25       
tags:   
    - 控制理论    
    - 线性定常系统  
---  

  
> 看[相图_相轨迹](https://www.bilibili.com/video/BV1ex411g7t3) 的笔记  
> 需要注意的是，下文中所有的$x,y,X,Y$ 都是关于时$t$ 的变量，而这里的$y, Y$ 也不是状态空间方程里的$Y$  
 
<!-- more -->
一般在求解微分方程（组）的时候，我们可以选择两种方法：解析法和数值法。在此之外，我们还有另外一种方案，即绘制向量场图，也被称为相轨迹图：  
![](exp_01.png)  
上图是关于微分方程组$\left\{\begin{array}{l}
    \dot{x}=y-0.5x  \\
    \dot{y}=sin(x)
\end{array} \right.$的相轨迹图，其横坐标为$x$，纵坐标为$y$，箭头的代表两个变量随时间的流动方向。例如取A 初始位置在`(-2,1)` 化，A 会沿绿色曲线流动。  

## 一维相轨迹图  
![](exp_02.png)  
以$\dot{f(x)} = x$ 为例，假设上图中横坐标是$x$，纵坐标是$\dot{x}$，红色的曲线与横轴交于左右两点。  
> 为了观察方便，我们未必会将时间$t$ 作为坐标轴，只要能观察到变量$x, \dot{x}$ 随时间变化的趋势就好了。  

- 在左边交点$x_1$的左侧，$\dot{x} > 0$，表示$x$ 随着时间的增加会向右移动，直到达到$x_1$。此时变化率为0，达到稳定状态  
- 在左边交点$x_1$的右侧，$\dot{x} < 0$，表示$x$ 随着时间的增加会向左移动，直到达到$x_1$。此时变化率为0，达到稳定状态  
- 在右边交点$x_2$的左侧，$\dot{x} < 0$，表示$x$ 随着时间的增加会向左移动，逐渐远离$x_2$。  
- 在右边交点$x_2$的右侧，$\dot{x} > 0$，表示$x$ 随着时间的增加会向右移动，逐渐远离$x_2$。  

## 二维相轨迹图  
同理，对于包含两个变量$x_1,x_2$ 的方程组$\begin{bmatrix}
    \dot{x_1} \\
    \dot{x_2}
\end{bmatrix} = \begin{bmatrix}
    a & b \\
    c & d
\end{bmatrix}\begin{bmatrix}
    x_1 \\
    x_2
\end{bmatrix}$，令$b=c=0$，则有：  
$$\begin{array}{c}
    \dot{x_1} = ax_1  \\
    \dot{x_2} = bx_2
\end{array}$$  

- 当$a=d>0$ 时，如下图所示,横坐标是$x_1$，纵坐标是$x_2$。无论起始位置在哪儿，都会远离原点，故不会稳定：  
    ![](exp_03.png)

- 当$a>d>0$ 时，如下图所示,横坐标是$x_1$，纵坐标是$x_2$。因为$a$ 更大，所以横方向上变化更快，但不会改变远离原点的趋势，故不会稳定：  
    ![](exp_04.png)

- 当$a>0, d<0$ 时，如下图所示,横坐标是$x_1$，纵坐标是$x_2$。横方向上发散，纵方向收敛，但整体会远离原点，故不会稳定：  
    ![](exp_05.png)


- 当$a<0, d<0$ 时，如下图所示,横坐标是$x_1$，纵坐标是$x_2$。横方向上收敛，纵方向收敛，系统是稳定的：  
    ![](exp_06.png)

上面前两种情况中，原点被称为`源点（source）`是不稳定的；第三种情况被称为`鞍点（saddle）`也是不稳定的；最后一种被称为`汇点（sink）`。  

### 更一般的情况  
$$\dot{X} = AX \tag{1}$$  
令$P=\begin{bmatrix}
    v_1 & v_2
\end{bmatrix}, X=PY, \dot{Y} = \Lambda Y$，以$\dot{x}=\begin{bmatrix}
    -3 & 4 \\
    -2 & 3
\end{bmatrix}X$为例：  
1. 求矩阵$A$ 的特征值，得$\Lambda=\begin{bmatrix}
    1 & 0 \\
    0 & -1
\end{bmatrix}$  
2. 求矩阵$A$ 的特征向量，得$\begin{bmatrix}
    v_1 & v_2
\end{bmatrix}=\begin{bmatrix}
    1 & 2 \\
    1 & 1
\end{bmatrix}=P$  
3. 计算$\dot{Y}=\begin{bmatrix}
    1 & 0 \\
    0 & -1
\end{bmatrix}Y, X= \begin{bmatrix}
    1 & 2 \\
    1 & 1
\end{bmatrix}Y$  
    - 对于$Y$ 来说，其$a>0, d<0$ 属于鞍点，是不稳定的  
    - 对于$X$ 来说，相当于对$Y$ 的坐标轴进行了线性变换，坐标轴从$y_1,y_2$ 变成了$x_1,x_2$，函数图像有了些许拉伸或压缩，但是不会改变稳定性  
    - **所以可以通过$\Lambda$ 判断系统的稳定性**（这里建议看视频）  

![](exp_07.png) 

虚部引入了震荡~

<iframe src="//player.bilibili.com/player.html?aid=15413302&bvid=BV1ex411g7t3&cid=25086419&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>  

### 相轨迹图的应用  
<iframe src="//player.bilibili.com/player.html?aid=15795540&bvid=BV19x41177Mo&cid=25722388&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>