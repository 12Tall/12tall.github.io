---
title: Gitlab简单安装
date: 2024-05-16 09:31:21
tags: [Gitlab, Ubuntu, ldap, synology]
categories: [运维]  
description: Gitlab 的简单安装配置教程    
---

以前一直在用Gogs，但是Gitlab 提供了CI/CD 的功能，故而尝试部署下。  

## 安装Gitlab   
Gitlab 官方提供了安装包，不用手动写启动脚本了。按照官方教程安装即可，安装时需要注意使用`ce` 版本。      

```bash   
# 安装依赖   
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl

sudo apt-get install -y postfix

# 注意，这里安装的是ce 版本  
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
# 预设域名，执行安装  
sudo EXTERNAL_URL="https://gitlab.example.com" apt-get install gitlab-ce
# sudo EXTERNAL_URL="http://ip:8080" apt-get install gitlab-ce  
```

安装后可以通过域名或IP 访问，默认管理员账号是`root`。密码可以通过以下命令进行重置：  
```bash  
sudo gitlab-rails console  
# 需要等待几秒   
> user = User.where(@root).first  
> user.password='password'  
> user.save!  
> exit  
```

## 自定义配置  

### 启用自定义Nginx   
GitLab 自带了Nginx 服务，但是我们可以选择禁用，然后利用系统上的Nginx 配置代理服务。  

 
1. 首先编辑配置文件  
```bash  
sudo vim /etc/gitlab/gitlab.rb
```

2. 修改相关配置如下：  
```yaml  
external_url 'http://localhost:8081'  # 在克隆项目时显示的域名

nginx['enable'] = false  # 禁用默认Nginx
web_server['external_users'] = ['www-data']
```

Nginx 在Ubuntu 上的默认用户是`www-data`，但是不清楚是否需要将用户添加到`gitlab-www` 用户组（应该是不用）。  



3. 更新配置  
```bash  
sudo gitlab-ctl reconfigure
# 手动更新用户组
sudo usermod -a -G gitlab-www www-data
sudo chmod g+rx /home/git/
```

#### 配置Nginx    
修改配置文件内容如下：
```nginx
# sudo vim /etc/nginx/sites-enabled/gitlab.xxxx.com  

upstream gitlab-workhorse {
        # 连接到Socket（参考资料里面的配置已经过期）
        server unix:/var/opt/gitlab/gitlab-workhorse/sockets/socket;
}

map $http_upgrade $connection_upgrade_gitlab {
    default upgrade;
    ''      close;
}

log_format gitlab_access '$remote_addr - $remote_user [$time_local] "$request_method $gitlab_filtered_request_uri $server_protocol" $status $body_bytes_sent "$gitlab_filtered_http_referer" "$http_user_agent"';

map $request_uri $gitlab_temp_request_uri_1 {
  default $request_uri;
  ~(?i)^(?<start>.*)(?<temp>[\?&]private[\-_]token)=[^&]*(?<rest>.*)$ "$start$temp=[FILTERED]$rest";
}

map $gitlab_temp_request_uri_1 $gitlab_temp_request_uri_2 {
  default $gitlab_temp_request_uri_1;
  ~(?i)^(?<start>.*)(?<temp>[\?&]authenticity[\-_]token)=[^&]*(?<rest>.*)$ "$start$temp=[FILTERED]$rest";
}

map $gitlab_temp_request_uri_2 $gitlab_filtered_request_uri {
  default $gitlab_temp_request_uri_2;
  ~(?i)^(?<start>.*)(?<temp>[\?&]feed[\-_]token)=[^&]*(?<rest>.*)$ "$start$temp=[FILTERED]$rest";
}

map $http_referer $gitlab_filtered_http_referer {
  default $http_referer;
  ~^(?<temp>.*)\? $temp;
}

server {
  listen 80 ;
  server_name gitlab.xxxxx.com; 
  server_tokens off; 

  real_ip_header X-Real-IP; 
  real_ip_recursive off;    

  access_log  /var/log/nginx/gitlab_access.log gitlab_access;
  error_log   /var/log/nginx/gitlab_error.log;

  location / {
    client_max_body_size 0;
    gzip off;

    proxy_read_timeout      300;
    proxy_connect_timeout   300;
    proxy_redirect          off;

    proxy_http_version 1.1;

    proxy_set_header    Host                $http_host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    Upgrade             $http_upgrade;
    proxy_set_header    Connection          $connection_upgrade_gitlab;

    proxy_pass http://gitlab-workhorse;
  }

  error_page 404 /404.html;
  error_page 422 /422.html;
  error_page 500 /500.html;
  error_page 502 /502.html;
  error_page 503 /503.html;
  location ~ ^/(404|422|500|502|503)\.html$ {
    root /home/git/gitlab/public;
    internal;
  }

}

# sudo systemctl restart nginx.service
```



