---
title: 线性定常系统的稳定性  
date: 2022-08-25    
tags:   
    - 控制理论    
    - 线性定常系统  
---  

> 看[稳定性_李雅普诺夫_Lyapunov](https://www.bilibili.com/video/BV1vx411V7EH) 的笔记  
 
<!-- more -->
![](stability.png)  
![](definition.png)
> - **Lyapunov stable**：简单来说，如果平衡状态$x_e$受到扰动后，仍然停留在$x_e$附近，我们就称$x_e$在李雅普诺夫意义下是稳定的。  
> - **Asymptotically stable**：进一步，如果平衡状态$x_e$受到扰动后，最终会收敛到$x_e$，我们就称$x_e$在李雅普诺夫意义下是渐进稳定的。    
> - **Asymptotically stable in large**：更进一步，如果平衡状态$x_e$受到**任何**扰动后，最终会收敛到$x_e$，我们就称$x_e$在李雅普诺夫意义下是大范围渐进稳定的。    
> - **Asymptotically stable in large**：更进一步，如果平衡状态$x_e$受到**任何**扰动后，最终会收敛到$x_e$，我们就称$x_e$在李雅普诺夫意义下是大范围渐进稳定的。    
> - **Unstable**：最后，如果平衡状态$x_e$受到某种扰动后，最终会偏离到$x_e$，我们就称$x_e$在李雅普诺夫意义下是不稳定的。  
> ![](lyapunov.jpg)    
> - 摘自知乎：[如何理解李雅普诺夫稳定性分析](https://zhuanlan.zhihu.com/p/58738073)

## 判定  
依据相平面的轨迹，我们可以得出：  
- 李雅普诺夫稳定，$A$ 矩阵的所有特征值都有非正的实部  
- 渐进稳定，$A$ 矩阵的所有特征值都有负的实部  
- 不稳定，$A$ 矩阵的特征值至少有一个有正实部  

### 非线性系统  
> 李雅普诺夫第二方法，寻找一个函数$V(x)$，而怎么寻找这个函数则是需要（以后）详细学习的问题，这里先忽略    
> ![](nolinear.png)



<iframe src="//player.bilibili.com/player.html?aid=16530002&bvid=BV1vx411V7EH&cid=26964635&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>