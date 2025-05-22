---
title: Python 多进程  
date: 2022-08-03
tags:   
    - python   
    - multiprocessing 
---  

> 处于跨平台考虑，仅记录multiprocessing 库的用法   

因为Python 中的多线程在CPU 密集型的任务中会变成线性的，并不能充分发挥多核处理器的优势。所以我们可以通过多进程来进行并行任务，并且我们还可以通过管道、共享内存、进程锁等机制来实现进程间的数据共享。  
<!-- more -->
## 创建一个子进程  
首先我们通过`multiprocessing.Process` 创建一个子进程，但是在`multiprocessing` 模块中`Process` 和`process` 是不同的东西，并且在Windows 平台上使用时必须要用`if __name__ == '__main__':`，尤其需要注意。  
```python
import os
from multiprocessing import Process, current_process


def task(param):
    info = """
进程名：%s  
进程Id：%s  
模块名：%s  
父进程Id：%s  
传入参数：%s  
""" % (current_process().name, os.getpid(), __name__, os.getppid(), param)
    print(info)


if __name__ == '__main__':
    t = Process(target=task, args=("233",))
    t.start()
    t.join()

```

## 共享数据  
因为每个进程都有自己的数据空间，在Python 脚本中声明的全局变量也是不能共享的：  
```python
import os
from multiprocessing import Process, current_process

arr = []  

def task(i):
    print("In process %s, the arr's address is: %s"%(i, id(arr)))


if __name__ == '__main__':
    for i in range(2):
        t = Process(target=task, args=(i,))
        t.start()
        t.join()
# 输出：
# In process 0, the arr's address is: 2172256009216
# In process 1, the arr's address is: 2485094464512        
```

如果要在进程间共享数据，可以使用`multiprocessing` 提供的`Queues`、`Array` 和`Manager` 三个类。  

### Array  
Array 类在初始化时必须指定类型与长度，也可以选择添加内容。如：`arr = Array('i',5)`。下面是数据类型的定义：  
```
'c': ctypes.c_char, 'u': ctypes.c_wchar,
'b': ctypes.c_byte, 'B': ctypes.c_ubyte,
'h': ctypes.c_short, 'H': ctypes.c_ushort,
'i': ctypes.c_int, 'I': ctypes.c_uint,
'l': ctypes.c_long, 'L': ctypes.c_ulong,
'f': ctypes.c_float, 'd': ctypes.c_double
```

需要注意的是：Array 对象必须作为参数传入子进程，否则也是不起作用的：
```python{11}
import os
from multiprocessing import Array, Process, current_process


def task(i, arr):
    arr[i] = i
    print("In process %s, the arr's address is: %s" % (i, id(arr)))


if __name__ == '__main__':
    arr = Array('i', [5, 5, 5, 5, 5])  # 因为Array 需要作为参数传入子进程，所以写在里面更清晰些
    for i in range(2):
        t = Process(target=task, args=(i, arr,))
        t.start()
        t.join()
    print(arr[0], arr[1], arr[2])

# 输出：
# In process 0, the arr's address is: 2163785163584  # 虽然地址不同，但内容是一样的
# In process 1, the arr's address is: 1995314455360
# 0 1 5
```

### Manager  
相比于Array，Manager 提供一个服务进程，其他进程可以通过代理的方式操作Python 对象，并且其支持的对象也更多：  
```python{11}
import os
from multiprocessing import Array, Manager, Process, current_process


def task(i, dic):
    dic[i] = i
    print("In process %s, the dic's address is: %s" % (i, id(dic)))


if __name__ == '__main__':
    dic = Manager().dict()  # 同样，Manager 需要作为参数传入子进程
    for i in range(2):
        t = Process(target=task, args=(i, dic,))
        t.start()
        t.join()
    print(dic)
# 输出：  
# In process 0, the dic's address is: 2803704884720
# In process 1, the dic's address is: 2914245176816
# {0: 0, 1: 1}
```

