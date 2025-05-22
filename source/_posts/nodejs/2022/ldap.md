---
title: LDAP 认证   
date: 2022-11-26    
tags:  
    - ldap    
    - 认证      
---  

通过阅读[shaozi/ldap-authentication](https://github.com/shaozi/ldap-authentication) 仓库的源码，来记录一下通过[ldapjs](http://ldapjs.org/index.html) 的过程。  

<!-- more -->
## ldap-authentication 源码逻辑  
这篇笔记中少了函数内部的Promise 的代码块，这样可能看起来逻辑更清晰吧。  

```js{43}
// ... 
const ldap = require('ldapjs')  // 项目底层是ldapjs 库  

// 创建ldap 连接，绑定并返回连接客户端对象  
async function _ldapBind(dn, password, starttls, ldapOpts){
    var client = ldap.createClient(ldapOpts);  
    // 判断连接并绑定成功
    return client;
}

// 查找并返回用户对象  
async function _searchUser(ldapClient, searchBase, usernameAttribute, username, attributes = null) {
    // 根据ldap 连接客户端查找并返回用户对象
    ldapClient.search(searchBase, searchOptions, function (err, res) {
      var user = null
      res.on('searchEntry', function (entry) {
        user = entry.object
      })
    }
    // 最后会解绑客户端
    res.on('end', function (result) {
        if (result.status != 0) {
          reject(new Error('ldap search status is not 0, search failed'))
        } else {
          resolve(user)
        }
        ldapClient.unbind()
    })
}

// 查找用户所在组
async function _searchUserGroups(ldapClient, searchBase, user, groupClass, groupMemberAttribute = 'member', groupMemberUserAttribute = 'dn') {
    // 基本上也是ldapClient.search() 方法的调用  
}

// 通过管理员账户认证
async function authenticateWithAdmin(...){
    // 1. 建立连接  
    ldapAdminClient = await _ldapBind()  
    // 2. 查找用户  
    var user = await _searchUser()  
    ldapAdminClient.unbind()  // 随即解除绑定  
    // 之后在查询组信息或者其他操作之前，都先进行了解绑操作，然后重新建立连接
}

// 通过普通用户自己的账号密码认证  
async function authenticateWithUser(){
    // 过程与上面大同小异，只不过不需要传入管理员账号密码了
}

// 验证用户是否存在
async function verifyUserExists(){
    // 与通过管理员账号认证类似，需要先传入有全局管理权限的用户信息  
}

// 最终的导出函数，对于上面方法的封装  
async function authenticate(options) {}
```
> The bind API only allows LDAP 'simple' binds (equivalent to HTTP Basic Authentication) for now.  
> 目前LDAPJS 只允许简单的绑定，也许这也是为什么上面代码会多次解绑的原因吧  
> Note that unbind operation is not an opposite operation for bind. Unbinding results in disconnecting the client regardless of whether a bind operation was performed.  
> 需要注意的是，取消绑定并不是绑定的逆操作，而是会直接断开客户端连接。

## 使用  
```js{29}
const { authenticate } = require('ldap-authentication')

async function main() {
    let authenticated = await authenticate({  // Simple 认证
        ldapOpts: {
            url: 'ldaps://10.9.250.2',  // 这里启用了ldaps 之后，需要禁用下面的startls 选项
            tlsOptions: {
                rejectUnauthorized: false  // 禁用证书验证
            }
        },
        userDn: 'cn=uname,cn=users,dc=domain,dc=local',  // 针对不同的服务器uname 可能是cn 也可能是uid
                                                         // 对于群晖则是cn
        userPassword: 'Passw0rd',
        userSearchBase: 'dc=domain,dc=local',
        usernameAttribute: 'sAMAccountName',  // 这里也是，有些服务器可能是uid 但是一般都为sAMAccountName
        username: 'uname',

        // 下面是返回组信息，用处不大  
        // groupsSearchBase: 'cn=users,dc=domain,dc=local',
        // groupClass: 'groupOfUniqueNames',
        // groupMemberAttribute: 'uniqueMember',
        // starttls: true
        // groupMemberUserAttribute: 'dn'
    })

    console.log(authenticated)
}

main().then()  // 异步主函数的用法:)
```

以上就是`ldap-authentication` 库的简单使用了，至于如何结合到自己的项目中，还需要进一步配合数据库、ORM、WebServer 一起使用。  

-----  
2022-11-26 Aachen  