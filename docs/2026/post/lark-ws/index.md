---
title: Lark websocket 长连接监听事件
date: 2026-03-24 08:36:29
description: Lark websocket 长连接监听事件
tags:
  - nodejs
  - websocket
  - lark

prev:
  text: Rime 输入法在Debian 上的安装过程
  link: "../rime-install"
next:
  text: Cloudflare Tunnel 配置与SSH 代理
  link: "../cloudflare-1"
---

# Lark websocket 长连接监听事件

一般的应用都是通过webhook 来传递事件信息的，最近忽然发现Lark/飞书居然支持用WebSocket 来传递事件了。这样自建服务应用就可以省去公网和域名了！

## 示例说明

关于自建应用与申请权限就过多不涉及了，详情可以参考[SDK 说明文档](https://open.larksuite.com/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN)。但是有两点需要注意：

1. 应用授权时尽量使用`tenant_access_token`而不是`user_access_token`，因为后者需要验证用户信息比较麻烦
2. 如果需要应用访问多维表格，则需要在多维表格右上角`…`，选择`更多`，添加`文档应用`，选择自己的应用，并赋予相关权限

:::code-group

```js [client.js]{17-20}
import * as Lark from "@larksuiteoapi/node-sdk";

// 创建Lark 客户端，用于主动调用Larek 的API
export const client = new Lark.Client({
  appId: "cli_xxxxxxxx",
  appSecret: "********",
  domain: Lark.Domain.Lark,
  loggerLevel: Lark.LoggerLevel.info,
});

// 创建Lark WS 长连接客户端，用于监听/分发事件
export const wsClient = new Lark.WSClient({
  appId: "cli_xxxxxxxx",
  appSecret: "********",
  domain: Lark.Domain.Lark,
  loggerLevel: Lark.LoggerLevel.info,
  wsConfig: {
    // 配置websocket 参数，否则容易报异常
    PingInterval: 30,
    PingTimeout: 5,
  },
});

/**
 * 回复用户消息
 * @param {string} user_id
 * @param {string} text
 */
export async function reply_message(user_id, text = "请稍候…") {
  await client.im.message.create({
    params: {
      receive_id_type: "user_id",
    },
    data: {
      receive_id: user_id,
      msg_type: "text",
      content: JSON.stringify({ text }),
    },
  });
}
```

```js [index.js]{12,17,21}
import * as Lark from "@larksuiteoapi/node-sdk";
import { wsClient, reply_message } from "./client.js";

// 注册事件分发
const eventDispatcher = new Lark.EventDispatcher({}).register({
  "card.action.trigger": async (data) => {},
  "im.chat.access_event.bot_p2p_chat_entered_v1": async (data) => {},
  p2p_chat_create: async (data) => {
    const user_id = data.sender.sender_id.user_id;
    reply_message(user_id, "Hello there!");
  },
  "im.message.receive_v1": async (data) => {
    let cmd = JSON.parse(data.message.content ?? "{}")["text"] ?? null;
    const user_id = data.sender.sender_id.user_id;
    switch (cmd) {
      case "生成周报": {
        export_weekly_report(user_id);
        break;
      }
      default: {
        reply_message(user_id, "当前消息只支持`生成周报`");
      }
    }
  },
});
// 启动监听
wsClient.start({ eventDispatcher });
```
:::
需要注意的是：ws 消息需要在3秒内响应完毕，否则就会触发重发，导致事件重复响应。因此，将事件处理程序通过异步函数封装处理是必须的选择。  

## 参考资料  
1. [[Bug]: [Feishu/Lark] WebSocket long connection fails - code: 1000040351, system busy #42354](https://github.com/openclaw/openclaw/issues/42354)
2. [SDK：消息](https://open.larksuite.com/document/server-docs/im-v1/introduction)  
3. [为什么飞书会回复多次呢？ #43](https://github.com/larksuite/node-sdk/issues/43)
