---
title: &desc Pybind11 基础
date: 2026-04-02 10:37:33
description: *desc
tags:
  - python
  - c
  - c++
  - pybind11

next:
  text: Todo
  link: "."
---

# Pybind11 基础

在做机械臂项目时，需要通过`.so|.dll` 动态连接库完成控制和通信，但是该库是C++ 开发的，给的头文件也是C++ 的。个人简单的C++ 能看懂，但是要写的话还是有难度的。尝试ffi 和研究ctypes 之后，最终准备通过Python 调用动态库的方式进行开发，封装一个python 可以直接import 的库，效果尚可，但也有一些需要注意的坑。毕竟和C++ 相关，就跳不过指针和内存。  
要说本节学会的最重要的东西是什么，那就是：**作为SDK的使用者，要仔细看文档，每个函数的说明；作为SDK的开发者，要写好文档，每一个可能存在的坑**。

## 环境配置

因为我现在已经习惯了Zed，所以就不再写VSCode 的配置了。Zed 除了输入法兼容不太好，然后有时容易无响应之外。整体用起来还是蛮舒服的。  
:::code-group

```shell[init-cmd]
$ uv init --python=3.12
$ uv sync
$ uv add pybind11  # 初始化python 环境并安装依赖

$ # 下面是编译python 模块时会用到的命令（uv 兼容，直接使用本机python3 还要更简单些）
$ g++ -O3 -Wall -shared -std=c++11 -fPIC $(uv run python -m pybind11 --includes) \
  I./sdk/cpp/include crp.cpp \
  -o crp$(uv run python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
$ # 上面命令会在本地生成一个crp.cpython-312-x86_64-linux-gnu.so
$ # 可以被直接import

$ uv run main.py
```

```python[main.py]{8-11}
import crp # 可以直接导入

# 下面这句话如果不放在函数里，容易出现动态链接库不能被及时回收
# 指针异常，导致segment fault 或者bus error
# loader = crp.CSDKLoader.CSDKLoader("./***.so")

def main():
  loader = crp.CSDKLoader.CSDKLoader("./***.so")  # 放在函数里也没好到哪而去
  # 原因在于*.so 中有自己维护的线程池，python 对象析构了。线程池还在等资源。  
  
  loader.initailize()
  svc = loader.create_IOService("xxxx") # 要注意谁负责管理内存，是C++ 还是Python
  loader.delete_IOService(svc)  # 容易出现悬空指针，所以最好都放函数里
  print("hello there!")

if __name__ == "__main__":
  main()
```

```yaml[.clangd]
# 用于Zed 编辑器语法高亮
CompileFlags:
  Add: [
    "-I./sdk/cpp/include",
    "-I.venv/lib/python3.11/site-packages/pybind11/include",
    # 可惜不能用变量
    "-I/home/{user}/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/include/python3.12"
  ]
```

:::

## C++ 头文件

以下是精简后的头文件，我们后面就是要将其中的类、函数以及常量等，包装成python 可用的形式：

```cpp{28-29,36-37}
// 省略了一些不必要的宏和中间代码

namespace Crp {
class IService;

/// SDK接口加载辅助类
class CSDKLoader {
private:    // ...
public:
  /// 构造函数，执行时将变量给到成员变量
  CSDKLoader(std::string const& sdkDllPath)
      : mSdkDllPath(sdkDllPath)
      , mhModule(NULL)  // ...
      {}

  ~CSDKLoader() {
    deinitialize();
  }

  /// 初始化DLL接口
  bool initialize();
  /// 销毁创建的资源(接口、句柄)
  void deinitialize();

  /// 根据接口ID, 获取接口服务，如果接口未被创建, 自动创建接口，内存由CSDKLoader管理
  /// - 成功返回T*接口指针，内存由dll管理，生命周期与CSDKLoader一致
  /// - 失败返回nullptr
  /// 注意接口类与接口ID要保持一致，此函数获取的接口内存由CSDKLoader管理,
  /// 在CSDKLoader析构时被自动释放。
  template <typename T>
  T* getService(const char* serviceId) ;

  /// 根据接口ID, 创建接口服务
  /// - 成功返回T*接口指针，内存由用户管理，生命周期由用户管理
  /// - 失败返回nullptr
  /// 注意接口类与接口ID要保持一致,接口创建的内存由用户管理,
  /// 释放的接口为deleteService, 如未正常释放，会造成内存泄露
  template <typename T>
  T* createService(const char* serviceId) ;

  /// 删除由用户创建的服务接口
  template <typename T>
  void deleteService(T* service) ;

  /// 返回已创建的服务数量
  size_t serviceSize() const {
    return mServiceList.size();
  }
}  // namespace Crp
```

