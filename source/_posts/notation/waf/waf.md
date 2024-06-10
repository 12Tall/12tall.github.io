---
title: 网页应用防火墙
date: 2024-06-10 08:27:33
tags: [firewall, ips, security]
---

高中那会儿通过黑客杂志了解到[啊D](https://www.d99net.net/)的WAF，感觉很神奇。现在才了解到是通过`ISAPI` 和[自定义模块](https://www.cnblogs.com/jmllc/p/14933269.html) 实现的。

<!--more-->

今天看到了雷池的介绍，没想到软件的工作原理也不复杂，是通过自建了一个代理服务器实现的。本来以为还要抓包，以及怎么将抓包的过程`透明地`嵌入HTTP 请求。通过代理就容易理解了。  

![雷池-配置教程](https://waf-ce.chaitin.cn/docs/assets/images/config_site3-b12ac242c64dc149db77d4f0741fa86f.png)  

-----  

20 岁时买到10 岁时喜欢的玩具，依然开心地像个孩子。