**需要注意的是，在修改代理之后需要重启浏览器登录，或者刷新缓存，否则会导致用户登录异常，例如无法跳转、资源错误等。**  


### 启用LDAP 登录  
下面是配合群晖`Active Directory Server` 的示例：  

1. 首先编辑配置文件  
```bash  
sudo vim /etc/gitlab/gitlab.rb
```

2. 修改`LDAP` 相关配置如下：  
```yaml  
gitlab_rails['ldap_enabled'] = true
gitlab_rails['prevent_ldap_sign_in'] = false
gitlab_rails['ldap_servers'] = YAML.load <<-'EOS'
  main: # 'main' is the GitLab 'provider ID' of this LDAP server
    label: 'Synology'
    host: 'IP'
    port: 389
    uid: 'sAMAccountName'
    # 管理员的DN（必须
    bind_dn: 'CN=xxxx,CN=Users,DC=your_domain,DC=com'
    # 管理员的密码（必须
    password: 'password'
    encryption: 'start_tls'  # 与389 端口匹配
    verify_certificates: false  # 不验证用户
    active_directory: true 
    # 用户过滤
    user_filter: '(&(objectClass=user)(memberOf=CN=GitLab_Users,CN=Users,DC=your_domain,DC=com))'
    lowercase_usernames: false
    base: 'CN=Users,DC=your_domain,DC=com'
EOS
```



3. 更新配置  
```bash  
sudo gitlab-ctl reconfigure
```

4. 检查  

```bash  
sudo gitlab-rake gitlab:ldap:check
```


### SMTP 邮件服务器  
下面是SMTP 服务器（SSL/TLS）配置的示例：  

1. 首先编辑配置文件  
```bash  
sudo vim /etc/gitlab/gitlab.rb
```

2. 修改`SMTP` 相关配置如下：  
```yaml  
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.domain.com"
gitlab_rails['smtp_port'] = 465
gitlab_rails['smtp_user_name'] = "xxx@domain.com"
gitlab_rails['smtp_password'] = "password"
gitlab_rails['smtp_domain'] = "smtp.domain.com"
gitlab_rails['smtp_authentication'] = "login"

# 下面两种加密方式只能二选一：start_tls 或SSL/TLS
gitlab_rails['smtp_enable_starttls_auto'] = false
gitlab_rails['smtp_tls'] = true

gitlab_rails['smtp_pool'] = false

# gitlab_rails['gitlab_email_enabled'] = true

gitlab_rails['gitlab_email_from'] = 'xxx@domain.com'
gitlab_rails['gitlab_email_display_name'] = 'GitLab'
```



3. 更新配置  
```bash  
sudo gitlab-ctl reconfigure
```

4. 检查  

```bash  
sudo gitlab-rails console
irb(main):001:0> Notify.test_email('XXXXXX@gmail.com','test Gitlab Email','Test').deliver_now
```

### 参考资料  
1. [CentOS7にGitLabをインストールする(既存nginxを使用)](https://qiita.com/inakadegaebal/items/3cc0603141a334fcc8af)  
2. [NGINX:Using a non-bundled web-server](https://docs.gitlab.com/omnibus/settings/nginx.html#using-a-non-bundled-web-server)  
3. [gitlab/lib/support/nginx](https://gitlab.com/gitlab-org/gitlab/-/tree/master/lib/support/nginx)
4. [Gitlab服务器邮箱配置，实现自动为用户发送邮件](https://juejin.cn/post/6991924908242501669)
