---
title: 拉普拉斯变换  
date: 2022-10-07   
tags:   
    - 积分变换 
    - 控制理论  
---  


[傅里叶变换](./fourier-transform.md)可以将一个函数用一组正弦函数表示，但是这种表示存在一种缺陷：因为正弦函数都是周期变化的，所以无法用来表示发散的函数，$f(t) = t$。  

为了弥补这个缺陷，我们需要一个函数因子来将快速增长的原函数压制下来，最为理想的就是指数函数$e^{-σt}$ 了，因为这个函数本身就是收敛的，且下降速度大于常见的大部分函数。  
<!-- more -->
## 推导过程  

$$F_{(ω)} = \int_{-\infty}^{\infty}f_{(t)} e^{-σt} e^{-jωt} dt \tag{1}$$   

其中：  
$$e^{-σt} e^{-jωt} = e^{-(σ+jω)t} \tag{2.a}$$  
令：  
$$s = σ+jω \tag{2.b}$$  

则有了拉普拉斯及其逆变换的标准形式：  
$$F_{(s)} = \mathscr{L}[f_{(t)}] = \int_{-\infty}^{\infty}f_{(t)} e^{-st} dt \tag{3.a}$$   
$$f_{(t)} = \frac{1}{2πj} \int_{σ-j\infty}^{σ+j\infty}F_{(s)} e^{st} ds \tag{3.b}$$  

拉普拉斯变换可以看作是将一个函数，用一组指数增长的正弦函数来表示。  

而在自动控制与信号处理上，积分区间一般为`[0, ∞]`，故而常写作：  
$$F_{(s)} = \mathscr{L}[f_{(t)}] = \int_{0^-}^{\infty}f_{(t)} e^{-st} dt \tag{4.a}$$ 
$$f_{(t)} = \frac{1}{2πj} \int_{σ-j\infty}^{σ+j\infty}F_{(s)} e^{st} ds \tag{4.b}$$ 

### 收敛域  
以$σ$ 为横坐标，$jω$ 为纵坐标，满足$σ$ 大于某个值时，才能使得原函数的增长速度不高于$e^{-st}$ 的收敛速度  

## 拉普拉斯变换性质
### 对照表  
虽然拉普拉斯变换的公式并不复杂，但工程上还是常用查表的方式来计算

| 原函数       | 变换后                   | 备注         |
| ------------ | ------------------------ | ------------ |
| $δ_{(t)}$    | $1$                      | 单位脉冲函数 |
| $t^ne^{-at}$ | $\frac{n!}{(s+a)^{n+1}}$ |              |
| $t^n$        | $\frac{n!}{s^{n+1}}$     |              |
| $t$          | $\frac{1}{s^{2}}$        |              |
| $1$          | $\frac{1}{s}$            | 单位阶跃函数 |
| $e^{-at}$    | $\frac{1}{s+a}$          |              |
| $te^{-at}$   | $\frac{1}{(s+a)^2}$      |              |
| $\sin{ωt}$   | $\frac{ω}{s^2+ω^2}$      |              |
| $\cos{ωt}$   | $\frac{s}{s^2+ω^2}$      |              |

这里推导几个比较常用的性质  
### 线性性质  
这里不做解释

### s 域平移  
若 $\mathscr{L}[f_{(t)}] = F_{(s)}$，则  
$$\int_{-\infty}^{\infty} f_{(t)} e^{-at} e^{-st} dt = \int_{-\infty}^{\infty}f_{(t)}e^{-(a+s)t} dt = F_{(s+a)}$$

### 时域微分定理
若 $\mathscr{L}[f_{(t)}] = F_{(s)}$，则  
$$\int_{-\infty}^{\infty} \frac{d f_{(t)}}{d t} e^{-st} dt = \int_{-\infty}^{\infty} e^{-st} d f_{(t)}$$  
$$= e^{-st} f_{(t)} |^{\infty}_{-\infty} - \int_{-\infty}^{\infty} f_{(t)} de^{-st} $$  
$$= e^{-st} f_{(t)} |^{\infty}_{-\infty} + s \int_{-\infty}^{\infty} f_{(t)} e^{-st} dt$$  
$$= sF_{(s)} + e^{-st} f_{(t)} |^{\infty}_{-\infty}$$  

### 时域积分定理  
若 $\mathscr{L}[f_{(t)}] = F_{(s)}, h_{(t)} = \int f_{(t)} dt$则   
$$F_{(s)} = \mathscr{L}[f_{(t)}] = \mathscr{L}[ \int_{-\infty}^{\infty} h'_{(t)}  dt ]$$
根据[时域微分定理](#时域微分定理)，得  
$$= sH_{(s)} + e^{-st} h_{(t)} |^{\infty}_{-\infty} $$    
$$H_{(s)}  = \frac{F_{(s)}}{s} - \frac{e^{-st} h_{(t)} |^{\infty}_{-\infty}}{s}$$ 

### 尺度变换  
若 $\mathscr{L}[f_{(t)}] = F_{(s)}$，则  
$$\int_{-\infty}^{\infty} f_{(at)} e^{-st} dt \overset{x=at}{====>} \int_{-\infty}^{\infty} f_{(x)} e^{-\frac{s}{a}x} d f_{(\frac{x}{a})}$$  
$$= \frac{1}{a} \int_{-\infty}^{\infty} f_{(x)} e^{-\frac{s}{a}x} d f_{(x)}$$
$$= \frac{1}{a} F_{(\frac{s}{a})}$$  

$$\int_{-\infty}^{\infty} f_{(t-\tau)} e^{-st} dt \overset{x=t-\tau}{====>} \int_{-\infty}^{\infty} f_{(x)} e^{-s(x+\tau)} d f_{(x+\tau)}$$  
$$= e^{-\tau s} \int_{-\infty}^{\infty} f_{(x)} e^{-x s} d f_{(x)}$$
$$= e^{-\tau s} F_{(s)} $$  

### 时域卷积  
若 $\mathscr{L}[f_{(t)}] = F_{(s)}$，$\mathscr{L}[h_{(t)}] = H_{(s)}$，则  
$$\mathscr{L}[(f*h)(t)] = F(s)H(s)$$

### 正弦函数  
$$\cos{ωt} = \frac{e^{jωt} + e^{-jωt}}{2}$$  

$$\mathscr{L}[\cos{ωt}] = \mathscr{L}[\frac{e^{jωt}}{2}] + \mathscr{L}[\frac{e^{-jωt}}{2}]$$  
$$= \frac{1}{2}( \frac{1}{s-jω} + \frac{1}{s+jω} )]$$  
$$= \frac{s}{s^2+ω^2}$$  
同理  
$$\sin{ωt} = -j \frac{e^{jωt} - e^{-jωt}}{2}$$
$$\mathscr{L}[\sin{ωt}]=-j (\mathscr{L}[\frac{e^{jωt}}{2}] - \mathscr{L}[\frac{e^{-jωt}}{2}])$$  
$$= \frac{-j}{2}( \frac{1}{s-jω} - \frac{1}{s+jω} )]$$  
$$= \frac{ω}{s^2+ω^2}$$  

## 参考链接  
1. [「珂学原理」No. 8 「傅里叶的变换哲学」](https://www.bilibili.com/video/BV1Rx41127UF)
2. [「珂学原理」No. 26「拉普拉斯变换了什么？」](https://www.bilibili.com/video/BV16x411M7HR)
3. [「珂学原理」No.37「拉普拉斯变换的福利」变换到底有何疗效？](https://www.bilibili.com/video/BV1EW41187LA?t=601)