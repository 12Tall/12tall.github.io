---
title: llvmlite 学习笔记（二）
date: 2025-09-26 17:38:15
tags:   
    - python    
    - llvm  
    - llvmlite  
---

本文记录些全局变量的定义。  

<!-- more -->

在llvm C++ 版本中有以下概念：
- 上下文：公共的数据结构  
- 模块：一般源文件的抽象，包含全局变量和函数
- IRBuilder：指令生成器，一般的类型在ir 包中
- verifier：校验模块

而在llvmlite 中：
1. 默认是用一个全局context，很少显式传递ctx
2. IRBuilder 也是从基本块Block 初始化，而不是从上下文开始

```python
from llvmlite import ir

ctx = ir.Context()
module = ir.Module("module_name",ctx)
print(str(module))
```

## 定义类型  
基本类型有：整型、浮点型、结构体、向量、数组、函数以及对应的指针等。

```python
int32_t = ir.IntType(32)              # 整型：1、8、16、32、64
double_t = ir.DoubleType()            # 浮点型：FloatType、DoubleType
vector_t = ir.VectorType(int32_t, 4)    # 向量类型：<类型, 数量>
double_arr_t = ir.ArrayType(double_t, 4)# 数组类型：<类型, 数量>
# 匿名结构体  
# 结构体packed 会紧凑布局，否则会自动扩充空间，类似于自动填充空指令，默认自动填充
struct_literal_t = ir.LiteralStructType(
    [int32_t, double_t]
)
# 具名结构体，构造函数只接受一个名字
struct_id_t = ir.IdentifiedStructType(ctx,'st_name') 
struct_id_t.set_body(int32_t, double_t)

# 函数：返回值，参数列表，是否为可变参数
function_t = ir.FunctionType(double_t, [int32_t, int32_t])

# 特殊类型
void_t = ir.VoidType()   # void
label_t = ir.LabelType() # 基本块标签类型

int32_ptr = int32_t.as_pointer()
# 指针：类型.as_pointer(address_space) 默认是0，位于普通内存

print(str(module))
```

## 定义全局变(常量)量
1. `ir.Constant()` 函数常用于传递初始值  
2. 初始化要通过`initializer`

下面代码不能重复运行，因为定义的变量不会被覆盖，而llvm 同一个作用域中不能有重名变量。

```python
# int a = 1;
a = ir.GlobalVariable(module, int32_t, "a")
a.initializer = ir.Constant(int32_t, 1)

# 字符串也是以数组的形式定义的
# char[] msg = "你好世界\0";
msg = "你好世界\0".encode("utf-8")
msg_arr_t = ir.ArrayType(ir.IntType(8), len(msg))
hello = ir.GlobalVariable(module, msg_arr_t, name="msg")
hello.global_constant = True  # 全局常量 
hello.initializer = ir.Constant(msg_arr_t, bytearray(msg))

# int *p = &a;
p = ir.GlobalVariable(module, int32_ptr, "p")
p.initializer = a

"""
匿名结构体
struct_literal_t st_l = {1, 2.2};
"""
st_l = ir.GlobalVariable(module, struct_literal_t, 'st_l')
st_l.global_constant = True
st_l.initializer = ir.Constant(
    struct_literal_t,
    [ir.Constant(int32_t, 1),ir.Constant(double_t, 2.2)])
"""
具名结构体
struct_id_t st_i = {1, 2.2};
"""
st_i = ir.GlobalVariable(module, struct_id_t, "st_i")
st_i.initializer = ir.Constant(
    struct_id_t,
    [
        ir.Constant(int32_t, 1), 
        ir.Constant(double_t, 2.2)
    ]
)

print(str(module))
```
结果如下：  
```llvm
; ModuleID = "module_name"
target triple = "unknown-unknown-unknown"
target datalayout = ""

@"a" = global i32 1
@"msg" = constant [13 x i8] c"\e4\bd\a0\e5\a5\bd\e4\b8\96\e7\95\8c\00"
@"p" = global i32* @"a"
@"st_l" = constant {i32, double} {i32 1, double 0x400199999999999a}
@"st_i" = global %"st_name" {i32 3, double 0x400199999999999a}
```

总之，数据的定义要遵循下面三步：
1. 定义类型  
2. 定义变量  
3. 变量赋值
> 不要试图用`format_constant()` 取代`ir.Constant()`

## 参考资料  
1. [C语言生成LLVM IR-Bilibili](https://www.bilibili.com/video/BV1eV4y1T7H2)