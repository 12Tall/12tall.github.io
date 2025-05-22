---
title: 信号发生器的实现  
date: 2022-08-03
tags:   
    - python    
    - 通信    
    - 多进程  
---  

本文受[How to terminate running Python threads using signals](https://www.g-loaded.eu/2016/11/24/how-to-terminate-running-python-threads-using-signals/) 文章启发，但只保留了多线程相关的部分。  
起因是最近想用Python 模拟信号发生器的功能，自然需要通过主线程控制子线程发送数据（开始，暂停，继续，停止等状态）。第一版是通过`lock` 锁加上各种标志属性来实现的，总感觉思路不太清晰。于是参考上面的链接，采用`event` 来重构代码，总算得到了一个自己较为满意的（可扩展的）版本。    
<!-- more -->
## V0.1 的设计思路  
`v0.0` 的设计思路是通过系统定时器来向端口定时发送数据，但Windows 平台的实时性不够，详见[关于采样频率的说明](#关于采样频率)。于是在基本逻辑不变的情况下采用了人为设置`Δt` 的策略，也就是`v0.1`。

### IGenerator 接口  
考虑我们的信号发生器，最重要的就是将信号及时准确地发送出去。所以我们需要一个发送信号的方法：  
```python  
from time import sleep

class IGenerator(object):
    """
    ISender 接口  
    可以发送数据、被重置
    """
    def __init__(self) -> None:
        pass  

    def reset(self):  # 重置功能
        pass  

    def generate_data(self):  # 生成数据
        pass

    def send(self):   # 发送功能
        # sleep(0.1)  # 可以通过sleep 函数控制数据发送的频率
        pass
```

这里我们通过类来表示接口的定义，通过实现接口方法，我们可以获取不同的信号发生器子类。

### 通过Event() 控制线程  
为了可以不间断地发送正确地数据，我们需要在一个独立的线程中调用`IGenerator` 对象的`generate_data/send` 方法，并且需要在主线程中控制子线程的`开始/暂停/停止` 等功能。这里我们通过`threading.Event()` 来实现：  
```python
from threading import Event, Thread  

class Executor(Thread):
    def __init__(self, generator: IGenerator):
        Thread.__init__(self)
        self.daemon = True  # 设置为守护线程，当主线程退出时自动结束
        self.generator = generator  # 接收一个IGenerator 对象，用于发送数据
        self.pause_flag = Event()   # 暂停线程
        self.stop_flag = Event()    # 结束线程

    def resume(self):  # 开始/继续发送
        self.pause_flag.set()

    def pause(self):   # 暂停发送  
        self.pause_flag.clear()

    def stop(self):    # 停止发送，结束线程
        self.stop_flag.set()

    def run(self):     # 线程体
        while True:
            self.pause_flag.wait()  
            if self.stop_flag.is_set():
                break
            self.generator.send()
```

关于上面代码关于`threading.Event` 有以下几点可以帮助理解：  
- `threading.Event` 对象作为一个特殊的标志，`is_set()`默认为`False`;  
- `threading.Event` 对象的`wait` 方法会在`is_set()` 标志位为`True` 的时候阻塞线程，直到其变为`False`;  
- `threading.Event` 对象的`clear` 方法可以将`is_set()` 设置为`False`；相反，`set` 方法可以将其设置为`True`。  

### 端口  
信号发生器需要通过端口连接到设备，端口可以是RS232、USB，抑或是并行端口。为了便于扩展，我们就需要抽象一个端口的接口，约定他要实现的功能：  
```python
class IPort(object):
    """
    IPort 输出接口
    需要重写接口函数
    """

    def __init__(self) -> None:
        self._is_on = False
        pass

    def turn_on(self):
        # 模拟端口打开，需要避免重复打开
        if not self._is_on:
            self._is_on = True

    def turn_off(self):
        # 端口关闭
        self._is_on = False

    def wait_writable(self):  # 等待端口可用
        while True:
            sleep(0.5)
            break

    def write(self, data: any):
        print("[%s] Port send: %s" % (datetime.now(), data))

    ##################################################
    # send 方法可以不用重写  
    ##################################################
    def send(self, data: any):
        # 模拟端口发送数据的过程
        if self._is_on:  # 模拟检查端口状态，如果端口已关闭就不再发送
            self.wait_writable()
            self.write(data)
```

### 测试代码  
我们新建一个简单的类来实现`IGenerator` 接口来验证我们的想法：  
```python
from datetime import datetime

class BaseGenerator(IGenerator):
    def __init__(self,deltaT=0.001) -> None:
        """
        deltaT: 采样周期，单位是s
        """
        super().__init__()
        self._is_on = False
        self.counter = 0
        self.deltaT = deltaT
        self.exe = Executor(self)

    def generate_data(self):
        self.counter += self.deltaT

    def reset(self):
        self.counter = 0

    def send(self):
        self.port.turn_on()   # 保证端口已经打开
        self.generate_data()  # 生成信号
        self.port.send(self.counter)  # 模拟发送数据
    

    ###########################################################    
    # 将Executor 嵌套进信号发生器，将会使我们的代码更整洁  
    # 而且只需要在基类中定义一次以下方法就好了
    ###########################################################
    def turn_on(self):  
        if not self._is_on:
            self.exe.start()  # 开启线程，此方法只能执行一次  
            self._is_on = True
    
    def resume(self):  
        self.exe.resume() 
    
    def pasue(self):
        self.exe.pause()
    
    def stop(self):  
        self.exe.stop()
        self.port.turn_off()
        self.exe = Executor(self)  # 为开始新一轮任务做准备
        self._is_on = False

# 开始功能验证  
if __name__ == "__main__":
    bg = BaseGenerator()

    bg.turn_on()  # 开启
    bg.resume()   # 开始输出
    sleep(3)

    bg.pasue()    # 暂停
    sleep(3)

    bg.resume()   # 继续输出
    sleep(1.5)

    bg.reset()    # 中间重置状态
    sleep(2.5)

    bg.stop()     # 停止
    sleep(3)
```

可以将上面的代码保存为`app.py` 并在命令行中执行：  
```shell-session  
$> python ./app.py  # 执行过程中Ctrl-C 中断进程
# 信号发生器打开
# 开始发送数据
[2022-07-28 21:14:40.003383] Port send: 0.001
[2022-07-28 21:14:40.521429] Port send: 0.002
[2022-07-28 21:14:41.050418] Port send: 0.003
[2022-07-28 21:14:41.579746] Port send: 0.004
[2022-07-28 21:14:42.107661] Port send: 0.005
[2022-07-28 21:14:42.637441] Port send: 0.006
Traceback (most recent call last):
  File "./app.py", line 113, in <module>
    sleep(3)
KeyboardInterrupt
$> 
$> 
$> python ./app.py  # 正常退出
# 发生器已打开
# 开始发送数据
[2022-07-28 21:14:54.380992] Port send: 0.001
[2022-07-28 21:14:54.909388] Port send: 0.002
[2022-07-28 21:14:55.439230] Port send: 0.003
[2022-07-28 21:14:55.956788] Port send: 0.004
[2022-07-28 21:14:56.487928] Port send: 0.005
[2022-07-28 21:14:57.018972] Port send: 0.006
[2022-07-28 21:15:00.378835] Port send: 0.007
[2022-07-28 21:15:00.910546] Port send: 0.008
# 发生器即将暂停，然后再次开始发送数据
[2022-07-28 21:15:31.822823] Port send: 0.007
[2022-07-28 21:15:32.340982] Port send: 0.008
[2022-07-28 21:15:32.860573] Port send: 0.0
# 中间人为重置信号
[2022-07-28 21:15:33.378901] Port send: 0.001
[2022-07-28 21:15:33.897071] Port send: 0.002
[2022-07-28 21:15:34.414886] Port send: 0.003
[2022-07-28 21:15:34.931465] Port send: 0.004
# 信号发生器停止并退出
$>
```

可见程序运行符合预期。并且可以通过继承`BaseGenerator` 重写`generate_data/send` 方法产生不同波形的数据向不同的设备发送数据。这也是这篇笔记最重要的想法。    

----  
📅2022-07-22 Aachen    


## 关于采样频率  
因为通信中最重要的就是数据的准确、及时，而Python 中的`sleep` 函数的精确度是不稳定的，所以我们就需要给产生的信号以时间信息，这里有三种方法：  
1. 采用C/C++ 扩展，但是这是一种出力不讨好的事情，因为很难保证Python 的其他代码的执行效率；  
2. 给发送数据带上时间戳，这样会占用一部分带宽；  
3. 我们按照某个步长产生数据，接收器按照同样的步长采集数据。  

经过与做电子产品设计的同学讨论，方案三是生产中最常用的方法。如果对精度要求更高，可以考虑常采用实时的设备、给数据带上时间戳等方案。  
关于Windows 平台下精确延时的方案可以参见[这篇笔记](../../notes/c-like/win-high-accuracy-timmer.md)。[VOFA+](https://www.vofa.plus/docs/learning/widgets/wave#%CE%B4t) 中同样也采用`Δt` 来人为地调整数据的采样周期。

## V0.2 版设计思路  
在实现`v0.1` 的过程中，逐渐意识到：信号发生器本身是一个空壳子，最核心的部分是其中包含的函数部分与通信端口。于是将`Generator` 设计为一个线程类，通过`Generator` 对象直接控制线程的运行，并且引入了生成函数的概念，使得信号的产生和输出更加灵活。  

### 端口接口  
通过引入抽象类的概念，我们现在可以理直气壮地称呼端口为接口了。其中仍然只包含端口打开、关闭、等待可用、发送数据的逻辑功能。具体功能需要在子类中实现。需要注意的是，`send` 函数可以接收一个`list` 对象，也就是不止一个信号生成函数的返回值，可以在写入端口时进一步筛选和加工：    
```python  
import abc
from threading import Event, Thread
from typing import List, Union


class IPort(abc.ABC):
    """
    IPort 信号发生器的输出接口    
    内置了一个状态标志self._is_on = False
    """

    def __init__(self) -> None:
        super().__init__()
        self._is_on = False

    @abc.abstractmethod
    def turn_on(self):
        """
        打开端口，而且只能打开一次。
        最后需要修改self._is_on = True
        """
        if not self._is_on:
            self._is_on = True

    @abc.abstractmethod
    def turn_off(self):
        """
        关闭端口。
        需要修改self._is_on = False 
        """
        self._is_on = False

    @abc.abstractmethod
    def wait_port_available(self):  # 等待端口可用
        """
        等待端口可用
        """

    @abc.abstractmethod
    def send_data(self, data: List[float]):
        """
        向端口写入数据
        可以自定义写入数据的格式
        """

    def send(self, data: List[float]):
        """
        等待端口可用后写入数据
        """
        if self._is_on:
            self.wait_port_available()
            self.send_data(data)
        else:
            raise IOError("端口未打开或不可用")
```

### 信号生成函数  
信号生成函数其实是一个对象，有自己的计数器属性，但是步长需要在`Generator` 对象中统一管理（也可以不这样设置，但是担心使用起来会比较混乱）。也可以在子类中添加其他自定义属性，用来生成更复杂的波形：  
```python
import abc
from threading import Event, Thread
from typing import List, Union

class IFunction(abc.ABC):
    """
    信号产生函数，包含以下属性：  
    - timer: 计数器  
    - value: 输出结果的缓存  
    - deltaT: 0.001s 函数产生的步长，在Generator 中自动设定
    """

    def __init__(self, deltaT=0.001):
        self.timer = 0.
        self.value = 0.
        self.setDeltaT(deltaT)

    def setDeltaT(self, deltaT=0.001):
        self.deltaT = deltaT

    @abc.abstractmethod
    def call(self):
        """
        进行一步计算，返回信号值
        """

    @abc.abstractmethod
    def reset(self):
        """
        重置函数：计数器、当前值等
        """
```

### 信号发生器  
信号发生器的基本控制逻辑没有变，还是通过`Event()` 事件控制线程的运行。不过将所有的控制函数都绑定在线程对象本身了，并且理论上可以添加任意多个信号生成函数和端口：

```python{25-27}
import abc
from threading import Event, Thread
from typing import List, Union

class Generator(Thread):
    """
    Generator 信号发生器类:
    本质上是一个线程，其中包含一个run() 函数，用于不间断地产生信号。此线程为守护线程，会在主线程退出后自动结束。 
    """

    def __init__(self, deltaT: float, funcs: Union[IFunction, List[IFunction]], ports: Union[IPort, List[IPort]]):
        """ 
        参数说明：  
        - deltaT: 产生信号的步长，非负数；  
        - funcs: 用于产生信号的函数规则集合；  
        - ports: 用于发送信号的（物理）端口，数据会以list 的形式传递给port 端口。  


        私有属性：  
        - self.pause_flag = Event() 默认为False，会造成self.pause_flag.wait 方法阻塞  
        - self.stop_flag = Event() 默认为False，会造成self.stop_flag.wait 方法阻塞
        """
        Thread.__init__(self)
        self.daemon = True  # 设置为守护线程，当主线程退出时自动结束
        self.deltaT = deltaT if deltaT > 0. else 0.001
        self.funcs = funcs if isinstance(funcs, list) else [funcs]
        self.ports = ports if isinstance(ports, list) else [ports]

        # 私有属性
        self.pause_flag = Event()
        self.stop_flag = Event()

        self.setDeltaT()

    def setDeltaT(self):
        """
        更改信号产生的步长
        """
        for func in self.funcs:
            func.setDeltaT(self.deltaT)

    def turn_on(self):
        for port in self.ports:
            port.turn_on()
        self.start()

    def resume(self):
        """
        继续执行
        """
        self.pause_flag.set()

    def pause(self):
        """
        暂停执行
        """
        self.pause_flag.clear()

    def reset(self):
        """
        重置所有的函数  
        在信号发生器运行时执行此函数可能造成意料之外的后果
        """
        for func in self.funcs:
            func.reset()

    def stop(self):
        """
        停止执行并退出
        """
        self.stop_flag.set()
        for port in self.ports:
            port.turn_off()

    def run(self):
        while True:
            self.pause_flag.wait()  # 暂停线程
            if self.stop_flag.is_set():
                break  # 退出线程
            data = [func.call() for func in self.funcs]
            for port in self.ports:
                port.send(data)
```

### 测试代码  
可以通过查看或下载[Github](https://github.com/12Tall/yan_serial_tools/tree/31e693f90a2dbfd8f258837080fe0cd3df88b9c5) 中的代码熟悉逻辑，并且其中也定义了几个基本的端口和信号生成函数。  

```python{5,6}
from time import sleep
from SignalGenerator import Generator, DefaultFunction, DefaultPort, DIntTFunction, CIntTFunction


bg = Generator(0.1, [DefaultFunction(), DIntTFunction(),  ## 初始化信号发生器时可以设置多路输出
               CIntTFunction()], [DefaultPort(),DefaultPort()])
bg.turn_on()  # 开启
bg.resume()   # 开始输出
sleep(3)

bg.pause()    # 暂停
sleep(3)

bg.resume()   # 继续输出
sleep(5)

bg.reset()    # 中间重置状态
sleep(2.5)

bg.stop()     # 停止
sleep(3)

```
经测试，代码的运行符合预期。  

----  
📅2022-08-03 Aachen  