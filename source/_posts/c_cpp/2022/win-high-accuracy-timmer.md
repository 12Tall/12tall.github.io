---
title: Windows 平台上的高精度定时器  
date: 2022-08-03
tags:   
    - win32  
    - c/cpp  
    - timer   
---  


> 因为使用Python 开发信号发生器需要一个精度较高的定时器，而Python 自带的`time.sleep` 函数的最小精度为1ms，且不太稳定。于是有了这篇笔记。  
<!-- more -->
## Python 中sleep 的精度问题  
虽然理论上Python 中的`sleep`  函数的精度是1ms，但实际使用中，不同平台上的误差最多可以到20ms，详情请参见：[About accuracy of time.sleep](https://stackoverflow.com/a/58553204/14791867)  
 
## 通过Win32 API 实现  
既然单靠Python 无法实现，那我们就去看一下能否依赖操作系统实现。于是找到了这篇文章[Windows实现高精度定时器的三种方法](https://blog.51cto.com/wangningyu/3248216)。文章介绍了分别使用`CreateWaitableTimer`、``、`` 来实现任务定时执行的。下面是代码分析：  

### CreateWaitableTimer  
`CreateWaitableTimer` 的精度为100ns，并且使用方法比较简单：创建定时器、设置等待时间、等待。
```c 
#include <windows.h>
#include <stdio.h>

int main()
{
    HANDLE hTimer = NULL;
    LARGE_INTEGER liDueTime;

    liDueTime.QuadPart = -100000000LL;

    // Create an unnamed waitable timer.
    hTimer = CreateWaitableTimer(NULL, TRUE, NULL);
    if (NULL == hTimer)
    {
        printf("CreateWaitableTimer failed (%d)\n", GetLastError());
        return 1;
    }

    printf("Waiting for 10 seconds...\n");

    // Set a timer to wait for 10 seconds.
    if (!SetWaitableTimer(hTimer, &liDueTime, 0, NULL, NULL, 0))
    {
        printf("SetWaitableTimer failed (%d)\n", GetLastError());
        return 2;
    }

    // Wait for the timer.
    if (WaitForSingleObject(hTimer, INFINITE) != WAIT_OBJECT_0)
        printf("WaitForSingleObject failed (%d)\n", GetLastError());
    else printf("Timer was signaled.\n");

    return 0;
}
```  

### QueryPerformanceFrequency 
此方法可以实现微秒级延时，但是代码看起来要复杂一点：  
```c  
void MSleep(long lTime)
{
	LARGE_INTEGER litmp;   // （大）整型时间戳
	LONGLONG QPart1,QPart2;  // 
	double dfMinus, dfFreq, dfTim, dfSpec; 
	QueryPerformanceFrequency(&litmp);  // 初始化
	dfFreq = (double)litmp.QuadPart;    // 获取计数频率
	QueryPerformanceCounter(&litmp);    // 初始化计数器
	QPart1 = litmp.QuadPart;            // 起始时间（计数）
	dfSpec = 0.000001*lTime;            // 毫秒数
		
	do
	{
		QueryPerformanceCounter(&litmp); // 获取当前计数
		QPart2 = litmp.QuadPart;         // 获取当前计数值
		dfMinus = (double)(QPart2-QPart1); // 获取与起始计数的数量差
		dfTim = dfMinus / dfFreq;        // 根据频率计算时间差
	}while(dfTim<dfSpec);                // 如果超过时间则退出循环
}
// -----------------------------------
// 代码摘自：https://blog.51cto.com/wangningyu/3248216
```

### timeSetEvent  
`timeSetEvent` 可以实现毫秒级的定时，而且是通过回调函数的形式执行：  
```c 
MMRESULT timeSetEvent（ UINT uDelay,   // 时间间隔
                        UINT uResolution, // 分辨率毫秒数，默认是1ms，为0 的话则分辨率会尽量小
                        LPTIMECALLBACK lpTimeProc, // 用户回调函数
                        WORD dwUser, // 用户提供的回调数据，会被传入到回调函数
                        UINT fuEvent  // 定时器类型：TIME_ONESHOT 一次性；TIME_PERIODIC 周期性
                    ）// 返回定时器Id
```  
- `timeSetEvent` 的最长时间不能超过1000 秒  
- `timeSetEvent` 会创建一个独立的线程  
- 可以通过`timeKillEvent` 根据Id 关闭定时器  

## Python 实现  
Python 中有对`timeSetEvent` 的封装，通过测试，误差可以稳定小于1ms，如果要求误差总是小于5%，则要求触发间隔不能小于20ms。详见：[How to implement high speed, consistent sampling?](https://stackoverflow.com/a/16315086/14791867)。比较遗憾的是原生不支持中间暂停 :(  

如果需要更高精度的延时,我们只能调用`QueryPerformanceFrequency`:  
```python
import ctypes


def getHPET():
    """
    BOOL QueryPerformanceFrequency(LARGE_INTEGER *lpFrequency);
    作用：返回硬件支持的高精度计数器的频率。
    返回值：非零，硬件支持高精度计数器；零。硬件不支持。读取失败。
    🍭系统上电后便不会变化:测试机器中的值为10,000,000🍭
    """
    freq = ctypes.c_longlong(0)
    ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
    return freq


def getCounter():
    counter = ctypes.c_longlong(0)
    ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter))
    return counter


for i in range(100):
    a = getCounter().value  # \
    freq = getHPET().value  # | 这段代码能稳定运行在2us 以内, 
    res = 1.*(a-i)/freq     # | 基本上我们可以10us 循环检测一下计数器来实现延时
    b = getCounter().value  # /
    res = 1.*(b-a)/freq
    print(b - a, res)
```  

也可以封装成一个专门的函数:  
```python
"""
此函数大部分时间运行是正确的,但在运行时间分析时偶尔会出现大的离谱的间隔,比如设置的延时是0.1ms,而运行时间分析显示花了23.7ms.
感觉问题出在Python 解释器或者是timeit 性能测试的代码上了应该:(  
将异常的数据(大于给定值50%)手动剔除后,循环调用该函数时平均需要2.5ns 左右的执行时间,保证100ns 的延时精度应该没有问题
"""
def msleep(ms):
    counter = ctypes.c_longlong(int(((ms-0.0025)*freq)/1000))
    start = getCounter()
    while True:
        if (getCounter().value - start.value) > counter.value:
            break
```


## 参考资料  
1. [About accuracy of time.sleep](https://stackoverflow.com/a/58553204/14791867)  
2. [C的定时器timeSetEvent使用](https://www.cnblogs.com/shikamaru/p/7656532.html)  
3. [How to implement high speed, consistent sampling?](https://stackoverflow.com/a/16315086/14791867)  
4. [Windows微秒级定时方法](https://blog.csdn.net/a29562268/article/details/68955533)