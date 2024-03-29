---  
title: Python 模拟退火算法理解  
date: 2023-05-26
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
tag:   
    - python    
    - 算法  
---  

> 急难成效，事缓则圆    
> 码整理自[Python手把手构建模拟退火算法（SA）实现最优化搜索](https://finthon.com/python-simulated-annealing/)。 

## 核心概念   
假定材料所包含的能量为函数`E(i)`，其在温度`T` 时，从状态`i` 进入状态`j`，如果：  
- `E(j) < E(i)` 则转换一定成立  
- 反之则有一定的概率成立，此概率为$e^{\frac{E(i)-E(j)}{KT}}$  

于是在给定的温度下，材料总会慢慢稳定在一个能量最低的状态。算法的核心在于第二条，在温度较高时$e^{\frac{E(i)-E(j)}{KT}}$ 的值越接近$\frac{1}{e^0} \approx 1$，状态越有可能迁移到高能状态，从而避免陷入局部最优解。     

## 案例  
以函数$y = 3x^2-60x+9$ 为例，求函数在$x \in [0,100]$ 上的最小值:  

```python  
# 构造能量函数  
def func(x):  
    return 3*x**2 - 60*x + 9

# 设置各种常数  
K=1  
T=1  
a=.999 # 降温系数  
std = .0000001  # 终止温度


while T > std:
    Ei = func(xi)   # 初始状态对应的能量值
    xj = xi + random.uniform(-1,1) # 在初始状态附近寻找一个新的状态
    Ej = func(xj)  # 新状态对应的能量值

    # 温度越高时e^(ei-ej/k/t) 的值越大，越可能跳出局部最优解
    # 从而寻找到全局最优解
    if Ej < Ei or random.uniform(0,1) < np.exp((Ei-Ej)/(K*T)):
        xi = xj  # 如果能量值符合要求，则替换初始状态  

    T = T*a  # 温度不断衰减，一般可以按指数衰减  

print(xi, Ei)
# 9.99973106356609 -290.9999997830196  
# 结果稳定在x=10 附近
```  

如果不考虑温度的影响的话，该算法很像是梯度下降算法。考虑温度系数，则更加容易跳出局部最优解从而获得全局最优解。