---
title: 端口聚合  
date: 2022-08-03 
tag:   
  - ccna
---  

## 端口聚合  
好处：
- 带宽扩容  
- 线路冗余  
- 负载均衡  
<!-- more -->
需要注意：  
1. 偶数个端口捆绑（一般为2 个）  
2. `交换机` 包负载均衡：直接均分，更加平均，但是会有包重组会有问题  
3. `路由器` 流负载均衡：五因素（源地址、目的IP、源端口、目的端口、协议号）  

### 协议分类  
- 动态  
  - 公有：LACP（直连的网络可以不用，一般用在广域网中，反应时间30S，通过BFD 检测来优化）  
  - 私有：PAgP  
- 静态  
  - （LACP）静态模式

### 配置  
```bash
# 思科  
int range g0/11 - 12
channel-group 1 mode on # on 静态
shutdown  # 先shutdown  
int port 1 # 进入捆绑口1，然后当普通接口用
# 配置完之后再一块启动  

# 华为  
clear conf int g0/0/1 # 还原接口配置
port-group group-member g0/0/1 g0/0/2  # 批量设置端口
int Eth-trunk 1 # 创建捆绑口
int g0/0/1
eth trunk 1 # 加入捆绑口1 
```
### 堆叠  
- 堆叠基本上都是采用静态协议  
- 堆叠+端口聚合，基本上可以取代生成树  

## 参考资料  
1. [哔哩哔哩](https://www.bilibili.com/video/BV1kE411N7JV)  