---
title: Linux 容器技术笔记
date: 2025-06-18 10:33:21
tags:
    - linux  
    - container  
    - docker
---

《自己动手写docker》 的读书笔记。有些代码块并不完整，还是需要结合原书一起看。    
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

## 构造容器  
首先是关于`/proc` 文件系统的基础知识，该系统并不是真正的文件系统，虽然可以以文件系统的形式读取，但是它实际存在于内存中。  

{% markmap 500px %}
---
markmap:
  title: /proc
  colorFreezeLevel: 2
---
# `/proc`
## `/N` 获取PID 为N 的进程信息
- `/cmdline` 进程的启动命令  
- `/cwd` 进程的工作目录  
- `/environ` 进程的环境变量  
- `/exe` 执行命令文件  
- `/fd` 相关的文件描述符  
- `/maps` 内存映射信息  
- `/mem` 进程池有的内存，不可读  
- `/root` 链接到进程的根目录   
- `/stat` 进程的状态  
- `/statm` 进程使用的内存状态  
- `/status` 进程的状态，更易读  
## `/self/` 链接到当前正在运行的进程
{% endmarkmap %} 


### 实现简单docker run 命令     
首先分析该命令的参数`docker run [-ti] {command}`，抛开容器和隔离的知识不谈，该命令就是创建一个进程:  
- `run` 是二级命令，固定的  
- `-ti` 表示是否将子进程的输入输出转发到docker 进程  
- `command` 子进程的启动命令  

下面是大致的流程图：  
{% mermaid sequenceDiagram %}
docker->>runCommand: 1. 解析命令行参数  
runCommand->>NewParentProcess: 2. 创建Namespace 隔离的容器进程（的对象）cmd  
NewParentProcess-->>runCommand: 3. 返回容器进程对象cmd，利用AUFS 初始化系统镜像文件  
runCommand-->>docker: 4. 启动容器进程cmd，调用init 二级命令  
docker->>docker: 5. 容器内进程调用自己（为初始化子进程环境需要）
docker->>RunContainerProcess: 6. 初始化容器内容，挂载proc 文件系统、系统镜像，最后执行command  
RunContainerProcess-->>docker: 7. 容器进程开始运行，转发标准输入输出到docker 进程
{% endmermaid %}

下面是几个比较关键的函数的部分节选：  
#### NewParentProcess 创建Namespace 隔离的容器进程
```go
// 2. NewParentProcess 创建Namespace 隔离的容器进程（的对象）cmd  
func NewParentProcess(tty bool, command string) *exec.Cmd {
    // tty 表示是否转发子进程stdio 这里忽略  
    args := []string{"init",command}
    // 将来该命令会调用自己的init 二级命令，为command 初始化环境 
    // 所以这里要有一个init 命令用于初始化容器内子进程的运行环境 RunContainerInitProcess()
    cmd := exec.Command("/proc/self/exe", args...)   
    // 隔离Namespace  
    cmd.SysProcAttr = &syscall.SysProcAttr{
        Cloneflags: syscall.CLONE_NEWUNS  | syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | 
                    syscall.CLONE_NEWUIPC | syscall.CLONE_NEWNET
    }
    return cmd  // 这里只创建了对象，并未运行  
}
```

#### RunContainerInitProcess 初始化容器环境
```go
func RunContainerInitProcess(command string, srgs []string)error{
    // 挂载 /proc
    defaultMountFlags := syscall.MS_NOEXEC | syscall.MS_NOSUID | syscall.MS_NODEV  
    /*
    * MS_NOEXEC 本文件系统中不允许其他程序运行  
    * MS_NOSUID 本文件系统运行程序时，不允许，不允许设置userid 和group include
    * MD_NODEV 是一个默认参数
    */
    syscall.Mount("proc", "/proc", "proc", uintptr(defaultMountFlags), "")
    argv := []string{command}
    if err:= syscall.Exec(command, argv, os.Environ()); err != nil{
        // 错误处理
        // 这里syscall.Exce 实际回到用内核的函数：
        // int execve(const char *filename, char *const argv[], char *const envp[])
        // 可以在执行filename 程序后覆盖掉当前进程的镜像、数据、堆栈信息，包括PID 这种会被重用
    }
    return nil
}
```

