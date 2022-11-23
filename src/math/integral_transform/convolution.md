---
title: 卷积  
date: 2022-10-07    
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学    
tag:   
    - 积分变换  
    - 离散系统  
    - 控制理论  
--- 

这里并不是普通意义上的卷积，专用于控制与信号处理中应用  

定义式：  
$$\int_{-\infty}^{\infty} f(\tau) g(t-\tau) d\tau \tag{1}$$

将函数拆分成无数个小段，每个小段的间隔为$\Delta t$，任何信号都可以表示为单位序列加权 

单位阶跃函数$u(t), u(t-t_0)$，则  
$$u(t)-u(t-t_0)$$  
可以用于筛选一段函数，注意n 等分可以表示横坐标位置    
$$f_n(t) = f(n\Delta t)\{u(t - n\Delta t)-u[t-(n+1)\Delta t]\}$$  

$$f(t) = \sum_{n=-\infty}^{\infty} f(n \Delta t)\{u(t - n\Delta t)-u[t-(n+1)\Delta t]\}$$  

将函数右边除以再乘以一个$\Delta t$，会得到关于冲激函数的形式  
$$\frac{u(t - n\Delta t)-u[t-(n+1)\Delta t]}{\Delta t} \Delta t = \delta(t) \Delta t$$  
即：  
$$f(t) = \sum_{n=-\infty}^{\infty} f(n \Delta t) \delta(0 - n \Delta t) \Delta t$$  

当$\Delta t \rightarrow 0$ 时，令$\tau = n \Delta t$ 得到  
$$f(t) = \int_{-\infty}^{\infty} f(\tau) \delta(0 - \tau) \tau$$

将原函数拆成了无穷个冲激函数的序列  

## 控制系统  
对于一个控制系统来说，我们一般会研究其响应函数与激励函数的关系。但是对于激励来说，可能千变万化，于是我们可以将激励拆分为无数个幅值变化的冲激函数序列，而对于系统，我们就只需要知道它的单位冲激相应$h(t)$ 就好了。于是对于一个线性时不变的系统来说，最终的输出就是一个个冲激响应的叠加，便有了以下方程：  
$$(f*h)(t) = \int_{0}^{\infty} f(t)h(0-t) dt$$  
根据[拉普拉斯变换](./laplace-transform.md)可以得到：  

$$Y(s) = \mathscr{L}[(f*h)(t)] = F(s)H(s)$$  
$$H(s) = \frac{Y(s)}{F(s)}$$  
其中$H(s)$ 就是系统的传递函数。传递函数的定义其实应该是来源于系统对单位冲激函数的相应。  





## 参考资料  
1. [「珂学原理」No. 28「卷积为谁而生？」](https://www.bilibili.com/video/BV1Vx41177sx)  
2. [「珂学原理」No.90「卷积应该怎么卷」卷积描述了什么运算？](https://www.bilibili.com/video/BV1Et411a7Az?t=632)
3. [「珂学原理」No.29「冲激冲出了什么？」](https://www.bilibili.com/video/BV11x411L7sj?t=611)
4. [「珂学原理」No.31「传递函数递了什么？」](https://www.bilibili.com/video/BV1Cx411V7Lo?t=637)