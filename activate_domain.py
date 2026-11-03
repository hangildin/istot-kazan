"""Finalize SEO URLs only after the LIVE site URL is known.
Accepts both a custom domain and a GitHub Pages project URL.
Examples:
  python activate_domain.py https://example.ru
  python activate_domain.py https://example.github.io/my-site
"""
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape
import re,sys
ROOT=Path(__file__).parent
if len(sys.argv)!=2:
    raise SystemExit('Usage: python activate_domain.py https://your-actual-domain.ru')
raw=sys.argv[1].rstrip('/')
p=urlparse(raw)
if p.scheme!='https' or not p.netloc or p.query or p.fragment or '..' in p.path:
    raise SystemExit('Use a verified HTTPS site URL, with no query or fragment')
files=sorted(ROOT.glob('**/index.html'))
urls=[]
for f in files:
    path=f.parent.relative_to(ROOT).as_posix()
    route='/' if path=='.' else '/'+path+'/'
    url=raw+route
    t=f.read_text('utf8')
    t=re.sub(r'<link rel="canonical"[^>]*>','',t)
    t=re.sub(r'<meta property="og:url"[^>]*>','',t)
    t=re.sub(r'<meta property="og:image"[^>]*>','',t)
    # Keep social-preview image fully absolute, no invented domain until this step.
    image=raw+'/assets/parnaya.webp'
    t=t.replace('</head>', f'<link rel="canonical" href="{url}">\n<meta property="og:url" content="{url}">\n<meta property="og:image" content="{image}">\n</head>')
    f.write_text(t,encoding='utf8')
    urls.append(url)
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{escape(u)}</loc></url>\n' for u in urls)+'</urlset>\n'
(ROOT/'sitemap.xml').write_text(xml,encoding='utf8')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {raw}/sitemap.xml\n',encoding='utf8')
print(f'Updated {len(urls)} canonical URLs, OpenGraph previews and sitemap.xml for {raw}')
