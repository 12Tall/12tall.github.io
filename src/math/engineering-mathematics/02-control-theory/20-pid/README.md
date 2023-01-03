---  
title: PID 控制算法  
date: 2023-01-04   
timeLine: true
sidebar: false  
icon: superscript
category:  
    - 数学  
tag:   
    - 工程数学  
    - 控制理论
    - python  
    - pid
---   

对于连续信号来说，PID 控制器的函数形式为：  
$$u(t) = K_pe(t) + K_i\int^t_0e(t)dt + K_d\frac{de(t)}{dt}$$  
其中$e(t) = r(t) - c(t)$ 表示系统反馈与输入直接按的误差。 

## 位置式PID    
在计算机中我们通过差分来替代微分，通过累加来代替积分。故有：  
$$u(k) = K_pe(k) + K_i\sum\limits_{i=0}^ke(i) + K_d[e(k)-e(k-1)]$$  

这样只需从$i=0$ 开始，依次迭代就好了。注意这是在时域而不是复域哦。  

```python
# 位置式PID  
class PosPIDController:  
    def __init__(self, P:float, I:float, D:float, limit:float):
        self.P = P
        self.I = I
        self.D = D
        self.error = 0
        self.lastError = 0  # 记录上一次的误差
        self.limit = limit  # 输出限幅

    # 后面就是简单的数值运算了
```  

## 增量式PID  
由于积分部分可能存在积分饱和，会让控制器需要很长时间才能退出饱和限幅。所以我们可以对PID 算法进行改进。PID 算法只返回控制器输出值的增量。  
$$\left\{\begin{array}{lllll}
    u(k) & = & K_pe(k) & + &K_i\sum\limits_{i=0}^ke(i)& +& K_d[e(k)-e(k-1)] \\
    u(k-1) & = & K_pe(k-1)& +& K_i\sum\limits_{i=0}^{k-1}e(i)& +& K_d[e(k-1)-e(k-2)] 
\end{array}\right.$$

得：
$$\begin{array}{ll}
    \Delta u(k) & =  u(k) - u(k-1) \\
    &= K_p[e(k) - e(k-1)] + K_ie(k) + K_d[e(k)-2e(k-1)+e(k-2)]
\end{array} \tag{1}
$$
于是控制器不需要再记忆积分运算的值，这样就能**快速从积分饱和中退出**。而最终输出值是上一次的输出值加上变化量：$u(k) = u(k-1) + \Delta u(k)$。  

```python
# 增量式PID  
class PosPIDController:  
    def __init__(self, P:float, I:float, D:float, limit:float):
        self.P = P
        self.I = I
        self.D = D
        self.error = 0
        self.lastError = 0  # 记录上一次的误差
        self.llastError = 0 # 上上次的误差
        self.limit = limit  # 输出限幅
        self.output = 0     # 上一次的输出值

    # 后面就是简单的数值运算了
```  

## 参考  
1. [位置式PID与增量式PID代码实现](https://blog.csdn.net/qq_43571752/article/details/120895749)  

-----  
2022-06-16 Aachen  