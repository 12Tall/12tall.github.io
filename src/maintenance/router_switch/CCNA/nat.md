---
title: NAT  
date: 2022-08-03
timeLine: true
sidebar: false  
icon: safe
category:  
    - 笔记  
    - 运维      
tag:   
---  

## 网路地址转换  
### 作用  
广域网中，高层网络设备，不能给私有网段回包。所以一般会需要将内网设备的端口映射到公网设备。  

### 步骤  
1. 匹配流量
   - 通过标准acl  
   - permit 抓取指定网段  
2. 定义接口，注意内外部的源地址
   - 一般只用`inside`  
```bash
# 内映射至外
int f0/1
ip nat inside # 会卡住一段时间

# 外映射至内（猜的） 
int f0/0
ip nat outside # 对外
```
3. 静态NAT  
```bash
# 匹配到ACL 1 的转化为f0/0 接口的IP
ip nat inside source <acl-list> interface f0/0 overload  

show ip nat tran
# ip nat inseide source static tcp 172.16.10.1 23 123.1.1.1 23
Switch(config)#ip nat inside source static 192.168.1.1 202.101.100.1
```  
4. 动态NAT  
```bash
Switch(config)#$ nat_name 202.101.100.1 202.101.100.10 netmask 255.255.255.0
Switch(config)#access-list ?
  <1-99>            IP standard access list
  <100-199>         IP extended access list
  <1000-1099>       IPX SAP access list
  <1100-1199>       Extended 48-bit MAC address access list
  <1200-1299>       IPX summary address access list
  <1300-1999>       IP standard access list (expanded range)
  <200-299>         Protocol type-code access list
  <2000-2699>       IP extended access list (expanded range)
  <2700-2799>       MPLS access list
  <300-399>         DECnet access list
  <400-499>         XNS standard access list
  <500-599>         XNS extended access list
  <600-699>         Appletalk access list
  <700-799>         48-bit MAC address access list
  <800-899>         IPX standard access list
  <900-999>         IPX extended access list
  dynamic-extended  Extend the dynamic ACL absolute timer
  rate-limit        Simple rate-limit specific access list

Switch(config)#access-list 1 permit 192.168.1.0 0.0.0.255
Switch(config)#ip nat inside source list 1 pool nat_name
Switch(config)#^Z

show ip nat tran
```

5. 端口映射  
```bash
Switch(config)#ip nat inside source static tcp 172.16.10.1 23 123.1.1.1 23
Switch(config)#^Z
Switch#s
*Sep 25 16:45:36.483: %SYS-5-CONFIG_I: Configured from console by console
Switch#show ip nat tr
Switch#show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 123.1.1.1:23       172.16.10.1:23     ---                ---
--- 202.101.100.1      192.168.1.1        ---                ---
```

## 参考资料  
1. [哔哩哔哩](https://www.bilibili.com/video/BV1kE411N7JV)  