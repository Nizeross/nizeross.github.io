# 架构与现状审计

审计日期：2026-10-29。工作区为 `D:\hugo`，实际 Git/Hugo 项目根为 `myblog/`；所有开发命令从该目录执行。初始工作区干净，基线提交 `efbb03e`，远程为 `git@github.com:Nizeross/nizeross.github.io.git`，默认分支 `main`。本次仅在本地 `refactor/blog-system` 开发。

## 决策：保留 Hugo + Blowfish

内容使用 Markdown + TOML Frontmatter；Hugo 在构建时生成 HTML、RSS、搜索 JSON。浏览器只加载主题现有库与少量原生 JavaScript，不引入 React、数据库或在线写作 API。Blowfish 子模块固定在 `3a9016a6d93f6d498ab5fc3b0aa7d51869962f25`，所有覆盖位于站点自己的 `layouts/` 和 `assets/`。

换成其他框架对三篇既有文章没有实质收益，却要重做 shortcode、图片处理、搜索和链接兼容。本方案保留 `/posts/<原目录>/`，用首页覆盖和独立 Projects 模板提供辨识度；构建和审核工具独立于主题，未来换主题仍能复用。

## 审计事实

| 项目 | 发现与处理策略 |
| --- | --- |
| 内容 | 三个 leaf bundle，含本地封面。保留文章正文与路径；首篇示例有未闭合代码围栏，修复语法并记录。 |
| 配置 | `config/_default/` 分文件；语言文件标为 English/en 但内容为中文，需修正；全站基础色遵循原生色板，白天纯白、夜间 #1E293B。 |
| 主题 | submodule，无本地改动；要求 Hugo Extended 0.141.0–0.154.5。工作区二进制为非 Extended 0.155.0，线上 workflow 用 Extended 0.141.0，需统一到受支持的 Extended 0.154.5。 |
| 输出 | 仓库根与 `public/` 都有历史生成文件。本次不删除；新本地构建输出到忽略的 `.build/site/`，避免修改这些历史文件。未来在确认后才从 Git 移除旧输出。 |
| 部署 | `.github/workflows/hugo.yaml` push main 后直接部署；整个 workflow 有 Pages 写权限、未做内容检查、Sass 未锁版本、npm 失败被忽略。保留现有 workflow 原样，提供待批准的替换方案。 |
| 域名 | 根 `CNAME` 为 `kirisame.me`；baseURL 仍为用户名地址。不能自行决定哪一个是权威域名，保持配置不变，批准迁移时再核对 Pages base URL。 |
| 远程 | 连接可见的 Nizeross 仓库只有 `nizeross.github.io`，未发现另一个可见用户名站点；这不是对所有私有仓库的证明。GitHub 最近一次部署 efbb03e 成功；读取 rulesets 返回空列表，不能证明已有审核保护。 |
| 安全 | 原 footer 请求第三方访问统计；有注释掉的 Firebase 配置。移除页面统计依赖，清理无效配置；自托管资源，不将在线 AI 设为必需。个人邮箱本来公开，保留用户身份资料。 |

## 数据与控制流

```text
Markdown + 本地图片 → 内容/格式检查 → Hugo → HTML/RSS/JSON
                                  ↓
                          链接、集成与浏览器测试
                                  ↓
                        PR 审核 → main → Pages artifact
```

站点代码：`layouts/`（首页、项目列表、小型扩展）、`assets/css/`（主题色板与排版）、`assets/js/`（阅读进度）。`content/` 是唯一文章来源；archetypes 定义五种文章与项目模板。`scripts/` 提供写作、验证、建议工具。Node 依赖只用于开发检查和浏览器测试；Python 3.11+ 使用标准库解析 TOML、HTML 与本地链接。

## 发布边界

新增 CI 只有 contents:read，不部署。生产 workflow 的建议版本保存在 `.github/workflow-proposals/`，不会被 GitHub 执行。最终需要人工批准替换旧工作流，并配置 main 必须 PR、必需检查、禁止绕过，以及 github-pages 环境审核。代码无法代替服务器端分支保护；未配置前不能声称审核已强制生效。本次不修改默认分支、远程、域名或 Pages 设置，也不推送。

参考：[Blowfish 自定义机制](https://blowfish.page/docs/advanced-customisation/)、[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[Hugo 安全配置](https://gohugo.io/configuration/security/)。
