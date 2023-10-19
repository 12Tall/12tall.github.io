---  
title: Poetry 简介  
date: 2023-10-19
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
tag:   
    - poetry   
    - pip  
    - npm
---   

> 类似于`venv`，`poetry` 可以提供一个干净的依赖环境。因为`pip` 是全局安装，如果项目比较多则不可避免地会出现依赖冲突。  

## 使用简介  
其实`poetry` 的使用方法，尤其是命令，比较像`npm`，安装的话最好也是全局安装：  

```shell-session
# pip install poetry  # 全局安装，并添加PATH 变量   

## 创建目录moo，并初始化项目 ##

> poetry install # 对于已经存在的项目安装依赖
> poetry init  # 初始化项目，需要填写一些信息  
> poetry env use Python  # 创建虚拟环境，移除用remove       
> poetry add packages  # 添加依赖项  
> poetry add packages --dev  # 添加开发依赖项，如打包工具等  
> poetry show [--tree] 显示依赖项  

## 其他命令 ##  

> poetry export # 导出依赖项到requirement.txt  
> poetry shell  # 启动shell 命令行  
```  

`Poetry` 生成的项目中，`pyproject.toml` 的作用类似于`pakage.json`。  

与VSCode 的配合，只需要选择新创建的Python 虚拟环境作为执行环境就好了，重启VSCode 之后，所有的代码提示都是可用的。  


## 参考资料  
1. [再見了 pip！最佳 Python 套件管理器——Poetry 完全入門指南](https://blog.kyomind.tw/python-poetry/)  
2. [What is needed to make VSCode respect Python Poetry in projects?](https://www.reddit.com/r/vscode/comments/11kvr74/what_is_needed_to_make_vscode_respect_python/jbabex7/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
