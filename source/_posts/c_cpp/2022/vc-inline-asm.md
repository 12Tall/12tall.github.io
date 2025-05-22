---
title: C 语言内联汇编    
date: 2022-08-03    
tag:   
    - c
    - cpp 
    - asm
---  


虽然C++ 是C 语言的超集，但是二者并不能做到无缝衔接。这里记一下C 和C++是如何以静态链接库的形式调用彼此的。 
<!-- more -->
<CodeGroup>
<CodeGroupItem title="C++ 调用C">  

```c++{13}
// + folder
//     + c_code.c  
//     + cpp_code.cpp  
//     + makefile

/***** c_code.c *****/
int add(int a, int b){
    return a + b;
}

/***** cpp_code.cpp *****/
#include <iostream>
extern "C" int add(int a, int b);

int main(){
    std::cout << add(1, 2) << std::endl;
    return 0;
}

/** makefile
 * build_c: c_code.c  
 *     gcc -c c_code.c 
 * build_cpp: build_c cpp_code.cpp
 *     g++ cpp_code.cpp c_code.o
 */
```
</CodeGroupItem>
<CodeGroupItem title="C 调用C++">

```c++{16}
// + folder
//     + c_code.c  
//     + cpp_code.cpp  
//     + makefile

/***** c_code.c *****/
#include <stdio.h>
int sub(int, int);

int main(){
    printf("%d\n", sub(1, 2));
    return 0;
}

/***** cpp_code.cpp *****/
extern "C" int sub(int a, int b){
    return a - b;
}

/** makefile
 * build_c: build_cpp c_code.c  
 *     gcc c_code.c  *.o
 * build_cpp:  build_c cpp_code.cpp
 *     g++ -c cpp_code.cpp 
 */
```
</CodeGroupItem>
</CodeGroup>

### C 语言调用C++ 的成员函数 
因为C 语言没有对象的概念，所有成员函数都需要写成method(Obj *, int param) 这种形式才行。所以，如果想在C 语言中调用C++ 中的成员函数，则需要提供（手写）一个wrapper，将其转化为C 风格。  
<CodeGroup>
<CodeGroupItem title="C 代码">  

```c++{7}
#include <stdio.h>

void *Create(int);
int GetAge(void *stu);

int main(){
    void *stu = Create(13);
    printf("%d\n", GetAge(stu));
    return 0;
}
```
</CodeGroupItem>
<CodeGroupItem title="C++ 类">

```c++{17-23}
// cpp_code.cpp
#include <iostream>
using namespace std;

class Student{
public:
    int _age;
    Student(int age);
    ~Student();
};

Student::Student(int age){
    this->_age = age;
    cout << "age: " << age << endl;
}

extern "C" void *Create(int age){
    return new Student(age);
}

extern "C" int GetAge(void *stu){
    return ((Student *)stu)->_age;
}

```
</CodeGroupItem>

<CodeGroupItem title="makefile">  

```makefile
build_cpp: cpp_code.cpp  
	g++ -c cpp_code.cpp  

# 在编译C++ 类的时候需要添加 -lstdc++ 标记  
# 否则gcc 不能识别C++ 的语法
build_c: build_cpp c_code.c  
	gcc c_code.c  *.o -lstdc++
```
</CodeGroupItem>
</CodeGroup>

### 函数的重载  
重载函数同成员函数没有区别，只是需要额外的字符来区分返回值或者参数，一般会用宏命令来自动生成，不多赘述。  

## C 语言调用Go  
在很多专业软件里面会提供C/C++，的接口，但是C 语言的内存管理操作过于复杂。于是想到是否可以通过C 做胶水语言，实际上调用golang 来完成任务。不过golang 导出到C 的数据，也是需要手工回收的，但是只需对接口交换的数据处理一次就够了。  

### 准备工作  
安装Golang、MinGW，这里要注意的是**Golang 与MinGW 的位宽一定要是一致的，否则在编译时会出错**。因为主要是采用动态链接库的形式来调用Go 函数。本文选择的都是64 位的程序。  

