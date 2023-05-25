---  
title: Python 遗传算法理解  
date: 2023-05-25
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
tag:   
    - python    
    - 算法  
---  

> Talk is cheap, show me the code. 代码整理自[Youtube: Genetic Algorithm In Python Super Basic Example](https://www.youtube.com/watch?v=4XZoVQOt-0I)。作者几乎没有将任何理论上的知识点，但是一切又是那么的自然而然。  

## 目标   
对于下面函数`foo`，我们需要求解一组参数`x,y,z`，使得函数值尽可能接近于`0`：  
```python  
def foo(x,y,z):  
    return 6*x**3 + 9*y**2 + 90*z - 25
```  

为此，我们还需要一个函数，来判断对于一组参数，函数`foo` 的返回值有多么接近`0`：  
```python  
def fitness(x,y,z):  
    ans = foo(x,y,z)  

    if ans == 0:  
        return 99999999   # 如果foo 等于0，则应返回无穷大
    else:  
        return abs(1/ans) # 否则则返回其倒数的绝对值，值越大，传入的参数越接近于最优解
```  

## 生成解的集合  
首先，随机生成1000 组解，也就是1009 个包含`x,y,z` 的数组：  
```python  
import random  

solutions = []  
for s in range(1000):
    solutions.append( (
                        random.uniform(0,1000),  # x
                        random.uniform(0,1000),  # y
                        random.uniform(0,1000)   # z
                      ) )

# 可以打印结的前几行  
print(solutions[:5])
```

## 主体功能  
主体功能包含：求解，筛选，组合，编译。往复循环直到满足条件或者找到最优解  

```python   
# 假设主体功能将循环1000 次  
for i in range(10000):  

    # 1. 求解，并将所有的解按合适的程度排序  
    rankedsolutions = []  
    for s in solutions:  
        rankedsolutions.append( (fitness(s[0],s[1],s[2]), s) )
    rankedsolutions.sort()    # 排序
    rankedsolutions.reverse() # 逆序

    print(f"=== Gen {i} best solutions ===")  # 打印运行信息

    # 2. 筛选前100 结果，并将所有解放入一个容器，随机抽奖  
    bestsolutions = rankedsolutions[:100]  # 筛选  

    topS = bestsolutions[0]
    if topS[0] > 10000:   # 终止循环，已找到最优解
        print(topS)
        break  
    
    elementsX = []   # 基因容器  
    elementsY = []   # 原视频并没有细分x,y,z 反而是把他们混在一起了  
    elementsZ = []   # 窃以为那样做是不合理的  

    # 为基因容器填入内容  
    for bs in bestsolutions:  
        s = bs[1]  # 因为上面的代码中，我们的bs 是这种形式(fitness, (x,y,z))
        elementsX.append(s[0])
        elementsY.append(s[1])
        elementsZ.append(s[2])

    # 交叉组合+变异，生成新一代解  
    newGen = []
    for _ in range(1000): 
        # 随机获取基因的组合             乘以一个随机数相当于是小幅度的变异 
        x = random.choice(elementsX) * random.uniform(0.99, 1.01) 
        y = random.choice(elementsY) * random.uniform(0.99, 1.01)
        z = random.choice(elementsZ) * random.uniform(0.99, 1.01)
        newGen.append((x,y,z))
    solutions = newGen
```

在理解了上述的流程之后，就很容易在基础的代码上进行扩展，比如基因池的构建和编译的算法，甚至可以进行一些细节的优化来提高计算效率。相信这种代码对于初学者来说更容易理解一些。  