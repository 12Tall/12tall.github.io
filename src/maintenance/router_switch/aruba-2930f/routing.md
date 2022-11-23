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
    - 交换  
    - 二层 
---  

# 交换功能  
在交换功能配置之前，还需要了解简单的端口配置

## 端口配置  
### 配置PoE 功能  
PoE 功能需要手动启用  
```bash
config  

show power-over-ethernet  # 查看PoE 使用情况
interface 10  
# 启用、禁用PoE 功能
power-over-ethernet  
no power-over-ethernet
exit   
write memory  
```  

### OOBM  
`Out-Of-Band Management` 带外管理模式，管理流量走交换网络之外，不受网络异常的影响。例如使用console 口和console server 集中管理，或者有专用的OOBM 接口，详见[Network Out-of-Band Management (OOBM)](https://techhub.hpe.com/eginfolib/networking/docs/switches/wb/15-18/5998-8162_wb_2920_mcg/content/apb.html)  
```bash  
config   
oobm  # 启用oobm  

ip address 10.199.111.21/24  # 设置OOBM IP

telnet-server listen oobm  # telnet 服务仅接受oobm 连接 
ip ssh listen data  # ssh 服务仅接受数据层的连接  
web-management listen both  # http 服务既允许oobm 又允许数据层的连接  
ntp server 10.199.111.251  # 使用OOBM 接口连接时间服务器  

ping 10.199.111.51 sorce oobm  # 通过oobm 接口ping 10.199.111.51

# 通过OOBM 接口访问tftp 服务器
copy tftp flash 10.199.111.200 KA_16_01_0006.swi primary oobm  
show lldp info remote-device oobm

```


### 端口绑定  
仅允许某些MAC 地址通过某个端口  
```bash
config  
# 仅允许01-23-45-67-89-AB 通过#11 端口
port-security 11 learn-mode static mac-address 01-23-45-67-89-AB

# 默认只允许一个MAC 地址经过物理端口，可以使用address-limit 限制MAC 地址范围  
port-security 1 address-limit ? 
# <1-32> Enter an integer number.
write memory
```


### 限制端口流量  
为了保障交换机重要业务，属于QoS 范围
```bash
config  

interface 7  
rate-limit all in kbps 100  # 限制7 号端口输入流量为100bps  
interface 8
rate-limit all out percent 10  # 限制15 号端口输出流量为端口的10%

# 查看限速  
show rate-limit all  

write memory
```

### 端口隔离  
通过端口隔离实现1-48 号端口不能互通，但是1-48 均可以与49-50 端口通信   
```bash
config  

# 方法1： 物理隔离，49-50 端口不做配置  
filter source-port 1 drop 2-48
filter source-port 2 drop 3-48
filter source-port 3 drop 4-48
...  
filter source-port 47 drop 48

# 方法2 协议端口隔离  
filter protocol ip forward 49-50 drop 1-48  

write memory  
```
还是通过ACL 好一些  

### 端口镜像  
Server通过交换机10号端口访问IP网，现需要分析Server流量，PC通过交换机的镜像端口抓取Server数据流量  
```bash
config  

# 方法1 
int 10 monitor  # 监控10  
mirror-port 20  # 20 为镜像  

# 方法2 镜像组  
int 10 monitor all both mirror 1  # 把被监控端口放入镜像组1  
mirror 1 port 20  # 端口20 负责抓取镜像组1 中的数据  

write memory  
```
之后用wireshark 直连交换机端口抓取数据就行了。但是要注意交换机端口的流量可能过大，PC 承受不住

### 端口聚合  
多个端口之间分担流量，增加带宽   
```bash

# 将端口1-2 以lacp 协议加入trunck1 组中 
# trk1 就相当于一个超级接口   
config 

# 动态trunk  
trunk 1-2 trk1 lacp

# 在vlan10 和vlan20 在trk1 中使用tagged 方式  
vlan 100 tagged trk1  
vlan 200 tagged trk1

# 静态trunk  
trunk 3-4 trk2   # 注意，没有lacp  
vlan 300 tagged trk2  
vlan 400 tagged trk2  

show trunks  # 查看聚合端口  
show lacp  

write memory
```  
防火墙的接口也支持端口聚合，详见[FortiGate端口聚合配置](https://www.cnblogs.com/xinghen1216/p/10012094.html)

### 配置堆叠  
专用于Aruba 2930F，通过Virtual Switching Framework (VSF) 虚拟交换框架技术，可在同一层中虚拟化最多八台物理设备。
首先将主副交换机25-26 端口两两连接。  
```bash
# 主交换机    

config
# 创建堆叠链路link1 并与25、26 绑定  
vsf member 1 link 1 25  
vsf member 1 link 1 26

# 修改优先级160，使之成为主控制器  
vsf member 1 priority 160  
# 在domain 5 中激活堆叠  
vsf enable domain 5  

write memory

# 副交换机  
config  

# 创建链路Link1，成员编号为2，并与25、26 绑定
vsf member 2 link 1 25  
vsf member 2 link 1 26  

# 修改优先级，使之成为备用控制器  
vsf member 2 priority 150  

# 在domain 5 中激活配置  
vsf enable domain 5

write memory
```

## VLAN  
在Aruba-OS 的交换机中，使用untagged 和tagged 来替代access 和trunk 命令。而trunk 则表示端口聚合。  

### 创建vlan  
```bash
# 创建vlan  
vlan 220  
    name test  

show vlans  
```  

### 将端口划入vlan  
```bash
vlan 220 
    tagged 6  # trunk 口
    untagged 5  # access 口

show vlans 220  # 查看220 号vlan  
show vlans ports 6 detail  # 查看 g1/0/6 端口
```

### 指定IP  
```bash
vlan 220  
    ip address 10.1.220.1./24  
show ip  
```

### IP Helper 中继-DHCP 请求转发  
将DHCP 请求转发至指定IP，以便于使用自定义DHCP 服务器
```bash
vlan 220  
    ip helper-address 10.0.100.251  

show ip helper-address vlan 20  
show dhcp-rely 
```  

### voice vlan  
voice vlan 的配置与普通vlan 区别不大  
```bash  
config  
vlan 3 voice  # vlan3 为voice vlan  
vlan 3 tagged 5  # 端口5 加入vlan3  

write memory
```

## 生成树STP 
这里仅介绍MSTP 的配置方法，因为MSTP 是目前应用最广的生成树协议。  
记住一点，生成树协议会自动阻塞一些物理接口，来避免环路  
```bash
# 在ArubaOS 中，MSTP 为默认生成树协议，启用MSTP 后，所有端口默认为边缘端口  

spanning-tree  
# 设置生成树配置名称（默认为MAC 地址
spanning-tree config-name ArubaOS-Switch-Comware-Cisco 
# 生成树协议版本（默认为0
spanning-tree config-revision 

# 管理MST 实例
spanning-tree instance 1 vlan 220
spanning-tree instance 2 vlan 100
spanning-tree instance 3 vlan 240

# 设置优先级（4096 的倍数，默认是8
spanning-tree priority 2  
spanning-tree instance 1 priority 3
spanning-tree instance 2 priority 4
spanning-tree instance 3 priority 5

spanning-tree 9 ? # 9 号端口？
# 设置（用于）管理边缘端口
spanning-tree 9 admin-edge-port
# 设置cost 值
spanning-tree 9 path-cost 10000
# 优先级（16 的倍数，默认是8  
spanning-tree 9 priority 10

# 设置1-9 端口的cost 值与优先级
spanning-tree instance 1 9 path-cost 10000
spanning-tree instance 1 9 priority 10

show spanning-tree
```
