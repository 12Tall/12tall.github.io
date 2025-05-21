---
title: 交换机基础 
date: 2022-08-03  
tag:   
  - ccna
---
 
## 交换机  
### 二层交换机  
- 二层交换机能且只能配置一个IP（管理用）  
- 二层交换机也可以配置一条静态路由  
<!-- more -->
### 三层交换机  
- 三层交换机可以配置vlan  
- 具有一部分路由的功能  
- 路由器中WAN 口为路由端口；LAN 为交换端口  

### 泛洪  
1. arp 泛洪，用于查找IP-MAC 对应关系  
2. 数据包泛洪  
3. 广播包泛洪

- 二层设备不能分割广播域，即不管跨多少二层交换机，设备还是在同一广播域  
- `eve-ng` 中`IOL` 三层设备好像不支持`vlan` 操作  
  - （L3 是路由器；L2 是交换机，包含三层交换机）  
  - 路由器不用配置vlan  
```bash
int g0/0.10
encapsulation dot1q 10 # 10 为vlan id
ip add 192.168.1.1 255.255.255.0
```
- 设备负载率：一般在30% 左右给比较好，超过50% 就是重负载  

## VLAN  
### 接口类型  
- access 接入接口  
  - access 进：有tag 则直接丢弃，否则加上tag；出：剥去tag  
- trunk 汇总接口  
  - trunk 进：没有tag 或者不对都会被丢弃；出：保持原tag  
  - 思科必须允许的vlan 1,2,1002-1005  
- vlan1 默认不加tag，存在风险，所以一般将vlan1 shutdown
- pvid：等同于tag，交换机内部使用pvid，因为可以直接通过硬件转发，而vid 会经过CPU，稍慢
  - trunk 的`Dot1q` 就是将pvid 转tag
- 不同VLAN 接口，如果直连的话也会能够正常通信。  

### vlan 间的路由  
主要是对路由器子接口的介绍（常见在单臂路由SVI 中）  
子接口的应用比较广泛，一般不用担心其对性能的影响，路由器就可以接交换机的trunk 接口了  
```bash
# 将一个物理接口虚拟成两个虚拟子接口
int f0/0.1
encapsulation vlan dot1q valn10
int f0/0.2
encapsulation vlan dot1q valn20
```



## 参考资料  
1. [哔哩哔哩](https://www.bilibili.com/video/BV1kE411N7JV)  
2. [交换机二层接口access、trunk、hybird三种模式对VLAN的处理过程](https://www.cnblogs.com/zhzblog/p/9583080.html)
3. [Cisco-VLAN间路由：SVI+单臂路由（子接口）](https://blog.csdn.net/ghwzjz/article/details/100659294)  
