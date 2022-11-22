import { defineUserConfig } from "vuepress";
import theme from "./theme.js";
import {path} from '@vuepress/utils'  
import {registerComponentsPlugin} from '@vuepress/plugin-register-components'

export default defineUserConfig({
  base: "/",

  locales: {
    "/": {
      lang: "zh-CN",
      title: "12Tall",
      description: "12Tall 的博客",
    },
  },

  theme,

  shouldPrefetch: false,
  plugins: [
    registerComponentsPlugin({
      componentsDir: path.resolve(__dirname, './components')
    }),
  ],
});
