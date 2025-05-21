---
title: Eve-Ng使用笔记
date: 2022-08-03 15:57:24
tags:
    - eve  
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
---

Eve-Ng 的简单使用教程。  

<!-- more -->

### VMware  
可以选择`VMware Workstation` 也可以选择`VMware Player(免费)`。但是在`Win10` 开启了`Hyper-V` 功能的机器上，虚拟机可能会报异常：  
```
VMware Workstation does not support nested virtualization on this host.  

module 'MonitorMode' power on failed.  
Failed to start the virtual machine.
```  
最简单的方法就是在虚拟机设置中取消使用虚拟化技术。  

### eve-ng  
直接从[官网](https://www.eve-ng.net/index.php/download/)下载以下两个安装包，~~`可能需要梯子`~~  
- 社区版（Free EVE Community Edition）  
- 客户端（Windows Client Side）  

1. 使用`VMware` 导入`*.ovf` 文件，并创建虚拟机  
2. 第一次登录。账号`root` 密码`eve`。登录后按要求重新设置密码。（输入新密码时文本框不会有任何内容）  
3. 偷个懒，一切按默认设置，直至完成（这里网卡可以选择一个仅主机可用的，避免与其他软件冲突）  
   
### 启动
- 虚拟机每次启动都会显示自己的IP 地址（也可以在虚拟机初始化时设置成固定的）  
- 需要用浏览器打开上面的IP 就能使用了，登陆时可以选择console 的类型  
  -  默认是：local（需要调用本地客户端）  
  -  可选：html5（在线运行）


## 加载镜像  
本节主要摘自：[EVE-NG镜像导入（Dynamipshe和IOL）](https://blog.csdn.net/m0_37871296/article/details/90906480)  

### ssh/scp 连接  
#### 1. ssh  
有时`ssh root@{ip}` 会报异常：  
```bash
$ ssh root@192.168.1.2
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ECDSA key sent by the remote host is
SHA256:HDjXJvu0VYXWF+SKMZjSGn4FQmg/+w6eV9ljJvIXpx0.
Please contact your system administrator.
Add correct host key in /Users/wangdong/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in /Users/wangdong/.ssh/known_hosts:46
ECDSA host key for 192.168.1.2 has changed and you have requested strict checking.
Host key verification failed.  

# 一般重置过服务器之后再次尝试连接会出现这个问题
# 这个时候需要重新执行一下  
ssh-keygen -R 192.168.1.2
```   

#### 2. scp  
通过ssh 协议进行文件传输  
```bash
scp -r ./* root@172.20.10.12:/opt/unetlab/addons/iol/bin
# scp -r {source} {destination}
# -r 遍历所有子文件（夹）
# 远程目录：{user}@{ip}:/{path}  
# 本地目录：就是正常的写法  
# 本地在前是上传；本地在后是下载  
```

### 镜像类型  
一般来说，有三种类型的镜像文件可供选择，但是真的是不好下载，有些还要先注册后下载  
1. Dynamipshe   
2. IOL   
3. QEMU 暂不涉及  

### Dynamipshe  
1. 下载文件：`链接：http://pan.baidu.com/s/1jIFzrWa 密码：gknq`，并解压  
2. 将`*.image` 文件上传至`eve-ng` 虚拟机`/opt/unetlab/addons/dynamips` 目录下  
3. 刷新浏览器，测试新增的镜像  

```bash
# 上传文件  
scp -r ./* root@172.20.10.12:/opt/unetlab/addons/dynamips  

ssh root@172.20.10.12
# 修复镜像（必需，否则镜像不能正常工作）
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions  
```  

### IOL  
1. 下载文件：`链接：http://pan.baidu.com/s/1dEHvhHf 密码：dqvm`，并解压  
2. 将所有子文件上传至`eve-ng` 虚拟机`/opt/unetlab/addons/iol/bin` 目录下  
3. 重新生成`iourc`文件，然后给予权限  
4. 刷新浏览器，测试新增的镜像  

```bash  
# 上传文件 
scp -r ./* root@172.20.10.12:/opt/unetlab/addons/iol/bin  

ssh root@172.20.10.12
# 重新生成iourc 文件，然后给予权限  
rm iourc  
python CiscoIOUKeygen.py | grep -A 1 'license' > iourc
chmod -R 777 *  
```

## 客户端配置  
- 默认安装可以直接打开本地的`Putty`  
- 但是打开`wireshark` 时可能会出现异常：  
  ```bash
  The server's host key is not cached in the registry. You
  have no guarantee that the server is the computer you
  think it is.
  ...

  # 这时需要执行以下命令  
  echo y | plink -ssh root@{ip} "exit"  # 向后一条命令输出y
  ```

暂时记录这么多，以后再补充


## 参考  
1. [解决Host key verification failed.(亲测有效)](https://blog.csdn.net/wd2014610/article/details/85639741)  
2. [EVE-NG镜像导入（Dynamipshe和IOL）](https://blog.csdn.net/m0_37871296/article/details/90906480)  
3. [使用ssh上传文件到服务器](https://blog.csdn.net/k_young1997/article/details/90072554)  
4. [Auto-storing server host key in cache with plink](https://serverfault.com/questions/420526/auto-storing-server-host-key-in-cache-with-plink)