---
title: acme 证书管理
date: 2025-05-22 08:30:26
tags:
    - certificate  
    - acme  
    - ssl  
    - https  
    - domain
    - Let's Encrypt  
    - nginx  
    - fnm  
    - nodejs
    - pm2
---

通过`acme.sh` 安装并更新Let's Encrypt 证书。  

<!-- more -->  

以下是安装到使用的基本过程：  
```bash  
# 下载安装acme
curl https://get.acme.sh | sh -s email=aaa@bbb.com
alias acme.sh=~/.acme.sh/acme.sh

## 签发证书
# 这里我用的是godaddy 的服务，可以通过指定api 来自动配置
# 预先在环境变量中设置key 和secret，最好带着双引号  
# 怎么获取key 和secret 可以搜索一下
export GD_Key="key"  
export GD_Secret="secret"
acme.sh --issue --dns dns_gd -d xxx.com -d *.xxx.com
# 或者如果不想自动配置，则需要手动添加TXT 记录`_acme-challenge.xxx.com`  
# acme.sh --issue --dns -d xxx.com -d *.xxx.com

# 签署证书成功后，证书文件会被保存到下面目录  
# Your cert is in: /home/{user_name}/.acme.sh/xxx.com_ecc/xxx.com.cer
# Your cert key is in: /home/{user_name}/.acme.sh/xxx.com_ecc/xxx.com.key
# The intermediate CA cert is in: /home/{user_name}/.acme.sh/xxx.com_ecc/ca.cer
# And the full-chain cert is in: /home/{user_name}/.acme.sh/xxx.com_ecc/fullchain.cer

# 创建证书安装目录  
sudo mkdir -p /etc/nginx/cert/xxx.com
sudo chmod 777 /etc/nginx/cert/xxx.com

# 安装证书  
acme.sh --install-cert -d xxx.com \
--key-file /etc/nginx/cert/xxx.com/xxx.com.key \  # 私钥保存位置
--fullchain-file /etc/nginx/cert/xxx.com/fullchain.cer \  # 证书链保存位置
--reloadcmd "systemctl force-reload nginx"  # 安装后重启Nginx  
# 该命令还会自动创建crontab 任务，自动更新证书

sudo openssl dhparam -out /etc/nginx/dhparam.pem 2048 # 提升https 的安全性   

# 更新证书
acme.sh --renew -d xxx.com -d '*.xxx.com' --dns dns_gd --force
# 或者
acme.sh --renew-all
```

## Nginx 配置  
这里有些Nginx 的配置，除了使用证书之外还有些其他功能，值得记录一下：  
```nginx  
server {
    listen              80;
    server_name         www.xxx.com;
    return              301 https://$host$request_uri;
}

server {
    listen              443 ssl;
    server_name         www.xxx.com;
    server_tokens       off; # 禁止在响应报文中包含Nginx版本信息

    # ssl 配置，主要引用之前生成的证书文件
    include             /etc/nginx/ssl-options.conf;
    ssl_certificate     /etc/nginx/cert/xxx.com/fullchain.cer;
    ssl_certificate_key /etc/nginx/cert/xxx.com/xxx.com.key;
    ssl_dhparam         /etc/nginx/dhparam.pem;
    
    location / {
        proxy_pass          http://127.0.0.1:8000;
        # ...
    }      
    # ... 
    location = /upload {
        # 只允许部分网段访问该路径，及其子路径
        allow               10.0.1.0/24;
        allow               10.0.2.0/24;
        deny                all;

        proxy_pass          http://localhost:8080/upload;
    }
    # ...
}
```

## fnm 配置pm2  
fnm 只是一个NodeJS 的环境版本管理工具。写到这里，还是把pm2 的记录贴一下：   
```bash
# 安装fnm
curl -o- https://fnm.vercel.app/install | bash
source /home/{user_name}/.bashrc
fnm install 20  

npm install pm2 -g
pm2 --version
pm2 init simple  # 创建基本的ecosystem.config.js 可以用来批量添加任务

# 创建开机自启动的服务
pm2 startup
# 启动任务
pm2 start ecosystem.config.js 
# 保存任务
pm2 save
```


## 参考资料  
1. [acme.sh 使用文档](https://docs.certcloud.cn/docs/installation/auto/acme/acmesh/)  
2. [使用 acme.sh 生成免费 90 天的 SSL 泛域名证书](https://www.cnblogs.com/hanzhe/p/18463948)：重要  
3. [使用ACME申请泛域名证书](https://www.panyanbin.com/article/e212b974.html)：重要  