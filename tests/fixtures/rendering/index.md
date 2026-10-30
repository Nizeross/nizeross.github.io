+++
title = "写作约定与排版示例"
description = "这个数字花园的内容约定、Markdown 与数学公式示例。"
showHero = false
showAuthor = false
showDate = false
+++

{{< katex >}}

## 先写清楚问题

技术笔记交代环境、步骤和验证方法；读书笔记区分原文、转述和自己的理解；推断与结论尽量附上依据。

## 代码

为围栏标记语言，方便高亮与复制：

```python
def learn_by_building(question: str) -> str:
    return f"提出问题 → 动手验证 → 记录：{question}"
```

## 数学公式

在文章中加入 `{{</* katex */>}}`，随后可以使用行内公式 \(O(n \log n)\) 和独立公式：

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

## 图片

图片放在文章自己的目录，与 `index.md` 同级，再以相对路径引用。点击下面的图片可以放大。

![站点标志](logo.png)

## 链接与锚点

站内路径使用根相对链接，例如[关于页面](/about/)；同页链接可以跳转到[代码](#代码)。发布前检查会验证本地文件和生成页面的锚点。

## 内容维护

小修改保留原 slug，实质更新补充 `lastmod`。文章默认创建为草稿，检查通过后再提交审核。
