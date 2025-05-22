
# 构造能量函数  
from math import exp
import random
from matplotlib import pyplot as plt
import numpy as np


def func(x):  
    return 3*x**2 - 60*x + 9


# x = [i for i in np.linspace(0, 100)]
# y = map(func, x)
# plt.plot(x, list(y))
# plt.show()

K=1  
T=1  
a=.999 # 降温系数  
std = .0000001  # 终止温度

# 定义初始状态
xi = np.random.uniform(0,100)  

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