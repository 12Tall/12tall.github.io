---  
title: Python 调用COM 组件  
date: 2023-05-12
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
tag:   
    - python   
    - COM 组件 
    - femm  
    - 注册表  
---   


> 以前通过COM 组件编辑过WORD 文件处理过PDF，当时觉得挺神奇的，现在发现FEMM 这款有限元软件也是通过COM 组件支持Matlab 和Python 调用的。感觉COM 组件在今后的学习中应该还是蛮有用的，这里就记一下Python 中如何调用COM 组件的简单步骤。 
> 附一个比较好的链接，关于COM 组件的，以后可能用得着：[com组件的从0-1](https://tttang.com/archive/1824/)

- 通过`CMD` 查询组件名：`reg query HKEY_CLASSES_ROOT`  
- 安装：`win32com` 包含在`pywin32` 库内部，所以直接使用`pip install pywin32` 安装即可   
- 使用：`o = win32com.client.Dispatch("femm.ActiveFEMM")`，创建组件的实例  
- 枚举属性：`dir(o)`，可以枚举属性名，以FEMM 为例，可以看到该组件只包含两个函数   

如果希望获取函数签名，则还需要看软件的说明文档。  
```python  
>>> import win32com.client
>>> femm = win32com.client.Dispatch("femm.ActiveFEMM")
>>> dir(femm)
['_ApplyTypes_', '_FlagAsMethod', '_LazyAddAttr_', '_NewEnum', '_Release_', '_UpdateWithITypeInfo_', '__AttrToID__', '__LazyMap__', '__bool__', '__call__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__int__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_builtMethods_', '_dir_ole_', '_enum_', '_find_dispatch_type_', '_get_good_object_', '_get_good_single_object_', '_lazydata_', '_make_method_', '_mapCachedItems_', '_oleobj_', '_olerepr_', '_print_details_', '_proc_', '_unicode_to_string_', '_username_', '_wrap_dispatch_', 'call2femm', 'mlab2femm']
```

## 调用方法  
以FEMM 为例，其主要用到`mlab2femm(cmd:string)` 方法，参数只有字符串指令，于是就可以这样去调用：  
```python  
>>> femm.mlab2femm('main_restore()')
''
```

于是便能够打开函数的主窗口。使用其他命令便可以模拟人工对程序进行操作了。  

了解了这些基本的使用方法，许多软件的自动化操作也就不会显得那么神奇了。但是怎么能用好，还是要对软件足够熟悉，并且有一本开发者文档。    