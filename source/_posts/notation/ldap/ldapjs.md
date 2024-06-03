---
title: ldapjs 笔记
date: 2024-06-03 20:45:27
tags: [ldap, monitor, 389, 636, synology, 群晖, monitor ]
categories: [开发]  
---

> 群晖中如果出现`636` 端口关闭、`389` 端口要求强认证，那么大概问题是出在证书配置错误了，需要将`Synology Directory Server` 的证书恢复为域名相同。

<!--more-->  

## LDAP 筛选器语法   
LDAP 筛选器的语法的逻辑运算符在前面，主要有`&,|,!`，然后以`()`包围。数值运算主要有`=,>=,<=`。再包含一个通配符`*`。基本就够用了，例如：  
```plaintext

(| (& (mail>=b@example.com) (mail=b@example.com)) (sn=c*d))
```
也许用语法图表示下更形象：  
```antlr4
filter: expr

expr
    : LP andExpr RP
    | LP orExpr RP
    | LP notExpr RP
    | simpleExpr

andExpr
    : AND expr expr

orExpr
    : OR expr expr

notExpr
    : NOT expr

simpleExpr
    : LP ATTR (EQ | GE | LE) VAL RP

LP    : '(' 
RP    : ')' 
AND   : '&' 
OR    : '|' 
NOT   : '!' 
EQ    : '=' 
GE    : '>=' 
LE    : '<=' 
```

还是要注意表达式在语法中的重要地位。

### LDAP 查询注入  
在某些LDAP 服务器中，会存在注入的漏洞。例如：将`(attribute=$input)` 中的`$input` 输入为`value)(injected_filter`，便有可能使后续的条件失效。

## LDAPJS 查询   
NodeJS 的所有IO 操作都是基于[libuv](https://luohaha.github.io/Chinese-uvbook/source/introduction.html)，是非阻塞的，`ldapjs` 也是类似，基本上是基于回调函数来实现查询：  
```js
// npm install ldapjs
const ldap = require('ldapjs');  

// LDAP服务器的URL
const ldapUrl = 'ldaps://10.22.33.36';

// LDAP服务器的基本DN
const baseDN = 'dc=exp,dc=com';

// 创建LDAP客户端
const client = ldap.createClient({
    url: ldapUrl,
    tlsOptions: {
        rejectUnauthorized: false // 忽略证书错误
    }
});

// bind 相当于用户登录
client.bind(user_dn, passwd, (err) => {
    console.log(err);
});

client.search('dc=exp,dc=com', {
    filter: '(objectClass=user)',  // 过滤器，查询用户
    scope: 'sub',  // 有三种，sub 是查询所有子节点
    attributes:['cn'],  // 需要的属性，默认全部属性
    // 还有分页信息可以传入，但不是必须
}, (err, res) => {
    res.on('searchRequest', (searchRequest) => {
        console.log('searchRequest: ', searchRequest.messageId);
    });
    res.on('searchEntry', (entry) => {
        // 这里是每一条符合条件的结果都会调用一次on-searchEntry 方法
        console.log(entry.pojo.attributes)
    });
    res.on('searchReference', (referral) => {
        console.log('referral: ' + referral.uris.join());
    });
    res.on('error', (err) => {
        console.error('error: ' + err.message);
    });
    res.on('end', (result) => {
        console.log('status: ' + result.status);
        client.unbind((err) => {
            assert.ifError(err);
        });
    });
})
```

### 查询结果  
以群晖为例，其中常用的属性有`[cn, mail, givenName, sn, displayName, memberOf, whenChanged, userPrincipalName, sAMAccountName, objectGUID]`：  
```js
[
  {
    type: 'objectClass',
    values: [ 'top', 'person', 'organizationalPerson', 'user' ]
  },
  { type: 'cn', values: [ 'xxx' ] },
  { type: 'instanceType', values: [ '4' ] },
  { type: 'whenCreated', values: [ '20240222023600.0Z' ] },
  { type: 'uSNCreated', values: [ '4038' ] },
  { type: 'name', values: [ 'xxx' ] },
  { type: 'objectGUID', values: [ 'xxxxxxxxxx' ] },
  { type: 'codePage', values: [ '0' ] },
  { type: 'countryCode', values: [ '0' ] },
  { type: 'lastLogoff', values: [ '0' ] },
  { type: 'primaryGroupID', values: [ '513' ] },
  {
    type: 'objectSid',
    values: [
      'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ]
  },
  { type: 'accountExpires', values: [ '9223372036854775807' ] },
  { type: 'sAMAccountName', values: [ 'xxx' ] },
  { type: 'sAMAccountType', values: [ '805306368' ] },
  { type: 'userPrincipalName', values: [ 'xxx@xxx.com' ] },
  {
    type: 'objectCategory',
    values: [ 'CN=Person,CN=Schema,CN=Configuration,DC=xxx,DC=com' ]
  },
  { type: 'mail', values: [ 'xxx@xxx.com' ] },
  { type: 'description', values: [ 'XXX' ] },
  { type: 'displayName', values: [ 'XXX' ] },
  { type: 'givenName', values: [ 'XXX' ] },
  { type: 'sn', values: [ 'XXX' ] },
  { type: 'userAccountControl', values: [ '66048' ] },
  { type: 'lockoutTime', values: [ '0' ] },
  {
    type: 'memberOf',
    values: [
      'CN=vpn-users,CN=Users,DC=xxx,DC=com',
      'CN=default-users,CN=Users,DC=xxx,DC=com',
      'CN=IT,CN=Users,DC=xxx,DC=com'
    ]
  },
  { type: 'lastLogonTimestamp', values: [ '133614245182887960' ] },
  { type: 'pwdLastSet', values: [ '133616164634316900' ] },
  { type: 'whenChanged', values: [ '20240531080743.0Z' ] },
  { type: 'uSNChanged', values: [ '4982' ] },
  { type: 'badPasswordTime', values: [ '133618697735623060' ] },
  { type: 'badPwdCount', values: [ '0' ] },
  { type: 'lastLogon', values: [ '133618902525867560' ] },
  { type: 'logonCount', values: [ '128' ] },
  {
    type: 'distinguishedName',
    values: [ 'CN=xxx,CN=Users,DC=xxx,DC=com' ]
  }
]
```

### 比较Entry 变化  
因为主要用到ldap 中的用户组信息，直接更新到`postgresql` 是没问题的，但是还要与Lark 进行数据同步，这样就要比较下哪些属性是新加的，哪些是作废的：  
```js
// 通过以下函数可以快速比较数组中的元素变化O(1)
function compareArrays(oldArray, newArray) {
    const result = {
        added: [],
        removed: []
    };

    // 创建集合来存储旧数组和新数组的元素
    const oldSet = new Set(oldArray);
    const newSet = new Set(newArray);

    // 找出新数组中有但旧数组中没有的元素
    newArray.forEach(item => {
        if (!oldSet.has(item)) {
            result.added.push(item);
        }
    });

    // 找出旧数组中有但新数组中没有的元素
    oldArray.forEach(item => {
        if (!newSet.has(item)) {
            result.removed.push(item);
        }
    });

    return result;
}

// 如果条目不多的话可以用下面方法O(n)
function compareArrays(oldArray, newArray) {
    const added = newArray.filter(item => !oldArray.includes(item));
    const removed = oldArray.filter(item => !newArray.includes(item));

    return { added, removed };
}
```