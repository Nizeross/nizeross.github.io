# NIZEROSS 的个人网站

一个基于 Hugo + Blowfish 的个人数字花园，记录计算机学习、项目实践、阅读与生活。站点无需数据库或在线写作 API；Node 只用于开发检查，浏览器不运行应用框架。

## 从哪里开始

实际 Git 根目录是 `myblog/`；外层 `D:\hugo` 还存放历史 Hugo 二进制。Windows、Linux 均使用 Python 3.11+ 与 Node 24。首次克隆需要初始化主题子模块。

```powershell
git clone --recurse-submodules git@github.com:Nizeross/nizeross.github.io.git
cd nizeross.github.io
npm ci --ignore-scripts
python scripts/install_hugo.py
python scripts/sync_vendor.py
python scripts/site.py preview
```

预览地址为 `http://127.0.0.1:1313`，包含草稿。安装器固定 Hugo Extended 0.154.5 并校验 SHA-256；不要使用外层旧二进制。Linux 安装流程相同；当前安装器支持 Windows/Linux AMD64，其他平台需手动安装相同版本 Extended 到 `.tools/`。

## 日常写作

```powershell
python scripts/site.py new technical "理解虚拟内存" --slug virtual-memory
python scripts/site.py check
npm run lint
python scripts/site.py build
python scripts/check_site.py
```

五种类型为 `technical`、`project`、`reading`、`essay`、`life`。新文章在 `content/posts/<slug>/index.md`，默认草稿；图片和文章放在同一目录。中文标题可自动生成中文 slug；想要便于输入的 URL，可以显式传英文 `--slug`。不要随意改已有文章目录名。

`python scripts/site.py commit-draft` 只展示差异摘要和提交信息建议，不自动暂存、提交或推送。`python scripts/suggest.py <文章路径>` 离线提供摘要片段、标签与相关文章候选；它不是生成式 AI，也不修改正文。外链报告用 `python scripts/check_external.py` 单独生成。

## 验证与发布

```powershell
python -m unittest discover -s tests -v
npm run test:workflows
python scripts/security_check.py
npm run browsers
npm run test:e2e
npm run audit:dependencies
```

本地发布目录是 `.build/site/`；Playwright 会自动启动并关闭测试服务器。截图和浏览器结果保存在 `reports/`，HTML 报告在 `playwright-report/`。开发前先构建再执行浏览器测试。

浏览器安装完成后，可以用 `npm run verify` 一次执行全部本地检查。失败会停在对应阶段，并将完整输出保存为 `reports/verify.log`。

当前正式部署 workflow 仍然是原来的 `hugo.yaml`。重构只新增验证 CI，安全发布替换方案位于 `.github/workflow-proposals/pages.yml`，需要确认后启用。不要把本地改造完成理解为线上已更新，也不要在审核前直接推送 main。

## 文档导航

- [架构与审计](ARCHITECTURE.md)：为什么保留 Hugo、目录与数据流。
- [迁移计划](MIGRATION_PLAN.md)：阶段交付、兼容性和回滚。
- [开发流程](DEVELOPMENT.md)：写作、项目页和检查规则。
- [发布原理](DEPLOYMENT.md)：审核门槛、权限和上线步骤。
- [学习笔记](LEARNING_NOTES.md)：Git、HTTP、静态站点与测试背后的概念。
- [交付报告](DELIVERY_REPORT.md)：实际运行结果与剩余事项。
- [安全说明](SECURITY.md)：本站依赖与上游主题审计的不同范围。

原有文章、域名文件与历史生成目录均保留。不要编辑 `themes/blowfish/`：站点覆盖文件才是定制入口。
