#!/usr/bin/env python3
"""Copy only publishable files into _site for GitHub Pages."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'_site'
if out.exists():shutil.rmtree(out)
out.mkdir()
for name in ('index.html','styles.css','script.js','404.html','robots.txt','.nojekyll','sitemap.xml','CNAME'):
 f=root/name
 if f.exists():shutil.copy2(f,out/name)
for directory in ('assets','programs','articles'):
 shutil.copytree(root/directory,out/directory)
print('Packaged',sum(f.is_file() for f in out.rglob('*')),'publishable files in',out)
