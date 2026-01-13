import { createContentLoader } from 'vitepress'

export default createContentLoader('../docs/20*/**/*.md', {
    includeSrc: true, // 包含原始 markdown 源?
    render: true,     // 包含渲染的整页 HTML?
    excerpt: true,    // 包含摘录?
    transform(rawData) {
        // 根据需要对原始数据进行 map、sort 或 filter
        // 最终的结果是将发送给客户端的内容
        return rawData.sort((a, b) => {
            return +new Date(b.frontmatter.date) - +new Date(a.frontmatter.date)
        })
    }
})

export interface ContentData {
    // 页面的映射 URL，如 /posts/hello.html（不包括 base）
    // 手动迭代或使用自定义 `transform` 来标准化路径
    url: string
    // 页面的 frontmatter 数据
    frontmatter: Record<string, any>

    // 只有启用了相关选项，才会出现以下内容
    // 我们将在下面讨论它们
    src: string | undefined
    html: string | undefined
    excerpt: string | undefined
}