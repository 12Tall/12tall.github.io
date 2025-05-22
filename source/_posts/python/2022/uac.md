---
title: Python 请求UAC  
date: 2022-08-03   
tags:   
    - python    
    - UAC
---  


在编写Python 代码时，有时我们会遇到请求管理员权限的情况，比如修改hosts 文件、打开某些端口等等。我们可以在打包Python 成可执行文件时附上UAC 相关的信息。然而更一般的，我们可以在代码中判断当前进程是否以管理员权限运行，如果不是，则调用系统的`runas` 命令，通过管理员权限重新启动一个进程。  
<!-- more -->
## 获取当前进程状态  
我们可以通过`ctypes` 库调用`shell32.dll(shlobj_core.h)` 中的`IsUserAnAdmin()` 方法来获取当前进程是否是以管理员权限运行：  

```python  
import ctypes  

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

print(is_admin())  
# 打印结果
# 0: False  
# 1: True
```

## 以管理员权限重新启动程序    
如果要以管理员权限重新启动脚本的话，方法比较直接： 
```python{15}
# python3  

if(is_admin()):  
    # 工作代码  
    pass  
else:  
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    # hWnd: 父窗口  
    # lpOperation: 动作。
    #     - edit: 启动编辑器，打开lpFile  
    #     - explore: 浏览lpFile 指定的的文件夹  
    #     - find: 在lpDirectory 指定的目录启动查找  
    #     - open: 打开lpFile，可以是一个文件或者是文件夹  
    #     - print: 打印lpFile，如果不是文档则报错  
    #     - runas: 以管理员权限运行，会弹出UAC 窗口  
    #     - NULL: 默认值  
    # lpFile: 将要被执行的文件或文件夹  
    # lpParameters: 如果lpFile 是可执行文件，则此参数表示调用的命令行参数  
    # lpDirectory: 表示动作的工作目录，如果为空则使用当前目录  
    # nShowCmd: 窗口选项  
    #     - SW_HIDE 0    
    #     - SW_SHOWNORMAL 1    
    #     - SW_SHOWMINIMIZED 2    
    #     - SW_SHOWMAXIMIZED 3    
    #     - 详见：https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
```

在可执行文件中调用时，那么`lpFile` 就应该是自己的文件名，参数仍然是`" ".join(sys.argv)`。


## 参考资料：  
1. [Python 获取Windows管理员权限](https://blog.csdn.net/MemoryD/article/details/83148305)  
2. [use shell execute to run cmd as Admin](https://stackoverflow.com/a/15326894/14791867)  
3. [Request UAC elevation from within a Python script?](https://stackoverflow.com/a/41930586/14791867)