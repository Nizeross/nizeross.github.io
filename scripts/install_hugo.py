"""Install the pinned Extended release, verifying its recorded SHA-256."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def install():
    lock = json.loads((ROOT / 'toolchain.json').read_text(encoding='utf-8'))
    suffix = {'Windows': 'windows-amd64.zip', 'Linux': 'linux-amd64.tar.gz',
              'Darwin': 'darwin-universal.tar.gz'}.get(platform.system())
    if suffix is None or (platform.system() != 'Darwin' and platform.machine().lower() not in ('amd64', 'x86_64')):
        raise SystemExit('Unsupported architecture; install the pinned Hugo Extended manually.')
    expected = lock['hugoDownloads'].get(suffix)
    if not expected:
        raise SystemExit('Missing release checksum in toolchain.json')
    target = ROOT / '.tools' / ('hugo.exe' if platform.system() == 'Windows' else 'hugo')
    version = lock['hugo']
    url = f'https://github.com/gohugoio/hugo/releases/download/v{version}/hugo_extended_{version}_{suffix}'
    print(f'Downloading Hugo Extended {version} ({suffix})', flush=True)
    data = urllib.request.urlopen(url, timeout=90).read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('Hugo download checksum mismatch; refusing installation')
    name = target.name
    if suffix.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            binary = archive.read(name)
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            binary = archive.extractfile(name).read()
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(binary)
    target.chmod(0o755)
    print(f'Verified and installed: {target}')


if __name__ == '__main__':
    install()
