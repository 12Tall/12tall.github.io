---
title: DLL 注入相关  
date: 2022-08-03
tags:   
    - win32  
    - c/cpp  
    - 远程线程  
    - 注入    
---  

## 远程线程注入  
文中代码多摘自[Win32创建远程线程](https://www.cnblogs.com/DarkBright/p/10820582.html)，仅作部分注释  
<!-- more -->
<CodeGroup>
<CodeGroupItem title="宿主程序">

```c++
#include <windows.h>
#include <stdio.h>

void Fun(void)
{
    for(size_t i = 0; i < 10; i++){
        // 打印函数地址
        // __FUNCTION__: 获取函数名
        // __FILE__: 获取文件名
        // __LINE__: 获取行号
        printf("%s addr:0x%p\r\n", __FUNCTION__, Fun);
    }         
}

int main(int argc, char* argv[])
{
    Fun();
    //MessageBox(NULL, TEXT("执行完成!"), TEXT("提示"), MB_OK);

    getchar();  // 暂停
    return 0;
}
```

</CodeGroupItem>


<CodeGroupItem title="测试远程线程">  

```c++
#include <windows.h>
#include <stdio.h>

// 宿主进程中打印的函数地址
#define FUN_ADDR 0x0000000000401550

DWORD getPid(LPTSTR name);
int main(int argc, char *argv[])
{

    HANDLE hProcess = 0;
    HANDLE hThread;
    DWORD dwThread = 0;

    // 打开进程，第三个参数是进程目标进程ID
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, 8684);

    if (hProcess == NULL)
    {
        printf("can not open process");
        return -1;
    }

    // 开启远程线程
    hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)FUN_ADDR, NULL, 0, &dwThread);  
    /**
    * hProcess：目标进程的句柄
    * lpThreadAttributes：安全描述符的结构体指针，填 NULL 即可
    * dwStackSize：要创建的远程线程的堆栈大小，一般填 0 使用默认大小
    * lpStartAddress：远程线程的执行体，也就是创建的线程要执行的过程函数
    * lpParameter：远程线程执行体的参数，与lpStartAddress 配合使用
    * dwCreationFlags：创建标志，一般填0
    * lpThreadId：线程ID的指针，用于接收远程线程创建成功后的ID
    */

    if (hThread == NULL)
    {
        printf("can not create remote thread");
        return -1;
    }

    CloseHandle(hProcess);
    CloseHandle(hThread);
    return 0;
}
```
</CodeGroupItem>

<CodeGroupItem title="寄生程序">  

```c++
#include <windows.h>
#include <stdio.h>

void func1()
{
    // 输出函数名及其地址
    printf("%s addr:0x%p\n", __FUNCTION__, func1);
}

BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        MessageBox(NULL, TEXT("DLL inject successfully"), TEXT("Warning:"), MB_OK);
        func1();
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
// 执行 gcc .\mydll.c -shared -o mydll.dll 以生成动态链接库  
```

</CodeGroupItem>
<CodeGroupItem title="注入器">

```c++
#include <windows.h>
#include <stdio.h>

// 进程id  
#define Pid 26036
// dll 可以用绝对路径，也可以用相对路径  
// 但最好还是用绝对路径
#define DLL_NAME "mydll.dll"

int main(int argc, char *argv[])
{
    HANDLE hProcess = 0;
    HANDLE hThread;
    DWORD dwThread = 0;

    // 打开进程  
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, Pid);
    if (hProcess == NULL)
    {
        printf("can not open process");
        return -1;
    }

    // 在进程内存入dll 路径字符串  
    // 即将`my_dll.dll` 字符串保存至进程空间
    PVOID pDllName = VirtualAllocEx(hProcess, NULL, strlen(DLL_NAME) + 1, MEM_COMMIT, PAGE_READWRITE);
    if (pDllName == NULL)
    {
        printf("can not allocate memory for dll");
        return -1;
    }
    // 写入dll 名称
    SIZE_T lenDll = 0;
    WriteProcessMemory(hProcess, pDllName, (BYTE *)DLL_NAME, strlen(DLL_NAME) + 1, &lenDll);
    
    // 获取Kernal32.dll 中的`LoadLibraryA` 方法
    HMODULE hModule = GetModuleHandle(TEXT("Kernel32.dll"));
    if (hModule == NULL)
    {
        printf("can not get ");
        return -1;
    }
    FARPROC func1 = GetProcAddress(hModule, "LoadLibraryA");
    
    // 在开启远程线程时，执行LoadLibraryA，加载my_dll.dll
    hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)func1, pDllName, 0, &dwThread);
    if (hThread == NULL)
    {
        printf("can not create remote thread");
        return -1;
    }

    CloseHandle(hProcess);
    CloseHandle(hThread);
    return 0;
}
```

</CodeGroupItem>
<CodeGroupItem title="根据进程名获取PID">

```c++
#include <Windows.h>
#include <stdio.h>
#include <TlHelp32.h>

DWORD GetPid(const char *strProcessName);

int main()
{
    GetPid("host.exe");
    return 0;
}

DWORD GetPid(const char *strProcessName)
{
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE)
    {
        printf("CreateToolhelp32Snapshot 调用失败.\n");
        return -1;
    }

    BOOL bMore = Process32First(hProcessSnap, &pe32);

    while (bMore)
    {
        // 打印所有进程信息
        // printf("Process Name: %s\n", pe32.szExeFile); 
        // printf("Process Id: %u\n\n", pe32.th32ProcessID);
        if (lstrcmp(pe32.szExeFile, strProcessName) == 0)
        {
            break;
        }

        bMore = Process32Next(hProcessSnap, &pe32);
    }
    CloseHandle(hProcessSnap);

    return pe32.th32ProcessID;
}
```

</CodeGroupItem>
</CodeGroup>

### 注意事项  
1. 对于32 位的目标进程，应当将源码编译为32 位的可执行程序然后注入。否则不会有任何结果；  
2. 对于MinGW 来说，仅支持32 位gcc；而Mingw64 仅支持64 位。虽然可以通过-m[32|64] 指定编译时的目标架构，但是会报异常。    

## C 语言调用Go 生成的DLL  
事情的起因是~~我想学黑~~，最近在看dll 远程线程注入的文章。迫于C/C++ 写起来太过繁琐，就想着能不能通过C 调用golang 编译的dll，进而将C 作为胶水语言使用。于是就有了本文。  
目标：在`notepad.exe` 上启动一个简单的http 服务。  
环境：`Win10 Pro 64 位`、`MinGW-w64`、`golang 15.6`

因为直接从头到尾开发的话，可能会让人看得一头雾水，我准备先从较小的模块开始写起。这也是一次完整的实践流程。  

### golang 编写http 服务  
代码参考自简书[go实现简单的http服务](https://www.jianshu.com/p/8f208a6596f7)，这里稍作修改：  
```go{19-29}  
// http.go
package main

import "C"
import (
	"fmt"
	"net/http"
)

// http 请求处理函数
func sayHello(w http.ResponseWriter, r *http.Request) {
	_, _ = w.Write([]byte("Hello World!"))
}

// 导出函数。在编译成DLL 后可被调用者发现  
// 下面的注释必须有 //export 函数名  
// 其中导出函数名最好与原函数名保持一致 

//export StartHttp
func StartHttp() {
	http.HandleFunc("/", sayHello)

	err := http.ListenAndServe("127.0.0.1:9999", nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Listening: http://127.0.0.1:9000")
}

func main() {
    // StartHttp();  // 调试时取消这一行的注释  
    // 编译时main 函数最好为空
}
```  
通过以下命令进行调试：  
```bash
# 注意调试时需要取消掉main 方法里面的注释
go run .\http.go  # 如果不出意外，访问`http://localhost:9999` 就能看到`Hello World!` 了  

# 编译  
go build -buildmode=c-shared -o http.dll .\http.go
```
编译好后待用。  

### c 编写dll  
如果我们需要从远程线程注入上面的`http.dll` 是不行的，因为它没有显式的入口函数。需要用C/C++ 开发一个带入口函数的`loader.dll` 来包装一下。注入`loader.dll`，在`loader.dll` 初始化的过程中，加载并获取`http.dll` 内`StartHttp()` 函数的地址。注意，只获取地址就行了，不要执行，因为一旦执行就会引发程序死锁。这是本文的重点一。  

#### dll 参数传递  
因为加载dll 时不能传入参数，所以我们需要在`loader.dll` 中开辟一块共享内存来存放从`http.dll` 获取到的`StartHttp()` 函数的句柄（可以理解为指针）。为什么要用共享内存，因为同一个dll 加载到不同的进程中的地址可能也是不一样的。这也是本文的重点二。  

```c++{4-13,47-51}
#include <windows.h>
#include <stdio.h>

// 开辟共享内存的宏命令
#ifdef __GNUC__
HANDLE k __attribute__((section(".shared"), shared)) = NULL;
#endif
#ifdef _MSC_VER
#pragma data_seg(".shared")
HANDLE k = NULL;
#pragma data_seg()
#pragma comment(linker, "/section:.shared,RWS")
#endif

typedef void (*StartHttp)();  // 函数类型定义

HMODULE hHttp = NULL;  // 用来存放http.dll 句柄

BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        // 简化了一些一场判断
        hHttp = LoadLibrary("http.dll");
        StartHttp startWorker = (StartHttp)GetProcAddress(hHttp, "StartHttp");
        k = startWorker;  // 将http.dll 中的StartHttp() 的句柄（指针）放入共享内存
        break;
    }

    case DLL_PROCESS_DETACH:
    {
        FreeLibrary(hHttp);  // 进程结束时释放http.dll
        break;
    }
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    default:
        break;
    }
    return TRUE;
}

