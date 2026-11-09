#!/usr/bin/env python3
"""R226: independent rendered-anchor occurrence custody, staging only.
No network, WordPress writes, analytics, or merchant activation. Needs pinned R225 build.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

R225_MANIFEST = '4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'


def sha(buf): return hashlib.sha256(buf).hexdigest()
def dump(data): return (json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode()
def check(truth, message):
    if not truth: raise AssertionError(message)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items=[];self.a=None;self.ids=[];self.refs=[];self.invalid=[]
    def handle_starttag(self,tag,attrs):
        x=dict(attrs)
        if tag in ('script','iframe','form','object','embed') or any(k.startswith('on') or k in ('data-lat','data-lon','srcdoc') for k in x):
            self.invalid.append(tag)
        if 'id' in x:self.ids.append(x['id'])
        for k in ('aria-labelledby','aria-describedby'):self.refs.extend(x.get(k,'').split())
        if tag=='a':
            self.a={'href':x.get('href',''),'name':'','source_id':x.get('data-source-id',''),
                    'hidden':x.get('aria-hidden')=='true','target':x.get('target',''),
                    'rel':sorted(x.get('rel','').split())}
            self.a['name']+=x.get('aria-label','')
            self.items.append(self.a)
    def handle_data(self,text):
        if self.a is not None:self.a['name']+=text
    def handle_endtag(self,tag):
        if tag=='a':self.a=None


def census(html,allow):
    parser=Links();parser.feed(html)
    check(not parser.invalid,'active or speculative markup')
    check(len(parser.ids)==len(set(parser.ids)),'duplicate IDs')
    check(not set(parser.refs).difference(parser.ids),'orphan ARIA references')
    external=[]
    for item in parser.items:
        item['name']=' '.join(item['name'].split())
        h=item['href'];check(item['name'] and not item['hidden'],'unusable source navigation')
        if h.startswith('https://'):
            check(h in allow,'unreviewed outbound destination')
            external.append(item)
        else:
            check(h.startswith('#') and h[1:] in parser.ids,'broken in-page navigation')
        if item['target']=='_blank':
            check({'noopener','noreferrer'}<=set(item['rel']),'unprotected new-tab link')
    check(len(external)==56 and len(set(x['href'] for x in external))==11,'source-link census changed')
    check(sum(x['href']==FREE for x in external)==1,'one free editorial CTA required')
    check(sum(bool(x['source_id']) for x in external)==6,'source binding count changed')
    return parser.items


def run(dist,out):
    out.mkdir(parents=True,exist_ok=True)
    check(sha((dist/'manifest.json').read_bytes())==R225_MANIFEST,'unverified R225 manifest')
    manifest=json.loads((dist/'manifest.json').read_text())
    for path,expected in manifest['files'].items():
        check(sha((dist/path).read_bytes())==expected,'drifted staging artifact: '+path)
    html=(dist/'templates/atlas-fragment.html').read_text()
    css=(dist/'assets/atlas-scoped.css').read_text()
    cross=json.loads((dist/'source-url-crosswalk.json').read_text())
    allowed=set(cross['external_urls'])
    expected=census(html,allowed)
    baseline=sha(dump(expected))
    # A two-way swap preserves count, approved URL set and source ID count. R225
    # checks cannot see it; the R226 ordered-occurrence ledger does.
    anchors=list(re.finditer(r'<a\b[^>]*href="https://[^"]+"[^>]*>',html))
    candidates=[]
    for m in anchors:
        raw=m.group(0)
        if 'data-source-id=' not in raw and FREE not in raw:
            candidates.append((m,re.search(r'href="([^"]+)"',raw).group(1)))
    pair=next(((a,b) for i,a in enumerate(candidates) for b in candidates[i+1:] if a[1]!=b[1]),None)
    check(pair is not None,'mutation source links unavailable')
    (a,ua),(b,ub)=pair
    corrupt=(html[:a.start()]+a.group(0).replace('href="'+ua+'"','href="'+ub+'"',1)
             +html[a.end():b.start()]+b.group(0).replace('href="'+ub+'"','href="'+ua+'"',1)+html[b.end():])
    swapped=census(corrupt,allowed)
    check(len(swapped)==len(expected) and sha(dump(swapped))!=baseline,'allowlisted URL swap undetected')
    renamed=html.replace("Read the Board's findings", "NASA approved this offer",1)
    check(renamed!=html and sha(dump(census(renamed,allowed)))!=baseline,'misleading source label undetected')
    (out/'ordered-link-ledger.json').write_bytes(dump({'sha256':baseline,'anchors':expected}))
    body='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
    images=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for js in (False,True):
                ctx=b.new_context(viewport={'width':width,'height':850},java_script_enabled=js,
                                  has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
                p=ctx.new_page();p.set_content(body)
                check(p.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),'horizontal overflow '+str(width))
                summary=p.locator('#fv-apollo-source-drawer summary');summary.scroll_into_view_if_needed()
                if width<=390:
                    box=summary.bounding_box();p.touchscreen.tap(box['x']+20,box['y']+box['height']/2)
                else:summary.focus();p.keyboard.press('Enter')
                check(p.locator('#fv-apollo-source-drawer').evaluate('el=>el.open'),'disclosure inaccessible')
                p.locator('#fv-apollo-chronology').scroll_into_view_if_needed()
                path=out/('%s-%s.png'%(width,'js' if js else 'nojs'));p.screenshot(path=str(path),animations='disabled')
                images.append({'width':width,'js':js,'sha256':sha(path.read_bytes())})
                ctx.close()
        b.close()
    result={'status':'LOCAL_PASS_STAGING_HOLD','manifest_sha256':R225_MANIFEST,'ordered_links_sha256':baseline,
            'allowlisted_swap_rejected':True,'misleading_label_rejected':True,'screenshots':images,
            'axe_core':'NOT_EXECUTED','http_wordpress':'NOT_TESTED','paid_order':'NOT_VERIFIED'}
    (out/'result.json').write_bytes(dump(result))
    print('R226 PASS:',len(images),'browser contexts; ordered link custody',baseline)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dist',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.dist,a.out)
