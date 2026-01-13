---
title: 迁移记录
date: 2026-01-09 12:00:00
tags:
    - 迁移
---

- [x] `~-2025.05`: `VuePress Theme Hope` 文件多了之后感觉组织结构变得很复杂，整体感觉有些笨重。    
- [x] `2025.05~2026.01`: `Hexo Next` 方便，但是只要主题比较简单，对Markdown 功能的支持有限。  
- [ ] `2026.01~至今`: `VitePress` 配置不简单，但是对Markdown 支持较好，对Latex 需要单独配置。  


## MathJax 配置  
默认`markdown-it-mathjax3` 不支持直接复制公式图片为文本，因此需要给这个包打补丁。效果如下：  

1. 行内公式渲染：$\frac{1}{2}$    
2. 独立公式渲染（因为Markdown 字符串转义限制，换行时需要用`\\`替换`\`，或者通过`<p></p>` 包含公式内容）：  

$$
\begin{array}{c}
\nabla \times \vec{\mathbf{B}} -\, \frac1c\, \frac{\partial\vec{\mathbf{E}}}{\partial t} &
= \frac{4\pi}{c}\vec{\mathbf{j}}   \\
 \nabla \cdot \vec{\mathbf{E}} & = 4 \pi \rho \\
\nabla \times \vec{\mathbf{E}}\, +\, \frac1c\, \frac{\partial\vec{\mathbf{B}}}{\partial t} & = \vec{\mathbf{0}} \\
\nabla \cdot \vec{\mathbf{B}} & = 0
\end{array} \tag{1}
$$  

## 参考资料  
2. [数学方程](https://vitepress.dev/zh/guide/markdown#math-equations)
