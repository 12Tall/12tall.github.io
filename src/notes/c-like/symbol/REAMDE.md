---  
title: GCC 中的符号  
date: 2023-06-16
timeLine: true
sidebar: false  
icon: c
category:  
    - 笔记      
tag:   
    - c/cpp  
    - 编译  
---    

> 在C 语言中没有命名空间的概念，于是就存在可能的命名冲突的问题，例如：两个文件中都存在`abc()` 函数，而程序员又不愿意修改源代码，否则可能会污染其他项目。  
> 这时，我们可以通过`objcopy` 命令来手动修改`object` 文件中的符号来进行解决。  

## 编译与链接  

通过`gcc` 命令可以直接编译并链接`.o` 文件：  
```shell  
> gcc -c .\t1.c   # 编译t1.c 生成object 文件 

> nm -C t1.o     # 查看符号表
0000000000000000 b .bss
0000000000000000 d .data
0000000000000000 p .pdata
0000000000000000 r .rdata
0000000000000000 r .rdata$zzz
0000000000000000 t .text
0000000000000000 r .xdata
                 U __imp___acrt_iob_func  # 未定义符号，不能随便修改
                 U __mingw_vfprintf
0000000000000000 R a                 # 代码段符号，可修改
0000000000000000 D b
0000000000000000 t printf
0000000000000054 T test

> gcc .\main.c .\t1.h .\t1.o
```
但是需要注意的是，如果`.o` 文件中的符号是`static` 的，则编译可能报错，因为静态的符号不能直接通过链接器。   
```c
const int a = 1;
int b =2;

// 包含其他库会给编译结果引入其他符号
#include <stdio.h>

static int sum(int a, int b){
    // 静态符号不能被外部代码直接调用，否则编译会出错  
    return a+b;
}

void test()
{
    printf("test 1");
}
```

## 修改object 符号  
- `objcopy --prefix-symbols=my_ .\t1.o`，此命令会给目标文件中的所有符号添加前缀，如果此文件中包含了其他库文件代码则可能会导致错误  
- `objcopy --redefine-sym test=test1 ./t1.o`，此命令可以修改一个符号名`test -> test1`   
- `objcopy --redefine-syms symbols.txt ./t1.o` 此命令可以根据输入文件批量修改符号名  
- `void name1() __attribute__((alias ("name2")));` 为函数添加别名  
- `gcc -c foo.c -Dfoo=foo_renamed` 编译  
- `gcc -c foo.c -Dfoo=foo_renamed` 通过`-D` 指令预设宏定义  

至于是不是需要将所有的符号名都添加上前缀呢？应该在编译器上做文章了吧。如果想给C 打补丁，还不如自己写一个编译器感觉。至此，所有的线索都指向了`llvm`。      

## 其他方案  

有一篇[GCC的符号可见性——解决多个库同名符号冲突问题](https://www.cnblogs.com/langqi250/p/7516230.html)，其中提到了通过宏命令隐藏外部依赖的符号，但是试了下似乎在windows 上不生效。。。。
