---
title: 交换机简介  
date: 2022-08-03
timeLine: true
sidebar: false  
icon: safe
category:  
    - 笔记  
    - 运维      
tag:   
---  

## 硬件结构  
- Flash:  相当于硬盘。存放系统、vlan 信息等
- Nvram： 存放启动配置文件（华为的配置文件也都在flash，没有此硬件）。
- Ram： 运行内存
- Rom： 相当于BIOS  
- 新设备基本都是基于x86，可以升级内存  

## 命令行模式  
- 用户模式 `>`：查看一些IP、路由配置  
- 特权模式 `#`：具有所有的查看权限  
- 全局配置 `(config)#`：查看一些IP、路由配置  

## 软件升级  
1. 连接console 口  
2. 给设备配置IP 地址，需要给设备连上网线  
3. 通过`FTP` 进行拷贝  

### FTP 用法简介  

命令|用法|说明  
---|---|---
open|open {ip} [port]|建立连接  
cd| cd {directory}|切换远程目录  
lcd| lcd {directory}|切换本地目录  
dir| dir [directory]|列出远程文件  
ls| ls [directory]|列出本地文件  
get|get {remote file} [local file]|下载到本地
mget|mget {remote files}|下载多个文件到本地
put|put {local file} [remote file]|上传  
mput|mput {local files} |上传多个文件  
bye|bye|断开连接  

## 参考资料  
1. [哔哩哔哩](https://www.bilibili.com/video/BV1kE411N7JV)  
2. [Windows命令行使用FTP](https://www.cnblogs.com/whseay/p/3456038.html) 
