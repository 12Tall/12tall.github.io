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

# 开始  

## 在NAT 模式下安装FortiGate  

防火墙安装于内外网之间，用于隐藏内网IP，并提供NAT 转换。是最为常用的工作模式。  

### 连接设备  
将防火墙与服务商提供的网络设备连接。并通过Web 访问防火墙管理界面。  

### 配置接口  
1. 进入`Network > Interfaces` 界面，编辑互联网端的接口（如：`wan1`  
2. 设置上下行速率（`Estimated Bandwidth`  
3. 将接口设置为`WAN`  
4. 设置`WAN`口地址：静态、动态、PPPoE  
5. 编辑局域网接口，也被叫做内网接口  
6. 设置`LAN`接口角色  
7. 设置`LAN`接口IP，或者启用DHCP  
8. 管理权限：HTTPS、PING、SNMP 等等  

### 添加默认路由  
1. 进入`Network > Static Routes`。一般来说只需要配置一条默认路由；  
2. 设置`Destination`为`Subnet`（以子网匹配）并且IP 为`0.0.0.0/0.0.0.0`  
3. 设置网关（ISP 提供），接口为之前设置的`wan1`  

### 设置DNS服务（可选
进入`Network > DNS` 指定DNS 服务器即可。也可以使用默认的FortiGuard DNS服务  

### 创建策略  
1. 进入`Policy & Objects > IPv4 Policy`。设置一条用于流向Internet 的流量策略（名为Internet）  
2. 设置输入端口为`lan`、输出端口为`wan1`，设置源、目的、周期和服务信息  
3. 设置动作为允许  
4. 开启`NAT`并选择`Using Outgoing Interface Address`  
5. 启用`Log Allowed Traffic`并选择所有会话  

### 结果  
1. 使用浏览器浏览内网  
2. 可以通过`FortiView > Traffic From LAN/DMZ > Sources`观察流量信息  
3. 右键`Drill Down to Details`查看详情  

如果防火墙拥有内置存储并且启用了日志，那么我们可以查看历史日志信息。查看[特性-平台矩阵](https://docs.fortinet.com/document/fortigate/5.6.0/fortigatefortiosfeatureplatformmatrix)  

## 使用Zones来简化防火墙策略  
通过将多个接口加入一个`zone`可以简化防火墙策略。例如：我们可以创建`VLAN10,20,30`，并将它们加入名称为`LAN`的`zone`。那么我们就可以使用这一个`zone`来达到分开管理每个vlan 的效果。  
除了vlan，zones 嗐可以用来管理物理接口和`IPsec` 隧道。  

### 创建VLAN  
1. 进入`Network > Interfaces`，选择`Create New > Interface`  
2. 创建VLAN 接口，并设置VLAN ID 为10，启用DHCP 服务  
3. 同理创建VLAN 20、VLAN 30  

### 创建zone  
1. 进入`Network > Interfaces`，选择`New > Zone`  
2. 设置一个名字（如：`LAN Zone`），并添加新创建的vlan  
    - 注意：可以选择`Block intra-zone traffic`来阻止vlan 间的通信   

### 创建zone的策略  
1. 进入`Policy & Objectes > IPv4`，创建一条策略：赋予`LAN Zone`内所有vlan 访问互联网的权限  
2. 根据需要，设置安全选项（Security Profiles  

### 结果  
当有新的vlan 时，只需将vlan 加入zone 就可以应用已创建的策略了。  

## 利用SD-WAN来冗余Internet  
SD-WAN 可以无缝管理OSI 模型中的二层流量，而不需要硬件交换机和控制器。  
通过基于基于`volume`的加权平均，我们分配流量wan1：wan2=3：1。当其中一条线路不可用时，将自动将流量转移到另一条线路。  

### 将防火墙接入ISP  
按上文步骤，将防火墙的wan1、wan2 口，分别接入两个ISP 网络。  

### 修改现有策略  
任何在用的接口都不能被加入到SD-WAN 接口。所以我们必须先删除掉wan1、wan2 上已有的策略。  
1. 进入`Policy & Objects > IPv4 Policy`并删除所有wan1、wan2 上的策略  

### 创建SD-WAN接口  
1. 进入`Network > SD-WAN`  
2. 设置接口状态为`Enable`  
3. 在SD-WAN 下，添加两个WAN 口  
4. 在`Load Balancing Algorithm`下，选择基于卷的算法，并配置权重百分比  
5. `SD-WAN Usage`可以看到使用情况  


### 配置SD-WAN状态检查（可选  
1. 进入`Network > SD WAN Status Check`，选择`Create New`。可以设置检测方法   

### 允许内网流量通过SD-WAN
1. 进入`Policy & Objects > IPv4`创建新的策略  
2. 设置出入端口  
3. 启用NAT 和安全配置  
4. 启用日志功能  

### 结果  
1. 访问互联网，在防火墙`Network > SD-WAN > SD-WAN Usage`可以看到使用情况 
2. 通过`Network > SD-WAN Status Check`检测状态  
3. 通过`Monitor > SD-WAN Monitor`显示每个wan 口的使用情况  

### 测试故障转移  
就直接拔掉wan1 的线即可。然后还是通过上方的面板去查看结果。  

## 安全框架的安装与认证  
略  

## 透明web代理  
略  

## 带宽限制与流量整形  
略  


## 基于策略的模式  
在策略模式下，可以直接将web 和应用添加到策略里面。切换防火墙模式会修改配置文件，需要提前备份配置文件。而且基于策略的模式可能会阻止合法流量。还需要设置`Central SNAT`策略来配置NAT。  

演示阻止Facebook
### 启用基于策略的模式  
1. 进入`System > Settings`，滚动至`System Operation Settings`  
2. 选择`Flow-based`、`Policy-based.`以及一个`Select an SSL/SSH Inspection`配置  

### 创建Central SNAT 策略  
1. 进入`Policy & Objects > Central SNAT`点击创建，并设置：  
    - 入口  
    - 出口  
    - 源、目的IP  
    - 协议  

### 创建IPv4策略  
1. 进入`Policy & Objects`创建策略，设置端口与源、目的地址（默认  
2. 在应用选项中，选择添加需要的应用   


### 策略表排序  
1. 进入`Policy & Objects > IPv4 Policy` 可以查看策略表。一般要将更具体的策略放在顶部  
2. 直接拖动行就可以了  

### 结果  
1. 浏览Facebook 打不开  
2. 查看`FortiView > Threats`发现流量被阻止  

## 包捕获  
用于流量分析，略  









