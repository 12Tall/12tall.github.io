---
title: PNet-Lab 使用笔记 
date: 2023-07-05
timeLine: true
sidebar: false  
icon: config
category:  
    - 笔记  
    - 运维      
tag:   
    - pnet  
    - cisco  
    - switch  
    - router  
    - image  
    - dynamipshe  
    - iol  
    - ssh  
    - scp  
    - vmware  
    - chmod  
    - fortigate
---  

> [PNet-Lab](https://www.pnetlab.com/) 应该是我见过最好用的网工实验室了。它一般运行于VMware 或VBox 之上，也可以[裸机安装](https://www.pnetlab.com/pages/documentation?slug=install-bare-metal)。并且：  
> - 相比于普通的客户端，它具有一个Web 界面，可以多用户同时使用  
> - 相比于EVE，它支持热插拔   
> - 自带了一款镜像管理软件`ishare2`，可以方便地下载很多镜像  

这里仅记录几个使用的坑：  
- 在VMware 中运行虚拟机时，要注意勾选[VT-x 虚拟化支持](https://www.pnetlab.com/pages/documentation?slug=install-PNETlab)。否则基于QEMU 的镜像在启动后会闪退。  
- 如果国内网络不能下载[ishar2](https://github.com/pnetlabrepo/ishare2)。则可以手动将该仓库下的`ishare2` 文件内容复制到`/usr/sbin/ishare2`，然后对照说明设置权限`chmod +x /usr/sbin/ishare2`即可。  
- 官网下载的OVA 虚拟机是`v4.2.10` 版本的。很多镜像包括`ishare2` 不能正确运行。于是可以通过`ishare2 upgrade` 先升级pnet-lab 到最新稳定版，然后在升级`ishare2` 到最新稳定版（当前是`v5.3`）即可。  
- `ishare2 web gui` 需要python 3.7 及以上版本才能运行，如果使用官方的虚拟机还需要升级python 环境，但是一般通过cli 就已经够用了。  
  - 可以[升级Ubuntu 中自带的Python 版本](https://blog.csdn.net/mbdong/article/details/127662406)到`v3.7`，注意切换优先级（似乎解决不了问题，再看吧）  
- 在下载了镜像之后，最好通过网页中的`System --> System Setting --> Fix Permission` 修复一下权限，尤其是下载了Windows 的镜像之后。  

![](./img/demo.png)
