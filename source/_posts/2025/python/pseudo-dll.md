---
title: Python 实现动态链接库效果
date: 2025-05-21 13:56:55
tags:  
    - 编程技巧
---

需求来源是做`OSM` 编辑项目中要用Python 对`.osm` 文件进行校验，但是嘞，我的Python 代码
是需要用Nuitka 打包成二进制的，而校验规则又可能会随时调整，每次增减规则都要重新打包的话非常浪费时间。因此，便想能否通过类似与调用`.dll` 一样来动态加载`.py` 文件（伪动态链接库）。  

<!-- more -->

## 前置要求  
1. Nuitka 打包后的二进制文件要包含完整的Python 运行时；✅  
2. `.py` 文件要有统一的入口函数；✅  
3. `.py` 文件的依赖项要提前在二进制文件中`import`。✅

## 实现代码  
演示代码主要分为主文件`main.py` 和库文件`ddl.py`，二者在相同目录：  
```python
# main.py

import os
import uuid
import importlib.util

###  调用外部.py 前的准备工作 ###
import numpy as np  # 外部模块中需要用到的依赖项，需要提前导入准备
module_path = os.path.abspath("dll.py")  # 获取目标.py 文件的绝对路径（此处可以读取该目录下的所有.py 文件，循环导入）
module_name = f"_dynamic_module_{uuid.uuid4().hex}"  # 生成随机的模块名
# 模块名作为模块身份的唯一标识，仅会被导入一次，通过随机化处理可以避免命名重复而无法导入

spec = importlib.util.spec_from_file_location(module_name, module_path)  # 创建一个加载说明（描述符）
module = importlib.util.module_from_spec(spec)  # 根据加载说明加载.py 文件为模块
spec.loader.exec_module(module) # 执行模块

# 使用模块中的函数
module.hello()  # 有必要约定模块中的函数签名保持一致，否则可能会报错
```

以下是库文件
```python
# dll.py
import numpy as np  # numpy 需要提前打包在二进制文件中

def hello():
    print("Hello from dll.py!")
```

通过`python -m nuitka --clang --standalone --onefile main.py` 即可打包成二进制文件，即便在没有安装Python 环境的机器上也可以运行了。    
```shell-session
$ ./main.bin 
Hello from dll.py!
```
