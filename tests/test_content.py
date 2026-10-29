import sys
import importlib.util
import shutil
import tempfile
from unittest.mock import patch
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_content import ROOT, check_document, parse_document
from check_site import Document, resolve_reference
from suggest import similarity, tokens

spec = importlib.util.spec_from_file_location('blog_cli', ROOT / 'scripts/site.py')
blog_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blog_cli)
slugify = blog_cli.slugify

VALID = '''+++
title = "测试"
date = 2026-10-29T12:00:00+08:00
draft = true
contentType = "technical"
categories = ["技术学习"]
tags = ["Python"]
summary = "测试解析与验证。"
+++

## 一个标题

```python
print("ok")
```
'''


class ContentTests(unittest.TestCase):
    path = ROOT / 'content/posts/test-article/index.md'

    def errors(self, text):
        return check_document(self.path, text)

    def test_valid_toml_and_python(self):
        self.assertEqual(self.errors(VALID), [])

    def test_missing_frontmatter(self):
        self.assertTrue(self.errors('hello'))

    def test_unclosed_frontmatter(self):
        self.assertTrue(self.errors('+++\ntitle="oops"'))

    def test_invalid_toml(self):
        self.assertTrue(self.errors(VALID.replace('draft = true', 'draft = ???')))

    def test_missing_summary(self):
        self.assertTrue(self.errors(VALID.replace('summary = "测试解析与验证。"', '')))

    def test_draft_type(self):
        self.assertTrue(self.errors(VALID.replace('draft = true', 'draft = "true"')))

    def test_unknown_type(self):
        self.assertTrue(self.errors(VALID.replace('technical', 'unknown')))

    def test_reserved_kind(self):
        self.assertTrue(self.errors(VALID.replace('contentType', 'kind')))

    def test_naive_date(self):
        self.assertTrue(self.errors(VALID.replace('+08:00', '')))

    def test_invalid_tags(self):
        self.assertTrue(self.errors(VALID.replace('["Python"]', '"Python"')))

    def test_unclosed_code(self):
        self.assertIn('Unclosed code fence', self.errors(VALID.rstrip()[:-3]))

    def test_invalid_python(self):
        self.assertTrue(self.errors(VALID.replace('print("ok")', 'def broken(')))

    def test_missing_image(self):
        self.assertTrue(self.errors(VALID + '\n![alt](missing.png)'))

    def test_script_rejected(self):
        self.assertTrue(self.errors(VALID + '\n<script>alert(1)</script>'))

    def test_script_example_allowed(self):
        self.assertEqual(self.errors(VALID + '\n```html\n<script>alert(1)</script>\n```'), [])

    def test_chinese_slug(self):
        self.assertEqual(slugify('我的 第一篇！'), '我的-第一篇')

    def test_slug_blocks_paths(self):
        self.assertNotIn('/', slugify('../../unsafe/path'))

    def test_parser_body(self):
        self.assertIn('一个标题', parse_document(VALID)[1])

    def test_similarity(self):
        self.assertEqual(similarity({'a'}, {'a'}), 1)
        self.assertEqual(similarity({'a'}, {'b'}), 0)

    def test_chinese_tokens(self):
        self.assertIn('计算', tokens('计算机 Python'))


class LinkTests(unittest.TestCase):
    def test_relative_asset(self):
        site = ROOT / '.build/site'
        target, fragment = resolve_reference(site, '/posts/a/index.html', 'image.png')
        self.assertEqual(target, (site / 'posts/a/image.png').resolve())

    def test_external_skipped(self):
        self.assertIsNone(resolve_reference(ROOT, '/', 'https://example.com/'))

    def test_mail_skipped(self):
        self.assertIsNone(resolve_reference(ROOT, '/', 'mailto:x@example.com'))

    def test_fragments_decoded(self):
        self.assertEqual(resolve_reference(ROOT, '/', '#%E4%BB%A3%E7%A0%81')[1], '代码')

    def test_html_ids(self):
        doc = Document('<h2 id="a">Hi</h2><a href="#a">Link</a>')
        self.assertIn('a', doc.ids)
        self.assertEqual(doc.references, ['#a'])

    def test_duplicate_ids(self):
        self.assertEqual(Document('<p id="x"></p><p id="x"></p>').duplicates, ['x'])


class WritingAssistantTests(unittest.TestCase):
    def setUp(self):
        workspace_dir = ROOT / '.build/test-workspaces'
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(dir=workspace_dir)
        self.root = Path(self.workspace.name)
        (self.root / 'content/posts').mkdir(parents=True)
        (self.root / 'archetypes').mkdir()
        shutil.copy2(ROOT / 'archetypes/technical.md', self.root / 'archetypes/technical.md')
        self.root_patch = patch.object(blog_cli, 'ROOT', self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.workspace.cleanup()

    def test_creates_valid_draft(self):
        blog_cli.new_post('technical', '中文标题', 'safe-slug')
        path = self.root / 'content/posts/safe-slug/index.md'
        meta, body = parse_document(path.read_text(encoding='utf-8'))
        self.assertTrue(meta['draft'])
        self.assertEqual(meta['title'], '中文标题')
        self.assertEqual(check_document(path, path.read_text(encoding='utf-8'), self.root), [])

    def test_refuses_path_traversal(self):
        with self.assertRaises(ValueError):
            blog_cli.new_post('technical', 'Unsafe', '../../escape')

    def test_never_overwrites_existing_post(self):
        blog_cli.new_post('technical', 'First', 'same-slug')
        with self.assertRaises(FileExistsError):
            blog_cli.new_post('technical', 'Second', 'same-slug')
        meta, body = parse_document((self.root / 'content/posts/same-slug/index.md').read_text(encoding='utf-8'))
        self.assertEqual(meta['title'], 'First')


if __name__ == '__main__':
    unittest.main()
