---
title: 反馈
date: 2022-10-07 14:59:46
tags:
    - math  
    - 我理解的  
    - circuit  
    - 控制理论
---

> 想到以前解证明题：条件推导下，结论推导下，中间一凑，解决战斗~  

<!-- more -->

## 反馈的基本概念  
反馈（Feedback）是控制理论中的基本概念，假设控制系统框图如下：  
![](feedback_basic.svg)  

其对应的传递函数为：  
$$\left\{ 
    \begin{array}{lll}
        E(s) = R(s) + H(s)   \\  
        C(s) = E(s) * G(s)   
    \end{array}    
\right.$$  
化简后得到公式：  
$$\Psi(s) = \frac{C(s)}{R(s)} = \frac{G(s)}{1+G(s)H(s)}$$  
一般来说，带有负反馈环节的传递函数$\Psi(s)$ 会比原传递函数$G(s)$ 增益减小，但是稳定性增加。例如电子电路中加入负反馈后可以使得电路抗干扰能力增强。   

## 共射极放大电路  
以[微变等效电路法分析放大电路](https://www.cnblogs.com/jiangyiming/p/15853903.html) 中第二节的共射极放大电路为例电路图为例：  
![](feedback_circuit.png)  
在动态分析时，可以得到：  
$$\left\{ 
    \begin{array}{lll}
        \dot{U}_i = \dot{I}_br_{be} + \dot{I}_eR_e =[r_{be} + (1+\beta)R_e]\dot{I}_b   \\  
        \dot{U}_o = -\dot{I}_cR'_L=-\beta \dot{I}_bR'_L  
    \end{array}    
\right.$$   
其中，$R'_L = R_L // R_c$ ，计算后得到：  
$$\left\{ 
    \begin{array}{lll}
        \dot{A}_u = \frac{\dot{U}_o}{\dot{U}_i} = - \frac{\beta R'_L}{r_{be}+(1+\beta)R_e}   \\ 
        R_i = \frac{\dot{U}_i}{\dot{I}_i} = [r_{be} + (1+\beta)R_e]\dot{I}_b // R_b 
    \end{array}    
\right.$$  
看$\dot{A}_u$ 是不是很眼熟啊，因为$\beta \gg 1$，所以可以进一步化简为：  
$$
\begin{array}{lll}
    \dot{A}_u & = & - \frac{K R'_L}{r_{be}+KR_e}\\
    & = & - \frac{\frac{K R'_L}{r_{be}}}{1+\frac{K R'_L}{r_{be}} *\frac{R_e}{R'_L}}
\end{array} 
$$