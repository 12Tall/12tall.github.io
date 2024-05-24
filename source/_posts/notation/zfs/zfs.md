---
title: Ubuntu 安装zfs  
date: 2024-05-24 15:24:16
tags: [Ubuntu, zfs, raid, backup]
categories: [运维]  
description: Ubuntu 安装zfs 并配置Mirror（RAID-1）     
---

关于`zfs` 文件系统的介绍，可以参考：[初学者指南：ZFS 是什么，为什么要使用 ZFS？](https://zhuanlan.zhihu.com/p/45137745)  



## RAIDZ 的存储效率  

存储效率应理解为存储空间利用率，可以用以下表格表示：  
RAID 类型|存储效率|校验设备数量  
---|---|--- 
RAID0|100%|0  
RAID1|$\frac{1}{n}$|0  
RAIDZ-1|$\frac{n-1}{n}$|1  
RAIDZ-2|$\frac{n-2}{n}$|2  
RAIDZ-3|$\frac{n-3}{n}$|3  

按照[ZFS: You should use mirror vdevs, not RAIDZ.](https://jrs-s.net/2015/02/06/zfs-you-should-use-mirror-vdevs-not-raidz/) 文章介绍，更推荐使用`RAID1` 而不是`RAID5`，因为硬盘损坏时会导致文件系统的效率大幅降低。并且一个存储池里面最好不要超过8 块硬盘。  

## 安装配置zfs  

Ubuntu 系统并没有自带zfs 工具，需要自己安装`sudo apt-get install zfsutils-linux`，之后可以通过`sudo zpool` 命令使用。  

```bash  
# 查看硬盘以及分区信息  
sudo fdisk -l    

# zfs 组RAID1 可以是硬盘与硬盘、硬盘与分区  
sudo zpool create pool_name mirror /dev/sdb /dev/sdc[1|2|3]  
# 查看zpool 状态  
sudo zpool status [pool_name]
# DEGRADED 降级：有问题  
# ONLINE 正常  
# OFFLINE 离线       
# OFFLINE 离线       
# 查看详细信息
sudo zpool list [pool_name]

# 建立测试文件  
sudo dd if=/dev/zero of=/pool_name/test.data bs=1M count=512
# 检查md5  
md5sum /pool_name/test.data  
# 强行移除一块硬盘后，查看文件md5 并没有变化（证明没有损坏）

# 添加新硬盘后，可以替换损坏的硬盘
sudo zpool replace pool_name sdc1 sdd  # 可以省略/dev/sdd 这种写法  
# 更换新硬盘后注意观察数据同步的状态，在name 列有`replacing` 字样

# 如果需要对存储设备扩容，则需要在更新所有设备后执行
sudo zpool set autoexpand=on [pool_name]
sudo zpool online -e pool_name sdb
sudo zpool online -e pool_name sdd
```

文中的命令摘自[Ubuntu 22.04 环境 zfs raid1 mirror配置，在线无损替换故障硬盘](https://www.pocketdigi.com/article/linux_zfs_raid1_mirror_replace.html)，另外`mdadm` 工具也可以配置软RAID。但即使配置了RAID 也需要设置数据的定期备份，这一点也是很重要的。