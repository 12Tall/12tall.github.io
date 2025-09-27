---
title: llvmlite 学习笔记（三）
date: 2025-09-27 14:18:39
tags:   
    - python    
    - llvm  
    - llvmlite 
---
本文记录函数的定义与调用
1. 函数中每一个跳转都会引入新的代码块；
2. 一个函数体中可以有很多代码块；
3. 代码块就算没有名字也会自动命名,基本不需要手动设置名字；  
4. 最好每个代码块对应一个builder,builder 用于构建具体指令代码；
5. `alloca` 声明的变量需要通过`store/load` 存取数据；
6. 如果作为返回值用的话则不使用`alloca` 更便捷一些；
7. 循环也要通过跳转实现(`branch/cbranch`)；
8. 分支语句也有`if/then,if/else` 的实现


<!-- more -->

```python
from llvmlite import ir
import ctypes

from llvmlite import binding as llvm
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
# 创建 执行引擎
target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine()
backing_mod = llvm.parse_assembly("")
engine = llvm.create_mcjit_compiler(backing_mod, target_machine)

# 创建 execution engine
target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine()
backing_mod = llvm.parse_assembly("")
engine = llvm.create_mcjit_compiler(backing_mod, target_machine)

ctx = ir.Context()
module = ir.Module("module_name",ctx)

bool_t = ir.IntType(1)  # 布尔类型用一位整数代替
# llvm 中没有单独的无符号数，符号在运算符中体现
i8_t = ir.IntType(8)
i16_t = ir.IntType(16)
i32_t = ir.IntType(32)
i64_t = ir.IntType(64)
f16_t = ir.HalfType()
f32_t = ir.FloatType()
f64_t = ir.DoubleType()

print(str(module))
```

## 定义函数  
1. 单纯声明函数类型，生成的`.ll` 代码用的关键字是`declare`  
2. 有函数体的是`define`

```c
int max(int a, int b){
    int c;  
    if(a>=b){
        c=a;
    }
    else{
        c=b;
    }
    return c;
}
```

```python
fun_max_t = ir.FunctionType(i32_t, [i32_t, i32_t])
fun_max = ir.Function(module, fun_max_t, 'max')
# 如果要设置变量名的话，需要在函数声明中实现，而不是在函数类型定义中实现
fun_max.args[0].name = "a"
fun_max.args[1].name = "b"

# 定义了，没有实现函数体，就是declare
print(str(module))
```
结果如下:  
```llvm
; ModuleID = "module_name"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"max"(i32 %"a", i32 %"b")
```
实现函数体:
```python
# 创建基本代码块标签
fun_max_entry = fun_max.append_basic_block("entry")
fun_max_a2c = fun_max.append_basic_block("a2c")
fun_max_b2c = fun_max.append_basic_block("b2c")
fun_max_ret = fun_max.append_basic_block("ret")

# 通过IRBuilder 构建对应的基本代码块
entry_builder = ir.IRBuilder(fun_max_entry)
a2c_builder = ir.IRBuilder(fun_max_a2c)
b2c_builder = ir.IRBuilder(fun_max_b2c)
ret_builder = ir.IRBuilder(fun_max_ret)

## 虽然也可以混在一起写，但是感觉提前一起定义了更清晰一些 ##

# 入口代码 
# 参数初始化，比较跳转
a,b = fun_max.args
# int c;
c = entry_builder.alloca(i32_t, name="c")
# 有符号比较
le = entry_builder.icmp_signed(">=", a,b, "le")  # 这条指令只是定义了一个临时值用于存放结果
entry_builder.cbranch(le, fun_max_a2c, fun_max_b2c)

# 赋值代码  
a2c_builder.store(a, c)  # a=c;
a2c_builder.branch(fun_max_ret)
# 如果要从指针中读取值，则用load()
b2c_builder.store(b, c)  # a=c;
b2c_builder.branch(fun_max_ret)

# 返回值
ret_builder.ret(ret_builder.load(c))

print(str(module))
```

