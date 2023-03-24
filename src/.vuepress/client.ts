// import { defi } from '@vuepress/client'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import { defineClientConfig } from '@vuepress/client'

export default defineClientConfig({
  enhance: ({ app, router, siteData }) => {
    app.use(ElementPlus);
  },
})

