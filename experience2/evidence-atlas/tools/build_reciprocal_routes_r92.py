#!/usr/bin/env python3
"""R92: source-exact reciprocal navigation for Apollo's FOUR isolated review surfaces.

No NASA photographs, client-side routing, map pins, CMS writes or publication.
The original R91 builder continues to verify actual Research Desk/Atlas custody.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from html import escape
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
VIEWS={
 'R89_REVIEW_HUB.html':('r89-source-','review_hub_r89.css','Evidence Review Hub'),
 'R88_READING_ROOM.html':('r88-','reading_room_r88.css','Research Reading Room'),
 'R87_PHOTOGRAPH_DATE_RAIL.html':('r87-record-','chronology_r87.css','Photograph-date ChronologyRail'),
 'R85_NASA_SOURCE_REVIEW.html':('r85-source-','rights_board_r85.css','NASA Photo Rights Review'),
}
SOURCE=(
 'experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py',
 'experience2/evidence-atlas/tests/test_reciprocal_routes_r92.py',
 'experience2/evidence-atlas/tests/browser_reciprocal_routes_r92.py',
 'experience2/evidence-atlas/R92_RECIPROCAL_EVIDENCE_ROUTES_STAGING_HOLD.md',
 '.github/workflows/ex2-apollo-r92-reciprocal-routes.yml',
)
CSS='''
/* R92 same-source route switcher. Functional without JavaScript. */
.r92-evidence-routes{display:flex;flex-wrap:wrap;gap:.55rem;margin-block:1.5rem .65rem;padding-block:1rem;border-top:1px solid currentColor;max-width:100%;min-width:0}
.r92-evidence-routes a{box-sizing:border-box;min-height:44px;display:inline-flex;align-items:center;max-width:100%;overflow-wrap:anywhere;border:1px solid currentColor;padding:.65rem .8rem;color:inherit;text-underline-offset:.18em;text-decoration:underline;background:transparent;font:600 13px/1.4 system-ui,sans-serif}
.r92-evidence-routes a:focus-visible{outline:3px solid currentColor;outline-offset:3px}
@media(max-width:480px){.r92-evidence-routes{display:grid;grid-template-columns:minmax(0,1fr)}.r92-evidence-routes a{width:100%}}
@media(forced-colors:active){.r92-evidence-routes a{border-color:LinkText;color:LinkText}}
.r92-print-rights{display:none}\n@media print{.r92-evidence-routes{display:none!important}.r92-print-rights{display:block!important;color:#000!important;background:#fff!important;font:normal 10pt/1.4 system-ui,sans-serif;padding:4pt 0;break-inside:avoid}}
'''
ARTICLE=re.compile(r'(<article\b[^>]*\bid="(?P<id>[^"]+)"[^>]*>)(?P<content>.*?)(</article>)',re.S|re.I)

def digest(x:bytes)->str:return hashlib.sha256(x).hexdigest()

def import_r91():
    path=HERE/'build_release_candidate_r91.py'
    spec=importlib.util.spec_from_file_location('apollo_r91_readonly',path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=obj
    spec.loader.exec_module(obj)
    return obj

def source_href(view:str,record:str)->str:
    return view+'#'+VIEWS[view][0]+record

def postprocess(folder:Path)->None:
    """Add no-JS reciprocal same-record routes, then re-run inherited asset gate."""
    parent=import_r91()
    parent.audit_asset_boundary(folder)
    for view, (prefix,stylesheet,_) in VIEWS.items():
        if view=='R89_REVIEW_HUB.html':continue
        path=folder/view
        html=path.read_text('utf8')
        seen=set()
        def add(match):
            rid=match.group('id')
            if not re.fullmatch(re.escape(prefix)+r'0[1-6]',rid) or rid in seen:
                raise ValueError('R92_CARD_IDENTITY_INVALID')
            seen.add(rid)
            record=rid[-2:]
            links=''.join('<a href="'+escape(source_href(target,record),quote=True)+'">'+
                escape(title)+'</a>' for target,(_,_,title) in VIEWS.items() if target!=view)
            nav='<nav class="r92-evidence-routes" aria-label="Other evidence views for source '+record+'">'+links+'</nav>'
            return match.group(1)+match.group('content')+'\n'+nav+'\n'+('<p class="r92-print-rights"><strong>Photographic reuse: INDIVIDUAL REVIEW REQUIRED.</strong> This link is not media clearance.</p>')+'\n'+match.group(4)
        modified,count=ARTICLE.subn(add,html)
        if count!=6 or seen!={prefix+f'{i:02}' for i in range(1,7)}:
            raise ValueError('R92_INCOMPLETE_SOURCE_IDS:'+view)
        path.write_text(modified,encoding='utf8')
        css_path=folder/stylesheet
        css=css_path.read_text('utf8')
        if '.r92-evidence-routes' in css:raise ValueError('R92_STYLES_ALREADY_PRESENT')
        css_path.write_text(css+CSS,encoding='utf8')
    refreshed=parent.audit_asset_boundary(folder)
    (folder/'R91_ASSET_BOUNDARY_RECEIPT.json').write_text(
        json.dumps(refreshed,sort_keys=True,indent=2)+'\n',encoding='utf8')

class RouteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.articles=[];self.current=None;self.innav=False;self.all_ids=set();self.duplicates=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if len(a)!=len(attrs):self.duplicates=True
        if 'id' in a:
            if a['id'] in self.all_ids:self.duplicates=True
            self.all_ids.add(a['id'])
        if tag=='article':
            if self.current is not None:self.duplicates=True
            self.current={'id':a.get('id'),'routes':[],'nasa':[]}
        elif tag=='nav' and self.current and 'r92-evidence-routes' in a.get('class','').split():
            if self.innav:self.duplicates=True
            self.innav=True;self.current['nav_label']=a.get('aria-label')
        elif tag=='a' and self.current:
            href=a.get('href','')
            if self.innav:self.current['routes'].append(href)
            elif href.startswith('https://www.nasa.gov/image-detail/'):
                self.current['nasa'].append(href)
    def handle_endtag(self,tag):
        if tag=='nav' and self.innav:self.innav=False
        if tag=='article' and self.current is not None:
            self.articles.append(self.current);self.current=None

def audit(folder:Path)->dict:
    parent=import_r91()
    backup=folder/'R91_ASSET_BOUNDARY_RECEIPT.json'
    current=json.loads(backup.read_text('utf8'))
    backup.unlink()
    r92_receipt=folder/'R92_RECIPROCAL_ROUTES_RECEIPT.json'
    preserved_r92=r92_receipt.read_bytes() if r92_receipt.exists() else None
    if preserved_r92 is not None:r92_receipt.unlink()
    try:expected=parent.audit_asset_boundary(folder)
    finally:
        backup.write_text(json.dumps(current,sort_keys=True,indent=2)+'\n',encoding='utf8')
        if preserved_r92 is not None:r92_receipt.write_bytes(preserved_r92)
    if expected!=current:raise ValueError('R92_R91_RECEIPT_MISMATCH')
    original=json.loads((folder/'R89_INTEGRITY_RECEIPT.json').read_text('utf8'))
    if len(original.get('source_urls_by_id',{}))!=6 or len(original.get('record_source_bindings',{}))!=24:
        raise ValueError('R92_UNVERIFIED_SOURCE_BASE')
    canonical=original['source_urls_by_id']
    routecount=0;sourcecount=0;files={}
    for view,(prefix,css,_) in VIEWS.items():
        raw=(folder/view).read_text('utf8')
        p=RouteParser();p.feed(raw);p.close()
        if p.duplicates or len(p.articles)!=6:raise ValueError('R92_INCOMPLETE_OR_DUPLICATE_ARTICLES:'+view)
        for item in p.articles:
            rid=item['id']
            if rid not in {prefix+str(i).zfill(2) for i in range(1,7)}:
                raise ValueError('R92_INVALID_ARTICLE_ID')
            n=rid[-2:]
            if item['nasa']!=[canonical[n]]:
                raise ValueError('R92_NASA_LINK_CHANGED:'+view+'/'+n)
            sourcecount+=1
            expected_routes=[source_href(v,n) for v in VIEWS if v!=view]
            if view=='R89_REVIEW_HUB.html':
                for target in expected_routes:
                    if raw.count('href="'+target+'"')!=1:
                        raise ValueError('R92_HUB_ROUTE_MISSING:'+target)
            else:
                if item.get('nav_label')!='Other evidence views for source '+n or item['routes']!=expected_routes:
                    raise ValueError('R92_CROSS_VIEW_ROUTE_CORRUPT:'+view+'/'+n)
                routecount+=len(item['routes'])
        if view!='R89_REVIEW_HUB.html' and raw.count('class="r92-print-rights"')!=6:
            raise ValueError('R92_PRINT_RIGHTS_INCOMPLETE:'+view)
        files[view]=digest((folder/view).read_bytes())
        files[css]=digest((folder/css).read_bytes())
    if routecount!=54 or sourcecount!=24:raise ValueError('R92_BAD_ROUTE_COUNTS')
    return {'schema':'fv.apollo.r92.same-record-routes.v1','release':'STAGING_HOLD',
            'deployment_allowed':False,'photographic_rights_cleared':0,
            'source_bindings':24,'verified_new_reciprocal_routes':54,
            'existing_hub_routes':18,'new_inferred_historical_edges':0,
            'reviewed_geographic_pins':0,'hosted_wordpress_verified':False,
            'asset_checks_inherited':'R91','files':dict(sorted(files.items()))}

def build(out:Path,archive:Path|None=None)->dict:
    if out.exists() and any(out.iterdir()):raise ValueError('R92_OUTPUT_NOT_EMPTY')
    if archive is not None and archive.exists():raise ValueError('R92_ARCHIVE_EXISTS')
    with tempfile.TemporaryDirectory(prefix='fv-apollo-r92-') as temp:
        stage=Path(temp)/'stage'
        import_r91().build(stage)
        (stage/'R91_ASSET_BOUNDARY_RECEIPT.json').unlink()
        postprocess(stage)
        result=audit(stage)
        (stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n','utf8')
        out.mkdir(parents=True,exist_ok=True)
        for f in sorted(stage.iterdir()):shutil.copyfile(f,out/f.name)
    if archive:
        payload={'built/'+p.name:p.read_bytes() for p in sorted(out.iterdir())}
        for name in SOURCE:payload['source/'+name]=(ROOT/name).read_bytes()
        payload['SHA256_MANIFEST.json']=(json.dumps({'release':'STAGING_HOLD','deployment_allowed':False,
             'files':{k:digest(v) for k,v in sorted(payload.items())}},sort_keys=True,indent=2)+'\n').encode()
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(payload.items()):
                info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED
                info.external_attr=0o100644<<16;info.create_system=3
                z.writestr(info,data)
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('out',type=Path);a.add_argument('archive',nargs='?',type=Path)
    args=a.parse_args()
    try:print(json.dumps(build(args.out,args.archive),sort_keys=True))
    except Exception:
        print('R92_STAGING_HOLD: source-exact navigation build failed',file=sys.stderr)
        raise SystemExit(1)
