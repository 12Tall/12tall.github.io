---
title: 浏览器中移除事件监听
date: 2025-07-10 15:53:53
tags:
    - hack
    - chrome
---

某些页面会拦截事件，导致无法复制粘贴内容。这时可以通过调试工具移除事件监听。该方法仅在控制台可用。  
```js
// 以`复制`事件为例
document.removeEventListener('copy', getEventListeners(document)['copy'][0].listener)
```