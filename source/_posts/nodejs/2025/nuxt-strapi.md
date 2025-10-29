---
title: Nuxt 结合Strapi 建站
date: 2025-10-29 15:27:01
tags:
    - nuxt4  
    - vue3
    - strapi  
    - cms
---

曾经用`Nuxt3/Strapi` 建了一个公司主页，但是将近一年没看，几乎忘完了。权且做些笔记，如果后面重构的话可以快速上手。  

`Nuxt`的很多功能都是通过模块实现的，在[集成/模块](https://nuxt.com.cn/modules)可以搜索需要的模块。

<!-- more -->  

## 国际化/i18n  
[@nuxtjs/i18n ](https://nuxt.com.cn/modules/i18n) 通过`json` 配置多语言。在其官方仓库内有[示例](https://github.com/nuxt-modules/i18n/tree/main/playground)，同时该模块可以配合[VSCode/i18n-ally](https://github.com/lokalise/i18n-ally)插件使用。唯一需要注意的是，可能需要配置一下该插件的[路径匹配规则](https://github.com/lokalise/i18n-ally/wiki/Path-Matcher#example-1)。


## Strapi 模块  
[@nuxtjs/strapi ](https://nuxt.com.cn/modules/strapi)基本按教程配置就行，但是开发环境下可能需要配置代理服务器： 
```js
export default defineNuxtConfig({
  // ...
  strapi: {
    // Options
    url: "https://www.xxxx.com",
    prefix: "/strapi",
    admin: "/admin",
    version: "v5",
    cookie: {},
    cookieName: "strapi_jwt",
  },
 
  // ...
  nitro: {
    devProxy: {
      "/uploads": {
        target: "http://127.0.0.1:1337/uploads",
        changeOrigin: true,
      },
    },
  },
  // ...
});
```

## 富文本  
虽然Strapi 插件市场提供了一些富文本插件，但是要想白嫖又好用，可以使用[@_sh/strapi-plugin-ckeditor](https://github.com/nshenderov/strapi-plugin-ckeditor)。该插件是strapi 插件，注意不要安装到nuxt 环境中。使用时可能有一些css 样式不能正确显示，需要在nuxt 中微调：
```css
figure.image {
  display: table;
  clear: both;
  text-align: center;
  margin: 0.9em auto;
  min-width: 50px;
}

figure.image img {
  max-width: 100%;  /* 图片宽度最多与父容器相等 */
  height: auto;     /* 按比例缩放 */
  display: block;   /* 避免默认的 inline 间隙 */
}

figure.image.image-style-block-align-left {
  margin-left: 0;
  margin-right: auto;
}

figure.image.image-style-block-align-right {
  margin-left: auto;
  margin-right: 0;
}
```

## Nuxt 注意事项  
Nuxt 新建项目中许多文件夹是不需要的，比较重要的是：  
- `pages` 用于处理路由  
- `servers` 用于处理特殊的前端请求，如数据交互等  
- `public` 表示公共资源  
- `plugins` 注册前端插件，用`element-plus-icon` 时用到了

其他的就还好。  

配合[pm2/Nginx/Let's Encrypt](https://12tall.github.io/2025/05/22/linux/acme/)，基本功能就搞定了。