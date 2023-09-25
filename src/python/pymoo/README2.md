---  
title: Pymoo 多目标优化笔记（二）  
date: 2023-09-25
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
tag:   
    - python   
    - pymoo  
    - math  
    - optimization  
    - multiple object  
    - pareto
---     

> 因为许多任务并不是一个简单的函数调用可以解决的，但是我们可以将`pymoo` 问题定义为一个泛函数，下面的点**很重要**：  
> - `n_offspring`：每一代产生多少个新个体，如果太小，则会收敛的很慢，如果太大，则会过度探索空间；  
> - 需要将`g` 都写作：$g(x) \le 0$ 的形式；  
> - 并且`f` 也都应写作$min$ 形式；  

## 定义问题  

$$\begin{array}{lll}
    min  & f_m(x)       & m=1,\dots,M  \\\\
    s.t. & g_j(x) \le 0 & j=1,\dots, J \\
         & h_k(x) = 0   & k=1,\dots, K \\\\
         & x_i^L \le x_i \le x_i^U & i=1,\dots,N  \\
         & x \in \mathbb{\Omega}
\end{array}$$ 

现实情况是我们可能需要利用其他程序来求解问题，例如有限元或者CFD 方法，所以我们的程序应该可以调用其他进程：  
- 通过命令行工具调用，如`shell/cmd`  
- 通过`com+` 组件调用  
- 通过官方提供的API 接口调用     

### 调用其他进程  
这里我们选择第一个，通过命令行调用。而我们的`求解程序`则是通过另一个`demo01_script.py`   
```python  
import os
import sys
import numpy as np
import pandas as pd

if __name__ == "__main__":  
    x1 = float(sys.argv[1])
    x2 = float(sys.argv[2])
    output = sys.argv[3]
    f1 = 100*(x1**2+ x2**2)  
    f2 = (x1-1)**2 + x2**2
    g1 = 2*(x1-0.1)*(x1-0.9)
    g2 = -20*(x1-0.4)*(x1-0.6)

    data = pd.DataFrame({
        'x1':[x1],
        'x2':[x2],
        'f1':[f1],
        'f2':[f2],
        'g1':[g1],
        'g2':[g2]})
    data.to_csv(output, index=False)

# 输出：   
# x1,x2,f1,f2,g1,g2
# 0.862116483026748,-0.026949728032658448,74.39711181474433,0.019738152093947317,-0.057743305440677836,-2.422566945593222
```  

### 修改问题的定义   
在`_evaluate` 中去执行其他程序，并读取其中的结果。可以改进的地方就是如何高效地在进程间传递数据：
```python{20-21,23-24}  
import os
import numpy as np
import pandas as pd  
from pymoo.core.problem import ElementwiseProblem  

class DemoProblem01(ElementwiseProblem):  

    def __init__(self):
        super().__init__(
            n_var = 2,  
            n_obj = 2,  
            n_ieq_constr = 2,  
            xl = np.array([-2, -2]),  
            xu = np.array([2, 2])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        x1 = x[0]
        x2 = x[1]  
        os.system(f"python demo01_script.py {x1} {x2} res.csv")
        data = pd.read_csv('res.csv')
        
        out["F"] = [data['f1'], data['f2']]
        out["G"] = [data['g1'], data['g2']]

problem = DemoProblem01()
```  

余下的代码不用修改，结果也类似于[上一篇笔记](./README.md)。  
> 上面代码运行时间：8min10s

## 多线程    
通过多线程可以有效地加速计算过程，实测下面的代码要比上面的代码速度快了五到六倍：  
```python{2,5-6,8-10,14,21,27-30,35}  
import os
import threading
import numpy as np
import pandas as pd  
from pymoo.core.problem import ElementwiseProblem, StarmapParallelization  
from multiprocessing.pool import ThreadPool  

n_process = 8  
pool = ThreadPool(n_process)
runner = StarmapParallelization(pool.starmap)

class DemoProblem01(ElementwiseProblem):  

    def __init__(self, **kwargs):
        super().__init__(
            n_var = 2,  
            n_obj = 2,  
            n_ieq_constr = 2,  
            xl = np.array([-2, -2]),  
            xu = np.array([2, 2]), 
            **kwargs
        )

    def _evaluate(self, x, out, *args, **kwargs):
        x1 = x[0]
        x2 = x[1]  
        tid = threading.get_ident()
        # print(pid)
        os.system(f"python demo01_script.py {x1} {x2} res_{tid}.csv")
        data = pd.read_csv(f'res_{tid}.csv')
        
        out["F"] = [data['f1'], data['f2']]
        out["G"] = [data['g1'], data['g2']]

problem = DemoProblem01(elementwise_runner=runner)
```  
    
> 上面代码运行时间：1min30s  


可以通过 ~~命名管道（不适合）~~ 来实现与子进程/子线程的通信，但是也要看目标程序是不是支持很多特性。最简单的还是文件读写。

## 参考资料  
1. [pymoo - Parallelization](https://pymoo.org/problems/parallelization.html)  
2. [Python笔记-windows管道通信](https://juejin.cn/post/7087742273043038239)  
3. [Python通过Manager方式实现多个无关联进程共享数据](https://blog.csdn.net/hellocsz/article/details/79520479)