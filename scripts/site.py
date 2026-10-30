"""Local writing/build assistant. It never pushes or commits automatically."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'technical': '技术学习', 'project': '项目开发', 'reading': '读书笔记',
         'essay': '思想随笔', 'life': '生活记录'}


def slugify(text):
    text = unicodedata.normalize('NFKC', text).lower().strip()
    return re.sub(r'-+', '-', re.sub(r'[^\w\-]+', '-', text, flags=re.UNICODE)).strip('-_')


def hugo():
    binary = ROOT / '.tools' / ('hugo.exe' if os.name == 'nt' else 'hugo')
    if not binary.exists():
        raise SystemExit('Run python scripts/install_hugo.py first.')
    result = subprocess.check_output([str(binary), 'version'], text=True)
    pin = json.loads((ROOT / 'toolchain.json').read_text())['hugo']
    if f'v{pin}' not in result or 'extended' not in result:
        raise SystemExit(f'Requires Hugo Extended {pin}: {result}')
    return str(binary)


def run(*args):
    env = dict(os.environ, HUGO_RESOURCEDIR=str(ROOT / '.build/resources'))
    subprocess.run(args, cwd=ROOT, check=True, env=env)


def new_post(kind, title, slug=None):
    if kind not in KINDS:
        raise ValueError('Unknown content kind')
    slug = slug or slugify(title)
    if not slug or not re.fullmatch(r'[\w]+(?:[-][\w]+)*', slug):
        raise ValueError('Slug must contain letters, numbers and hyphens; no paths')
    folder = ROOT / 'content' / 'posts' / slug
    if folder.exists():
        raise FileExistsError(f'Article already exists: {folder}')
    folder.mkdir()
    template = (ROOT / 'archetypes' / f'{kind}.md').read_text(encoding='utf-8')
    template = template.replace('{{ .Date }}', dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    template = template.replace('{{ printf "%q" .Name }}', json.dumps(title, ensure_ascii=False))
    (folder / 'index.md').write_text(template, encoding='utf-8')
    print(f'Created draft: {folder / "index.md"}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('new')
    new.add_argument('kind', choices=KINDS)
    new.add_argument('title')
    new.add_argument('--slug')
    for name in ('build', 'preview', 'check', 'commit-draft'):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == 'new':
        new_post(args.kind, args.title, args.slug)
    elif args.command == 'build':
        run(sys.executable, 'scripts/sync_vendor.py')
        run(hugo(), '--destination', '.build/site', '--cacheDir', str(ROOT / '.cache/hugo'), '--cleanDestinationDir', '--gc', '--minify')
    elif args.command == 'preview':
        run(hugo(), 'server', '--buildDrafts', '--destination', '.build/preview', '--bind', '127.0.0.1', '--port', '1313')
    elif args.command == 'check':
        run(sys.executable, 'scripts/check_content.py')
    else:
        run('git', 'diff', '--stat')
        print('\nCommit draft: docs: add <article slug>\nReview with git diff, stage exact paths, then git commit. No commit or push was performed.')


if __name__ == '__main__':
    main()
