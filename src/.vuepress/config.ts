import { defineUserConfig, PluginFunction } from "vuepress";
import theme from "./theme.js";
import { path } from '@vuepress/utils'
import { registerComponentsPlugin } from '@vuepress/plugin-register-components'
import { feedPlugin } from "vuepress-plugin-feed2"
import { commentPlugin } from "vuepress-plugin-comment2";


export default defineUserConfig({
  base: "/",

  locales: {
    "/": {
      lang: "zh-CN",
      title: "12Tall",
      description: "12Tall 的博客",
    },
  },

  head: [
    ['meta', { charset: 'utf-8' }],
    ['script', { type: 'text/javascript', src: 'https://cn.vercount.one/js', defer: true }],
  ],

  theme,

  shouldPrefetch: false,
  plugins: [
    <PluginFunction>registerComponentsPlugin({
      componentsDir: path.resolve(__dirname, './components')
    }),

    feedPlugin({
      hostname: "12tall.cn",
      rss: true
      // 插件选项
    }),

    commentPlugin({
      provider: "Giscus",
      repo: "12Tall/12tall.github.io",
      repoId: "MDEwOlJlcG9zaXRvcnkyOTY1NjE5MzU=",
      category: "General",
      categoryId: "DIC_kwDOEa0tD84CXgDH",
      lazyLoading: true
    }),
  ],
});
