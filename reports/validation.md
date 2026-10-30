# 本地验证记录

## 2026-10-30：回归文章博客

恢复原生背景图首页后，完整 `npm run verify` 已通过：38 项 Python 测试、3 项工作流测试、8 组桌面/移动端浏览器测试。正式构建输出 22 个 HTML，575 个内部引用与三个旧文章 URL 全部通过检查。新增检查确认 Categories、Projects、Links、Writing 不再生成，也不进入搜索索引。

公式与排版测试使用 tests/fixtures/rendering，并单独构建 .build/browser-site，不向正式站点添加测试页面。原公开页面与工作台模板已移入 archive/removed-site-sections/2026-10-30，可恢复。首页截图已更新；进入本轮前 public/ 中已有的未提交构建文件保持原样。

以下为上一轮重构的历史验证记录。

日期：2026-10-29。环境：Windows AMD64、Node 24.16.0、Python 3.14.3、Hugo Extended 0.154.5、Playwright Chromium。CI 准备使用 Ubuntu 24.04 / Python 3.11，但本次没有执行远程 workflow。

| 检查 | 实际结果 |
| --- | --- |
| Python 核心/内容/链接/写作助手/审核门槛单元测试 | 37/37 通过 |
| Workflow YAML 与发布依赖关系测试 | 3/3 通过 |
| 内容检查 | 13 份 Markdown，Frontmatter、命名、图片、Python 示例语法通过 |
| Markdown lint | 所有站点内容与根文档通过 |
| Hugo 构建 | 成功，Hugo 报告 49 Pages；输出到 .build/site |
| 生成页检查 | 40 个 HTML、1213 个内部引用，缺失文件/锚点和重复 ID 为 0 |
| 旧文章 URL | 3/3 保留 |
| Playwright 桌面与移动端 | 8/8 通过，包含复制到剪贴板与 Mermaid SVG 渲染 |
| axe WCAG A/AA | 首页、文章与移动菜单的受测状态未发现违规 |
| 本站 npm audit | 0 个已知漏洞（含开发依赖） |
| 上游主题锁文件审计 | 29 个有告警包节点，详见 SECURITY.md |
| 外链探测 | 8 个：7 个返回成功；知乎返回 403，保留原链接待人工验证 |
| Hugo 原生 archetype | technical 模板在隔离目录成功生成草稿 |

浏览器用例覆盖：主题切换后的实际计算颜色、水平溢出、搜索与文章跳转、代码高亮与复制、公式显示、图片放大、标题锚点、目录、阅读进度、Projects/About/Links/分类/标签页面、键盘打开移动菜单。截图和 HTML 报告已在本地生成。

首页资源在本地无压缩 HTTP 服务器下测得 11 个资源、约 286 KB（不含 HTML）；没有加载 KaTeX 或 Mermaid。该数据用于资源预算，不代表真实网络加载速度评分。

## 发现并修复的问题

- 旧文章未闭合代码围栏与 Markdown 格式问题。
- 主题的两份目录产生重复 ID，改为单份可折叠目录。
- 首页头像需要通过 Hugo 资源管线发布，不能直接假设磁盘文件就是静态 URL。
- 主题搜索初始化存在索引未加载就查询的竞态，现改为等待本地索引并安全创建结果节点。
- 装饰 SVG 与移动菜单缺少辅助说明，补充语义、键盘操作与焦点管理。
- Windows 沙箱各命令缓存路径不同，浏览器缓存固定到项目 .cache，测试服务器由单一运行器管理。
- Hugo GC 会清理原资源缓存，改为隔离 resourceDir；本次触及的历史缓存已恢复。
- npm 包的预构建图表 bundle 可能内嵌旧依赖，改从已审计的锁定依赖重建 Mermaid。

## 验证边界

本次没有更改远程仓库、Pages 设置、默认分支或域名，没有执行生产发布。Linux CI、GitHub 的环境审批和分支保护仍需授权后在远程验证。自动无障碍检查并不覆盖全部阅读器与所有交互状态；外链 403 不等于链接不存在。

复现命令见 README。机器报告与截图保存在本目录的 JSON/PNG 文件（默认忽略），HTML 浏览器报告位于 playwright-report/。完整上游审计与本站 audit 可通过 scripts/audit_dependencies.cjs 重新生成。