// 导出函数，用于调用者获取共享内存中的变量
HANDLE GetHttpStarter()
{
    return k;
}
```

如果是直接调用`http.dll` 的话，是不需要这个C 语言中间层的。编译备用  
```bash
gcc .\loader.c -shared -o .\loader.dll
```  

### 调试  
下面是通过C 语言调用`loader.dll` 进而调用`http.dll` 的例子。
```c++{15-18}
// client.c  
#include <windows.h>
#include <stdio.h>
#include <memory.h>

typedef void (*StartHttp)();  // http.dll 中的到处方法类型
typedef HMODULE (*GetHttpStarter)();  // loader.dll 中的导出方法类型

int main()
{
    char *dllPath = "loader.dll";
    HMODULE hLoader = NULL;

    hLoader = LoadLibrary("loader.dll");
    GetHttpStarter getHttpStarter = (GetHttpStarter)GetProcAddress(hLoader, "GetHttpStarter");
    // 获取loader.dll 中的到处方法
    StartHttp startHttp = (StartHttp)getHttpStarter();
    // 获取http.dll 中的导出方法
    startHttp();  // 启动http 服务
    printf("^^\n");
    FreeLibrary(hLoader);
    return 0;
}

```  
编译，并且将`loader.dll`、`http.dll` 放在同一目录，然后执行  
```bash
gcc .\client.c -o .\client.exe  

