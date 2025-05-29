---
title: GitHub Actions  
date: 2022-08-03 
tag:   
  - CI
  - shell
  - vuepress
---


不出意外的话，在百度上搜索`GitHub Actions 自动部署`，大概率会得到阮一峰老师的[GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html)。然正如费曼先生所言：凡我不能创造,我就不能理解。这里记录一下在尽量不采用外部Actions 的情况下如何一步一步搭建本仓库的。  
<!-- more -->
## 基本概念  
按照个人理解，`GitHub Actions` 应该是Github 给提供的一个虚拟机环境，在开发者执行push、pull request 或其他指令时，自动触发事件，继而再执行一系列的脚本命令，用于打包、编译甚至发布代码的目的。  

`GitHub Actions` 保存在仓库`.github/workflows` 目录下：一系列的命令可以分组为一个`step`，顺序执行的`steps` 可以组成一个`job`，顺序执行的`jobs` 组成一个`workflow`。一个仓库可以定义多个`workflow`。最简单的Action 可以只包含一条命令`echo "Hello World!"`。  

::: details 这里是一个基本的`workflow` 模板：
```yaml
# This is a basic workflow to help you get started with Actions
# 基本的workflow 工作流

name: CI

# Controls when the action will run. 
# action 触发事件
on:
  # Triggers the workflow on push or pull request events but only for the master branch  
  # 只有在master 分支push 或pull request 时出发时间
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

  # Allows you to run this workflow manually from the Actions tab
  # 允许手动在Actions 面板执行workflow
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
# 一个workflow 由一个或多个顺序执行的job 组成
jobs:
  # This workflow contains a single job called "build"
  # 这个workflow 只包含一个build job
  build:
    # The type of runner that the job will run on
    # job 的运行环境
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    # job 中包含顺序执行的任务
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      # 检出$GITHUB_WORKSPACE 下的仓库代码，使job 可以访问
      - uses: actions/checkout@v2

      # Runs a single command using the runners shell
      # 运行一个shell 命令
      - name: Run a one-line script
        run: echo Hello, world!

      # Runs a set of commands using the runners shell
      # 运行一系列命令
      - name: Run a multi-line script
        run: |
          echo Add other actions to build,
          echo test, and deploy your project.

```
:::

于是，我们便可以利用这个虚拟机环境，在push 代码时，让其为我们自动签出`master` 分支、打包、部署到`gh-pages` 分支，在此之前我们需要：一个使用VuePress 的GitHub Pages 的仓库。至于如何创建这里不作赘述。    

## Vuepress 自动部署  
`GitHub Actions` 提供的虚拟机环境并不能记住我们的用户信息，和`http` 一样，属于无状态的，所以我们就需要一种类似于`jwt` 的令牌来表明我们的身份。
### Personal Access Token
在账号密码、ssh 之外，GitHub 还支持第三种用户身份验证方式：Personal Access Token(PAT)。生成PAT 的步骤请见[创建个人访问令牌](https://docs.github.com/cn/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token)，可以通过配置项赋予其一定的权限。有了PAT 之后，我们可以通过HTTPS 来执行一些Git 操作。例如：  
```bash
# http://user:password@doamin/path 也是http 传输用户信息的标准形式
git clone "https://{username}:{pat}@github.com/{username}/{repo}.git"
```
而在`GitHub Actions` 的`workflow` 中，我们可以通过环境变量`${ {secrets.TOKEN_NAME} }` 来传递。注意这里花括号间是不应该有空格的，但是为了避免vuepress 渲染时的问题，故而添加了空格。

### 自动部署脚本  
首先将上文生成的PAT 添加到仓库的secrets 中，然后在仓库中创建文件`.github/workflows/ci.yml`，参考[Vuepress-部署](https://www.vuepress.cn/guide/deploy.html#github-pages)编写如下脚本：  

```yaml
name: Deploy Hexo to GitHub Pages

on:
  push:
    branches:
      - master # 或你使用的默认分支名称

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout blog source
        uses: actions/checkout@v4
        with:
          path: blog

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20" # 设置 Node.js 版本

      - name: Install dependencies
        run: npm install
        working-directory: ./blog

      - name: Install Hexo CLI
        run: npm install -g hexo-cli
        working-directory: ./blog

      - name: Generate static pages
        run: hexo generate
        working-directory: ./blog

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          personal_token: ${{ secrets.ACCESS_TOKEN }}
          publish_dir: ./blog/public
          # external_repository: 12tall/12tall.github.io # 更改为你的 GitHub Pages 仓库, username 是你的用户名
          publish_branch: gh-pages # GitHub Pages 分支
```

将上述代码保存、提交并推送到master 分支，就可以自动打包并部署到GitHub Pages 了。

## 参考资料  
1. [GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html)
2. [Vuepress-部署](https://www.vuepress.cn/guide/deploy.html#github-pages)  
3. [利用 GitHub Actions 实现自动化部署 Hexo 到 Github Pages](https://hackergavin.com/2024/01/11/hexo-automate-deploy/)