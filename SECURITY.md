# 安全审查与维护范围

## 本次执行的检查

2026-10-29 对本站锁定的 npm 依赖执行了完整 audit，并扫描作者维护的配置、模板和内容中常见凭据模式。检查 CI 最小权限、Actions 提交 SHA 与主题提交固定情况。扫描结果不等于完整渗透测试，尤其不能发现所有未知漏洞或历史 Git 对象中的敏感信息。

原来的第三方访问统计脚本已从 footer 与阅读量覆盖模板移除。注释中的旧 Firebase 集成配置已清理；Firebase 公共配置本身通常不是服务器密钥，但未启用的配置不应给维护者造成错觉。网站仍保留作者主动公开的联系信息。

## 主题上游审计需要单独解读

对固定 Blowfish 子模块的 package-lock 执行 `npm audit --prefix themes/blowfish --json`，发现 29 个有告警的包节点：1 low、10 moderate、17 high、1 critical。包含 Puppeteer、FTP、翻译工具、CSS 工具及图表相关依赖。本项目不会安装或运行主题的 Node 工具链；构建使用主题已编译 CSS。不能因此把 29 个告警全部归为网站运行时漏洞，也不能声称上游依赖没有问题。

涉及当前/潜在阅读运行时的 KaTeX 与 Mermaid 已通过站点资源覆盖处理：KaTeX 固定 0.19.1；Mermaid 固定 11.17.2，并从锁文件依赖重新打包，使用 DOMPurify 3.4.17 与 lodash-es 4.18.1。直接复制 npm 包里的预构建 bundle 可能仍携带旧版内嵌依赖，因此 Mermaid 使用 esbuild 根据审核后的依赖图打包。主题文件与子模块提交不变。

首页不会加载公式或图表脚本；只有相应文章按需加载。本项目不启用主题的图表、视频、图库等其他可选 shortcodes。后续启用新 shortcode 之前，应先审核它带入的前端脚本；本次没有对每个未使用的供应商 bundle 作“安全”背书。

报告可重生成：

```powershell
node scripts/audit_dependencies.cjs
```

本站与主题分别输出到 `reports/dependency-audit.json` 和 `reports/theme-audit.json`。脚本对本站漏洞或审计服务失败返回非零；上游主题结果保留为待跟踪信息。CI 的强制 audit 针对实际采用的站点工具链。

## 发布保护

PR 检查不读取生产密钥，不使用 `pull_request_target`。待批准的发布方案检查最终提交的人工审核，部署 job 才有 Pages 写权限与 OIDC 权限。分支保护与环境 reviewer 必须在 GitHub 设置中启用；当前现有生产 workflow 未改动，所以这项保护尚未在线生效。

## 后续维护

定期在独立分支更新依赖与主题，复核兼容范围和告警，再执行完整验证。公开问题报告不要包含 token、完整凭据或可利用的个人数据；先通过作者公开邮箱联系。不要用 `npm audit fix --force` 在未经检查的情况下升级整个主题。
