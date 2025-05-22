---
title: 龙格-库塔算法求微分方程（组） 
date: 2022-10-07      
tags:   
    - 微分方程   
    - 数值分析  
---  

> 我记得关于单个微分方程的求法我已经写过笔记了，可是竟然忘记放在什么地方了 :(。关于微分方程组的求法，这里有一个可以用、但是有点抽象的项目[tosys](https://github.com/12Tall/tosys) 可以尝试运行一下。这篇笔记主要是对一些实现细节上的补充和扩展。    
<!-- more -->
## 算法原理   
龙格-库塔（Runge-Kutta，以下简称RK）法可以求微分方程（组）的数值解，但其实求微分方程的数值解不止这一种方法，只不过RK 精度较高思路简单而更为常用。  

对于函数$y=y(x)$，其可以在$x=x_n$ 处展开为**泰勒级数**：  
$$y(x_{n+1}) = y(x_n) + hy'(\epsilon), x_n<\epsilon<x_{n+1}$$  
令$y'=f(x_n, y_n)$，则可得：  
$$y(x_{n+1}) = y(x_n) + hf(\epsilon, y(\epsilon)), x_n<\epsilon<x_{n+1}$$  
令$k^*$ 为$f(\epsilon, y(\epsilon))$ 在区间$(x_n,x_{n+1})$ 上的平均值，就能精确求得$y(x_{n+1})$ 的值:   
$$y(x_{n+1}) = y(x_n) + hk^*$$

### 欧拉法  
在上式中，如果取$k* = k_1 = f(x_n,y_n)$，则可以得到显式欧拉（Euler）法，思路简单可惜只有一阶精度。  

于是我们可以取$k* = \frac{k_1 + k_2}{2} = \frac{f(x_n,y_n)+f(x_{n+1},y_{n+1})}{2}$，就得到了改进欧拉法，具有二阶精度。  

取得点越多，则计算的精度越高……  

### 龙格库塔公式    
在区间$[x_n,x_{n+1}]$ 内取n 个点，就被称为n 阶龙格-库塔公式，一般称为RKn。实际中常用到四阶，也就是RK4：  
$$\left\{ \begin{array}{llll}
    k_1 & = & f(x_n, y_n)  \\
    k_2 & = & f(x_{n}+\frac{h}{2}, y_n+\frac{h}{2}k_1)  \\
    k_3 & = & f(x_{n}+\frac{h}{2}, y_n+\frac{h}{2}k_2)  \\
    k_4 & = & f(x_{n}+h, y_n+hk_3)  \\  
    y(x_{n+1}) & = & y(x_n) + \frac{1}{6}(k_1+2k_2+2k_3+k_4)h & x_{n+1} = x{n} + h
\end{array} \right.$$   

RK4 的算法很直接，实现起来也很简单。需要注意的是**计算$K_2,k_3$ 的自变量是相同的**。然后我们以`Lorenz` 混沌公式来看一下微分方程组中的RK4 逻辑是怎样的。已知`Lorenz` 公式如下：  
$$\left\{ \begin{array}{lllll}
    f_1(x,y,z) & = & \dot{x} & = & -\sigma x + \sigma y  \\
    f_2(x,y,z) & = & \dot{y} & = & -xz + rx - y  \\
    f_3(x,y,z) & = & \dot{z} & = & xy - bz 
\end{array} \right.$$  

其中 **$x,y,z$ 均是关于$t$ 的函数**，则其对应的RK4 计算步骤应如下所示：  
$$\left\{ \begin{array}{lllll}
    k_1 & = & f_1(x_n,y_n,z_n) & = & -\sigma x_n + \sigma y_n   \\
    l_1 & = & f_2(x_n,y_n,z_n) & = & -x_n z_n + rx_n - y_n   \\
    p_1 & = & f_3(x_n,y_n,z_n) & = & x_n y_n - bz_n    \\
    k_2 & = & f_1(x_n+\frac{h}{2}k_1,y_n+\frac{h}{2}l_1,z_n+\frac{h}{2}p_1) \\
    l_2 & = & f_2(x_n+\frac{h}{2}k_1,y_n+\frac{h}{2}l_1,z_n+\frac{h}{2}p_1) \\
    p_2 & = & f_3(x_n+\frac{h}{2}k_1,y_n+\frac{h}{2}l_1,z_n+\frac{h}{2}p_1) \\
    k_3 & = & f_1(x_n+\frac{h}{2}k_2,y_n+\frac{h}{2}l_2,z_n+\frac{h}{2}p_2) \\
    l_3 & = & f_2(x_n+\frac{h}{2}k_2,y_n+\frac{h}{2}l_2,z_n+\frac{h}{2}p_2) \\
    p_3 & = & f_3(x_n+\frac{h}{2}k_2,y_n+\frac{h}{2}l_2,z_n+\frac{h}{2}p_2) \\
    k_4 & = & f_1(x_n+hk_3,y_n+hl_3,z_n+hp_3) \\
    l_4 & = & f_2(x_n+hk_3,y_n+hl_3,z_n+hp_3) \\
    p_4 & = & f_3(x_n+hk_3,y_n+hl_3,z_n+hp_3) 
\end{array} \right. $$  

最后得到：  
$$\left\{ \begin{array}{lllll}
    x_{n+1} & = & x_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 +k_4)  \\
    y_{n+1} & = & y_n + \frac{h}{6}(l_1 + 2l_2 + 2l_3 +l_4)  \\
    z_{n+1} & = & z_n + \frac{h}{6}(p_1 + 2p_2 + 2p_3 +p_4) 
\end{array} \right. $$  

可见，微分方程组中没有明显用到时间$t$，而是蕴含在在步长$h$ 中。

## 效率vs通用   
在[tosys-system.py](https://github.com/12Tall/tosys/blob/master/tosys/system.py) 的代码中，我采用了字典/哈希表的方式来存储状态变量，然后通过循环遍历来计算新的状态和赋值操作。这样在使用上用户就无需修改类代码、只需在`system` 对象中不断添加状态属性就好了。 
```python{7-8}
# ...  
class System():

    def __init__(self, start=0, end=0, dt=0, input=lambda t: 1):

        # ...  
        self.state = OrderedDict()  # 有序字典，可以按添加顺序进行遍历，非必须
        self.equation = OrderedDict()
        # ...
    
    # ...
    def RK4(self):
       
        # ... 
        for t in numpy.arange(start, end, dt):
            reset_state(next_state)
            for state in self.state:
                reset_state(temp_state)
                k1 = dt*self.equation[state](t, temp_state)
                for key in temp_state:
                    temp_state[key] += 0.5*k1
                k2 = dt*self.equation[state](t+0.5*k1, temp_state)
                for key in temp_state:
                    temp_state[key] += 0.5*(k2-k1)
                k3 = dt*self.equation[state](t, temp_state)
                for key in temp_state:
                    temp_state[key] += (k3-k2)
                k4 = dt*self.equation[state](t, temp_state)
                next_state[state] = self.state[state] + (k1+2*k2+2*k3+k4)/6.
        # ...
```
但是有一点：哈希表再快也快不过指针，也就是硬编码。于是还有一种思路，就是不使用哈希表，而是让用户手动继承`system` 类，并将状态量作为类的属性进行计算。也许这在解释型语言中算不上什么，但是在编译型语言中，编译器就可以将类的属性直接编码为指针了。但这样做需要用户直接接触龙格库塔算法，多少有些烦人。如果有比较好的语法糖或者宏命令的话，则可以优先选择此项。  

## 参考资料  
1. [多元变量的龙格-库塔(Runge-Kutta)公式](http://muchong.com/html/201302/5507081.html)  
2. [龙格-库塔方法](https://www.cnblogs.com/philolif/p/runge-kutta.html)  
3. [Runge-Kutta（龙格-库塔）方法 | 基本思想 + 二阶格式 + 四阶格式](https://blog.csdn.net/SanyHo/article/details/107017076)

---  
📅 2022-08-15 Aachen