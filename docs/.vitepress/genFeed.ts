import path from 'path'
import { writeFileSync } from 'fs'
import { Feed } from 'feed'
import { createContentLoader, type SiteConfig } from 'vitepress'

const baseUrl = `https://12tall.github.io`

export async function genFeed(config: SiteConfig) {
    // https://laros.io/generating-an-rss-feed-with-vitepress
    const feed = new Feed({
        title: '逗苗二号',
        description: '蝉噪林愈静 鸟鸣山更幽',
        id: baseUrl,
        link: baseUrl,
        language: 'zh-CN',
        image: `${baseUrl}/logo.jpeg`,
        favicon: `${baseUrl}/favicon.ico`,
        copyright:
            'Copyright © 2016-present 12Tall'
    })

    // You might need to adjust this if your Markdown files 
    // are located in a subfolder
    const posts = await createContentLoader('*.md', {
        excerpt: true,
        render: true
    }).load()

    posts.sort(
        (a, b) =>
            +new Date(b.frontmatter.date as string) -
            +new Date(a.frontmatter.date as string)
    )

    for (const { url, excerpt, frontmatter, html } of posts) {
        feed.addItem({
            title: frontmatter.title,
            id: `${baseUrl}${url}`,
            link: `${baseUrl}${url}`,
            description: excerpt,
            content: html,
            author: [
                {
                    name: '12Tall',
                    email: 'fb.ouyang@outlook.com',
                    link: `${baseUrl}`
                }
            ],
            date: frontmatter.date
        })
    }

    writeFileSync(path.join(config.outDir, 'rss.xml'), feed.rss2())
}