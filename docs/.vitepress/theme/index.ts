import { Theme, useData } from "vitepress"
import { watch } from "vue"
import "./custom.css"
import Layout from "./Layout.vue"

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import DefaultTheme from 'vitepress/theme'
import ContentTimeLine from "../components/ContentTimeLine.vue"
import ContentCategories from "../components/ContentCategories.vue"
import ContentTags from "../components/ContentTags.vue"
// import MathJax from "../components/MathJax.vue"



export default {
    Layout,
    extends: DefaultTheme,
    enhanceApp: ({ app, router, siteData }) => {
        app.use(ElementPlus)
        app.component('content-time-line', ContentTimeLine)
        app.component('content-categories', ContentCategories)
        app.component('content-tags', ContentTags)    
        // app.component('mathjax', MathJax)    
    },
    setup() {
        const { isDark } = useData()

        // 监听 VitePress 主题变化
        watch(
            () => isDark.value,
            (dark) => {
                // 切换 Element Plus 的 dark 模式
                if (dark) {
                    document.documentElement.classList.add('dark')
                } else {
                    document.documentElement.classList.remove('dark')
                }
            },
            { immediate: true }
        )
    }
} as Theme