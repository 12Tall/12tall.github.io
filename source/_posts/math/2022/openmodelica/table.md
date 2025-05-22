---
title: 表格插值 table  
date: 2022-08-25 
tags:   
    - OpenModelica  
    - 建模
---

在实际生产中，会经常用到插值而不是数学函数来获取数据，而Modelica 语言则内置了一维、二维的插值模块供我们调用：  
![](table_0.png)  
<!-- more -->
## 输入数据格式  
Modelica 支持三种数据输入格式，分别是：txt、mat 和C 代码。如果不想暴露插值数据的话可以采用C 代码的方式，而且编译后的文件体积也比较小，但是比较不好写，使用起来还需要一些C 基础，这里先略过。详情可参考[说明文档](https://doc.modelica.org/Modelica%204.0.0/Resources/helpDymola/Modelica_Blocks_Tables.html#Modelica.Blocks.Tables)。mat 文件使用简单，但是需要先用Matlab 做数据处理。于是这里我们重点介绍txt 格式。  

```txt
#1    # `#1` 是必须的，表示版本号  

float tab0(2,2)   # float 表示数据类型，tab0 就是表名，(2,3) 表示数据的维度  
1 2 3 4           # 数据之间以空白或tab 或逗号或分号隔开，不一定在同一行，也不一定要对齐，Modelica 会根据维度信息逐个读取（按行）  

double a(2,3)  
1 2, 3  
4   5;6  
```

然后就按上图调用即可。需要注意的是，如果要以`modelica://...` 引用资源文件需要借助于`loadResources` 工具函数！  
仿真结果输出为：  
```txt  
input: 2.5; output: [3.5, 4.5]  √
```

## CombiTable1Ds/CombiTable1Dv  
二者的区别在于，`CombiTable1Ds` 是单输入多输出的，而`CombiTable1Dv` 是多输入多输出的，即一次可以计算好多点的插值结果。二维插值的使用类似。    

## 三维的插值  
Modelica 语言提供的标准插值功能模块只包含一维和二维的，并且标准模块仿真时需要将数据编译进去的，所以我们需要自己想办法去实现三维或更高维的插值方法。我们可以用C/Python 去实现，也可以用二维和一维的功能来组合出来：  
1. 首先用N 个二维插值可以获取N 个输出Y，这个输出是一个数组，并且与另一个维度相关；  
2. 再利用`Modelica.Math.Vectors.interpolate` 函数对Y 进行插值，之所以不用`CombiTable1Ds` 是因为`CombiTable1Ds` 内部的table 中的数据是不能更改的。  

这种方法只能完成线性插值的的功能，但是只要我们的采样点足够多，线性插值是足够的。  