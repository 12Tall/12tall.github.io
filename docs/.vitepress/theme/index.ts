import { Theme, useData } from "vitepress"
import { onMounted, watch } from "vue"
import "./custom.css"
import Layout from "./Layout.vue"

import ElementPlus, { ElMessage } from 'element-plus'
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

        onMounted(() => {
            watch(
                () => isDark.value,
                (dark) => {
                    const html = document.documentElement
                    if (dark) {
                        html.classList.add('dark')
                    } else {
                        html.classList.remove('dark')
                    }
                },
                { immediate: true }
            )

            // const menu = document.getElementById('context-menu');
            document.addEventListener('contextmenu', async (e) => {
                // @ts-ignore
                const mjxContainer = e.target.closest('mjx-container');
                // @ts-ignore
                if (mjxContainer && e.target.tagName == "svg") {
                    e.preventDefault()
                    const tex = mjxContainer.getAttribute("data-tex") ?? ""
                    await navigator.clipboard.writeText(tex);

                    ElMessage.success('公式已复制')
                }
            })
        })
    }
} as Theme