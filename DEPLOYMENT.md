# 自动化发布与审核边界

## 当前与拟议流程

线上现有 `.github/workflows/hugo.yaml` 未改动，仍是 push main 后构建发布。新增 `quality.yml` 只验证 PR、非 main 分支和手动运行；没有 Pages 写权限。它也可被审核后的发布流程复用。生产替换配置保存在 `.github/workflow-proposals/pages.yml`，GitHub 不会执行这个目录的文件。

因此，现阶段不能承诺远程 main 已被保护；连接读取的 rulesets 列表为空，经典分支保护与 Pages 环境设置未获得完整验证。本地代码已经提供审核门槛，但启用需要你批准并配置仓库。

## 为什么发布产物而不是再构建

拟议流程：PR 检查 → 人工批准最终文章 → 合并 main → 校验该提交关联的已合并 PR 与有效审核 → 完整质量检查 → 上传已经测试的 site artifact → github-pages 环境批准 → 发布。构建与测试失败不会触发部署，上一份线上成功版本继续存在。

审核门槛要求其他真人审核者批准最终 head commit，拒绝直接 push、过期审核、撤销审核和仍存在的请求修改。独立 gate 不替代分支保护，二者共同防止遗漏。单人维护时需要先选择一名可信审核者；作者不能在 GitHub 上批准自己的 PR。若要改为环境审批模式，需要另外讨论审核策略，不会自动降低门槛。

部署只获得 `pages:write` 与 `id-token:write`；验证仅有 `contents:read`。artifact 下载另需 `actions:read`。OIDC 让 GitHub 给部署 job 发短时凭据，不需要把长期个人 token 写进仓库。PR 流程不使用 `pull_request_target`，也不读取生产密钥。

## 缓存、版本和日志

Hugo Extended 版本、下载校验和、主题提交、npm 包和 Actions 提交 SHA 均有记录。Node 限定 24 大版本并使用 lockfile；Python 3.11 使用标准库。Hugo 缓存 key 包含工具链与提交，恢复只影响构建加速，不替代最终构建与测试。npm 缓存由 setup-node 按 lockfile 管理。

失败日志直接保留在对应 job step；Playwright 截图、trace、HTML/JSON 报告在失败时仍上传为 quality-reports，保留 7 天。网络外链检查不设为主检查，因为目标站反爬和临时故障会产生误报。密钥不出现在命令参数或脚本输出。

## 获得批准后的上线清单

1. 审阅 DELIVERY_REPORT 与截图，确认新首页、文章和项目内容。
2. 在 Pages 页面核对当前域名：仓库 CNAME 为 `kirisame.me`，原 baseURL 为 `https://nizeross.github.io`。确认唯一权威 URL 后，才修改 baseURL 或静态 CNAME 策略；目前两个都保留。
3. 将 proposal 作为 PR 中的新 `hugo.yaml`，避免两个发布 workflow 并行运行。首次切换 PR 可以先由旧流程发布，或者在维护窗口人工启用门槛；提前确认，不直接操作生产。
4. main 配置必须 PR、至少一名批准、撤销过期批准、必须通过 `Verify content and site`，禁止 force push 和审核绕过。为 `.github/` 变化指定可信维护者审核。
5. github-pages 环境设置 reviewer 和 main 分支限制。不要自动批准环境。确认 GitHub 账户与套餐支持所需保护。
6. 明确授权后推送本地分支、打开 PR；通过审阅后合并。检查 Actions、HTTPS、canonical、RSS、站内搜索和三个旧 URL。

本次不更改默认分支、Pages 发布源、域名或远程设置，不推送，也不部署。

## 回滚

通过回退变更的 PR 恢复已知可用版本并重新验证；不要 force push 回写 main。如果新发布失败，先保留当前线上版本，读第一个失败步骤，再修复并重跑。构建日志中的失败和浏览器报告中的断言失败需要分别排查。

参考：[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[保护分支](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)。
