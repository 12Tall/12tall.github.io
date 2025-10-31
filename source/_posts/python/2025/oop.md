---
title: Python 面向对象编程
date: 2025-10-31 11:29:10
tags:
    - python  
    - 面向对象编程
---

面向对象/设计模式虽然越来越少被提及了，但并不是没用了。只是现在比较火的AI 用的相对较少。在复杂的系统中，OOP 的思想还是非常有用的，比如游戏开发。  

<!-- more -->

## 举个栗子  
尽量在下面一段代码中展示所有的关键点：  
```python
class DemoClass(object):  # DemoClass 类继承object
    version = "0.1"  # 类变量  

    def __init__(self, name:str):
        # 构造函数
        super.__init__()  # 调用父类方法

        self._name = name  # 实例变量（各对象独立） 
        # 下划线开头表示私有变量，不应直接操作（非强制）

    def __del__(self):
        print("执行析构函数")
    # 类似的函数还有__str__(),__len__(),__add__(),__call__()等  
    # 用于重定义一些默认操作

    @classmethod  # 类方法装饰器
    def info(cls):  
        # cls 指代类自身
        return f"版本：{cls.version}"

    @staticmethod  # 静态方法不是必须放在类中
    def say_hi():
        print("Hi~")

    # 属性控制
    @property  # 装饰器，相当于getter 方法
    def name(self):
        return self._name      
    
    @name.setter  # 装饰器，setter 方法
    def name(self, val:str):
        self._name = val
```

### 上下文管理  
```python
class FileManager:
    def __enter__(self): print("打开文件")
    def __exit__(self, exc_type, exc, tb): print("关闭文件")

with FileManager():
    print("处理中")
```

### 对象拷贝  
```python
import copy
a = [1, [2, 3]]
b = copy.copy(a)     # 浅拷贝
c = copy.deepcopy(a) # 深拷贝
```


## 抽象类与接口  
通常使用`abc` 模块来定义抽象类，然后可以把抽象类当接口使用。通过抽象类定义接口的好处是：IDE 在定义子类方法时会自动补全函数签名。
```python
from abc import ABC, abstractmethod

class IArea(ABC):
    @abstractmethod
    def area(self):...

class IPerimeter(ABC):
    @abstractmethod
    def perimeter(self):...

class Square(IArea, IPerimeter):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2
    def perimeter(self):
        return self.side * 4
```

### 元类  
元类表示类的类型，以单例模式为例，虽然可以用类属性定义，但是通过元类表示则更通用一些：  
```python
# 单例模式  

class SingletonMeta(type):
    _instances = {}
    # 创建类对象时调用
    def __new__(cls, name, bases, dct): ...
    # 初始化类对象
    def __init__(cls, name, bases, dct): ...
    # 类对象实例化时调用
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MyClass(metaclass=SingletonMeta):
    pass

a = MyClass()
b = MyClass()
print(a is b)  # True
```
元类因为Python `读取->执行`的特性在`ORM` 中比较常见，但是不建议在日常代码中使用，避免引起混乱。 

## 函数重载  
函数重载在python 中并没有一个比较好的实现，一般可以通过判断参数类型实现：
```python
def add(a:int|str, b:int|float|str):
    if isinstance(a, int):...
    if isinstance(b, (int, float)):...
```
也可以通过`functools.singledispath` 注解实现，具体原理见下面函数装饰器。  

### 函数装饰器  
#### 简单的装饰器  
函数装饰器主要用来执行一些通用的，函数调用前后的准备或清理工作。
```python
def simple_decorator(func):
    """一个最简单的装饰器示例"""
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        print(f"传入参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)  # 调用原函数
        print(f"返回结果: {result}")
        return result
    return wrapper

# 使用装饰器
@simple_decorator
def add(a, b):
    return a + b

# 调用
add(3, 5)
```

#### 实现函数重载  
1. 声明函数入口`@overload`  
2. 注册函数`@overload.register`  
3. 根据参数类型，调用函数`target = registry.get(types)`

