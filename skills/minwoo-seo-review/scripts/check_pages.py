"""Inspect explicitly supplied HTML snapshots; no crawling, network, writes or ranking guarantee."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,urljoin

MAX_BYTES=2*1024*1024
def http_url(value):
    if not isinstance(value,str):raise ValueError('URL must be a string')
    parsed=urlsplit(value)
    if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.username or parsed.password:raise ValueError('HTTP URL without credentials required')
    return value

def read_local(root,name):
    if not isinstance(name,str) or not name:raise ValueError('Local file required')
    p=root/name
    if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Relative local path required')
    for candidate in (p,*p.parents):
        if candidate==root.parent:break
        if candidate.is_symlink() or (candidate.exists() and getattr(candidate.stat(),'st_file_attributes',0)&0x400):raise ValueError('Linked input rejected')
    if not p.resolve().is_relative_to(root.resolve()):raise ValueError('Input outside manifest directory')
    if p.stat().st_size>MAX_BYTES:raise ValueError('Input too large')
    return p.read_text(encoding='utf-8-sig')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles=[];self.metas=[];self.canonicals=[];self.jsonld=[];self._title=None;self._json=None
    def handle_starttag(self,tag,attrs):
        a={k.lower():v or '' for k,v in attrs}
        if tag=='title':self._title=[];self.titles.append(self._title)
        if tag=='meta':self.metas.append(a)
        if tag=='link' and 'canonical' in a.get('rel','').lower().split():self.canonicals.append(a.get('href',''))
        if tag=='script' and a.get('type','').lower()=='application/ld+json':self._json=[];self.jsonld.append(self._json)
    def handle_endtag(self,tag):
        if tag=='title':self._title=None
        if tag=='script':self._json=None
    def handle_data(self,data):
        if self._title is not None:self._title.append(data)
        if self._json is not None:self._json.append(data)

def check(manifest_path):
    manifest_path=Path(manifest_path)
    if manifest_path.stat().st_size>MAX_BYTES:raise ValueError('Manifest too large')
    data=json.loads(manifest_path.read_text(encoding='utf-8-sig'));root=manifest_path.parent
    pages=data.get('pages')
    if not isinstance(pages,list) or not 1<=len(pages)<=100:raise ValueError('Expected 1..100 pages')
    findings=[];titles=[];urls=[];page_reports=[]
    def add(code,index,severity='review'):findings.append({'code':code,'page':index,'severity':severity})
    for index,entry in enumerate(pages):
        if not isinstance(entry,dict):raise ValueError('Page must be an object')
        url=http_url(entry['url'])
        if url in urls:raise ValueError('Duplicate page URL')
        urls.append(url);expected=entry.get('expectIndexable',True)
        if not isinstance(expected,bool):raise ValueError('expectIndexable must be boolean')
        page=Page();page.feed(read_local(root,entry['html']));page.close()
        title=' '.join(''.join(page.titles[0]).split()) if page.titles else ''
        titles.append(title)
        if len(page.titles)!=1 or not title:add('title-missing-or-multiple',index,'error')
        descriptions=[m.get('content','').strip() for m in page.metas if m.get('name','').lower()=='description']
        if len(descriptions)!=1 or not descriptions[0]:add('description-missing-or-multiple',index)
        status=entry.get('status')
        if status is None:add('http-status-not-observed',index)
        elif not isinstance(status,int) or isinstance(status,bool) or not 100<=status<=599:raise ValueError('Invalid HTTP status')
        elif status>=400:add('http-error',index,'error')
        elif not 200<=status<300:add('non-success-status',index)
        headers=entry.get('headers')
        if headers is None:add('http-headers-not-observed',index);headers={}
        if not isinstance(headers,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in headers.items()):raise ValueError('String HTTP headers required')
        robots=[m.get('content','') for m in page.metas if m.get('name','').lower() in ('robots','googlebot')]
        # Agent-qualified X-Robots-Tag headers need manual interpretation.
        for k,v in headers.items():
            if k.lower()=='x-robots-tag':
                if ':' in v:
                    agent,rest=v.split(':',1)
                    if agent.strip().lower()=='googlebot':robots.append(rest)
                    else:add('agent-qualified-robots-header',index)
                else:robots.append(v)
        noindex=any(set(re.split(r'[\s,;]+',s.lower())) & {'noindex','none'} for s in robots)
        if expected and noindex:add('unexpected-noindex',index,'error')
        if not expected and not noindex:add('expected-noindex-not-observed',index,'error')
        if len(page.canonicals)>1:add('multiple-canonicals',index,'error')
        for canonical in page.canonicals:
            if not canonical:add('empty-canonical',index,'error');continue
            absolute=urljoin(url,canonical)
            try:http_url(absolute)
            except ValueError:add('invalid-canonical',index,'error');continue
            if not urlsplit(canonical).scheme:add('relative-canonical',index)
            if urlsplit(absolute).fragment:add('canonical-fragment',index)
            if urlsplit(absolute).netloc!=urlsplit(url).netloc:add('cross-origin-canonical',index)
        for text in page.jsonld:
            try:json.loads(''.join(text))
            except (ValueError,RecursionError):add('invalid-jsonld',index,'error')
        page_reports.append({'page':index,'expectIndexable':expected,'noindex_observed':noindex,'canonical_count':len(page.canonicals),'jsonld_count':len(page.jsonld)})
    duplicate_titles={s for s,n in Counter(titles).items() if s and n>1}
    for index,title in enumerate(titles):
        if title in duplicate_titles:add('duplicate-title',index)
    if data.get('robots'):
        robots=read_local(root,data['robots'])
        # Only this unambiguous single wildcard group is classified automatically.
        lines=[tuple(part.strip().lower() for part in line.split('#',1)[0].split(':',1)) for line in robots.splitlines() if line.split('#',1)[0].strip()]
        if lines==[('user-agent','*'),('disallow','/')]:
            for index,entry in enumerate(pages):
                if entry.get('expectIndexable',True):add('robots-disallow-all',index,'error')
        elif lines not in ([('user-agent','*'),('allow','/')],[('user-agent','*'),('disallow','')]):add('robots-rules-require-manual-review',None)
    else:add('robots-not-supplied',None)
    if data.get('sitemap'):
        xml=read_local(root,data['sitemap'])
        if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():raise ValueError('XML entities/DOCTYPE unsupported')
        tree=ET.fromstring(xml)
        if tree.tag!='{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':add('sitemap-format-requires-review',None)
        else:
            locations=[node.text or '' for node in tree.findall('./{*}url/{*}loc')]
            for location in locations:
                try:http_url(location)
                except ValueError:add('invalid-sitemap-url',None,'error')
            if len(set(locations))!=len(locations):add('duplicate-sitemap-url',None)
            for index,entry in enumerate(pages):
                if not entry.get('expectIndexable',True) and entry['url'] in locations:add('noindex-page-in-sitemap',index)
                if entry.get('expectIndexable',True) and entry['url'] not in locations:add('page-not-in-supplied-sitemap',index)
    else:add('sitemap-not-supplied',None)
    counts=Counter(f['severity'] for f in findings)
    return {'status':'issues' if counts['error'] else 'review' if counts['review'] else 'no-issues-detected',
        'counts':{'error':counts['error'],'review':counts['review']},'findings':findings,'pages':page_reports,
        'scope':'supplied HTML/header snapshots only; robots subset, JSON syntax only; no live crawling, indexing, ranking or rich-result eligibility guarantee'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);args=parser.parse_args()
    try:
        result=check(args.manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 1 if result['status']=='issues' else 2 if result['status']=='review' else 0
    except (OSError,ValueError,KeyError,TypeError,ET.ParseError) as exc:
        print(json.dumps({'status':'incomplete','reason':str(exc)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
