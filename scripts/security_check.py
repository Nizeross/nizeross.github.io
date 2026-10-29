"""Scan authored inputs for obvious credentials and unsafe CI patterns."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}',
            r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'AKIA[0-9A-Z]{16}']


def main():
    failures = []
    for folder in ('content', 'config', 'assets/js', 'layouts', '.github'):
        for path in (ROOT / folder).rglob('*'):
            if path.is_file() and path.suffix in ('.md', '.toml', '.js', '.html', '.yml', '.yaml'):
                text = path.read_text(encoding='utf-8')
                if any(re.search(pattern, text) for pattern in PATTERNS):
                    failures.append(f'Possible credential in {path.relative_to(ROOT)} (value redacted)')
                if 'busuanzi.ibruce.info' in text:
                    failures.append('Unexpected external analytics script')
    workflow = (ROOT / '.github/workflows/quality.yml').read_text()
    if 'pull_request_target' in workflow or 'pages: write' in workflow or 'id-token: write' in workflow:
        failures.append('Quality workflow must not publish or run privileged PR code')
    for reference in re.findall(r'uses:\s*(\S+)', workflow):
        if not re.fullmatch(r'[\w.-]+/[\w.-]+@[a-f0-9]{40}', reference):
            failures.append('Unpinned quality workflow action')
    lock = json.loads((ROOT / 'toolchain.json').read_text())
    commit = subprocess.check_output(['git', '-C', 'themes/blowfish', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if commit != lock['themeCommit']:
        failures.append('Theme commit changed; re-audit and update toolchain.json intentionally')
    print('\n'.join(failures) if failures else 'PASS: authored inputs, minimal CI permissions and pinned theme')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
