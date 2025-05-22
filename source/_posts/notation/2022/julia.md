---
title: Julia 编程语言
date: 2022-12-08  
tag:   
    - julia   
---  

> Julia 是一种高性能的动态编程语言，她是一种通用语言，但尤其适用数值分析和计算科学，并且支持并发、并行、和分布式计算。底层调用llvm 编译，可以直接调用C 和Fortran 库。  
<!-- more -->
这篇笔记不记录julia 的详细语法，重点在于如何组织代码、包管理。一般更推荐在`Jupyter` 或者[Pluto](https://github.com/fonsp/Pluto.jl) 中开发。VScode 也有专门的开发调试工具。  

## 命令行模式  

通过在命令行使用`julia` 即可打开REPL 界面，在实际使用中需要频繁地在不同模式下切换：  
```shell-session  
               _
   _       _ _(_)_     |  Documentation: https://docs.julialang.org
  (_)     | (_) (_)    |
   _ _   _| |_  __ _   |  Type "?" for help, "]?" for Pkg help.
  | | | | | | |/ _` |  |
  | | |_| | | | (_| |  |  Version 1.8.3 (2022-11-14)
 _/ |\__'_|_|_|\__'_|  |  Official https://julialang.org/ release
|__/                   |

julia>                    # REPL 模式，用于即时执行Julia 指令
help?>                    # REPL 下按`?` 进入帮助模式
shell>                    # REPL 下按`;` 进入shell 模式，主要用于与操作系统交互  
(@v1.8) pkg>              # REPL 下按`]` 进入包管理模式，此模式下可以为项目安装局部的依赖、或者生成项目 
(reverse-i-search)`':     # REPL 下按`Ctrl+R` 检索模式，可以检索已经输入的命令记录
julia>                    # 任何其他模式下，按`Backspace` 即可返回REPL 模式
```

### 包的安装  
1. 在包管理模式下进行安装，可以将包安装到局部项目  
2. 在REPL 模型下通过`using Pkg; Pkg.add("package name")`，可以将包安装套全局  
3. 安装完之后可以在代码中`using` 使用包  

## 语法  
> Julia 也没有用花括号表示代码块的概念，而是通过`end` 关键字来表示代码块的结束。  
> 宏：通过`@` 开头，常见的有`@show`、`@info` 用于显示变量数据    

## 项目结构  
1. 可以在REPL 模式下通过`using Pkg; Pkg.generate("project_name")` 来创建项目  
2. 在cmd/bash 中，通过`julia --project[={<dir>|@.}]` 即可将项目设置为起始项目，例如：`shell> julia --project=project_name`；也可以在切换到项目目录后，在包管理模式下通过`activate .` 激活当前项目     
```shell-session  
PS D:\demo> julia
               _
   _       _ _(_)_     |  Documentation: https://docs.julialang.org
  (_)     | (_) (_)    |
   _ _   _| |_  __ _   |  Type "?" for help, "]?" for Pkg help.
  | | | | | | |/ _` |  |
  | | |_| | | | (_| |  |  Version 1.8.3 (2022-11-14)
 _/ |\__'_|_|_|\__'_|  |  Official https://julialang.org/ release
|__/                   |

shell> cd project_name
D:\demo\project_name

(@v1.8) pkg> activate .
  Activating project at `D:\demo\project_name`

(project_name) pkg> 
```

3. 步骤2 会启动一个新的julia 会话，在此会话中切换到包管理模式，可以将包安装为局部依赖：`(project_name) pkg> add CSV`  
4. 最简单的项目一般包含：`src/` 和`Project.toml` 两部分，前者是代码后者是关于项目的描述，项目中也可以包含测试、文档等文件（夹），但这不是必须的  
5. 当`src` 目录下有很多文件时，可以在适当的位置通过`include("file.jl")` 将它们导入到主文件中，但是不能直接包含文件夹。这也是组织代码最常用的方式。  

每次在修改完包代码后，切换回REPL 界面，发现改动不会自动生效。这时需要我们安装`Revise` 包，并在每次启动REPL 时都自动`using Revise`（添加`using Revise` 到`~/.julia/config/startup.jl`），这样代码的改动就能够实时更新到REPL 了。相应的，我们会感觉到每次更新源码后都需要重新编译。如果遇到修改后（新增）的代码不能直接生效，可能需要重启julia REPL 才行。

### 模块  

julia 中以`module end` 关键字定义模块，模块间可以嵌套、也可以定义在不同的文件中。在引用内部模块时可以缩写内部模块名，例如：`using .Inner`。  

模块可以导出内部的方法、变量，通过`export` 关键字即可以实现。但是julia 并不具有隐藏内部模块的功能。    

所以一个基本项目的结构应该如下：  
```shell-session  
# tree project_name  
project_name  
├── src
│   ├── sub         # 通过include 组织代码
│   │   └── sub.jl
│   └── project_name.jl
├── Manifest.toml
├── Project.toml
└── ...
```


## 参考  
1. [Julia中文文档-手册-模块](https://juliacn.gitlab.io/JuliaZH.jl/manual/modules.html)