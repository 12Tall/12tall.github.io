---
title: Nuitka 打包问题
date: 2025-05-30 08:50:14
tags:  
    - python  
    - Nuitka
---

Nuitka 虽然是一个比较好用的跨平台打包工具，但是有时打包也存在许多问题：  
<!-- more -->  

## 找不到动态链接库  
基本可以通过`--include-data-files="{src_dir/dll_file}=./"` 手动拷贝动态链接库到二进制根目录解决。此问题常见于PyQt 打包  

## 避免使用Conda 包  
Conda 包安装方便，可以直接在Python 代码使用。但是在打包成二进制文件时容易遇到`rpath` 的问题，此问题在`Nuitka>=2.6.8` 以上版本容易出现  
可以使用低版本Nuitka 外加`--include-data-files="$CONDA_PREFIX/lib/{dll_file}.so*=./"` 解决

## 使用预编译.whl 的问题  
有些库为了跨平台使用了一些包，但是打包的时候会出问题，例如`ImportError: libtiff-d0580107.so.5.7.0: ELF load command address/offset not properly aligned`。  
这时需要从源码编译库文件，例如`pip install --no-binary :all: Pillow`  
- `--no-binary` 不使用预编译二进制包  
- `:all:` 应用于所有库  

## 二进制文件的问题  
尽量不要依赖虚拟环境，太痛苦了