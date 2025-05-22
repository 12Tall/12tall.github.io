---
title: aruba 设备
date: 2022-08-03 16:02:52
tags:
    - Aruba  
    - 路由  
    - 三层 
    - 交换  
    - 二层 
    - 登录  
    - ssh  
    - web  
    - telnet  
    - console  
---

本文主要包含交换机设备的权限、登录、升级、备份、恢复等操作。  
2930F 可以采用多种途径登录管理，但除了Console 以外，其余的方式均需要提前设置交换机的IP。
<!-- more -->
## 登录设备  
1. 通过Console 线连接PC 与交换机；  
2. 通过PuTTY 连接COM 口即可。 

ArubaOS 有三种模式：运维、管理、配置模式，与Cisco 设备类似  
```bash 
# 默认是运维模式
ArubaOS-Switch> enable  # 进入管理模式
ArubaOS-Switch# configure ? # 进入配置模式  
  terminal # 可选
  <cr>
ArubaOS-Switch(config) # 
```

如无特殊说明，本文及后续笔记中的命令均运行于配置模式下。  

在Console 登录之后，需要配置交换机的IP 地址，然后才能选择其他登录方式。  
```bash
hostname XXX  # 配置设备名称  

clock timezone gmt +8:00 # 设置时区
clock summer-time  # 夏时令
timesync ntp  # 配置ntp 同步  
ntp unicast  # ntp 单播  
ntp server-name 1.1.1.1 iburst # 设置ntp 服务器  
ntp enable 
show ntp status  

# 设置设备IP
vlan 1  # vlan 1 是ArubaOS 的默认VLAN
  # untagged 相当于Cisco 中的access；
  # tagged 相当于trunk；
  # 而trunk 在ArubaOS 中表示链路聚合的意思
  untagged 10  

  # 为端口设置IP
  ip address 192.168.1.100 255.255.255.0 
  exit  

# 在配置了IP 之后，我们就可以通过启用telnet、ssh、web 等其他方式登录方式。
# 通过192.168.1.100，来远程管理交换机。 
# 在此之前，我们最好创建一个本地的管理员账户！

# 1. 创建管理员账户
password manager user-name <name> plaintext <password>
# 2. 创建operator 用户  
password operator user-name <name> plaintext <password>

# 启用http/https
# 1. 启用http 访问  
web-management plaintext # 不安全  
# 2. 启用https 访问  
web-management ssl  # 安全  

# 启用telnet 
# Telnet 默认开启，在配置好IP 之后就可以使用
show telnet  

# 启用ssh  
crypto key generate ssh  # 生成ssh-key  
ip ssh  # 启用ssh 服务  
no telnet-server  # 关闭telnet 服务
show ip ssh  
show crypto host-public-key  
show ip host-public-key  
ssh x.x.x.x ipv4/ipv6  # 设置哪些ip 可以通过ssh 管理设备

write memory  # 保存配置
```


## 文件管理  
### 系统镜像管理
ArubaOS 有两个分区，一般用主分区，但在必要时也可以用第二分区引导启动。导入、导出配置文件属于`系统镜像文件管理`，在备份配置文件时，需要已经有sftp、tftp、usb 服务才行。
```bash
show flash  # 查看镜像文件  
show version # 查看当前系统版本

# 将文件拷贝到flash，可在命令行最后指定分区：primary 或secondary 或oobm  
# 默认是primary（猜的或者同时拷贝
copy tftp flash 10.0.100.111 K_15_16_0004.swi  #
copy sftp flash 10.0.100.111 K_15_16_0004.swi  #
copy usb flash K_15_16_0004.swi  #
copy xmodem flash  #

copy flash flash secondary  # 用于flash 之间互拷

copy flash tftp 10.0.100.111 K_15_16_0004.swi  #
copy flash sftp 10.0.100.111 K_15_16_0004.swi  #
copy flash usb K_15_16_0004.swi  #
copy xmodem flash  #


# 设置交换机从第二分区启动  
boot system flash secondary  
y  
# 查看当前固件版本  
show version  


# 其他命令
boot set-default flash primary  # 将主分区设置为默认启动分区  
boot system flash secondary  # 将第二分区设置为默认启动分区  
copy flash flash primary  # 将固件从第二分区复制到主分区  
copy flash flash secondary  # 将固件从主分区复制到第二分区  
# 如果版本跨度太大，最好多次小版本升级。 
```
### 配置文件管理  
```bash
# 备份至PC
copy startup-config tftp {ip} config-backup.cfg

# 恢复备份  
copy tftp startup-config {ip} config-backup.cfg

# 重启设备
y
```

## 其他
### 密码丢失  
所有的步骤都需要连接Console 线完成。  
1. 按住交换机前面的`clear` 键1s，清除用户名密码；  
2. 清除密码后会自动进入# 模式；  
3. 如再次遇到输入密码，重复步骤1 即可。

### 恢复出厂设置  
恢复出厂设置主要有以下两种方式：  
- 通过删除配置文件  
```bash  
config  

# 删除起始配置文件
erase startup-configuration
```

- 物理按键  
  1. 同时按下Reset 和Clear  
  2. 两秒后松开Reset  
  3. 当自检灯(Test) 闪烁时，松开Clear  

### 选择启动分区  
2930F 系列有两个启动分区：Primary 和Secondary。系统默认从Primary 分区启动，如果主分区异常可以通过Monitor 界面选择从第二分区引导启动：  
1. 同时按下交换机Reset和Clear    
2. 约2秒钟左右松开“Reset”按键，同时继续按住“Clear”按键   
3. 当自检灯(Test)的LED指示灯经过闪烁-直到常亮时，松开“Clear”按键，交换机进入monitor界面  
4. 输入`JP 2`，使用secondery固件启动系统  

### 日志服务器  
可以将交换机的日志发送到指定的日志服务器，统一分析  
```bash
config  

logging 192.168.1.100  

# 选择日志等级
logging severity ?  
major  
error  
warning  
info  
debug  
```


### 计划任务  
需要16.0 及以上的固件版本，详情见"Job Schedule" 章节。  
```bash
config  

# 创建job：saveconfig 时间 日期 执行的命令save 执行次数  
job saveconfig at 23:00 on 11/11 config-save save count 2  

# 查看job  
show job saveconfig  

# 激活job  
job saveconfig enable  

write memory  
```


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