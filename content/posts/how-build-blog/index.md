+++
date = '2026-03-31T17:01:46+08:00'
draft = false
tags = ["Hugo", "Blowfish"]
title = '记录一下折腾blog的经历'
+++

## 前言
   搭建本博客参考了Gemini 3.0 Pro，Blowfish官方文档以及其他人的博客，还是踩了不少坑的，有的文档已经过时或者操作过于繁琐，官方文档又很庞杂，AI也有一定幻觉.
 - [hugo官方文档](https://gohugo.io/documentation/)
 - [Blowfish文档](https://blowfish.page/zh-cn/docs/)
 - [褐瞳さん - 如何使用 Github Page 搭建自己的博客](https://www.hetong-re4per.com/posts/how-bulid-blog-on-github-page/)
## Step
### 创建项目
首先创建一个 Hugo 项目，site-name 记得替换成你的网站的名称（其实就是待会创建的文件夹名称）`hugo new site site-name`
可以看一眼它的项目结构，项目结构大概像这样：
```
site-name
├── archetypes  # 模板文件
├── assets      # 资源文件，如 Logo
├── config      # 配置文件夹
├── content     # 文章存放处
├── i18n        # 多语言资源
├── layouts     # 存放布局的文件夹
├── static      # 存放静态文件
├── themes      # 主题文件夹
└── hugo.toml   # 项目配置文件
```
然后可以添加第一篇文章
```
hugo new content posts/first-blog.md
```
这条命令会向 content 文件夹内新建一个 posts 文件夹，然后再根据默认模板创建一个 first-blog.md 文件
然后使用`hugo server`
即可在本地运行

### 覆盖主题
在 Hugo 中，你自己所写的主题文件优先级都是高于 `themes/主题名称/` 文件夹内主题的，所以可以很轻松的覆写你想 DIY 的部分

对于 themes 文件夹内的文件，你只需要保证在根目录有着同样文件结构就能够覆盖

例如目录部分，对于 blowfish 它的位置是 `themes/blowfish/layouts/partials/toc.html`，而我们只需要复制这个文件，并把它放在 layouts/partials/toc.html 即可

### 部署到Github Pages
* **本地预览**：`hugo server`
* **部署发布**：`git add .` -> `git commit -m "..."` -> `git push`
* **在线编辑**：在 GitHub 仓库按 `.` 进入 Web 编辑器。

## Tips
### 自定义图标添加
- [simpleicon](https://simpleicons.org/)


