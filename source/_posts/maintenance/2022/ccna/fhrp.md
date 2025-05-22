---
title: 首跳冗余协议
date: 2022-08-03     
tag:   
  - vrrp 
  - ccna
---

## 常见故障与对策  
- 单线路故障：端口聚合
- 单设备故障：
  - 堆叠
  - VRRP
- 单电源故障：双电源（市电+UPS）
- 单服务器故障：做集群
- 机房冗余
<!-- more -->
## VRRP  
虚拟一个逻辑地址，会随着VRRP 切换实际的物理IP  

### 配置  
```bash
# 思科
int vlan 10
ip addr 192.168.1.1 255.255.255.0
vrrp vrid 1 virtual-id 172.16.10.254 (两台设置一样的虚拟IP)

优先级，抢占式  
vrrp vrid 1 priority 101 越大越优先
虚拟IP 的MAC 是根据vrid 生成的

dis vrrp brief
```

### 分流  
两个设备互为主备，见下图：  
![vrrp](vrrp.png)  

### 自动降级  
NQA 检测  


## 参考资料  
1. [哔哩哔哩](https://www.bilibili.com/video/BV1kE411N7JV)  