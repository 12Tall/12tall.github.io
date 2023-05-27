---
title: 使用PyFemm 进行电磁场仿真  
date: 2023-05-12  
timeLine: true
icon: notebook
category:  
    - 笔记  
    - Python
    - 我理解的  
tag:  
    - 仿真  
    - Python  
    - 有限元  
    - 我理解的  
---   

> 通过[Python 调用COM 组件](../../python/win32com/README.md) 可以调用FEMM 软件来自动构建仿真项目，软件官方也提供了[pyfemm](https://pypi.org/project/pyfemm/) 可以用来以类似于交互命令行的形式操作软件。但是，这样并不能让项目看起来非常清爽。感觉可以通过面向对象的方法来进一步封装。这里仅记录下探索的过程。   

## 思路    
交互式命令很难获取项目中各个对象的状态，于是想先通过Python 创建一个对象，在执行仿真计算时，在根据对象内部的状态生成仿真项目，这样也便于修改。   


### 持久化  
可以通过JSON 文件保存，但是这样重新加载出来的对象是一个字典；也可以尝试使用`pickle` 工具将文件保存为二进制，这样还能保存方法和子对象。详见示例[test.ipynb](./test.ipynb)，缺点就是不能通过文本编辑器直接修改项目了。  

> 关于项目的实现可以在这个[仓库](https://github.com/12Tall/tpyFEMM) 里面找到，正如上面提到的FEMM 软件命令不会保存各个对象的状态，只能通过自己重写各种图形变换的算法。虽然不多，倒也有意思。
> 仓库本身的代码只包含了磁场仿真的部分操作，关于后处理部分仍然没想好如何设计，才能简化用户操作的同时还能保证程序的灵活性。  


## 感悟  
但是从这个项目中想到了许多以前没想清楚的问题，并且也很自然地复习了面向对象开发的知识。本人的经历有限，能够看到的东西肯定也有很大的局限性。  

### Python 真的适合大型项目吗？  
Python 最大的优点就是它的社区了，尤其是库资源`极其`丰富。并且语法相对友好、包管理也比较容易，这让其非常适合用于学习或者做一些简单的工作：`程序员只需写少量代码就可以完成大量任务`。但是，他的优点也成为了它的缺点：  
- 在代码的结构复杂时，类型系统就变成了不可缺少的部分，虽然python 可以添加类型注解，但是缺少泛型的语法糖
- 语言特性的原因很容易出现循环引用的错误  

当然这些可以通过某些技巧去弥补，就看用到什么程度了，真正的项目还是回归设计模式的。  

### 绘图时的疑问  
以前自己关于如何高效绘图存在着一些问题，但是在FEMM 中，`软件通过鼠标邮件可以选择离鼠标最近的点`这一特性给了我许多启发：  
- 假如绘图区域的大小（宽和高）是一定的，那么：
  - 可以通过（循环）链表来存储数据，然后通过一个位置标识来确定起止位置  
  - 在绘图时可以只修改动的部分，也就是几个像素而不是大面积重绘  
  - 关于鼠标选取，可以判断鼠标位置（与横坐标有对应关系），再根据对应的横坐标选取相应的数据点（或者范围）  
- 图形定义：是否可以相对位置定义图形，虽然绝对位置在图形变换时似乎更有优势，或者二者结合一下  
- 图形变换：通过对象间的包含关系，可以在内存中实现旋转和平移操作，然后再渲染到绘图区域  

### 软件自动化   
通过COM+ 组件调用软件确实是一个比较好玩的方式，但是从头做的话会耗费大量的精力重复造轮子。而真正需要关注的问题应该是如何通过软件改善既有的流程，并非重新开发一个软件出来，以FEMM 为例：  
- 建模：虽然参数化建模听起来很高端，但是人机交互是一个复杂的过程，并且FEMM 的交互几乎完全是单向的，完全参数化倒不如只关注其中需要变动的部分  
- 计算：计算部分任务单纯，适合软件调用，并且不需要什么设计  
- 后处理：后处理部分通过GUI 操作比较简单，但是程序调用却比较复杂，最好能够设计一些任务的模板来进行分析  

还有就是COM+ 组件虽然功能强大，但是接口对于开发者来说几乎是个黑盒子，所以需要相关的API 文档并且使用者本身要能用好该软件才行。这里附一个[COM+ 调用Ansys Maxwell 的仓库](https://github.com/MarkWengSTR/ansys-maxwell-EM-design-online/) 以及其作者的[博客](https://mark-weng.com/)。

### 我需要什么样的语言  
我可能更需要一种解释型的Java 语言，并且应该可以编译成本地可执行二进制文件。  