.\client.exe 
# 正常来说，访问`http://localshost:9999` 也是能看到`Hello World!` 的
```  
### 远程线程注入
一般来说，`LoadLibrary` 函数会默认加载同目录下的dll 文件。由于我们是在目标进程中开启远程线程，那么在加载dll 文件时的默认目录就需要手工指定了，最好是绝对目录。   

::: details Client.c 
```c++{15-19,}
// client.c  
#include <windows.h>
#include <stdio.h>
#include <TlHelp32.h>
#include <string.h>

typedef void (*StartHttp)();
typedef HMODULE (*GetHttpStarter)();

DWORD GetProcIdByName(const char *sProcName);
void InjectDll(DWORD nPid, const char *sDllName);

int main(int argc, char *argv[])
{
    // 获取loader.dll 的绝对路径
    char dllPath[MAX_PATH],
        *dllName = "\\loader.dll";
    GetCurrentDirectory(MAX_PATH, dllPath);
    strncat(dllPath, dllName, strlen(dllName));

    // 获取目标进程
    char *sTarget = argv[1];
    int nPid = 0;
    if (0 == (nPid = GetProcIdByName(sTarget)))
    {
        printf("There is no process named %s\n", sTarget);
        exit(1);
    }
    // 第一次开启远程线程，注入loader.dll  
    // 自动加载http.dll  
    InjectDll(nPid, dllPath);
    
    // 客户端加载loader.dll 通过共享内存获取http.dll 中函数的实际位置
    HMODULE hLoader = LoadLibrary(dllPath);
    GetHttpStarter getHttpStarter = (GetHttpStarter)GetProcAddress(hLoader, "GetHttpStarter");
    StartHttp startHttp = (StartHttp)getHttpStarter();

    // 第二次开启远程线程  
    // 启动http 服务
    HANDLE hProcess =OpenProcess(PROCESS_ALL_ACCESS, FALSE, nPid);
    HANDLE hThread;
    DWORD dwThread = 0;
    hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)startHttp, NULL, 0, &dwThread);    
    CloseHandle(hProcess);
    CloseHandle(hThread);
    
    printf("^^\n");
    FreeLibrary(hLoader);
    return 0;
}


// 通过进程名获取进程Id
DWORD GetProcIdByName(const char *sProcName)
{
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE)
    {
        return -1;
    }

    BOOL bMore = Process32First(hProcessSnap, &pe32);

    while (bMore)
    {
        if (strcasecmp(pe32.szExeFile, sProcName) == 0)
        {
            return pe32.th32ProcessID;
        }
        bMore = Process32Next(hProcessSnap, &pe32);
    }
    CloseHandle(hProcessSnap);
    return 0;
}

