---
title: 域控制器杂谈 
date: 2022-08-03
timeLine: true
sidebar: false  
icon: linux
category:  
    - 笔记  
    - 运维      
tag:   
    - linux  
    - samba  
    - dns  
    - domain
---    

# 域控制器杂谈  

工作以来，最早接触的技术就是计算机加域了。但是对域的概念一直不太清晰，尤其是域控制器的搭建，DNS 服务器的配置。网络上的教程多是基于Windows 的，到了新的部门之后发现要是买正版真的太贵了。好在刚开始的时候可以使用群晖做域控制器，搭建过程傻瓜但是极其好用。不幸的是，群晖在做文件索引时，会导致用户认证的失败。于是想着是否可以用一台Linux 专门做认证、域控服务器。本文没有技术细节，只是泛泛谈一下最直观的认识。    

最早是想搭建一个LDAP 认证服务器的，因为我对Samba 的印象仅仅停留在它是一个文件共享的协议的层面上。但是随着检索的深入，逐渐了解到Samba 除了共享文件和打印机之外，还可以做域控制器，并且内置了DNS 服务器和LDAP 服务，并且还可以[配置`FreeRadius` 服务](https://wiki.samba.org/index.php/VPN_Single_SignOn_with_Samba_AD)，简直满足了我的所有需求。于是想着重点学习一下。

如果粗略地看一下官方的[说明文档](https://wiki.samba.org/index.php/Main_Page)，你会发现教程非常细致，细致到根本看不下去。因为对很多技术细节都没有概念，比如`Kerberos` 是什么、`BIND9_DLZ` 又是干啥的、为什么需要安装`winbind`？了解这些东西没啥用，但是不了解的话不管做什么都不踏实。于是照着示例和教程配置了三四遍，最终心里还是没太有底。想着先把目前的想法记下来，不然脑袋里太多乱七八糟的细节，根本学不进其他东西了。  

## 关于Samba  
`Samba` 是一个为网域内所有客户端提供文件和打印机共享服务的软件，支持Linux、Unix 和Windows（服务端需要`winbind` 服务组件）作为客户端。`Samba` 的一些特性、以及和其他软件系统的关系：  
- 内置`LDAP` 服务用于管理成员，但并不支持`OpenLdap` 作为后端。<https://wiki.samba.org/index.php/FAQ#LDAP>  
- 内置`DNS` 服务器作为域名解析，支持通过`DLZ` 模块将`BIND9` 绑定为后端域名解析服务。但内置的服务器已基本够用。  
- 采用`Kerberos` 加密用于身份认证。需要进行稍许的配置。    
- 可以作为`FreeRadius` 单点登录的后端。<https://wiki.samba.org/index.php/VPN_Single_SignOn_with_Samba_AD>  
- 利用`samba-tool` 工具可以重新配置Samba 服务，以及管理用户和DNS 记录等资源。


## 关于BIND9  

`bind9` 是一个网路地址解析的服务，如果要详细学习的话，需要了解许多关于DNS 协议的支持，可以参考《鸟哥Linux 私房菜--服务器》相关的章节。这里主要记一下BIND9 与Samba 如何协同工作的，尽管一般情况下我们用不着很复杂的功能。  
一般我们架设DNS 服务器时，总是需要有一个地方存放域名和IP 的对应关系，默认情况下BIND9 会从文本文件中读取这些信息，例如：`name.conf` 文件。但是这样做不够灵活，尤其是当我们想更新DNS 记录的时候。这时就有大神开发了`BIND9_DLZ` 模块，这个东西就相当于一个数据库驱动服务，让我们的BIND9 程序可以从数据库中读取数据，这样我们的DNS 记录就可以实时更新，并且可以做出漂亮的Web UI 来管理。网络上有很多关于BIND9 与MySQL 配合使用的案例与教程。  
因为我们的Samba 内的机器资源也是通过FQDN 唯一确定的，并且可以通过LDAP 的协议和语法进程增删改查，于是通过配置`BIND9_DLZ` 模块就可以让BIND9 解析到我们Samba 中的主机名。需要注意的是数据库文件是由Samba 提供的，BIND9 只有使用权，所以一切DNS 记录的更细还是要通过samba 工具来完成。  
Samba 内置有一个DNS 服务器，不支持多个域、且在域名解析转移时有BUG。但是一般小企业也不会有多个网域，倒也足够。


如此以来，就简单的理解了几个服务组件之间的关系，这样再去看配置命令时目的性就会更强一些。当然，关于域控的许多技术细节，还是要结合实际慢慢啃的。  

## 参考  
- [SAMBA](https://www.jianshu.com/p/15893eece2ee)  
- [Installing Samba as Active Directory Domain Controller Using Internal DNS on Ubuntu 18.04](http://biroinfotek.com/installing-samba-as-active-directory-domain-controller-using-internal-dns-on-ubuntu-18-04/)：在新版Ubuntu 中依然可用    
- [Install Samba 4.7.6 AD DC – Ubuntu 18.04 – Bind 9.11 DNS – Backend AD RFC2307](http://biroinfotek.com/install-samba-4-7-6-ad-dc-ubuntu-18-04-bind-9-11-dns-backend-ad-rfc2307/)：在新版Ubuntu 中依然可用  
- [VPN Single SignOn with Samba AD](https://wiki.samba.org/index.php/VPN_Single_SignOn_with_Samba_AD)：主要是Radius 服务器配置   
- [How to Compile Samba 4.10.5 on Ubuntu 16.04](https://www.kombitz.com/2019/07/08/how-to-compile-samba-4-10-5-on-ubuntu-16-04/) 在Ubuntu 22.04+Samba 4.17.2 依然可用。编译前配置如下：  
    ```bash  
    ./configure \
    --with-systemd \
    --systemd-install-services \
    --with-systemddir=/etc/systemd/system \
    --sysconfdir=/etc \
    --localstatedir=/var \
    --enable-selftest \
    --with-smbpasswd-file=/etc/samba/smbpasswd \
    --enable-fhs
    ```