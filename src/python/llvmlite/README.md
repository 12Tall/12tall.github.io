---  
title: llvmlite 学习笔记  
date: 2023-04-11
timeLine: true
sidebar: false  
icon: python
category:  
    - Python      
    - 编译原理  
tag:   
    - python    
    - llvm  
    - llvmlite  
    - clang 
---  

> 通过[µGo语言实现——从头开发一个迷你Go语言编译器](https://wa-lang.org/ugo-compiler-book/index.html) 来学习llvmlite 的使用，以及将IR 编译为可执行程序。  

## Hello World   
通过llvmlite 构建一个`hello world!` 程序，来展示代码的基本工作流程。下面是参考的C 代码：  
```c  
#include<stdio.h>  

char * fstr= "🦒 hello %s! \n\0";  

int main(){
    char * c_str = "world\0";
    printf(fstr, c_str);
    return 0;
}
```

但是要通过llvm 的IR 构建，就需要从类型声明开始、中间变量的创建与赋值都要按部就班地完成，调用`printf`的部分参考自[alendit/call_printf.py](https://gist.github.com/alendit/defe3d518cd8f3f3e28cb46708d4c9d6)：  
```python{11,28}  
from llvmlite import ir  

# 创建模块，模块名可以为空  
module = ir.Module(name="main")  

# 创建int32 类型  
i32 = ir.IntType(32)  
# 创建int8 * 指针类型  
voidptr_ty = ir.IntType(8).as_pointer()  

## 没有函数体的函数在IR 中会被写作declare
# 创建函数类型 int func(void * ...)，支持可变长参数  
printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)  
# 声明int printf(void * ...)
printf = ir.Function(module, printf_ty, name="printf")

# 注释的代码是不支持中文和emoji 的
# fmt = "hello %s!\n\0"
# c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
fmt = bytearray("🦒 hello %s! \n\0".encode('utf-8'))  # 创建一个可变字节数组对象
c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),fmt) # 根据上面的对象创建一个字符串常量
global_fmt = ir.GlobalVariable(module, c_fmt.type, name="fstr") # 创建全局变量fstr
global_fmt.linkage = 'internal'  # 链接方式  
global_fmt.global_constant = True  # 全局常量
global_fmt.initializer = c_fmt  # 通过c_fmt 初始化


# 有函数体的函数会被写作define  
# 创建函数类型int func()，无参数  
fn_ty = ir.FunctionType(i32,())  
# 创建int main() 函数
func = ir.Function(module, fn_ty, name='main')  
# 添加函数体block    
block = func.append_basic_block(name="entry")  
# 构建函数体
builder = ir.IRBuilder(block)    

## 创建函数体的局部变量  
arg = "world\0"  # 注意不要忘记\0
c_arg = ir.Constant(ir.ArrayType(ir.IntType(8), len(arg)), bytearray(arg.encode("utf8")))
# 分配空间
c_str = builder.alloca(c_arg.type)
# 赋值
builder.store(c_arg, c_str)

# 指针类型转换
fmt_arg = builder.bitcast(global_fmt, voidptr_ty)
builder.call(printf, [fmt_arg, c_str])

# 创建返回值
res = i32(0)  
# 添加返回值
builder.ret(res)  
```   

### 生成IR  
所有的代码都包含在`module` 变量中，可以将其以字符串的形式保存在文本文件中：  
```python  
with open('./a.out.ll', 'w') as f:
    f.write(str(module))
```  
生成的中间代码如下：  
```llvm{5}  
; ModuleID = "main"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

@"fstr" = internal constant [17 x i8] c"\f0\9f\a6\92 hello %s! \0a\00"
define i32 @"main"()
{
entry:
  %".2" = alloca [6 x i8]
  store [6 x i8] c"world\00", [6 x i8]* %".2"
  %".4" = bitcast [17 x i8]* @"fstr" to i8*
  %".5" = call i32 (i8*, ...) @"printf"(i8* %".4", [6 x i8]* %".2")
  ret i32 0
}
```

### 编译   
因为llvmlite 暂时还没有集成`lld` 工具，所以只能通过系统命令将生成的`.ll` 源码或者`.obj` 文件编译成可执行程序。看Github 上的[PR 898](https://github.com/numba/llvmlite/pull/898) 应该在`v4.0` 正式版就将集成`lld` 工具。  
```python  
import subprocess

p = subprocess.Popen("clang ./a.out.ll", shell=True, stdout=subprocess.PIPE)
r = p.stdout.read()
print(r)
```  

### 测试  
有以下三个命令来查看程序退出时的代码，`ipynb` 默认用的是`cmd`。  
- `*nix`：`echo $?`  
- `powershell`：`echo $LASTEXITCODE`  
- `cmd`：`echo %errorlevel%`  

```powershell  
> ./a.exe  
🦒 hello world!  
> echo $LASTEXITCODE
0

# 编译C 到ir，用于对照代码
> clang -emit-llvm -Wimplicit-function-declaration -S -c main.c -o main.ll
```  

从上面的实验结果可以得出：通过llvmlite 构建并编辑可执行程序是行得通的。但是真的要设计一门语言还要结合词法分析、语法分析、语义分析以及通过遍历AST 构建IR 的过程。此过程可以想象是比较繁琐的，通过面向对象的设计方法设计AST 节点可能能简化这一过程。但应该也不会太多。  