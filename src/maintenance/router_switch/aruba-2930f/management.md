---
title: 2930F 设备管理  
date: 2022-08-03
timeLine: true
sidebar: false  
icon: config
category:  
    - 笔记  
    - 运维      
tag:   
    - Aruba  
    - 登录  
    - ssh  
    - web  
    - telnet  
    - console  
---  
# 设备管理   
本文主要包含交换机设备的权限、登录、升级、备份、恢复等操作。  
2930F 可以采用多种途径登录管理，但除了Console 以外，其余的方式均需要提前设置交换机的IP。

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