## Pybind11 包装

以下`crp.cpp`是Pybind11 对上面头文件的包装：

```cpp
// 按需引入头文件
#include "CSDKLoader.h"
#include "IIOService.h"
#include <pybind11/cast.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string.h>

namespace py = pybind11;  // 对命名空间进行简写

// 定义python 模块，第一个参数必须是模块名，m 就代指模块本身
PYBIND11_MODULE(crp, m){
    m.doc() = "对于C++ 库的Python 包装";
    py::class_<Crp::IIOService>(m, "IIOService")  // 在模块上声明一个类
        .def("getSXCount", &Crp::IIOService::getSXCount);  // 该类下面有一个方法

    auto CSDKLoader = m.sef_submodule("CSDKLoader");  // 创建一个子模块

    py::class_<Crp::CSDKLoader>(CSDKLoader, "CSDKLoader")  // 子模块下创建类
        .def(
            py::init<const std::string &(),  // 定义构造函数，接收一个字符串常量为参数
            py::arg("sdkDllPath")            // 参数名为sdkDllPath
        )
        .def("initialize", &Crp::CSDKLoader::initialize)  // 定义普通成员方法
        .def(
            "get_IOService",                                // 派生于泛型函数getService
            &Crp::CSDKLoader::getService<Crp::IIOService>,  // 但是每次只能定义某一种
            py::arg("serviceId") = ID_IO_SERVICE,           // 给定默认参数
            py::return_value_policy::reference_internal     // 链接库自身管理对象生命周期
        )
        .def(
            "create_FileService",                                // 派生于泛型函数createService
            &Crp::CSDKLoader::getService<Crp::IFileService>,  // 但是每次只能定义某一种
            py::arg("serviceId") = ID_FILE_SERVICE,           // 给定默认参数
            py::return_value_policy::reference                // Python 仅持有指针，不管里对象生命周期
        )
}
```

## 容易踩坑的地方

### C++ 函数返回指针

需要声明`py::return_value_policy::*`，规则如下：  
策略|内存管理方式|说明
---|---|---
`reference`|Python 仅持有指针，不管对象的生命周期（还是C++ 管理，但需要手工调用）|如上文`createService` 方法创建出的对象需要`deleteService` 删除  
`reference_internal`|Python 持有对象，但对象的生命周期由外部C++ 自动管理，一般用于指向类成员，能够保持父对象存活|如上文`getService` 方法创建出的对象会随`CSDKLoader` 析构自动删除，用户想手动干预可能会出错  
`take_ownership` | Python 拥有对象，析构时会delete|比较少用，C++ 再也不会使用该对象。例如函数返回`new Object()`
`automatic`|默认自动判断|在返回指针时可能存在安全问题

**如果要引入外部库，尽量在函数中引入，不要全局引入，否则有可能会出现指针释放错误的问题**

### 泛型函数的包装

Pybind11 不能直接包装泛型函数，考虑到C++ 中泛型函数最终会被编译为N 多个普通函数，所以需要手工声明需要的函数。如：

```cpp
py::class_<Crp::CSDKLoader>(CSDKLoader, "CSDKLoader")  // 子模块下创建类
    .def("get_IOService", &Crp::CSDKLoader::getService<Crp::IIOService>)
    .def("get_FileService", &Crp::CSDKLoader::getService<Crp::IFileService>)
    // ...
```

