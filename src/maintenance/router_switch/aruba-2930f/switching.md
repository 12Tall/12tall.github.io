---
title: 2930F 交换功能  
date: 2022-08-03
timeLine: true
sidebar: false  
icon: config
category:  
    - 笔记  
    - 运维      
tag:   
    - Aruba  
    - 路由  
    - 三层 
---  


# 路由功能
路由的工作方式：  
1. 匹配目标网段  
2. 成功后将消息发往出口或下一跳

每次经过三层设备TTL 都会减一  
除非经过NAT，否则IP 不变  
但是每次经过三层设备，都会改变MAC  

## 静态路由  
静态路由的配置与Cisco 设备类似  

SWB|SWA|SWC  
:---:|:---:|:---:
vlan2|vlan2,vlan3|vlan3  
192.168.2.1/24|<-->|192.168.3.1/24  

```bash
vlan 2 tagged 2  # trunk 
vlan 3 tagged 3  

# 配置交换机IP  
vlan 2 ip address 192.168.2.1 255.255.255.0  
vlan 3 ip address 192.168.3.1 255.255.255.0  

# 配置swb  
vlan 2 tagged 1  
vlan 2 ip address 192.168.2.100 255.255.255.0  
# 静态路由  
ip route 192.168.3.0 255.255.255.0 192.168.2.1  

# 配置swc  
vlan 3 tagged 1  
vlan 3 ip address 192.168.3.100 255.255.255.0  
# 静态路由  
ip route 0.0.0.0 0.0.0.0 192.168.3.1  
# 注意ip 与掩码的配合
```

## OSPF  
OSPF 属于链路状态路由协议，是目前应用最广的路由协议。  

### 单个区域  
```bash
ip router-id 10.0.0.21  # 注意，这里并不是ip
router ospf  
    enable  # 启用  
    area 0  # 或area backone 或area 0.0.0.0

vlan 220 
    ip ospf area 0  # 同上
    router ospf  
    redistribute connected  # 重新发布路由

# 可以在多个vlan 上加入区域0  
vlan 300 
    ip ospf area 0  
    router ospf  
    redistribute connected
```

### 多个区域  
```bash
router ospf  
    area 1  # 或area 0.0.0.1
    area 2  

vlan 100
    ip ospf area 1  # 或area 0.0.0.1
vlan 230 
    ip ospf area 2  

```

### 末节区域（stub）  
```bash
area 1 stub 11
```

### 完全末节区域（totally stub）  
```bash
area 2 stub no-summary 11
vlan 230
    ip ospf cost 10
```

## DHCP  
Aruba 交换机需要在接口上明确启用dhcp-server  
```bash
vlan 10  
    name "user_vlan"  
    untagged 1/3  # 配置L3 接口
    ip address 192.168.10.1 255.255.255.0  
    dhcp-server exit  

# 配置dhcp 服务器  
dhcp-server pool "user-pool"
    default-router "192.168.10.1"  # 网关
    dns-server "114.114.114.114,8.8.8.8" 
    lease 00:24:00  # 租约时间dd:hh:mm
    network 192.168.10.0 255.255.255.0  # 网路地址
    range 192.168.10.10 192.168.10.200  # 地址范围，必须配置
    exit  
dhcp-server enable
```

## ACL 

### 标准-扩展ACL  
```bash
ip access-list standard ?  
    NAME-STR 
    <1-99>

ip access-list extended ?  
    NAME-STR 
    <1-99>
```

### 功能配置  
ACL 是逐条匹配的，当满足一条之后就会立即退出。所以以`permit any any` 作为最终的acl

```bash
ip access-list standard 1  
    permit 10.0.100.111 0.0.0.0  

ip access-list standard std_cal  
    permit 10.0.100.111/32

ip access-list extended 100  
    deny ip 10.1.200.0 0.0.255 10.100.111 0.0.0.0 
    permit ip any any  

ip access-list extended ext_cal  
    deny ip 10.1.100.0/24 10.0.100.111/32  
    permit ip any any  

access-list grouping  
access-list grouping 100 in shared  
access-list grouping 100 out shared

vlan 100 
    ip access-group 1 in  
vlan 220 
    ip access-group std_acl in

```

- in。数据即将进入设备  
- out。数据即将离开设备

一般来说，用in 会比较好一些，因为acl 基本都是拒绝的。详见[ACL in 和 out 区别 （重要）](https://www.cnblogs.com/fatt/p/4353806.html)

### 三层ACL  
比较常用，见上节  

### 二层CAL  
二层CAL 是对于vlan 而言的  
```bash
ip access-list standard 10  
    deny 10.1.220.102 0.0.0.0

ip access-list standard std_vacl  
    deny 10.1.220.103/32  

vlan 220
    ip access-group 10 vlan
```

### 端口ACL  
```bash
ip access-list standard 11  
    permit 10.0.100.111 0.0.0.0  

ip access-list standard std_pacl  
    permit 10.0.100.111/32  

interface 4  
ip access-group 11 in  
ip access-group std_pacl in  
```


## 参考资料  
1. [router-id的作用](https://blog.51cto.com/woniudream/1610475)