### 增加资源限制   
通过hierarchy 和subsystem 对容器中的资源进行限制，抛开参数解析和命令执行，修改的点在创建容器进程之后，容器初始化之前：
```go
func Run(tty bool, /* */){
    parent, writePipe := NewParentProcess(tty)
    // 创建并应用资源管理规则

    // 初始化容器
    sendInitCommand(/**/, writePipe)
    parent.Wait()
}
```
这一步骤的主要工作是在容器初始化之前**封装**好subsystem/hierarchy 查找、新建以及删除的方法。工作量很大，但是逻辑很直接，相当于自己实现了一个Cgroups 树和管理器：  
{% mermaid sequenceDiagram %}
CgroupManager-->>Subsystem 实例: 发现并创建Subsystem 实例    
CgroupManager->>Subsystem 实例: 在每个Subsystem 对应的hierarchy 上创建cgroup  
Subsystem 实例-->>CgroupManager: 创建完成
CgroupManager->>Subsystem 实例: 将容器进程加入cgroup  
Subsystem 实例-->>CgroupManager: 完成
{% endmermaid %}

### 管道与环境变量  
管道是进程间通信的消息通道，可以按照文件的方式读写，一般有4KB 的缓存区，缓存满时写入会被阻塞。常见的管道类型一般分为：  
- 匿名管道：具有亲缘关系间的进程通信   
- 具名管道：用于任意进程间通信  

因为在启动容器之后需要与容器中子进程通信，于是需要至少有一个匿名的管道来实现：  
```go
func NewPipe()(*os.File, *os.File, error){
    read, write, err := os.Pipe()
    if err != nil {
        return nil, nil, err
    }

    return read, write, nil
}
```

然后再修改容器进程的构造方法`NewParentProcess()`：  
```go
// 因为无需执行固定的命令，所以就不需要传入command 了
func NewParentProcess(tty bool) (*exec.Cmd, *os.File) {
    read, write, err :=  NewPipe()  // 省略判断为空的语句

    // tty 表示是否转发子进程stdio 这里忽略  
    args := []string{"init"}
    // 将来该命令会调用自己的init 二级命令，为command 初始化环境 
    // 所以这里要有一个init 命令用于初始化容器内子进程的运行环境 RunContainerInitProcess()
    cmd := exec.Command("/proc/self/exe", args...)   
    // 隔离Namespace  
    cmd.SysProcAttr = &syscall.SysProcAttr{
        Cloneflags: syscall.CLONE_NEWUNS  | syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | 
                    syscall.CLONE_NEWUIPC | syscall.CLONE_NEWNET
    }

    // ※ 重点在这里，该管道的文件描述符在容器进程中的id 会是3  
    // 因为前面会有标准输入、标准输出和标准错误的id 分别为0，1，2  
    cmd.ExtraFiles = []*os.File(read)
    return cmd  // 这里只创建了对象，并未运行  
}
```
因此在子进程中，我们需要一个获取管道并从管道读取指令的方法：  
```go
// 读取id 为3 的文件，也就是上面生成的管道
// 并从管道中读取命令，重新组合成字符串数组
func readUserCommand() []string{
    pipe := os.NewFile(uintptr(3), "pipe")
    msg, err := ioutil.ReadAll(pipe)
    // 省略异常处理  
    msgStr := string(msg)
    return strings.Split(msgStr, " ")
}
```
最后我们需要重新在`RunContainerInitProcess()` 方法中，去尝试调用管道传入的命令：  
```go
func RunContainerInitProcess() error{
    cmdArray := readUserCommand()
    // 挂载/proc
    path, err := exec.LookPath(cmdArray[0])  // 此语句会让子进程
    // 在系统PATH 中寻找命令的绝对路径

    if err:= syscall.Exec(path, cmdArray[0:], os.Environ()); err != nil{
        // 错误处理
    }
    return nil
}
```
但是最终还是需要手动调用在主进程写入管道，并且该命令似乎只会执行一次。而我们需要的是主进程可以循环写入，在子进程中可以循环读取并执行。 

## 构造镜像（挂载文件系统）  
通过上述步骤虽然创建了独立的pid和ipc，但是子进程中还是能看到父进程所有的挂载点，
这样文件系统便无法隔离，并且该容器也不容易迁移。因此，我们需要将常用的工具打包在一起，
然后在子进程中将这些工具集替换掉系统默认的工具。该操作在容器init进程执行之中，容器内命令执行之前。  

### pivot_root  
在 Linux 中，/（也叫 root 目录）是文件系统的最顶层目录。
所有文件和目录——无论是 `/home`、`/usr`、还是设备如 `/dev`——都在它下面。
```text
/(root)
├── bin/
├── boot/
├── dev/
├── etc/
├── home/
├── lib/
└── ...
```

