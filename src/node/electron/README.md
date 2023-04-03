---
title: Electron 跨域     
date: 2023-04-03    
timeLine: true
sidebar: false  
icon: nodeJS  
category:  
    - 开发  
    - Javascript  
    - Electron   
tag:  
    - cookie  
    - 跨域        
---    

因为Chrome 内核的限制，Electron 不能获取第三方站点的`set-cookie` 信息，从而无法保存用户登登录状态。

## 自定义消息   

本来以为自定义消息可以解决跨域不能设置`cookie` 的问题，但是后来发现并不能。  

```js  
const { protocol } = require('electron');
const path = require('path');

// fix cros issue: https://stackoverflow.com/a/57216953/14791867
protocol.registerSchemesAsPrivileged([{
    scheme: 'app',
    privileges: {
        standard: true,
        secure: true
    }
}]);

app.whenReady().then(() => {
    // fix cros issue: https://stackoverflow.com/a/57216953/14791867
    // and: https://www.electronjs.org/zh/docs/latest/api/protocol
    protocol.registerFileProtocol('app', (request, callback) => {
        const filePath = path.normalize(`${__dirname}/${request.url.slice('app://'.length)}`)
        console.log(filePath);
        callback(filePath)
    })
}
```


## 拦截HTTP 消息  

通过修改消息头，可以让Electron 误认为`SameSite=None; Secure`，但是要求链接必须是`https` 的。没办法，只能设置自签名证书了。

```js  
app.whenReady().then(() => {

    // fixed electron CROS issue:  https://cloud.tencent.com/developer/article/2137540  
    session.defaultSession.webRequest.onHeadersReceived(
        { urls: ['*://*/*'] },
        (details, callback) => {
            if (
                details.responseHeaders &&
                details.responseHeaders['Set-Cookie'] &&
                details.responseHeaders['Set-Cookie'].length &&
                !details.responseHeaders['Set-Cookie'][0].includes('SameSite=none')
            ) {
                for (var i = 0; i < details.responseHeaders['Set-Cookie'].length; i++) {
                    details.responseHeaders['Set-Cookie'][i] += '; SameSite=None; Secure';
                }
                details.responseHeaders['Access-Control-Allow-Origin'] = ['*']
            }
            callback({ cancel: false, responseHeaders: details.responseHeaders });
        },
    );
}
```

## 生成自签名证书  
在Ubuntu 下生成自签名证书的过程，可以参考[SSL 自签证书](https://juejin.cn/post/7173200213086044174)和[创建自用CA根证书并颁发自签名的泛域名证书](https://blog.jtwo.me/create-ca-root-and-self-signed-certificate/)
```bash  
# 1. 创建CA 私钥 
openssl genrsa -des3 -out ca.key 4096 

# 2. 创建CA 公钥
openssl req -x509 -new -key ca.key -out ca.pem -days 3650 # 10 年  
# 需要填写国家地区等信息  

# 3. 创建自签名服务私钥（可用于Nginx等程序）
openssl genrsa -out server.key 2048 # 即Nginx中的ssl_certificate_key参数  

# 4. 创建自签名请求  
openssl req -new -key server.key -out server.csr # Common Name: *.12tall.cn  

# 5. 生成签名证书   
openssl x509 -req -CAkey ca.key -CA ca.pem -in server.csr -out server.pem -CAcreateserial -days 3650  

# 6. 创建Server证书之后，与Ca证书合成完整的证书链
cat ca.pem server.pem > full-cert.pem  
```  

## Nginx 配置  
```nginx  
server {  
    # ... 
    ssl_certificate server/full.pem;
    ssl_certificate_key server/server-key.pem;
    # ...
}
```

## Electron 忽略证书错误  

```js  
app.commandLine.appendSwitch('--ignore-certificate-errors', 'true')
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    event.preventDefault()
    callback(true)
});    
```


因为个人比较懒，生成了一个`100` 年的证书，再配合上面的各种办法，一劳永逸了。