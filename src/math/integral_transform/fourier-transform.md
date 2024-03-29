---
title: 傅里叶变换  
date: 2022-10-07    
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学    
tag:   
    - 积分变换 
    - 控制理论  
    - 电路
--- 
 
傅里叶变换是将一个函数用一组正弦函数的叠加来无限逼近/等效。发展历程大致如下：  

- 牛顿三色光实验  
- 泊松用三角级数表示一些周期性的函数  
- 傅里叶在研究热传导时，将所有函数都以三角级数的形式表示，见`《热的解析理论》`  
- 狄利克雷给出傅里叶变换的充分必要条件  
- 拉普拉斯变换扩展了傅里叶变换的适用范围  

## 三角函数  
- 三角函数的微积分还是三角函数  
- 天然包含了周期性的振动信息  
- **三角函数的正交性**：下面三角函数系中，任取两个不同的函数在区间`[-π,π]` 上的积分等于0，所以可以用正弦函数来筛选函数中某一正弦分量      
  $$\{ 1, \cos{x}, \sin{x}, \cos{2x}, \sin{2x}, ..., \cos{nx}, \sin{nx}, ... \} \tag{1}$$  

## 推导过程  
推导过程可能不严谨，但是应该算比较好懂。首先我们将一个函数`f(x)` 写作一组正弦函数累加的形式：      
$$f_{(t)} = \sum_{n=1}^\infty A_n\cos{(nω_0t+φ_n)}+C \tag{2}$$    

右边表示一系列n 倍频的正弦波的叠加，其中：  
$$\cos{(nω_0t+φ_n)} = a_n\cos{(nω_0t)}+b_n\sin{(nω_0t)} \tag{3}$$  

根据欧拉公式  
$$e^{it} = \cos{t} + i\sin{t} \tag{4}$$ 

进一步地，可以将正弦函数表示为复指数形式： 
$$\sin{t} = \frac{e^{it}-e^{-it}}{2}\tag{5.a}$$  
$$\cos{t} = \frac{e^{it}+e^{-it}}{2}\tag{5.b}$$  

那么，`(2)` 式就可以下面形式，其中$F_{(ω_n)}$ 是与周期相关的表示幅值的函数：  
$$f_{(t)} = \sum_{n=1}^\infty F_{(ω_n)}e^{iω_nt}+C \tag{6}$$  

如果要求某一周期的正弦分量的幅值，则应该是：  
$$F_{(ω_n)} = \int_{-\infty}^{\infty}f_{(t)} e^{-iω_nt} dt \tag{7.a}$$
电学上，`i` 一般表示电流，为避免冲突，一般用`j` 代替`i` 作为虚数符号：  
$$F_{(ω_n)} = \int_{-\infty}^{\infty}f_{(t)} e^{-jω_nt} dt \tag{7.b}$$  

最终，得到连续的傅里叶变换的定义式如下：  
$$F_{(ω)} = \mathscr{F}[f_{(t)}] = \int_{-\infty}^{\infty}f_{(t)}e^{-iωt}dt \tag{8}$$   


## 参考链接  
1. [「珂学原理」No. 8 「傅里叶的变换哲学」](https://www.bilibili.com/video/BV1Rx41127UF)
2. [「珂学原理」No. 26「拉普拉斯变换了什么？」](https://www.bilibili.com/video/BV16x411M7HR)
3. [[傅里叶变换及其应用学习笔记]](https://www.cnblogs.com/TaigaCon/category/1189650.html)


