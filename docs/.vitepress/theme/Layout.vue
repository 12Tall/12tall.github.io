<!--Layout.vue-->

<template>
    <Layout>
        <template #doc-footer-before> </template>
        <template #doc-after>
            <div style="margin-top: 24px" v-if="frontmatter.comment !== false">
                <Giscus :key="page.filePath" repo="12Tall/12tall.github.io" repo-id="MDEwOlJlcG9zaXRvcnkyOTY1NjE5MzU="
                    category="General" category-id="DIC_kwDOEa0tD84CXgDH" mapping="pathname" reactions-enabled="1"
                    emit-metadata="1" input-position="bottom" lang="zh-CN" loading="lazy"
                    :theme="isDark ? 'dark' : 'light'" />
            </div>
        </template>
    </Layout>
</template>

<script lang="ts" setup>
import Giscus from "@giscus/vue";
import DefaultTheme from "vitepress/theme";
import { watch } from "vue";
import { inBrowser, useData } from "vitepress";

const { frontmatter } = useData()

const { isDark, page } = useData();

const { Layout } = DefaultTheme;

watch(isDark, (dark) => {
    if (!inBrowser) return;

    const iframe = document
        .querySelector("giscus-widget")
        ?.shadowRoot?.querySelector("iframe");

    iframe?.contentWindow?.postMessage(
        { giscus: { setConfig: { theme: dark ? "dark" : "light" } } },
        "https://giscus.app"
    );
});
</script>