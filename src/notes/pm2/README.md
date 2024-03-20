---
title: 简单PM2 使用笔记
date: 2024-03-20
timeLine: true
sidebar: false  
icon: node
category:  
    - 笔记      
tag:   
    - pm2  
    - 服务  
    - node  
    - 集群  
    - 均衡负载    
---    

> 以前简单了解过`PM2`，但是没有太多的使用经验。现在因为手头上要部署各种类型的脚本或者服务，所以还是记一下常用的指令，尤其是开机自启动与定时任务这一块。


PM2 就是一个管理进程的进程，可以用于部署web 服务，自动化脚本。它能够实现基本的故障重启、均衡负载。相较于systemd 或者是windows 服务，使用起来更加简单。
### 添加并启动一个实例  

```bash  
# 启动脚本
pm2 start app.js  

# 给脚本传入参数，要用 -- 隔开  
pm2 start app.exe -- --port 2333

# 常用参数  
--name <pm2 实例名>  

# 监控当前文件夹（含子文件夹）变化，指定排除项  
--watch --ignore-watch="node_modules"

# 超过内存自动重启
--max-momory-restart <200MB>  

# <日志文件路径>
--log  
# 日志添加时间前缀
--time

# 重启延迟
--restart-delay <毫秒数>  

# 不自动重启  
--no-autorestart

# 定时重启任务  
--cron <规则>  

# 不作为后台进程运行（不常用）
--no-daemon

##  集群  ##
# 对于NodeJS 的应用，可以自动启动多个实例并且均衡负载  
pm2 start app.js -i number  

# 对于计划任务，可以采用下面的方式（对于单次任务脚本，要禁用掉自动重启）：  
pm2 start app.js --cron-restart="0/10 * * * * *" --no-autorestart
# cron 的模式为
# 1. 秒（0 - 59）
# 2. 分钟（0 - 59）
# 3. 小时（0 - 23）
# 4. 日（1 - 31）
# 5. 月份（1 - 12）
# 6. 星期（0 - 7，其中0和7代表星期日）
```

### 管理实例  
```bash  
# 列举实例  
pm2 [list|ls|status]

# 
pm2 delete name

# 查看日志  
pm2 logs [--lines 200] # 限制行数

# 简单的仪表盘  
pm2 monit  
pm2 plus  # 网页仪表盘  
```

### Ecosystem 文件  

通过`Ecosystem` 可以批量管理实例，设置启动参数
```bash  
# 生成配置文件 ecosystem.config.js  
pm2 ecosystem  

# 通过配置文件启动  
pm2 start ecosystem.config.js
pm2 reload ecosystem.config.js
pm2 [start|reload] ecosystem.config.js --only name
```
下面是`ecosystem.config.js` 文件的结构：  
```js
const app = {
	name: "app",
    script: "./app.js",
    env: {
      NODE_ENV: "development",
    },
    env_production: {
      NODE_ENV: "production",
    }
}

const app2 = {
     name: '实例名，默认是脚本文件名',
     script: '脚本的路径',
     cwd: '指定工作目录',  
     args: '指定参数',  
     interpreter: '解释器路径，默认为Node， 但其实也可用于Poetry',
     interpreter_args: '解释器参数',  
     node_args: '解释器参数的别名',  

	 // 高级参数  
	 instance: -1,  // 实例数量，为0 的话，自动创建CPU 核心数  
	 exec_mode: 'fork', // 也可以选择集群模式`cluster`
	 watch: false,  // 监控文件变化  
	 ignore_watch: ['[\/\\]\./'],  // 忽略项  
	 env: {
       NODE_ENV: "development",
     },
	 env_production: {
	   NODE_ENV: "production",
	 },  

	 // 控制流
     cron_restart: '0 0 * * *',  //定时重启
     autorestart: false,  // 自动重启  
     restart_delay: 0,  // 重启延时，微秒

  }

module.exports = {
  apps : [app, app2]
}
```

### 开机启动  
```bash  
# 生成一个开机启动项
pm2 startup  

# 保存当前运行的实例为开机启动项
pm2 save 
```

## 使用实例  

以安装`Gogs` 为例，因为通过包安装不比通过二进制文件配合PM2 简单

```bash  
# 1. 创建git 用户，禁止交互式（如ssh）登录  
sudo adduser --disabled-login --gecos 'Gogs' git # --gecos 'Gogs' 信息不重要  
```
安装配置好数据库的信息，之后切换到git 用户  
```bash
sudo -i -u git  
curl https://dl.gogs.io/0.13.0/gogs_0.13.0_linux_amd64.zip --output gogs.zip  
unzip gogs.zip 

# 其实这里就已经可以通过pm2 启动了  
pm2 start ./gogs web  

# 但是还有更好的方案  
```

因为要设置为开机启动，所以最好通过`su` 账户统一启动，但同时又考虑到服务的权限问题，因此需要设置一个启动脚本：  
```bash  
# 配置pm2 开机自启动  
sudo pm2 startup  

# 创建一个从其他用户启动gogs 实例的脚本
sudo vim /home/git/gogs/gogs.sh  

# 以下为脚本内容， <<EOF 表示创建一个文本块，并传递给脚本命令。EOF 可以自己定义  
sudo su - git <<EOF
    # 进入 git 用户的主目录
    cd ~

    # 进入 gogs 目录
    cd gogs

    # 启动 gogs
    ./gogs web
EOF
# 结束

# 将上述脚本设置内可执行  
sudo chmod +x /home/git/gogs/gogs.sh

# 启动服务  
sudo pm2 start /home/git/gogs/gogs.sh  

# 保存  
sudo pm2 save
```
比较重要的就是上面创建用户，和用户脚本的编写了。🎂