### Queue  
Queue 队列类似于管道的概念，多个进程可以同时往里面放数据和取数据：  
```python{12-18}
import os
import multiprocessing as mp
from multiprocessing import Process, Queue,queues


def task(i, q: Queue):
    res = q.get(block=True, timeout=3)
    print("In process %s, get: %s" % (i, res))


if __name__ == '__main__':
    q = Queue(maxsize=5)  # 同样，Queue 需要作为参数传入子进程
    # # 等价于     
    # q = queues.Queue(maxsize=5, ctx=mp.get_context())
    # # 关于队列上下文的问题，参考：
    # # 1. https://stackoverflow.com/a/24941654/14791867  
    # # 2. https://docs.python.org/3.4/library/multiprocessing.html#contexts-and-start-methods
    # # 简单理解就是要告诉multiprocessing 通过哪种方法创建子进程  

    q.put(5)
    for i in range(2):
        t = Process(target=task, args=(i, q,))
        t.start()
        # t.join()
    sleep(0.5)
    q.put(6)
    print("233")


# 输出：
# In process 1, get: 5
# 233
# In process 0, get: 6 
```

可以看到多个进程排队从一个队列里面取数据，取出以后再放进去一个给其他进程用。如果进程`get` 不到数据，则会一直等待。而且进程获取数据的顺序也是随机的。  

### Pipe 管道  
对于两个进程间的通信来说，我们更常用管道来作为载体，使用完后注意关闭管道：  
```python{10,15-16,24}
from multiprocessing.connection import _ConnectionBase
from multiprocessing import Pipe, Process
from time import sleep


def task(i, cEnd:_ConnectionBase):
    res = cEnd.recv()
    print("In process %s, get: %s" % (i, res))
    cEnd.send("pong")
    cEnd.close()



if __name__ == '__main__':
    (pEnd, cEnd) =Pipe(duplex=True)  # 同样，Pipe 需要作为参数传入子进程
    # 如果duplex=False，则pEnd 只能接收，cEnd 只能发送
    pEnd.send("ping")
    t = Process(target=task, args=(1, cEnd,))
    t.start()
    
    print("In main process, get: %s" % (pEnd.recv()))
    print("233")
    sleep(0.5)
    pEnd.close()

# 输出：  
# In process 1, get: ping
# In main process, get: pong
# 233
```

## 进程锁  
同多线程一样，进程间为了避免数据竞争或者脏数据的问题，页需要通过进程锁来保持数据同步：  
```python{9,13}
# 以下代码摘自：https://www.liujiangblog.com/course/python/82  

from multiprocessing import Process
from multiprocessing import Array
from multiprocessing import RLock, Lock, Event, Condition, Semaphore
import time

def func(i,lis,lc):
    lc.acquire()
    lis[0] = lis[0] - 1
    time.sleep(1)
    print('say hi', lis[0])
    lc.release()

if __name__ == "__main__":
    array = Array('i', 1)
    array[0] = 10
    lock = RLock()
    for i in range(10):
        p = Process(target=func, args=(i, array, lock))
        p.start()

# 输出：
# say hi 9
# say hi 8
# say hi 7
# say hi 6
# say hi 5
# say hi 4
# say hi 3
# say hi 2
# say hi 1
# say hi 0        
```

## 进程池  
创建进程的开销很大，如果需要同时启动很多进程，可以考虑使用进程池：  
```python{11-17}  
from multiprocessing import Pool
from time import sleep


def task(i):
    print("In process %s, sleep: %ss" % (i, 7-i))
    sleep(7-i)


if __name__ == '__main__':
    p = Pool(5)     # 创建一个包含5个进程的进程池
    for i in range(7):
        p.apply_async(func=task, args=(i,))  # 异步执行，并行
        # p.apply(func=task, args=(i,))  # 同步执行，串行
    p.close()  # 等所有进程结束后关闭进程池
    # p.terminate() # 立即关闭进程池
    p.join()  # 主进程等待进程池关闭后才退出

# 输出：
# In process 0, sleep: 7s
# In process 1, sleep: 6s
# In process 2, sleep: 5s
# In process 3, sleep: 4s
# In process 4, sleep: 3s
# In process 5, sleep: 2s
# In process 6, sleep: 1s
```

以上便是多进程同步的所有内容了，就自己的使用经验来看：应当尽量选择管道、队列，其次在选择进程锁、共享数据，一是写起来简单、再者不容易出错。  

## 参考资料  
1. [多进程-廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1017628290184064)
2. [多进程multiprocess](https://www.liujiangblog.com/course/python/82)
3. [多进程(Multiprocessing) | 莫烦Python](https://mofanpy.com/tutorials/python-basic/multiprocessing/)  
4. 🌟[Python3的multiprocessing多进程-Queue、Pipe进程间通信](https://www.cnblogs.com/lizm166/p/14658360.html)
