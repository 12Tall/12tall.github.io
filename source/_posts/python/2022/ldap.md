---
title: LDAP 相关   
date: 2022-08-03
tags:   
    - ldap      
    - server 
---  


轻量级目录访问协议。文中采用Python 来实现。代码运行在域控服务器上。  

<!-- more -->

## 准备工作  
- 微软[AD 域](../maintenance/windows/server/02_ad.md)  
- AD 域证书服务  
  - 证书颁发机构  
  - 证书颁发机构Web 注册 
  - 证书注册策略Web 服务（非必须）  
- 证书颁发机构  
- 包
  - ldap
  - pinyin 

### 安装AD 域证书服务  
安装AD 域证书的服务较简单，对于本文来说，只需安装`证书颁发机构`、`证书颁发机构Web 注册`两个服务就可以了。默认安装，如果不想在后面续签`CA` 证书，可以将证书期限设置为100 年。  

## 连接AD 域服务器  
可以选择是否采用ssl 协议来连接AD 域服务器。如果不采用ssl 则只能查询，否则还可以修改AD 域的内容。但是对于域外的计算机来说，配置CA 证书的教程不太好搜，于是我们可以在与服务器上安装AD 域证书服务，同时把ldap3 脚本托管在域服务器上。（因为加域的机器默认会信任域控签发的CA），LDAP3 的使用教程请参考[官方文档](https://ldap3.readthedocs.io/en/latest/)  

### 连接  
以ssl 连接为例  
```python
from ldap3 import MODIFY_REPLACE, Server, Connection, ALL, NTLM
import json
from datetime import datetime, timedelta
from dateutil.parser import parse

server = Server('192.168.227.10',  use_ssl=True,
                get_info=ALL, connect_timeout=5)
# server = Server('192.168.1.2',   # 域外查询
#                get_info=ALL, connect_timeout=5)

conn = Connection(server=server, user='12TALL\ldap3',
                  password='password',
                  authentication=NTLM,
                  auto_bind=True)

print(conn.extend.standard.who_am_i())  
# 输出：
# u:12TALL\Administrator
```

### ldap 查询条件  
- 整个ldap 查询条件必须被括号包起来  
- 逻辑运算以逻辑运算符开头，后接一系列条件，最后用括号包起来  
- 运算符
  - =：等于  
  - \>=：大于等于
  - \<=：小于等于  
  - \*：通配符 
- 逻辑运算符在表达式前面
  - &：逻辑与  
  - |：逻辑或
  - !：逻辑非  

### 查询用户  
一般用于管理员查询用户信息使用
```python
def get_user(account):
    conn.search(search_base='dc=12tall,dc=com',
                # 唯一用户名
                search_filter=f'(&(samAccountName={account}))',
                # 要查询的属性
                attributes=['memberOf', 'sn', 'department',
                            'createTimeStamp', 'accountExpires',
                            'userAccountControl', 'objectClass',
                            'pwdLastSet'],
                paged_size=5)

    return conn.response_to_json()
```

### 用户自查  
一般用于用户登录认证  
```python
def get_user_info(account, password):
    srv = Server('192.168.227.10', get_info=ALL, connect_timeout=5)
    # 注意：在bind 不成功时程序会报异常，而不是返回空值
    c = Connection(server=srv, user=f'12TALL\{account}',
                   password=password, authentication=NTLM,
                   auto_bind=True)
    c.search(search_base='dc=12tall,dc=com',
             # 唯一用户名
             search_filter=f'(&(samAccountName={account}))',
             # 要查询的属性
             attributes=['memberOf', 'sn', 'department',
                         'createTimeStamp', 'accountExpires',
                         'userAccountControl', 'objectClass',
                         'pwdLastSet'],
             paged_size=5)

    res = c.response_to_json()
    c.unbind()
    return res
```

### 查询组用户  
```python

def get_group_users(grp_name):
    user_list = []
    dn = json.loads(get_user(grp_name))['entries'][0]['dn']

    conn.search(search_base=dn,
                search_filter='(|(objectCategory=group)(objectCategory=user))',
                search_scope='SUBTREE',
                attributes=['member', 'objectClass',
                            'userAccountControl', 'samAccountName'],
                size_limit=5)
    for user in conn.entries[0].member:
        user_list.append(user)

    return user_list


if __name__ == "__main__":
    print(json.dumps(get_group_users('Domain Admins')))
```

### 添加账号  
主要是对照着填参数，比较繁琐。新增组织与新增用户基本操作一致。    
```python
def add_user(account, password, group='12TALL'):
    group_dn = json.loads(get_user(group))['entries'][0]['dn']
    user_dn = f'cn={account},{",".join(group_dn.split(",")[1:])}'
    print(group_dn, user_dn)
    conn.add(user_dn,
             attributes={
                 'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
                 'sAMAccountName': account,
                 'userPrincipalName': account,
                 'accountExpires': datetime.today()+timedelta(days=100*365),
                 'sn': '姓',
                 'GivenName':'名',
                 # 英文缩写
                 'Initials':'xingm', 
                 # 显示名为用户名
                 'displayName': account,
                 'telephoneNumber': '0000',
                 'Mail': 'mail@12tall.com',
                 "description": '描述'
             })
    # 添加用户到组
    conn.extend.microsoft.add_members_to_groups(user_dn, group_dn)
    # 修改用户密码
    conn.extend.microsoft.modify_password(
        user_dn, new_password=password)
    # 激活用户
    conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})
    return account, password


if __name__ == "__main__":
    print(add_user('u02', 'Cisco1234', 'Domain Admins'))
```

### 修改用户  
Windows 域的修改操作  
```python
def enable_user(account):
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})
    return


def disable_user(account):
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [514])]})
    return


def change_password(account, password):
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.extend.microsoft.modify_password(user_dn, new_password=password)
    return


def set_account_expires(account, expire_time):
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.modify(user_dn, {'accountExpires': [(MODIFY_REPLACE, [expire_time])]})
    return


def add_account_to_group(account, group):
    group_dn = json.loads(get_user(group))['entries'][0]['dn']
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.extend.microsoft.add_members_to_groups(user_dn, group_dn)
    

def del_account_from_group(account, group):
    group_dn = json.loads(get_user(group))['entries'][0]['dn']
    user_dn = json.loads(get_user(account))['entries'][0]['dn']
    conn.extend.microsoft.remove_members_from_groups(user_dn, group_dn)


if __name__ == "__main__":
    del_account_from_group('u02','Domain Admins')
```


## 参考链接  
1. [Pyhton LDAP操纵微软域](https://www.bilibili.com/video/BV1aa411F7W1)  
2. [Welcome to ldap3’s documentation](https://ldap3.readthedocs.io/en/latest/)  
3. [Ldap3 库使用方法（一）](https://zhuanlan.zhihu.com/p/52532191)  
4. [LDAP的filter查询详解](https://www.cnblogs.com/mafeng/p/10945220.html)  
5. [AD用户属性对照表](https://blog.51cto.com/gaowenlong/1970397)