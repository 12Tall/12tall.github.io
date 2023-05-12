---
title: 使用PyFemm 进行电磁场仿真  
date: 2023-05-12  
timeLine: true
icon: notebook
category:  
    - 笔记  
    - Python
tag:  
    - 仿真  
    - Python  
    - 有限元  
---   

> 通过[Python 调用COM 组件](../../python/win32com/README.md) 可以调用FEMM 软件来自动构建仿真项目，软件官方也提供了[pyfemm](https://pypi.org/project/pyfemm/) 可以用来以类似于交互命令行的形式操作软件。但是，这样并不能让项目看起来非常清爽。感觉可以通过面向对象的方法来进一步封装。这里仅记录下探索的过程。   

## 思路    
交互式命令很难获取项目中各个对象的状态，于是想先通过Python 创建一个对象，在执行仿真计算时，在根据对象内部的状态生成仿真项目，这样也便于修改。   


### 持久化  
可以通过JSON 文件保存，但是这样重新加载出来的对象是一个字典；也可以尝试使用`pickle` 工具将文件保存为二进制，这样还能保存方法和子对象。详见示例[test.ipynb](./test.ipynb)，缺点就是不能通过文本编辑器直接修改项目了。  

## todo  