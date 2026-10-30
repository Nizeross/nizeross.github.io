"""Copy audited KaTeX distribution into ignored Hugo asset overrides."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'node_modules/katex'
target = ROOT / 'assets/lib/katex'
target.mkdir(parents=True, exist_ok=True)
shutil.copy2(source / 'dist/katex.min.js', target / 'katex.min.js')
shutil.copy2(source / 'dist/katex.min.css', target / 'katex.min.css')
shutil.copy2(source / 'dist/contrib/auto-render.min.js', target / 'auto-render.min.js')
shutil.copytree(source / 'dist/fonts', target / 'fonts', dirs_exist_ok=True)
shutil.copy2(source / 'LICENSE', target / 'LICENSE')
print('KaTeX asset override synchronized from locked npm dependency')
mermaid_source = ROOT / 'node_modules/mermaid'
mermaid_target = ROOT / 'assets/lib/mermaid'
mermaid_target.mkdir(parents=True, exist_ok=True)
subprocess.run(['node', 'scripts/build_vendor.cjs'], cwd=ROOT, check=True)
shutil.copy2(mermaid_source / 'LICENSE', mermaid_target / 'LICENSE')
print('Mermaid asset override synchronized from locked npm dependency')
