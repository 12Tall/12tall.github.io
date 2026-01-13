import { defineConfig, } from 'vitepress'
import { genFeed } from './genFeed'
import markdownItTaskLists from 'markdown-it-task-lists'




// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "逗苗二号",
  lang: "zh-CN",

  description: "蝉噪林愈静 鸟鸣山更幽",
  themeConfig: {
    logo: '/logo.jpeg',
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '时间轴', link: '/timeline' },
      { text: '分类', link: '/categories' },
      { text: '标签', link: '/tags' },
      { text: '关于', link: '/about' }
    ],

    sidebar: {},
    // outline: {
    //   level: [2, 4]
    // },
    footer: {
      message: '蝉噪林愈静 鸟鸣山更幽',
      copyright: 'Copyright © 2016-present <a href="https://github.com/12Tall">12Tall</a> | <a href="/rss.xml">RSS 订阅</a>'
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/12Tall' },
    ],


    search: {
      provider: 'local'
    }
  },
  markdown: {
    math: true,
    config(md) {
      md.use(markdownItTaskLists)
    },
  },
  buildEnd: genFeed
})