结果如下:

```llvm
; ModuleID = "module_name"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"max"(i32 %"a", i32 %"b")
{
entry:
  %"c" = alloca i32
  %"le" = icmp sge i32 %"a", %"b"
  br i1 %"le", label %"a2c", label %"b2c"
a2c:
  store i32 %"a", i32* %"c"
  br label %"ret"
b2c:
  store i32 %"b", i32* %"c"
  br label %"ret"
ret:
  %".9" = load i32, i32* %"c"
  ret i32 %".9"
}
```

执行函数:
```python
# 编译模块
mod = llvm.parse_assembly(str(module))
mod.verify()
engine.add_module(mod)
engine.finalize_object()

# 获取max 函数指针并转成 ctypes
func_ptr = engine.get_function_address("max")
# 声明C 函数
cfunc = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_int32)(func_ptr)

print("max() result:", cfunc(10,20))  # 应该输出 20
```

## 斐波那契数列  
```c
int fib(int i){
    if(i<2){
        return i;
    }
    return fib(i-1)+fib(i-2);
}
```
定义函数  
```python
fun_fib_t = ir.FunctionType(i32_t, [i32_t,])
fun_fib = ir.Function(module, fun_fib_t, "fib")

fun_fib_entry = fun_fib.append_basic_block("entry")
builder_entry = ir.IRBuilder(fun_fib_entry)
fun_fib_less_2 = fun_fib.append_basic_block("less_2")
builder_less_2 = ir.IRBuilder(fun_fib_less_2)
fun_fib_recursion = fun_fib.append_basic_block("recursion")
builder_recursion = ir.IRBuilder(fun_fib_recursion)

(i,) = fun_fib.args
# 基本块
less_2 = builder_entry.icmp_unsigned("<", i, ir.Constant(i32_t,2))
builder_entry.cbranch(less_2, fun_fib_less_2, fun_fib_recursion)

# 小于2
builder_less_2.ret(i)

# 否则递归 
i_minus_1 = builder_recursion.sub(i, ir.Constant(i32_t, 1))
i_minus_2 = builder_recursion.sub(i, ir.Constant(i32_t, 2))
## 调用函数
fib_sub_1 = builder_recursion.call(fun_fib,[i_minus_1])
fib_sub_2 = builder_recursion.call(fun_fib, [i_minus_2])
sum = builder_recursion.add(fib_sub_1, fib_sub_2)
builder_recursion.ret(sum)
print(str(module))
```

输出结果:
```llvm
; ModuleID = "module_name"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"max"(i32 %"a", i32 %"b")
{
entry:
  %"c" = alloca i32
  %"le" = icmp sge i32 %"a", %"b"
  br i1 %"le", label %"a2c", label %"b2c"
a2c:
  store i32 %"a", i32* %"c"
  br label %"ret"
b2c:
  store i32 %"b", i32* %"c"
  br label %"ret"
ret:
  %".9" = load i32, i32* %"c"
  ret i32 %".9"
}

define i32 @"fib"(i32 %".1")
{
entry:
  %".3" = icmp ult i32 %".1", 2
  br i1 %".3", label %"less_2", label %"recursion"
less_2:
  ret i32 %".1"
recursion:
  %".6" = sub i32 %".1", 1
  %".7" = sub i32 %".1", 2
  %".8" = call i32 @"fib"(i32 %".6")
  %".9" = call i32 @"fib"(i32 %".7")
  %".10" = add i32 %".8", %".9"
  ret i32 %".10"
}
```

运行结果:
```python
mod = llvm.parse_assembly(str(module))
mod.verify()
engine.add_module(mod)
engine.finalize_object()

# 获取max 函数指针并转成 ctypes
func_ptr = engine.get_function_address("fib")
# 声明C 函数
cfunc = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32)(func_ptr)

print("fib() result:", cfunc(8))  # 应该输出 21
```