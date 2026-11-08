#!/usr/bin/env python3
"""R216 staging-only, source-pinned runtime custody and active-content denylist.
Only accepted parent bytes can enter the archive. Never deploy without independent approval.
"""
import hashlib, json, os, re, shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

HERE=Path(__file__).resolve().parent
BASE=Path(os.environ.get('FV_APOLLO_R215_DIST',HERE/'../r215/dist')).resolve()
OUT=HERE/'dist'
PIN='24de2b0adf1169a6c3b91873468d3af2be8216bb945ee0be8a3a24fb26d51033'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
ALLOWED={'www.nasa.gov','finalvestige.com'}
TAGS=set('a article aside b br dd details div dl dt em footer h1 h2 h3 header li nav ol p section small span strong summary time'.split())
ATTRS=set('aria-describedby aria-label aria-labelledby class data-authority data-evidence-kind data-evidence-type data-finding data-record-kind data-source-id data-source-record datetime href id rel role tabindex'.split())
SECURITY_CUSTODY=('source-records.json','custody-ledger.json','attribution-release-gate.json','commercial-offer-gate.json','link-custody-receipt.json')

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(o):return (json.dumps(o,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def require(b,msg):
    if not b: raise ValueError(msg)

class Proof(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.tags={};self.attrs={};self.errors=[];self.links=[];self.ids=[];self.refs=[];self.ctas=[]
    def handle_startendtag(self,t,a):self.handle_starttag(t,a)
    def handle_starttag(self,t,a):
        self.tags[t]=self.tags.get(t,0)+1
        if t not in TAGS:self.errors.append('Unapproved tag: '+t)
        keys=[k.lower() for k,v in a]
        if len(keys)!=len(set(keys)):self.errors.append('Duplicate HTML attribute on '+t)
        attrs=dict(a)
        for k,v in a:
            self.attrs[k]=self.attrs.get(k,0)+1
            if k not in ATTRS or k.startswith('on') or k in ('style','srcdoc','src','target','formaction'):
                self.errors.append('Unapproved HTML attribute '+k)
            if v is not None and ('\x00' in v or '\r' in v):self.errors.append('Control character in HTML attribute')
        if attrs.get('id'):self.ids.append(attrs['id'])
        for k in ('aria-labelledby','aria-describedby'):
            if attrs.get(k):self.refs.extend(attrs[k].split())
        if t=='a':
            href=attrs.get('href','')
            if href.startswith('#'):self.refs.append(href[1:])
            else:
                url=urlsplit(href)
                if url.scheme!='https' or url.hostname not in ALLOWED or url.username or url.password:
                    self.errors.append('Unsafe source destination: '+href)
                self.links.append(href)
            if 'cta' in attrs.get('class','').split():self.ctas.append(href)
    def handle_entityref(self,name):pass
    def handle_decl(self,decl):self.errors.append('Unexpected HTML declaration')
    def unknown_decl(self,decl):self.errors.append('Unexpected declaration')


def protect_markup(html,css):
    p=Proof();p.feed(html.decode('utf-8'));p.close()
    require(not p.errors,'; '.join(p.errors))
    require(len(set(p.ids))==len(p.ids),'Duplicate IDs')
    require(all(v in p.ids for v in p.refs),'Unresolved fragment/ARIA target')
    require(p.ctas==[FREE] and p.links.count(FREE)==1,'Sole editorial action was changed')
    require(p.tags.get('h1')==1 and p.tags.get('details',0)>=10,'Heading or source disclosures missing')
    require('https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' in p.links,'Review Board source missing')
    require('https://www.nasa.gov/nasa-brand-center/advertising-guidelines/' in p.links,'Commercial rights guidance missing')
    require(set(p.tags)<=TAGS and set(p.attrs)<=ATTRS,'Unapproved markup surface')
    lower=css.decode('utf-8').lower()
    forbidden=(r'@import\b',r'@font-face\b',r'url\s*\(',r'expression\s*\(',r'(?<!-)\bbehavior\s*:',
               r'javascript\s*:',r'@namespace\b',r'</style',r'-moz-binding\s*:')
    require(not any(re.search(rx,lower) for rx in forbidden),'Unapproved external CSS/active content')
    require('.fv-apollo-atlas' in lower and 'prefers-reduced-motion' in lower and 'forced-colors' in lower,
            'Scoped and accessible styling missing')
    return {'allowed_tags':sorted(p.tags),'observed_attributes':sorted(p.attrs),'tag_instances':sum(p.tags.values()),
            'anchor_links':len(p.links),'unique_ids':len(p.ids),'aria_fragment_targets':len(p.refs),
            'single_free_investigation':FREE,'scriptless':True,'remote_css_dependencies':0,
            'commercial_or_nasa_media_rights_cleared':False}


def build():
    require(sha((BASE/'manifest.json').read_bytes())==PIN,'Parent R215 manifest mismatch')
    manifest=json.loads((BASE/'manifest.json').read_bytes())
    require(manifest.get('release')=='r215' and manifest.get('script_shipped') is False,'Wrong parent')
    for flag in ('creator_attribution_verified','approved_purchase_offer','media_commercial_rights_cleared',
                 'installed_WordPress_accepted','upstream_R198_reconciled','axe_core_accepted','commercial_release_allowed'):
        require(manifest.get(flag) is False,'Parent falsely clears '+flag)
    for name,h in manifest['files'].items():
        require(sha((BASE/name).read_bytes())==h,'Parent provenance changed: '+name)
    html=(BASE/'templates/atlas-fragment.html').read_bytes()
    css=(BASE/'assets/atlas-scoped.css').read_bytes()
    receipt=protect_markup(html,css)
    src=(BASE/'fv-ex2-apollo-r215.php').read_text()
    require('function fv_ex2_r215_assets_ok()' in src and re.search(r'\bwp_enqueue_script\s*\(',src) is None,'Unexpected PHP base')
    check=''
    for name in SECURITY_CUSTODY:
        h=manifest['files'][name]
        check += ("\n        && is_readable($root.'"+name+"') && hash_file('sha256',$root.'"+name+"')==='"+h+"'")
    old="return is_readable($html) && is_readable($css)"
    require(src.count(old)==1,'PHP integrity insertion point changed')
    src=src.replace(old,"return is_readable($html) && is_readable($css)"+check)
    src=src.replace('r215','r216').replace('R215','R216')
    require('fv_ex2_r216_assets_ok' in src and re.search(r'\bwp_enqueue_script\s*\(',src) is None,'Runtime custody unexpectedly bypassed')
    shim=(BASE/'wp-render-shim-r215.php').read_text().replace('r215','r216').replace('R215','R216')
    files={name:(BASE/name).read_bytes() for name in manifest['files'] if name not in ('fv-ex2-apollo-r215.php','wp-render-shim-r215.php','link-custody-receipt.json')}
    files['fv-ex2-apollo-r216.php']=src.encode()
    files['wp-render-shim-r216.php']=shim.encode()
    files['link-custody-receipt.json']=(BASE/'link-custody-receipt.json').read_bytes()
    files['active-content-custody.json']=dump(receipt)
    files['manifest.json']=dump({'release':'r216','parent_manifest_sha256':PIN,
        'files':{n:sha(v) for n,v in sorted(files.items())},
        'source_and_commerce_gate_runtime_hash_checked':list(SECURITY_CUSTODY),
        'active_content_allowlist_verified':True,'script_shipped':False,'creator_attribution_verified':False,
        'approved_purchase_offer':False,'media_commercial_rights_cleared':False,
        'installed_WordPress_accepted':False,'axe_core_accepted':False,'upstream_R198_reconciled':False,
        'commercial_release_allowed':False,'release_gate':'STAGING HOLD: WP/axe/CI/QD/Founder and R198 discrepancy'})
    # Do not replace an existing dist until every source and artifact check passes.
    tmp=HERE/'_dist_pending'
    if tmp.exists():shutil.rmtree(tmp)
    for name,data in sorted(files.items()):
        f=tmp/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
    if OUT.exists():shutil.rmtree(OUT)
    tmp.rename(OUT)
    return sha(files['manifest.json'])

if __name__=='__main__':print('R216 SOURCE-GATED STAGING MANIFEST:',build())
