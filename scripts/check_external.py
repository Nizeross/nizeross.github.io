"""Optional online link report, separate from offline publication checks."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def check(url):
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'NizerossBlogLinkCheck/1.0'})
        with urllib.request.urlopen(request, timeout=15) as response:
            return {'url': url, 'status': response.status, 'ok': response.status < 400}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {'url': url, 'ok': False, 'reason': str(exc)}


if __name__ == '__main__':
    urls = set()
    for path in (ROOT / 'content').rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        urls.update(re.findall(r'https?://[^\s)\]>"\']+', text))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(check, sorted(urls)))
    target = ROOT / 'reports/external-links.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(results)} external links; {sum(x["ok"] for x in results)} reachable. Report: {target}')
    for result in results:
        if not result['ok']:
            print(f'Review: {result["url"]}: {result.get("reason", result.get("status"))}')
