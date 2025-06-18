---
title: Linux 容器技术笔记
date: 2025-06-18 10:33:21
tags:
    - linux  
    - container  
    - docker
---

《自己动手写docker》 的读书笔记。  
<!-- more -->

## 基础技术  
基础技术主要包含Namespace 隔离技术、Cgroups 资源管理以及~~AUFS~~ 文件系统等。
而容器技术的核心理念就是通过Linux 提供的一系列工具或者API，以类似搭积木的形式去创造一个相对独立、干净的虚拟环境。
对于虚拟环境中的进程而言，对于外界是无感的，甚至以为自己有root 权限；但是宿主环境却是能够看到或者管理虚拟环境中的进程。   

### Namespace 隔离  
Namespace 是Linux Kernel 的一个功能，用于隔离一系列的系统资源，当前Linux 一共实现了6 种不同类型的Namespace：  
Namespace 类型|系统调用参数|说明  
---|---|---  
Mount Namespace | CLONE_NEWNS | linux 2.4.19 引入，主要用来隔离文件挂载点，因为未考虑后续更多的命名空间，所以系统调用参数名与其他参数名不一致  
UTS Namespace | CLONE_NEWUTS | linux 2.6.19 引入，主要用于隔离主机名和域名  
IPC Namespace | CLONE_NEWIPC | linux 2.6.19 引入，主要用于隔离SystemV IPC 和POSIX message queue  
PID Namespace | CLONE_NEWPID | linux 2.6.24 引入，主要用于隔离PID 关系  
Network Namespace | CLONE_NENET | linux 2.6.29 引入，主要用于隔离网络环境
User Namespace | CLONE_NEWUSER | linux 3.8 引入，主要用于隔离用户和用户组设置  

与Namespace 相关的系统API 主要有以下3 个：   

{% markmap 300px %}
---
markmap:
  colorFreezeLevel: 2
---
# Namespace  
## `clone()` 用于创建新进程，根据传入参数创建Namespace 隔离，并且其子进程也会继承这些配置  
```c
int clone(int (*fn)(void *), void *child_stack,
          int flags, void *arg, ...
          /* pid_t *ptid, struct user_desc *tls, pid_t *ctid */ );
```
## `unshare()` 用于将进程移出某个Namespace    
## `setns()`  将进程加入到Namespace    
{% endmarkmap %}  

### 创建Namespace  
1. 在Bash 中可以通过`unshare` 命令创建指定的Namespace：  
```bash  
#!/bin/bash

# 使用 unshare 创建新 namespace
unshare --fork --pid --mount --uts --ipc --net --user bash <<EOF
echo "当前进程 PID: $$"
echo "主机名: $(hostname)"
hostname "new-namespace"
echo "新主机名: $(hostname)"
EOF
```

2. 或者可以通过C 语言调用系统API 创建：  
```c
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// 注意需要预先分配栈空间，这也导致只能通过底层的编程语言实现这一功能
// 而python/node 则只能通过ffi 调用共享库的方式实现
#define STACK_SIZE (1024 * 1024)

static char child_stack[STACK_SIZE];

int child_func(void *arg) {
    printf("Child PID: %ld\n", (long)getpid());
    execlp("/bin/bash", "bash", NULL);
    return 0;
}

int main() {
    // namespace 标志
    int flags = CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNS | SIGCHLD; 
    pid_t pid = clone(child_func, child_stack + STACK_SIZE, flags, NULL);
    if (pid == -1) {
        perror("clone");
        exit(EXIT_FAILURE);
    }
    waitpid(pid, NULL, 0);
    return 0;
}
```

3. Go 语言则封装了`clone()` 方法，通过以上示例：  
```go  
package main
import(
    "log"
    "oS"
    "os/exec"
    "syscall"
)
func main(){
    cmd := exec.Command("sh" )
    cmd.SysProcAttr=&syscall.SysProcAttr{
        Cloneflags:syscall.CLONE_NEWUTS | SyScall.CLONE_NEWIPC
    }
    cmd.Stdin =os.Stdin
    cmd.Stdout =os.Stdout
    cmd.Stderr =os.Stderr
    if err:=cmdRun();err != nil{
        log.Fatal(err)
    }
}
```
可以发现，创建Namespace 的关键操作在于设置标志位。 

### 常用的调试命令  
{% markmap 500px  %}
---
markmap:
  colorFreezeLevel: 2
---
## Mount Namespace  

### `mount -t proc proc /proc` 挂载proc（为文件系统），存储当前内核运行状态 <!-- markmap: fold -->
- `-t proc` 文件系统类型为`proc`  
- `proc` 源文件  
- `/proc` 目标目录  
- 因为`proc` 表示当前内核状态，故在新Namespace 中会更简洁  
- 其中数字表示的是进程id  

## UTC Namespace   
- `hostname` 用于现实主机名信息  
- `hostname -b new_hostname` 修改主机名     

## IPC Namespace   
- `ipcs -q` 查看现有ipc 消息队列   
- `ipcmk -Q` 创建新的消息队列      