```python
# 装饰器代码结构
from functools import wraps  
# 导入 wraps，用于保留被装饰函数的元信息（__name__ / __doc__ 等）

def decorator(func):
    ... # 装饰器内部闭包变量

    @wraps(func)  # 装饰器函数体
    def wrapper(*args, **kwargs):...

    def register(func_impl):
        ... # 用来注册不同参数签名的函数到warpper
        return wrapper

    # 把 register 方法附加到 wrapper 上，使用方式：@f.register
    wrapper.register = register

    # 返回最外层的 wrapper，作为装饰器的实际效果函数
    return wrapper
```

ChatGPT 具体实现：
```python
import inspect                   # 导入 inspect 模块，用于获取函数签名等元数据
from functools import wraps      # 导入 wraps，用于保留被装饰函数的元信息（__name__ / __doc__ 等）

def overload(func):
    """定义重载装饰器 factory，传入一个占位函数 func（通常是 *args 占位）"""
    registry = {}  # 存放已注册的重载实现：key = 类型元组 (int, str, ...)，value = 对应实现函数

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取装饰器外层占位函数的签名（我们把它当作“调用签名”的基准）
        sig = inspect.signature(func)

        # 部分绑定实际传入的参数（bind_partial 允许缺省某些参数，用于只推断传入的实参）
        bound = sig.bind_partial(*args, **kwargs)

        # types 列表将保存实际调用时每个位置参数的类型（例如 (<class 'str'>, <class 'int'>)）
        types = []
        # bound.arguments 是一个 OrderedDict，键是形参名，值是对应的实参
        for v in bound.arguments.values():
            # 如果 v 是 tuple（通常对应 *args 收到的位置参数），我们需要展开它
            if isinstance(v, tuple):
                # 将元组每一项的类型加入 types 列表
                types.extend(type(x) for x in v)
            else:
                # 否则直接将该参数的类型加入
                types.append(type(v))
        types = tuple(types)  # 转成不可变的元组用于字典查找

        # 调试/可视化输出，显示调用时的参数类型元组
        print(f"调用参数类型: {types}")

        # 在 registry 中查找是否存在匹配的重载实现
        target = registry.get(types)
        if target:
            # 如果找到，就调用该实现并返回结果
            print(f"→ 匹配到重载函数: {target.__name__}{types}")
            return target(*args, **kwargs)
        else:
            # 没找到则抛出 TypeError（也可以改为回退到默认实现或做模糊匹配）
            raise TypeError(f"没有找到匹配的函数版本: {types}")

    # 定义 register 子函数，用来注册不同参数签名的实现到 registry
    def register(func_impl):
        # 获取被注册实现的签名（即注册时写的具体函数签名）
        sig = inspect.signature(func_impl)

        # types_key 是这个实现函数的参数注解元组（作为 registry 的 key）
        # 注意：这里使用注解（annotation）作为注册 key，因此注册函数必须对参数做注解
        types = tuple(param.annotation for param in sig.parameters.values())

        # 输出注册信息（可选，便于调试）
        print(f"注册重载函数: {func_impl.__name__}{types}")

        # 把实现函数存进 registry 中
        registry[types] = func_impl

        # 返回 wrapper（使得 @overload 和 @f.register 都能链式工作）
        return wrapper

    # 把 register 方法附加到 wrapper 上，使用方式：@f.register
    wrapper.register = register

    # 返回最外层的 wrapper，作为装饰器的实际效果函数
    return wrapper


# ---------- 使用示例 ----------

@overload
def greet(name:str, age:int|str):
    """占位函数：实际实现通过 @greet.register 注册"""
    pass

# 注册：只有一个字符串参数的实现
@greet.register
def _(name: str):
    print(f"你好，{name}！")

# 注册：字符串 + 整数 的实现
@greet.register
def _(name: str, age: int):
    print(f"你好，{name}，你 {age} 岁！")

# 注册：字符串 + 字符串 的实现
@greet.register
def _(name: str, age: str):
    print(f"你好，{name}，年龄字符串：{age}")


# 测试调用（正常调用）
greet("Alice")
greet("Bob", 25)
greet("Charlie", "二十五")
# 你也可以用 greet(("D", 40)) 这种单元组形式调用，本实现不会展开外层 args，因为我们从 greet 的签名（*args）来 bind
```

## 参考文献  
1. [Python 装饰器](https://www.runoob.com/python3/python-decorators.html)