// 将dll 注入目标进程
void InjectDll(DWORD nPid, const char *sDllName)
{
    HANDLE hProcess = 0;
    HANDLE hThread;
    DWORD dwThread = 0;

    hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, nPid);
    if (hProcess == NULL)
    {
        printf("open process failed\n");
        CloseHandle(hProcess);
        exit(1);
    }

    PVOID pDllName = VirtualAllocEx(hProcess, NULL, strlen(sDllName) + 1, MEM_COMMIT, PAGE_READWRITE);
    if (pDllName == NULL)
    {
        printf("allocate memory for dll failed\n");
        CloseHandle(hProcess);
        exit(1);
    }

    SIZE_T lenDll = 0;
    WriteProcessMemory(hProcess, pDllName, (BYTE *)sDllName, strlen(sDllName) + 1, &lenDll);

    // 获取Kernal32.dll 中的`LoadLibraryA` 方法
    HMODULE hModule = GetModuleHandle(TEXT("Kernel32.dll"));
    if (hModule == NULL)
    {
        printf("Load Kernel32.dll failed\n");
        CloseHandle(hProcess);
        exit(1);
    }
    FARPROC func1 = GetProcAddress(hModule, "LoadLibraryA");

    hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)func1, pDllName, 0, &dwThread);
    
    if (hThread == 0)
    {
        printf("create remote thread failed");
        CloseHandle(hProcess);
        CloseHandle(hThread);
        exit(1);
    }

    CloseHandle(hProcess);
    CloseHandle(hThread);
}
```
:::  

同时`loader.dll` 在加载`http.dll` 时也需要绝对路径。  

::: details loader.c
```c++{29-35}
#include <windows.h>
#include <stdio.h>

#ifdef __GNUC__
HANDLE k __attribute__((section(".shared"), shared)) = NULL;
#endif
#ifdef _MSC_VER
#pragma data_seg(".shared")
HANDLE k = NULL;
#pragma data_seg()
#pragma comment(linker, "/section:.shared,RWS")
#endif

typedef void (*StartHttp)();

HMODULE hHttp = NULL;
char dllPath[MAX_PATH],
    *dllName = "loader.dll",
    *workerName = "http.dll";

BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        // 获取http.dll 的绝对路径
        int nameLen = strlen(dllName) - 1;
        GetModuleFileName(hModule, dllPath, strlen(dllPath) - 1);
        int fullLen = strlen(dllPath) - 1;
        memset(dllPath + fullLen - nameLen, '\0', nameLen);
        strncat(dllPath, workerName, strlen(workerName));
        hHttp = LoadLibrary(dllPath);

        // hHttp = LoadLibrary("http.dll");
        StartHttp startWorker = (StartHttp)GetProcAddress(hHttp, "StartHttp");
        k = startWorker;
        break;
    }

    case DLL_PROCESS_DETACH:
    {
        FreeLibrary(hHttp);
        break;
    }
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    default:
        break;
    }
    return TRUE;
}

HANDLE GetHttpStarter()
{
    return k;
}
```
:::

重新编译，先启动`notepad.exe`，再执行`.\client.exe`。就能在`notepad.exe` 进程上创建一个`http` 服务，访问`http://localhost:9999/` 将会看到`Hello World!` 字样。大功告成！

本文可以说是这三天思考的成果，也可以说是这两年一直想搞定的东西（~~干坏事儿~~）。因为C 语言虽然执行效率比较高，但是开发效率却是太低了，对开发人员要求比较高。而很多专业工具只提供了C/C++（对，没有python） 的接口，如果用C 做胶水，而实际工作用其他带GC 的高级语言，则开发效率也会高不少。

## 参考链接  

1. [Win32创建远程线程](https://www.cnblogs.com/DarkBright/p/10820582.html)
2. [远程线程注入DLL](https://www.cnblogs.com/DarkBright/p/10821038.html)  
3. [Windows 获取进程ID](https://www.cnblogs.com/zhangxuechao/p/11709366.html)  

1. [Is it possible to load a go-dll in c-dll on Windows?](https://stackoverflow.com/questions/65304131/is-it-possible-to-load-a-go-dll-in-c-dll-on-windows?noredirect=1#comment115450808_65304131)
2. [Dynamic-Link Library Best Practices](https://docs.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices)
3. [Shared memory segment in a C++ Class Library (DLL) using #pragma data seg](https://forum.pellesc.de/index.php?topic=4725.0)