## PID Namespace   
- `echo $$` 打印当前进程id     
- `readlink /proc/{pid}/ns/uts` 查看指定进程的Namespace 信息       

## User Namespace   
- `id` 显示当前用户和用户组信息  
- 使用用户隔离需要调用`clone()` 时验证用户身份  
- 需要root 权限的话还需要提前修改用户组信息

## NetWork Namespace   
- `ifconfig` 显示当前网络信息           

## 其他  

{% endmarkmap %}  


### Cgroups 资源管理  
Cgroups 可以管理进程组及其子进程，闲置资源占用并可以监控和统计进程信息。Cgroups 包含三个组件：  
{% markmap 300px  %}
---
markmap:
  colorFreezeLevel: 2
---
# Cgroups  

## cgroup 分组管理模块  

## subsystem 资源控制模块，主要包含  
- `blkio` 块设备IO 控制    
- `cpu`   
- `devices` 设备访问  
- `memory` 内存管理  
- `net_*` 网络管理  
- `freezer` 用于挂起和恢复进程   
- 一般都是预定义好的了

## hierarchy 使cgroup 可以继承   
{% endmarkmap %}  

#### 通过命令行操作Cgroups  
Cgroups 是工作在内核中，一般在容器外进行设置。  
1. 创建和管理cgroup  
```bash  
# 创建并挂载一个hierarchy（cgroup 树）  
mkdir cgroup-test  # 创建一个挂载点  
# 挂载proc
sudo mount -t cgroup -o none,name=cgroup-test cgroup-test ./cgroup-test 
ls ./cgroup-test  # 可以看到一些默认文件  
# cgroup.clone_children cpuset 会读取这个文件，如果是1 子cgroup 会继承cpuset 设置  
# cgroup.procs 当前节点的进程组id  
# notify_on_release 和release_agent 一起使用，通常用于进程退出后清理cgroup  
# tasks 当前节点下的进程id  
cd cgroup-test  
sudo mkdir cgroup-1
sudo mkdir cgroup-2
tree # 扩展子节点会自动添加默认文件

# 移动进程到cgroup  
cd cgroup-1 # 切换到目标cgroup
sudo sh -c "echo $$ >> tasks" # 将当前终端进程移动到cgroup-1  
cat /proc/{pid}/cgroup # 打印cgroup 信息
```
2. 通过subsystem 限制cgroup 资源占用  
```bash  
# 系统会默认为每个subsystem（每种计算机资源）创建一个hierarchy（cgroup 树）， 例如内存管理  
mount | grep memory  # 查看memory subsystem 
# cgroup on /sys/fs/cgroup/memory type .....
cd /sys/fs/cgroup/memory   
sudo mkdir test-limit-memory && cd test-limit-memory # 创建一个cgroup    
sudo sh -c "echo \"100m\" > memory.limit_in_bytes"  # 设置当前cgroup 中所有进程的总内存占用  
sudo sh -c "echo $$ > tasks"  # 将当前进程移动到该cgroup  
# 运行一个占用200M 内存的stress 进程  
stress --vm-bytes 200m --vm-keep -m 1  
# 通过top 命令查看该进程实际占用了100M 内存空间
```

而以内存限制为例，Docker 会为每个容器创建一个相关的cgroup，即使是通过代码实现，也是遵循上面命令的步骤。当然对于不同的计算机资源可以新增更多的cgroup。  

### Union File System 联合文件系统  
`写时复制（Copy-on-Write）`，对于同一个文件，可能存在不同的应用场景，而今当该文件被修改时，才会创建新的资源，以减小系统开销，并且文件可以同步最新状态。  
`AUFS` 对UnionFS 1.x 进行了重写，然后是Docker 选用的第一种存储驱动但是因对Linux 的支持不好，因此更推荐选择OverlayFS。 AUFS 具有分层的概念，还是值得学习的：  
```bash  
# cd 至任意文件夹  
# 创建文件夹container_layer 文件f1-f4 以及挂载目标目录mnt  
sudo mount -t aufs -o dirs=./container-layer:./f1:./f2:./f3:./f4 none ./mnt  
# dirs 后跟的第一个路径是可读写的，后面都是只读的  

echo -e "\nNew Line!" >> ./mnt/f4  
# 因为f4 在mnt 挂载时是只读的，故而在该文件更新时
# 会在container-layer 文件夹中创建一个副本

cat f4  # 仍然会输出原先f4 文件中的内容  
cat ./mnt/f4  # 会显示更新后的f4 内容
```


## 参考  
1. [hexo-markmap](https://markmap.org/hexo-markmap/) 为hexo 添加思维导图的功能。  
2. [Linux 系统调用 fork()、vfork() 和 clone()](https://feng-qi.github.io/2017/04/19/linux-system-call-fork-vfork-clone/)  
3. [Linux资源管理之cgroups简介](https://tech.meituan.com/2015/03/31/cgroups.html)