#### 变量类型  
通过引入`C` 包，可以使用C 兼容的变量类型。  
| C                      | Golang         | 宽度             |
| ---------------------- | -------------- | ---------------- |
| char                   | C.char         | byte             |
| signed char            | C.schar        | int8             |
| unsigned char          | C.uchar        | uint8            |
| short int              | C.short        | int16            |
| short unsigned int     | C.ushort       | uint16           |
| int                    | C.int          | int              |
| unsigned int           | C.uint         | uint32           |
| long int               | C.long         | int32 or int64   |
| long unsigned int      | C.ulong        | uint32 or uint64 |
| long long int          | C.longlong     | int64            |
| long long unsigned int | C.ulonglong    | uint64           |
| float                  | C.float        | float32          |
| double                 | C.double       | float64          |
| wchar_t                | C.wchar_t      |                  |
| void *                 | unsafe.Pointer |                  |  

在使用时注意内存的释放:  
```go
cs := C.CString("PN")
// ...
C.free(unsafe.Pointer(cs))
```  

### 示例代码  
示例包含两个文件：trj.go 和main.c。
需要注意的是，golang 中需要有特殊的注释来声明导出函数。  

<CodeGroup>
<CodeGroupItem title="trj.go">  

```go{13}
package main

import "C"
// 添加C 库的支持，用于类型转换
// 使用C.free 时，必须按照上面格式引入C 语言的头文件。

import (
	"fmt"
	"unsafe"
)

// 下面的注释是必须的，声明该函数会被导出
// export 前后分别必须只有0 个和1 个空格

//export PrintBye
func PrintBye() {
	fmt.Println("bye")
}

//export Sum
func Sum(a C.int, b C.int) C.int {
	return a + b
}

//export GetStr
func GetStr() *C.char {
	var a = "1"
	var b = "2"
	return C.CString(a + b)
}

//export FreeStr
func FreeStr(str unsafe.Pointer) {
	C.free(str)
}

func main() {
    // main 方法是必须的
}
```
</CodeGroupItem>
<CodeGroupItem title="main.c">

```c++
#include <windows.h>
#include <stdio.h>

typedef void (*LPPrintBye)();
typedef int (*Sum)(int, int);
typedef char *(*GetStr)();
typedef void (*FreeStr)(void *);

int main()
{
    HMODULE hTrj = LoadLibrary("trj.dll");
    printf("dll addr: %p\n", hTrj);
    LPPrintBye printBye = (LPPrintBye)GetProcAddress(hTrj, "PrintBye");
    Sum sum = (Sum)GetProcAddress(hTrj, "Sum");
    printf("Sum addr: %p\n", sum);
    printf("1+2 = %d\n", sum(1, 2));
    GetStr getStr = (GetStr)GetProcAddress(hTrj, "GetStr");
    printf("GetStr addr: %p\n", getStr);
    char *str = getStr();
    printf("str = %p\n", str);
    printf("str addr: %s\n", str);

    FreeStr freeStr = (FreeStr)GetProcAddress(hTrj, "FreeStr");
    printf("FreeStr addr: %p\n", freeStr);
    freeStr(str);
    
    // 注意这里字符串已经被回收了，但是指针的指向还没变
    printf("----- free str -----\n");
    printf("str = %p\n", str);
    printf("str addr: %s\n", str);
    str = NULL; // 指针指向安全位置

    printBye();
    FreeLibrary(hTrj);
    return 0;
}
```
</CodeGroupItem>

<CodeGroupItem title="编译执行">  

```bash
# 编译命令很简单，编译后会产生.dll 和.h 两个文件
go build -ldflags "-s -w" -buildmode=c-shared -o trj.dll trj.go  
# -s, -w 用于减小动态链接库的体积  
# -s 压缩  
# -w 去掉调试信息  

# 但是一般用更简单的命令 
go build -buildmode=c-shared -o trj.dll trj.go

# 当然，也可以生成静态链接库文件  
go build -buildmode=c-archive trj.go    
# 此命令会生成`.a` 和`.h` 文件

gcc .\main.c  
.\a.exe # 即可看到执行的结果  
```
</CodeGroupItem>
</CodeGroup>