### 函数重载

**在C++ 中返回值不能作为判断函数签名的依据，所以不能定义只有返回值不同的函数重载。**

#### 1. 对于普通C++ 函数

```cpp
int add(int a, int b);
double add(double a, double b);
```

需要进行一次强制类型转换，否则编译器不知道选哪个

```cpp
m.def("add", (int (*)(int, int)) &add);
m.def("add", (double (*)(double, double)) &add);
```

#### 2. 对于类方法

```cpp
class Foo {
public:
    int bar(int x) { return x; }
    double bar(double x, int y) { return x; }
};
```

类型转换时需要加上类信息

```cpp
py::class_<Foo>(m, "Foo")
    .def("bar", (int (Foo::*)(int)) &Foo::bar)
    .def("bar", (double (Foo::*)(double, int)) &Foo::bar);
```

#### 3. Pybind11 自带类型转换

同上是对于上面类方法，有：

```cpp
py::class_<Foo>(m, "Foo")
    .def("bar", py::overload_cast<int>(&Foo::bar))
    .def("bar", py::overload_cast<double, int>(&Foo::bar));
```

### 释放GIL 锁

因为Python 实质上是单线程的，如果需要C++ 中真正跑出多线程的效果需要释放GIL 锁。释放GIL 锁并不会影响其他Python 代码，只是说从释放GIL 开始，到下次获取到GIL 之前，代码运行不再受Python 解释器调度。
但是对于Python 对象的操作必须持有GIL 锁。也就是说，除非线程不需要有返回值，否则，即使释放了GIL 锁，最后也要重新获取，以保证指令同步。

```cpp
int task(){
    py::gil_scoped_release release;     // 释放GIL锁
    // 耗时操作

    // C++执行结束前恢复GIL锁，但是Pybind11 在函数结束前会自动获取GIL
    // py::gil_scoped_acquire acquire;     //
    retuen 0；
}
```

在下面Python 代码执行时，速度会明显加快：

```python
# 伪代码
t = threading.Thread(target=task)  # 创建线程
t.start()  # 运行线程，释放GIL 之后会放飞自我
t.join()  # 等待线程结束
```

### C++ 处理Python 数据

如下代码：

```cpp
void foo(py::object obj) {  // 接收python 对象
    // 在操作Python 对象时，一定不要释放GIL，即使释放了也要提前require
    py::print(obj);

    // 获取对象属性
    auto name = obj.attr("name");
    py::print(name);

    // ✔ 安全调用函数
    if (py::hasattr(obj, "func")) {
        py::object f = obj.attr("func");

        if (py::callable(f)) {
            f(123);
        } else {
            py::print("func exists but not callable");
        }
    }
}

py::object make() {  //返回Python 对象
    return py::int_(0);
}

// 简单数据类型可以自动转换
int add(int a, int b) {
    return a + b;
}
```

### 静态资源释放顺序  
有时动态链接库中存在一些静态资源、线程池，如`spdlog` 相关的异步打印日志函数，在Python 解释器结束时可能在资源释放时报Segment Fault。如果不能修改动态链接库本身，则最好能将任务封装到Python 子进程中。（不知道有无更好地解决方案）。
```python
import crp
from multiprocessing import Process  

def sub_process():
    loader = crp.CSDKLoader.CSDKLoader("***.so")
    # 一系列操作  
    print("sub process")

if __name__ == "__main__":
    p = Process(target=sub_process)
    p.start()
    p.join()
    print("main process")
```
不是子进程不会崩溃，而是把崩溃的影响限制到子进程内部了。


## 参考资料

1. [Pybind11高级功能：函数绑定与返回值策略详解](https://blog.csdn.net/gitblog_00430/article/details/148375627)
2. [给Python算法插上性能的翅膀——pybind11落地实践](https://zhuanlan.zhihu.com/p/436664470)
