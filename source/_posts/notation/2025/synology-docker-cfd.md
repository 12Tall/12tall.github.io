---
title: 群晖通过docker 配置Cloudflare Tunnel
date: 2025-10-18 12:16:04
tags:
    - 群晖
    - docker  
    - cloudfare  
    - 零信任  
    - 内网穿透  
---

以前了解过通过[通过群晖的 QuickConnect 访问第三方应用](https://null.studio/2020/02/16/access-thirdparty-web-via-synology-quickconnect/),但是配置比较麻烦,于是采用cloudfare 的零信任隧道配置.算是一个比较通用的方案,而且是免费的.  

<!-- more -->

## Cloudfare 配置 
登录`Cloudfare Dashboard`，进入`Zero Trust` 选择免费计划。在`Networks-Tunnels` 中创建docker 类型的隧道。保存给出的安装命令中`tunnel --no-autoupdate run --token ...` 字符串备用。 

设置Public Hostname，给定域名和服务。但是服务端口用`https/5001` 会有问题，所以用`http/5000` 的组合更好一些。URL 中的IP 可以设置为docker 宿主机IP：`172.0.0.1`  

![cf-app](cf-app.png)


## 群晖安装docker 镜像 

在在国内的群晖几乎自动下载docker 镜像，可以通过以下命令保存`.tar` 压缩包，然后再手动导入到群晖的Container Management。  
```console
$ docker pull --platform linux/amd64 cloudfare/cloudfared:latest  

$ docker save -o cfd.tar cloudfare/cloudfared:latest  

$ # 如果是sudo 运行的，还需要修改文件权限才能上传使用  
$ # sudo chmode 777 cfd.tar  
```

如果要导入其他镜像，还可以通过以下命令：  
```bash
# 拉取指定架构的镜像
docker pull --platform linux/amd64 【镜像名称】

# 导出镜像为 tar 文件
docker save -o package.tar 【镜像名称】
```

### 启动docker 镜像  
将上面保存的`tunnel --no-autoupdate run --token ...` 粘贴至`command/命令` 文本框中，其他配置保持默认。  
![docker](run-docker.png)


## Cloudfare 安全配置  
可以做但非必须，详见参考资料3。需要注意的是，验证邮箱的后缀我留的`@outlook.com` 无法收到验证码，但是换成自定义域名的邮箱则可以收到。

### 部分路径绕过安全设置  
可以通过新增一个子路径，将其测略设置为`bypass`，这样对于某些不需要验证的url 就可以直接访问了。  

![cf-bypass-policy.png](cf-bypass-policy.png)
![cf-bypass-app.png](cf-bypass-app.png)


## 参考资料  
1. [Docker 镜像源下线，Image 越来越难以拉取？试试下载后离线转移到线上环境](https://utgd.net/article/20798)  
2. [通过群晖的 QuickConnect 访问第三方应用](https://null.studio/2020/02/16/access-thirdparty-web-via-synology-quickconnect/)  
3. [群晖7.1 docker搭建cloudflared，使用Cloudflare Tunnel内网穿透，公网访问内网服务](https://www.thsink.com/notes/1665/)