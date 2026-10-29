"""Check every generated internal link, asset reference and fragment."""
import argparse
from html.parser import HTMLParser
import json
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'nizeross.github.io', 'kirisame.me', 'localhost', '127.0.0.1'}


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.references, self.duplicates = set(), [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.duplicates.append(attrs['id'])
            self.ids.add(attrs['id'])
        for attr in ('href', 'src', 'poster'):
            if attrs.get(attr):
                self.references.append(attrs[attr])


def resolve_reference(site, source_url, reference):
    parsed = urlsplit(urljoin('https://nizeross.github.io' + source_url, reference))
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in HOSTS:
        return None
    target = (site / unquote(parsed.path).lstrip('/')).resolve()
    if not target.is_relative_to(site.resolve()):
        raise ValueError('Link escapes output directory')
    if target.is_dir() or parsed.path.endswith('/'):
        target /= 'index.html'
    return target, unquote(parsed.fragment)


def check_site(site):
    site = site.resolve()
    pages = {p: Document(p.read_text(encoding='utf-8')) for p in site.rglob('*.html')}
    errors, count = [], 0
    for path, doc in pages.items():
        relative = path.relative_to(site).as_posix()
        source = '/' + relative
        for duplicate in doc.duplicates:
            errors.append(f'{relative}: duplicate id #{duplicate}')
        for reference in doc.references:
            try:
                resolved = resolve_reference(site, source, reference)
            except ValueError as exc:
                errors.append(f'{relative}: {exc}: {reference}')
                continue
            if not resolved:
                continue
            count += 1
            target, fragment = resolved
            if not target.is_file():
                errors.append(f'{relative}: missing {reference}')
            elif fragment and target in pages and fragment not in pages[target].ids:
                errors.append(f'{relative}: missing fragment {reference}')
    legacy = json.loads((ROOT / 'tests/legacy-urls.json').read_text())
    for url in legacy:
        if not (site / url.strip('/') / 'index.html').is_file():
            errors.append(f'Legacy URL removed: {url}')
    for asset in ('index.xml', 'index.json', 'sitemap.xml', 'robots.txt'):
        if not (site / asset).is_file():
            errors.append(f'Missing feed/search/SEO output: {asset}')
    search = json.loads((site / 'index.json').read_text(encoding='utf-8'))
    if not any('PCL2' in x.get('title', '') for x in search):
        errors.append('Existing PCL2 article is missing from search index')
    print(f'{len(pages)} HTML pages, {count} internal references, {len(legacy)} legacy URLs')
    return errors


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', default='.build/site')
    args = parser.parse_args()
    failures = check_site(Path(args.directory))
    print('\n'.join(failures) if failures else 'PASS: internal links, assets, anchors, RSS, search and legacy URLs')
    raise SystemExit(bool(failures))
