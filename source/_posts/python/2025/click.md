---
title: Python 命令行模块Click 笔记
date: 2025-06-26 14:11:35
tags:
    - python  
    - cli  
    - click
---

通过click 模块，可以帮助快速创建命令行工具，仅以一个例子来分析其常用功能。    
<!-- more -->
## 一般概念  
在click 模块中有下面三个关键概念，都是以装饰器的形式使用：  
1. group: 命令组，分类管理命令  
2. command: 命令，一般是指被装饰的函数名  
3. option: 接受参数  

### 命令command  
command 是最基本的单位：
```python
import click

@click.command()
def main():
    click.echo("hello")

if __name__ == '__main__':
    main()
```


### 命令组group  
如果命令比较简单（比如只有一个命令）可以不需要命令组，只需用command 就行了，但是如果命令比较复杂，则需要创建命令组：  
```python
import click

@click.group(invoke_without_command=True)
# 无需次级命令（init）也可运行
def cli():
    click.echo("hello world!")

@cli.command()  # cli 命令组下的命令
def init():
    click.echo("Initialized.")
# 每个组下面可以添加多个子命令

if __name__ == '__main__':
    cli()
```

则可以通过`python cli.py init` 执行`init()` 函数。  

### 参数option  
命令和命令组都可以读取相关参数，而option 可以通过设置参数名、全名、默认值是否必填和帮助信息等：  
```python
import click

@click.group(invoke_without_command=True)
@click.option("-ng","--nogui",is_flag=True, default=False, help="running without GUI")
def cli(nogui):  # 参数名与option 中定义的全名一致
    if nogui:
        click.echo("No GUI mode")
    else:
        click.echo("GUI mode")

@cli.command()
def init():
    click.echo("Initialized.")

@cli.command()
def status():
    click.echo("Status: OK")

if __name__ == '__main__':
    cli()
```
则可以通过`python cli.py --nogui init` 执行`init()` 函数。

## 上下文与控制流  
可以向命令组中传入上下文，已提前结束或终止命令：  
```python
import click

@click.group(invoke_without_command=True)
# 无需次级命令也可运行
@click.option("--nogui",is_flag=True, default=False )
@click.pass_context
def cli(ctx:click.Context,nogui):
    if nogui:
        click.echo("No GUI mode")
    else:
        click.echo("GUI mode")
        ctx.exit()  

@cli.command()
def init():
    click.echo("Initialized.")

@cli.command()
def status():
    click.echo("Status: OK")

if __name__ == '__main__':
    cli()
```
在`nogui==False` 的情况下，即使命令行参数添加了`init`，`init()` 函数也不会被执行。 