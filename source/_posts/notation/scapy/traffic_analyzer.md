---
title: Scapy 抓包分析代码阅读
date: 2024-05-26 15:33:23
tags: [python, scapy, sniff]
categories: [安全, 开发]  
description: Python+Scapy打造网络流量分析监控工具的源码阅读       
---

<!--more-->  

通过阅读[源码](https://github.com/kidultff/TrafficAnalyzer)，可以学到以下有意思的知识点：  
1. 可以通过`queue` 和`thread` 库来进行数据处理（生产者-消费者模式）    
2. `@functools.lru_cache(n)` 装饰器缓存函数执行结果，在某些场景下比较比较有用（科学计算时是否也可以用？）  
3. `scapy` 抓包以及数据的处理（内置数据结构）  
4. 根据数据报文特征判断`Application` 信息（能否添加从`session` 提取）  
5. [Open App Filter](https://www.openappfilter.com/#/) 特征库  


## Main.py  

```python  
from scapy.all import *
import config
import db
import util

# 创建数据队列
import queue
pkt_queue = queue.Queue()  

def _sniff():
    """
    _sniff 抓取数据表，打上时间戳并存储到数据包的队列
    """
    while True:
        sniff(iface=config.interface, prn=lambda pkt: pkt_queue.put((pkt, int(time.time()))), count=100)
        # 监听端口


def deal_pkt():
    """
    deal_pkt 分析数据包
    """
    from protocol import dns, tcp, udp, app

    cnt = 0
    while True:
        try:
            pkt, timestamp = pkt_queue.get()
            if not dns.read(pkt, timestamp):
                udp.read(pkt, timestamp)
                tcp.read(pkt, timestamp)
        except Exception as e:
            print("[deal_pkt] ", e)

if __name__ == '__main__':
    util.add_thread(deal_pkt)
    util.add_thread(_sniff)
    util.start_all_thread()

try:
    while True:
        time.sleep(10)
        print("queue size: {} , TCP sess: {}, UDP sess: {}, APP sess: {}"
              .format(pkt_queue.qsize(), len(tcp.sessions), len(udp.sessions), len(app.sessions)))

except KeyboardInterrupt:
    db.close()
    print("Bye")
    exit()
```

### config.py  
config.py 主要包含一些配置信息：  
```python  
mysql_settings = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": ""
}

interface = "eth0"
tcp_timeout = 600
udp_timeout = 600
app_timeout = 500
```

### util.py  
因为抓包和处理包都需要在独立的线程中执行，util.py 主要包含线程相关的方法：  
```python  
import time
from threading import Thread

threads = []  # 线程函数容器
threads_status = [] # 线程容器
crontab = []


def add_thread(func):
    """
    add_thread 添加线程函数
    """
    global threads
    threads.append(func)


def start_all_thread():
    """
    start_all_thread 将函数组装为线程，并执行
    """
    for thread_func in threads:
        # 组装线程
        threads_status.append(Thread(target=thread_func))

    for thread in threads_status:
        # 执行线程
        thread.start()


def add_cron(func, intval):
    """
    add_cron 添加定时任务：方法、周期
    """
    crontab.append({
        "func": func,
        "intval": intval,
        "_": 0  # 计时器，用于判断是否到达执行周期
    })


def crond():
    """
    周期性执行定时任务，每秒轮询一次
    """
    while True:
        time.sleep(1)
        # ...

add_thread(crond)  # 程序初始化时就添加定时任务的执行器
```

### db.py  
因为抓包的数据要存储在数据库中，db.py 主要是封装的数据库操作  

```python
def query(sql, callback=None):
    """
    query 并不会立即查询数据库，而是先暂存在一个全局变量
    """
    global sqls
    lock.acquire()
    sqls.append((sql, callback))
    lock.release()


def autocommit():
    """
    autocommit 每秒自动提交一次查询
    """
```

## protocol.py  
protocol.py 预先定义了流量的解析规则，包含DNS、TCP、UDP 和APP 分析等。在main.py 中可以发现`read(pkt, timestamp)` 方法是关键入口：     

### dns.py  
scapy 中预设了DNS 相关的数据结构：  
```python  
import functools

import db
from scapy.layers.dns import DNSRR, DNSQR, DNS
from scapy.layers.l2 import Ether  

def byte2str(s):
    """字节转字符串"""
    return s if isinstance(s, str) else s.decode()

def deal_dns_query(pkt, timestamp):
    # clean_dns 函数的作用是去掉域名最后的`.`
    qname = clean_dns(byte2str(pkt[DNSQR].qname))  # 数据包的DNS 信息
    reg_dns_rev_cache(qname, None)
    res = {
        "client_mac": pkt[Ether].src, # 数据包的以太网信息
        "domain": qname,
        "time": timestamp
    }
    sql = dns_query_sql.format(**res)
    db.query(sql)
    return True


def deal_dns_response(pkt, timestamp):
    for i in range(pkt[DNS].ancount):
        """        
        ancount 是 DNS 数据包中的一个字段，用于指示 DNS 响应中包含的资源记录（Answer Records）的数量。
        """
        dnsrr = pkt[DNS].an[i]
        rdata = clean_dns(byte2str(dnsrr.rdata))
        rrname = clean_dns(byte2str(dnsrr.rrname))
        reg_dns_rev_cache(rdata, rrname)
        res = {
            "type": pkt[DNS].an[i].type,
            "client_mac": pkt[Ether].dst,
            "domain": rrname,
            "rdata": rdata,
            "time": timestamp
        }
        sql = dns_response_sql.format(**res)
        db.query(sql)
    return True

def read(pkt, timestamp):
    """
    read 判断是否为DNS 包，如果不是则返回False，继续判断是否为TCP 或UDP  
    """
    try:
        if not pkt.haslayer(DNS): 
            return False
        if DNSQR in pkt and pkt.dport == 53:
            # 如果是包含查询的DNS 包
            return deal_dns_query(pkt, timestamp)
        elif DNSRR in pkt and pkt.sport == 53:
            # 如果是包含响应的DNS 包
            return deal_dns_response(pkt, timestamp)
        return False
    except Exception as e:
        print("[DNS] ", e)
        return False
```

这里有一个很有意思的装饰器`@functools.lru_cache(n)`，用于缓存函数的执行结果。如果传入的参数相同，则直接返回结果，从而加速程序执行。      
```python  
@functools.lru_cache(10000)
def _dns_reverse(rdata):
    if rdata == g_rdata:
        return g_qdata
    sql = "SELECT `domain` FROM `log_dns` WHERE `rdata`='{}' ORDER BY `id` DESC LIMIT 1"
    if g_dns_reverse_db_cur.execute(sql.format(rdata)):
        return g_dns_reverse_db_cur.fetchall()[0][0]
    return None
```


### tcp.py  
在处理tcp 报文时需要注意到session 的概念：  
```python
def deal_tcp(pkt, timestamp):
    # 基本的tcp 信息
    client_mac = pkt[Ether].src
    # ...
    sequin_str = ','.join([ip_src, port_src, ip_dst, port_dst])  
    rev_sequin_str = ','.join([ip_dst, port_dst, ip_src, port_src])
    seq_now = pkt["TCP"].seq

    # 会话已存在（只要源、目的端口一致即可）
    if sequin_str in sessions:
        """请求会话包"""
        pkt_dir = 1
        if pkt['TCP'].flags == 'S':
            # pkt['TCP'].flags == 'S' 用于检查数据包中的 TCP 标志是否为 SYN 
            # 如果是的话表示上一次的会话已经断开，应当中心建立新的会话
            write_db(sessions[sequin_str])
            del sessions[sequin_str]
            return deal_tcp(pkt, timestamp)
    elif rev_sequin_str in sessions:
        """响应会话包"""
        sequin_str = rev_sequin_str
        pkt_dir = 2
        if pkt['TCP'].flags == 'S':
            write_db(sessions[sequin_str])
            del sessions[sequin_str]
            return deal_tcp(pkt, timestamp)

    # 创建新的会话记录
    elif pkt['TCP'].flags == 'S':
        pkt_dir = 1
        # item 是预设的数据结构，包含tcp 报文信息
        sessions[sequin_str] = copy.deepcopy(item)
        sessions[sequin_str]["client_mac"] = client_mac
        # ... 报文信息
        sessions[sequin_str]["time_start"] = timestamp
        host = dns.dns_reverse(ip_dst)  # 根据IP 反查域名
        if host != ip_dst:  # 并不一定准确
            sessions[sequin_str]["host"] = host
    else:
        """
        在程序启动前就建立的tcp 链接不做处理
        """
        return True

    session = sessions[sequin_str]

    # 检查应用类型，是根据报文判断的，而不是根据session 的内容判断
    if pkt_dir == 1:
        tcp_features = app.get_features("TCP")  # 获取app 的特征信息
        for feature in tcp_features:
            app_name, sport, dport, host, dic = feature
            """
            # app_name:[proto;sport;dport;host;dict]
            # dict，以00:02 为例，表示tcp 载荷的int(00) 位置的数据为int(02, 16) 
            # -1:03 表示以0x03 结尾
            QQ:       [udp;  ;    ;     ;    00:02|-1:03,
                       tcp;  ;    ;     ;    02:02|-1:03,
                       tcp;  ;14000;    ;               ,
                       tcp;  ;8080;     ;    00:ca|01:3c,
                       tcp;  ;    ;     ;    00:00|01:00|02:00|03:15]
            """
            flag = True
            if sport != '' and sport != str(session['port_src']):
                continue
            if dport != '' and dport != str(session['port_dst']):
                continue
            if host != '' and host not in session['host']:
                continue
            flag = True
            try:
                for d in dic:
                    if len(d) == 2 and pkt['TCP'].payload.load[int(d[0])] != int(d[1], 16):
                        flag = False
                        break
            except:
                flag = False
            if flag:
                app.add(client_mac, app_name, timestamp, session["host"])
                break

    # 检查DUP，检查是否为Duplicated 报文  
    if seq_now in session['seq' + str(pkt_dir)]:
        return True

    # 写入session 信息（每隔一秒自动更新，而不是每次函数执行时再更新）
    session['len'] += payload_len
    session['seq' + str(pkt_dir)].append(seq_now)
    session['time_end'] = timestamp
    session['pkt_list'].append({
        "d": pkt_dir,
        "l": payload_len,
        "f": tcp_flag,
        "t": timestamp - session['time_start']
    })

    # check RST
    if 'R' in tcp_flag:
        result = write_db(session)
        del sessions[sequin_str]
        return result

    # check FIN
    if session['fin' + str(pkt_dir)] == 1:
        session['fin' + str(pkt_dir)] = 2
    if 'F' in tcp_flag:
        session['fin' + str(pkt_dir)] = 1

    if session['fin1'] == 2 and session['fin2'] == 2:
        result = write_db(session)
        del sessions[sequin_str]
        return result

    return True


def tcp_timeout():
    """
    检查TCP 连接的超时信息
    """
    print("[TCP] check tcp timeout")
    _del = []
    for session in sessions:
        if sessions[session]["fin1"] + sessions[session]["fin2"] >= 2 and \
                int(time.time()) - sessions[session]['time_end'] >= 60:
            write_db(sessions[session])
            _del.append(session)
        elif int(time.time()) - sessions[session]["time_end"] >= config.tcp_timeout:
            write_db(sessions[session])
            _del.append(session)
    for i in _del:
        del sessions[i]


util.add_cron(tcp_timeout, 60)

def read(pkt, timestamp):
    try:
        if not (pkt.haslayer(IP) and pkt.haslayer(TCP)):
            return False
        else:
            return deal_tcp(pkt, timestamp)
        return False
    except Exception as e:
        print("[TCP] ", e)
        return False
```

### udp.py  
处理UDP 报文的方法与TCP 大同小异。  


源码的Web 界面是通过PHP 制作的，超出知识范围了~~~