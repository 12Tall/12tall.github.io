---
title: rpath 与patchelf
date: 2025-06-02 10:15:35
tags:
    - ELF
    - linux
    - Nuitka
---

在`Nuitka>=2.7.4` 打包含有`GDAL` 的Python 代码时，会遇到`rpath` 错误的问题。虽然尚未解决，但是先学一下相关知识备用。  
<!-- more -->

## rpath  
`rpath`(runtime library search path) 是ELF 文件中的一个字段，用于指定程序运行时查找共享库（动态链接库）的路径。  
### 共享库查找顺序  
程序运行时，Linux 动态链接器会按一下顺序查找依赖库：  
1. 编译时指定` -Wl,-rpath='.' `，灵活性较差；
2. `LD_LIBRARY_PATH` 环境变量指定的路径；  
3. `runpath` 属性（推荐）;  
4. ldconfig的缓存：配置文件/etc/ld.so.conf中指定的动态库搜索路径；(系统默认情况下未设置)
5. 系统默认路径：`/lib`、`/usr/lib` 等;  

### 查看RPATH
可以使用`$ readelf -d filename | grep PATH` 查看RPATH。
0x000000000000001d (RUNPATH) Library runpath: [$ORIGIN/]

- 一般情况下，RPATH为空，而RUNPATH不为空;  
- `$ORIGIN` 表示该elf文件自身所在的目录;  
- 如需从多个位置查找共享库，则需设置多个RPATH。  

### patchelf
`patchelf` 可以用来查看和修改elf 文件的一些属性。  
```bash  
# 修改 rpath
patchelf --set-rpath /new/lib/path myapp
patchelf --set-rpath '$ORIGIN/' myapp
# 移除 rpath
patchelf --remove-rpath myapp
# 修改动态链接的库（比如替换依赖的某个.so 文件）
patchelf --replace-needed libold.so libnew.so myapp
# 设置 interpreter（动态链接器）
patchelf --set-interpreter /lib64/ld-linux-x86-64.so.2 myapp

# 查看当前设置：
patchelf --print-rpath myapp
patchelf --print-needed myapp
```

## 参考资料  
1. [rpath和patchelf](https://www.cnblogs.com/ar-cheng/p/13225342.html)