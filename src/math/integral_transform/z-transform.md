---
title: Z 变换  
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


Z 变换主要用于分析离线系统（可能主要用于简化计算）。一般地，对于连续的输入函数，可以用单位冲激函数将其拆分为一串冲击函数序列（采样）：  
$$f(t) = \sum_{n=0}^{\infty} f(n \tau) \delta(t-n \tau) \tag{1}$$

对`1` 式进行拉普拉斯变换，得到：  
$$F_{sample}(s) = \int_{-\infty}^{\infty} [\sum_{n=0}^{\infty} f(n \tau) \delta(t-n \tau)] e^{-st} dt \tag{2}$$  
$$= \sum_{n=0}^{\infty} f(n \tau) e^{-sn \tau} \tag{3}$$  

不用管怎么来的（冲激函数筛选性质`4`），直接用即可。  
$$\int_{-\infty}^{\infty} f(t) \delta (t-t_0) dt = f(t_0) \tag{4}$$  

对于`3` 式中，$e^{sn \tau}, s = \sigma + j \omega \rightarrow e^{(\sigma + j \omega) n \tau} \rightarrow e^{\sigma n \tau} + e^{j \omega n \tau}$。相当于一串离散的拉普拉斯变换？  
令$Z = e^{s \tau} = e^{(\sigma + j \omega) \tau}$，Z 可以理解为一个螺旋前进的复数，而n 与离散有关。

$$X_{(z)} = \sum_{n= -\infty}^{\infty} x[n] z^{-n} \tag{5}$$

### 奈奎斯特采样定理  
在进行模拟/数字信号的转换过程中，当采样频率fs.max大于信号中最高频率fmax的2倍时(fs.max>2fmax)，采样之后的数字信号完整地保留了原始信号中的信息，一般实际应用中保证采样频率为信号最高频率的2.56～4倍。  


## 参考链接  
1. [「珂学原理」No.51「Z变换是怎样炼成的」](https://www.bilibili.com/video/BV1XW411s7s9)
2. [「珂学原理」No.62「傅里叶、拉普拉斯和Z变换的关系」](https://www.bilibili.com/video/BV1TW411F7wj)
3. [[离散时间信号处理学习笔记]](https://www.cnblogs.com/TaigaCon/category/1189648.html)