pivot_root 是一个系统调用，用以改变当前的root 文件系统：将当前root 移动到put_old 文件夹并将
new_root 设置为新的root，以摆脱对之前root 系统的依赖：
```go  
func pivotRoot(root string) error{
    if err:= syscall.Mount(root, root, "bind", syscall.MS_BIND|syscall.MS_REC, 
    ""); err != nil{
        // 以bind mount 重新挂载老root 
        // 把 root 目录“绑定挂载”到自己身上。这样是为了确保 root 是挂载点。
        // ...
    }

    pivotDir := filepath.Jion(root, ".pivot_root")  
    // 创建.pivot_root 文件夹用于临时存储old_root  

    if err:= syscall.PivotRoot(root, pivotDir); err != nil{
        // pivot_root 到新的rootfs  
        // 旧的root 必须在新root 中
    }
    if err:= syscall.Chdir("/"); err != nil{
        // 修改当前工作目录到根目录，以防进程还停留在旧root，引起错误  
    }

    pivotDir = filepath.Join("/", ".pivot_root")
    if err:= syscall.Unmount(pivotDir, syscall.MNT_DETACH); err != nil{
        // 卸载并删除旧root  
    }
    return os.Remove(pivotDir)
}
```

之后，我们可以在容器进程初始化时进行挂载操作：  
```go
func setMount(){
    pwd, err:= os.Getwd() // 获取当前路径  
    pivotRoot(pwd)  // 将进程当前目录设置为root 目录
    defaultMountFlags := syscall.MS_NOEXEC | syscall.MS_NOSUID | syscall.MS_NODEV  
    syscall.Mount("proc", "/proc", "proc", uintptr(defaultMountFlags), "")
    // 挂载 /proc, 不允许执行mount 出来的文件，且不允许访问设备文件
    syscall.Mount("tmpfs", "/dev", "tempfs", syscall.MS_NOSUID|syscall.MS_STRICTATIME, "mode=755")
    // 通过tmpfs（内存文件系统）挂载/dev 提供设备文件目录，例如：
    // /dev/null, /dev/zero, /dev/tty 等
}
```
整体流程图：  
```text
初始：              切换后：

宿主机             容器进程看到的视图
---------          -----------------------
/                →   /
├── rootfs/          ├── proc/    (挂载的虚拟 /proc)
│   └── ...          ├── dev/     (tmpfs 类型)
├── home/            └── ...
└── etc/
```
如果当前程序目录包含`busybox` 这类镜像文件则相当于有了有个崭新的系统环境，对于子进程来说。  

### 通过AUFS 包装busybox  
通过AUFS 创建container-init layer 只读文件层和write layer 读写层。以避免容器内操作影响镜像本身。
记住该操作是在宿主机进行的：  
```go
func NewWorkSpace(rootURL string, mntURL string){
    CreateReadOnlyLayer(rootURL)
    // 将busybox.tar 解压到busybox 目录下，作为只读层，
    // 就是解压、创建文件夹两步操作
    CreateWriteLayer(rootURL)
    // 创建一个新的文件夹write layer  
    CreateMountPoint(rootURL, mntURL)
    // 通过mount aufs 挂载目录，rootURL->/root/ mntURL->/root/mnt/ 
}
// 最后NewParenProcess 中将进程根目录修改为mntURL 即可  
// ...
    cmd.Dir = mntURL
    return cmd, writePipe
// ...
```
有始有终，在容器进程退出时要清理诸多挂载点和文件层，在`parent.Wait()` 之后。  

### 实现volume 数据卷  
因为容器进程退出时会清理所有系统文件，如果需要持久化容器里面的数据，则需要再挂载一些可写的文件夹： 
```go
func MountVolume(rootURL string, mntURL string, volumeURLs []string){
// 1. 读取宿主机给定文件目录，无则创建
    parentUrl := volumeURLs[0]
    if err := os.Mkdir(parentUrl, 0777); err != nil{
        // ...
    }

// 2. 在容器中创建挂载点  
    containerUrl := volumeURLs[1]
    containerVolumeUrl := mntURL + containerUrl
    if err := os.Mkdir(containerUrl, 0777); err != nil{
        // ...
    }
    
// 3. 挂载文件
    dirs := "dirs="+parentUrl  
    cmd := exec.Command("mount", "-t", "aufs", "-o", dirs, "none", containerVolumeUrl)
}
```

在容器退出时只清理挂载点即可，不要再删除数据。  

### 镜像打包  
如果我们需要把当前容器的状态储存成镜像保存下来，则可以通过`tar` 命令将当前系统镜像打包，需要在宿主机执行、并且要在容器退出前执行，否则可写层的数据会丢失。




## 参考  
1. [hexo-markmap](https://markmap.org/hexo-markmap/) 为hexo 添加思维导图的功能。  
2. [Linux 系统调用 fork()、vfork() 和 clone()](https://feng-qi.github.io/2017/04/19/linux-system-call-fork-vfork-clone/)  
3. [Linux资源管理之cgroups简介](https://tech.meituan.com/2015/03/31/cgroups.html)