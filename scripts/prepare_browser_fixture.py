"""Build test-only Markdown samples outside the public site's content tree."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    (ROOT / '.build').mkdir(exist_ok=True)
    content = Path(tempfile.mkdtemp(prefix='browser-content-', dir=ROOT / '.build'))
    shutil.copytree(ROOT / 'content', content, dirs_exist_ok=True)
    shutil.copytree(ROOT / 'tests/fixtures/rendering', content / 'test-rendering')
    binary = ROOT / '.tools' / ('hugo.exe' if os.name == 'nt' else 'hugo')
    env = dict(os.environ, HUGO_RESOURCEDIR=str(ROOT / '.build/resources'))
    subprocess.run([str(binary), '--contentDir', str(content), '--destination', '.build/browser-site',
                    '--cacheDir', str(ROOT / '.cache/hugo'), '--cleanDestinationDir', '--minify'],
                   cwd=ROOT, env=env, check=True)
