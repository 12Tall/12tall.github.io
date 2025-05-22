---
title: 容器技术简介    
date: 2022-08-03   
tags:   
    - podman  
    - docker  
    - 容器 
---  

 
> 关于容器技术的原理，可以参考[造轮子系列-手写docker](https://www.bilibili.com/video/BV1tB4y1S7nr)。通过容器技术，可以将我们不同服务的运行环境隔离开来，避免不必要的不兼容问题。  
> 容器在Linux 可以理解为一个独立的、具有隔离的运行环境的进程。
<!-- more -->
现在广泛应用的容器化工具是`docker`，但是docker 存在管理员权限的问题。为此，我们也可以采用[Podman](https://podman.io/)，几乎可以从docker 无缝迁移。  

与`docker` 不同，`podman` 可以以普通用户的身份运行，容器内部的用户身份、权限与运行容器时的用户一致，这样就避免了`docker` 中权限混乱的问题。详见[podman入门实践](https://juejin.cn/post/6990279582255579150)

## Podman Run 命令  
> `podman run --help`  

详细信息参考：[菜鸟教程](https://www.runoob.com/docker/docker-run-command.html)