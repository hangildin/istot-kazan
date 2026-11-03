#!/usr/bin/env python3
"""Dependency-free checks of a static site intended for GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import sys
import xml.etree.ElementTree as ET

BASE="https://hangildin.github.io/istot-kazan/"

ROOT=Path(__file__).resolve().parents[1]
FILES=sorted(f for f in ROOT.rglob('index.html') if '_site' not in f.relative_to(ROOT).parts)
ISSUES=[]
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[];self.images=[];self.anchors=[];self.h1=0;self.title=False;self.meta=[];self.json_ld=[];self._in_title=False;self._in_json=False;self._json=[];self.forms=0;self.canonicals=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.anchors.append(d['id'])
        if tag=='a':self.links.append(d.get('href',''))
        if tag=='img':self.images.append(d)
        if tag=='link' and d.get('rel')=='canonical': self.canonicals.append(d.get('href',''))
        if tag=='form':self.forms+=1
        if tag=='h1':self.h1+=1
        if tag=='title':self._in_title=True
        if tag=='meta':self.meta.append(d)
        if tag=='script' and d.get('type')=='application/ld+json':self._in_json=True;self._json=[]
    def handle_data(self,data):
        if self._in_title and data.strip():self.title=True
        if self._in_json:self._json.append(data)
    def handle_endtag(self,tag):
        if tag=='title':self._in_title=False
        if tag=='script' and self._in_json:
            self.json_ld.append(''.join(self._json));self._in_json=False

parsed={}
for f in FILES:
    p=Parser();p.feed(f.read_text('utf8'));parsed[f.resolve()]=p
for f,p in parsed.items():
    route=f.relative_to(ROOT).as_posix()
    expected_url=BASE+route.removesuffix('index.html')
    if p.canonicals!=[expected_url]:ISSUES.append(f'{route}: invalid canonical, expected {expected_url}, got {p.canonicals}')
    if p.h1!=1:ISSUES.append(f'{route}: expected one h1, found {p.h1}')
    if not p.title:ISSUES.append(f'{route}: missing title')
    if not any(x.get('name')=='description' and x.get('content') for x in p.meta):ISSUES.append(f'{route}: missing meta description')
    if p.forms:ISSUES.append(f'{route}: unexpected form, site uses direct contacts only')
    ids=Counter(p.anchors)
    for a,n in ids.items():
        if n>1:ISSUES.append(f'{route}: duplicate id {a}')
    for x in p.json_ld:
        try:json.loads(x)
        except ValueError as e:ISSUES.append(f'{route}: invalid JSON-LD {e}')
    for im in p.images:
        if 'alt' not in im:ISSUES.append(f'{route}: image missing alt')
        if 'src' not in im:continue # image element inside <dialog> populated when opened
        targets=[im['src']]
        if 'srcset' in im:
            targets.extend(z.strip().split()[0] for z in im['srcset'].split(','))
        for src in targets:
            local=(f.parent/src).resolve()
            if not local.is_relative_to(ROOT) or not local.is_file():ISSUES.append(f'{route}: missing image {src}')
        if 'width' not in im or 'height' not in im:ISSUES.append(f'{route}: image missing dimensions {im.get("alt")}')
    for href in p.links:
        if not href or href.startswith(('mailto:','tel:','https:','http:','data:')):continue
        parts=urlsplit(href)
        if parts.scheme:ISSUES.append(f'{route}: nonpermitted link scheme {href}');continue
        target=(f.parent/unquote(parts.path)).resolve() if parts.path else f
        if target.is_dir():target=target/'index.html'
        if not target.is_relative_to(ROOT) or not target.is_file():ISSUES.append(f'{route}: broken link {href}');continue
        if parts.fragment and target.suffix=='.html' and target.resolve() in parsed:
            if parts.fragment not in parsed[target.resolve()].anchors:ISSUES.append(f'{route}: dead anchor {href}')
    if not any(l.startswith('tel:+79061114424') for l in p.links):ISSUES.append(f'{route}: missing phone link')
    if not any('instagram.com/istotkazan' in l for l in p.links):ISSUES.append(f'{route}: missing Instagram link')

try:
    root=ET.parse(ROOT/'sitemap.xml').getroot()
    actual={e.text for e in root.iter() if e.tag.endswith('}loc') or e.tag=='loc'}
    expected={BASE+f.relative_to(ROOT).as_posix().removesuffix('index.html') for f in FILES}
    if actual!=expected:
        ISSUES.append(f'sitemap: missing={sorted(expected-actual)} unexpected={sorted(actual-expected)}')
except (ET.ParseError, OSError) as e:
    ISSUES.append(f'sitemap: cannot parse {e}')

print(f'Pages checked: {len(FILES)}; missing assets/dead links/HTML metadata/sitemap errors: {len(ISSUES)}')
for i in ISSUES:print('ERROR:',i)
if ISSUES:sys.exit(1)
