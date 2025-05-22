---
title: 树莓派开发参考
date: 2023-11-03    
tags:   
    - arm  
    - raspberrypi  
    - os  
    - c
    - boot
    - asm   
---  

## 链接器脚本  
<!-- more -->
```ld
/* 链接器脚本中定义的变量会覆盖程序中的变量，所以一定要小心 */
ENTRY(_start)  /* 程序入口 */
 
SECTIONS
{
    /* `.` 表示当前位置，在`=` 左边时表示重定位 */
    /* 重定位所段的起始位置为 0x8000 */
    . = 0x8000;
    __start = .;  
    __text_start = .;  /* 代码段开始 */
    .text :
    {
        KEEP(*(.text.boot))  /* KEEP 中的代码不会被编译器优化 */
        *(.text)  /* 链接时将所有的.text 和.text.boot 段都汇总在.text 段中 */  
        /* 这里的`*` 是通配符的意思 */
    }
    . = ALIGN(4096); /* 按内存页大小对齐 */
    __text_end = .;
 
    __rodata_start = .; /* 只读数据段的起始等于代码段的结束，段的范围遵循前闭后开的规律 */
    .rodata :
    {
        *(.rodata)
    }
    . = ALIGN(4096); /* align to page size */
    __rodata_end = .;
 
    __data_start = .;
    .data :
    {
        *(.data)
    }
    . = ALIGN(4096); /* align to page size */
    __data_end = .;
 
    __bss_start = .;
    .bss :
    {
        bss = .;
        *(.bss)
    }
    . = ALIGN(4096); /* align to page size */
    __bss_end = .;
    __end = .;
}
```