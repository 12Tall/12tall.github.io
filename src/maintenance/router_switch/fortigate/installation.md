---
title: 飞塔防火墙
date: 2022-08-03
timeLine: true
sidebar: false  
icon: safe
category:  
    - 笔记  
    - 运维      
tag:   
    - 防火墙
---   

只有在注册以后，才能得到技术支持、产品特性信息、最新威胁防护  

## Fortigate 配置  

### 浏览器配置  
1. 通过网线连接`MGMT`口或者`MGMT 1`口  
2. 将计算机IP 地址设置到同一网段，如：`192.168.1.2/24`  
3. 通过浏览器访问访问<192.168.1.99>  
4. 登录，用户名`admin`、密码为空  
5. 修改并保存配置  
6. 通过仪表盘注册设备  

### 局域网管理接口  
在视频[PNETLab - How to setup Fortinet Firewall Lab with win 10 client , Fortinet internet connectivity .](https://www.youtube.com/watch?v=XcUXoe3q_OA&t=655s)第22 分有演示，注意按下面配置好后，客户端需要通过`http` 协议才能访问防火墙的Web 服务。  
```console  
FortiGate-VM64-KVM (port1) # show 
config system interface
    edit "port1"
        set vdom "root"
        set ip 192.168.1.1 255.255.255.0
        set allowaccess ping https ssh http fgfm
        set type physical
        set snmp-index 1
    next
end
```

### 终端配置  
1. 通过`console` 线连接`console` 接口  
2. 通过`PuTTY` 连接`COM` 口  
    Baud rate: 9600  
    Data bits: 8  
    Parity: None  
    Stop bits: 1  
    Flow control: None  
3. 按`Enter` 键进入`cli`  
4. 通过`admin` 和空密码登录  
5. 按`?` 打开命令提示（同Cisco  

### iOS 配置  
1. 下载并启动`FortiExplorer iOS App`  
2. 通过USB 线连接手机与防火墙  
3. 通过用户密码登录  
4. 修改并保存配置  

## SFP 收发器  

### 安装  
略

### 移除  
略