## VC 内联汇编  
在Windows 下开发[N-API](./n-api.md)插件时，有时候会遇到回调函数的问题。WIN32 的API 给约定好了回调函数传递的参数类型和数量。如果我们需要添加额外的参数时，应该怎么办呢？  
```js
// 为方便理解，以JS 代替C 来做说明  
BOOL EnumWindows(
  WNDENUMPROC lpEnumFunc,  // 回调函数lpEnumFunc 接受两个参数
  // BOOL CALLBACK EnumWindowsProc(_In_ HWND hwnd, _In_ LPARAM lParam);
  LPARAM      lParam
);


// 下面是JS 演示的闭包的用法  
function closure(int a){
    // 返回一个函数
    return (_In_ HWND hwnd, _In_ LPARAM lParam)=>{
        a = 1;
        // 函数内部可以访问外层函数的局部变量
    }
}

EnumWindows(closure(1),0);  // 传递生成的回调函数
```

可惜的是，这种混合风格的代码在C 语言中并未得到支持。而网络上比较流行的关于C 语言实现闭包的方法是通过[libffi](https://github.com/libffi/libffi) 来实现，本质上是通过汇编语言，按照不同平台下的函数调用约定来动态构造函数。在谷歌了许久之后，发现网络上并没有很易懂的原理说明，遂放弃继续研究，因为看别人写的源码实在是太麻烦了，尤其是汇编语言。不得不说，汇编似乎是唯一的选择，而我们知道许多C 编译器都支持内联汇编，那我们能不能通过内联汇编来实现我们的需求呢？  

### 函数调用约定  
函数的调用约定主要是函数参数传递的约定，例如在x86 VC中，函数传递参数的方式如下：  
```c
// 代码取自官方文档：
// https://docs.microsoft.com/zh-cn/cpp/assembler/inline/calling-c-functions-in-inline-assembly?view=msvc-160
// InlineAssembler_Calling_C_Functions_in_Inline_Assembly.cpp
// processor: x86
#include <stdio.h>

char format[] = "%s %s\n";
char hello[] = "Hello";
char world[] = "world";
int main( void )
{
    // printf( format, hello, world );
   __asm
   {
      mov  eax, offset world  // 参数从右至左依次压栈
      push eax
      mov  eax, offset hello
      push eax
      mov  eax, offset format
      push eax
      call printf            // 调用函数
      //clean up the stack so that main can exit cleanly
      //use the unused register ebx to do the cleanup
                             // 函数调用之后参数出栈，使得堆栈平衡
      pop  ebx
      pop  ebx
      pop  ebx
   }
}
```

那我们很容易想到，在调用函数之前，我们提前将某些参数放入堆栈，然后再在函数体中取得这些参数，不就可以不受函数签名的限制了嘛？事实证明，这么做是可行的，只是稍微有些麻烦。  

### 简易实现  
为了减少其他因素的影响，这里推荐使用VS 来开发调试，因为VS 调试时支持查看汇编代码，这样会方便不少，而且不需要配置编译器环境等信息。  
```c
#include<stdio.h>

int add(int a) {
	__asm {
	    int val = 0;
        // 3. 在汇编语言中获取参数，可以直接将形参名当作地址用
        // 函数内部的局部变量应该都可以通过这种方式获取
		mov eax, dword ptr[a + 0x04];  // 4. 取得我们手动压入的参数
                                       // 这里有意思的一点就是，我们手动压入的参数地址都大于第一个形参
		mov dword ptr[val], eax;       // 5. 因为内存间不能直接赋值，我们采用eax 作为中转
                                       // 不用担心eax 受到污染，因为我们的代码是在函数最前面的
	}
	// 似乎只要变量未使用，就不会提前占用寄存器
	return a + val;
}

int main(void) {
	int i = 5;
	__asm push dword ptr[i];  // 1. 手动压入参数
	int a = add(3);           // 2. 调用函数
	__asm add esp, 0x04;      // 6. 平衡堆栈，即恢复原先的栈顶指针，也可以用pop 指令
	return a;                 // 7. 这里a 等于8，验证我们的想法是正确的
}

// y由上述代码，也可以看出，VC 内联汇编主要有两种方式：  
// 1. __asm 单条汇编指令  
// 2. __asm{ 汇编代码块 }  
// 而在汇编语言中要取得C 代码中的变量，也是非常简单，dword ptr[a] 就可以得到数值了   
// 需要注意的是，针对不同的目标平台，有不同的调用约定，这里只针对于x86 Windows
```

## Mingw 相关  
### 开发dll  
在mingw 下生成dll 文件很简单。  

<CodeGroup>
<CodeGroupItem title="开发">  

```c++
// my_dll.c  
#include<windows.h>
#include<stdio.h>

int add(int a, int b){
    return a+b;
}  

// dll 入口函数
BOOL APIENTRY DllMain( 
    HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved)
{
    printf("my_dll is loaded\n");
    return TRUE;
}
// 执行`gcc ./my_dll.c -shared -o my_dll.dll`，
// 将会在当前目录生成生成`my_dll.dll`。  
```  
</CodeGroupItem>
<CodeGroupItem title="调用">

```c++{16}
#include <windows.h>
#include<stdio.h>

typedef int (*Add)(int ,int);  // 定义函数指针类型

int main(void){
    HMODULE hDll = LoadLibrary("my_dll.dll");
    if (hDll != NULL){
        // 从my_dll.dll 中取得函数  
        Add add = (Add)GetProcAddress(hDll, "add");  

        if (add != NULL){  // 执行函数
            printf("a+b=%d\n",add(a,b));  
        }

        FreeLibrary(hDll);  // 释放my_dll.dll
    }
}
```
</CodeGroupItem>
<CodeGroupItem title="入口函数">

```c++{16}
BOOL APIENTRY DllMain( 
    HMODULE hModule,  // 指向dll 本身的句柄
    DWORD  ul_reason_for_call,  // 被调用的原因(触发事件)
    LPVOID lpReserved  // 保留参数，无意义  
    )
{
    // DWORD  ul_reason_for_call
    switch(ul_reason_for_call){
        case DLL_PROCESS_ATTACH: break;  // dll 第一次被进程加载
        case DLL_PROCESS_DETACH: break;  // 释放dll 
        case DLL_THREAD_ATTACH: break;   // 当进程创建线程时
        case DLL_THREAD_DETACH: break;   // 当进程销毁线程时
    }
    return TRUE;
}
```
</CodeGroupItem>
</CodeGroup>




## 参考阅读  
### C-Cpp 相关
1. [Bjarne Stroustrup's C++ Style and Technique FAQ](https://stroustrup.com/bs_faq2.html#callCpp)  
2. [gcc compiling C++ code: undefined reference to 'operator new...'](https://stackoverflow.com/questions/27390078/gcc-compiling-c-code-undefined-reference-to-operator-newunsigned-long-lon)  

### Go 相关  
1. [Go和C类型对应关系](https://studygolang.com/articles/6798)  
2. [golang之cgo一---go与C基本类型转换](https://www.cnblogs.com/adjk/p/9469845.html)  
3. [golang C.CString 必须Free](https://my.oschina.net/u/1431106/blog/188646?p=%7B%7BcurrentPage-1%7D%7D)  
4. [Golang编写Windows动态链接库(DLL)及C调用范例](https://www.cnblogs.com/Kingram/p/12088087.html) 
5. [golang —— 语言交互性](https://www.cnblogs.com/zhance/p/10135142.html)  

### VC 内联汇编
1. [Can anyone help me interpret this simple disassembly from WinDbg?](https://stackoverflow.com/questions/4024492/can-anyone-help-me-interpret-this-simple-disassembly-from-windbg)