#!/usr/bin/env python3
"""Apollo R222 isolated SourceDrawer build. No CMS writes, network, or external assets."""
from __future__ import annotations
import argparse, hashlib, json, shutil, re
from pathlib import Path
from html import escape

R217_MANIFEST = '90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72'
R217_HTML = 'd92997e5be6cd8425bc89e5a314310d813bfabfcf770e2b9caf5ad3078692f90'
R217_CSS = '84e75361f06281cfa4c388cf226b4041f83f37f06e4cc3ae0f211080d9cb28f6'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RIGHTS = 'https://www.nasa.gov/nasa-brand-center/advertising-guidelines/'
PHOTO = 'https://www.nasa.gov/image-detail/amf-s67-21294/'
DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
READING = '<aside class="fv-apollo-reading-bridge"'
CSS_APPEND = '''
/* R222: native source drawer between NASA claim trail and the sole free reading link. */
.fv-apollo-atlas .fv-apollo-source-drawer{margin:clamp(1.5rem,4vw,3rem) 0 1rem;border:1px solid #a38a61;border-radius:.5rem;background:#1a1b19;color:#f9f2e8}
.fv-apollo-atlas .fv-apollo-source-drawer>summary{cursor:pointer;padding:1.05rem 1.3rem;min-height:48px;font-size:1.05rem;font-weight:750;line-height:1.6;color:#f9e5bb}
.fv-apollo-atlas .fv-apollo-source-drawer>summary:focus-visible{outline:3px solid #fff;outline-offset:3px}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-body{padding:.5rem clamp(1rem,3vw,2rem) 1.4rem;border-top:1px solid #5f5341}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem;margin:1rem 0 1.1rem;padding:0;list-style:none}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-list li{min-width:0;padding:1rem;border:1px solid #655b4b;border-radius:.25rem;background:#23241f}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-list strong{display:block;margin-bottom:.35rem}
.fv-apollo-atlas .fv-apollo-source-drawer p{margin:.5rem 0 1rem;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-source-drawer a{color:#ffe0a6;text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-source-drawer a:focus-visible{outline:3px solid #fff;outline-offset:3px}
@media(max-width:600px){.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-list{grid-template-columns:1fr}.fv-apollo-atlas .fv-apollo-source-drawer>summary{padding:.85rem 1rem}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-source-drawer,.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-list li{border:1px solid CanvasText;background:Canvas;color:CanvasText}.fv-apollo-atlas .fv-apollo-source-drawer a,.fv-apollo-atlas .fv-apollo-source-drawer>summary{color:LinkText}}
@media print{.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-drawer-body{display:block!important}.fv-apollo-atlas .fv-apollo-source-drawer{color:#000;background:#fff;border:1px solid #000}.fv-apollo-atlas .fv-apollo-source-drawer a{color:#000}}
'''

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def require(x,msg):
    if not x: raise ValueError(msg)

def record_data():
    return {
     'schema':'fv-apollo-source-drawer-v1', 'feature':'offline-native-details',
     'no_licensed_media_embedded':True,'paid_offer_approved':False,'published_grok_asset_id':None,
     'rights_source':RIGHTS, 'free_action':DEST,
     'sources':[
        {'id':'Apollo 204 Review Board','type':'retrospective technical report','date':'1967-04','url':BOARD,
         'supports':'Board findings on ignition, test atmosphere, escape and pressure response.',
         'limit':'An electrical arc was most probable; no single ignition source was conclusively identified.'},
        {'id':'S66-58038','type':'pre-accident crew photograph','date':'1966-10-18', 'url':'https://www.nasa.gov/image-detail/amf-s66-58038/',
         'supports':'A dated NASA crew-preparation photograph.','limit':'Not a photograph of the January 1967 fire.'},
        {'id':'S67-15717','type':'pre-accident spacecraft processing photograph','date':'1967-01-03','url':'https://www.nasa.gov/image-detail/amf-s67-15717/',
         'supports':'A dated NASA spacecraft-preparations catalog record.','limit':'Does not depict or establish the initiating spark.'},
        {'id':'S67-21294','type':'post-accident damage photograph','date':'1967-01-28','url':PHOTO,
         'supports':'Aftermath damage to the spacecraft.','limit':'Not a picture of the ignition event.'}
     ]}

def drawer(data):
    li=[]
    for s in data['sources']:
        id_=escape(s['id']); kind=escape(s['type']);dt=escape(s['date']);url=escape(s['url'],quote=True)
        lim=escape(s['limit']); supports=escape(s['supports']);limit_id='fv-apollo-drawer-limit-'+re.sub('[^a-z0-9]+','-',s['id'].lower()).strip('-')
        li.append(f'<li data-drawer-source="{id_}"><strong>{id_} · {kind}</strong><p>Record date: <time datetime="{dt}">{dt}</time>. {supports}</p><p id="{limit_id}"><b>Limit:</b> {lim}</p><a href="{url}" aria-describedby="{limit_id}" rel="noopener noreferrer">Verify {id_} at NASA</a></li>')
    return ('<details class="fv-apollo-source-drawer" id="fv-apollo-source-drawer">'
        '<summary>Open the four original NASA records and their limitations</summary>'
        '<div class="fv-apollo-drawer-body"><h2>Source drawer · primary records, separate evidentiary roles</h2>'
        '<p>The photographs document preparation or aftermath; the technical report is a retrospective investigation. '
        'They cannot independently establish the exact ignition point.</p>'
        '<ol class="fv-apollo-drawer-list">'+''.join(li)+'</ol>'
        '<p><strong>Rights boundary:</strong> NASA links are for verification, not commercial endorsement or promotional image clearance. '
        f'<a href="{escape(RIGHTS,quote=True)}">Read NASA usage guidance</a>. '
        'The original Final Vestige investigation remains free; no signup or purchase is needed.</p>'
        '</div></details>')

def build(parent:Path, target:Path):
    require(sha((parent/'manifest.json').read_bytes())==R217_MANIFEST,'R217 manifest mismatch')
    require(sha((parent/'templates/atlas-fragment.html').read_bytes())==R217_HTML,'R217 HTML drift')
    require(sha((parent/'assets/atlas-scoped.css').read_bytes())==R217_CSS,'R217 stylesheet drift')
    require(READING in (parent/'templates/atlas-fragment.html').read_text(),'Reading bridge anchor missing')
    if target.exists(): shutil.rmtree(target)
    shutil.copytree(parent,target)
    data=record_data()
    crosswalk=json.loads((parent/'source-url-crosswalk.json').read_text())
    for entry in data['sources']:
        require({'source_id':entry['id'],'url':entry['url']} in crosswalk['source_bindings'],'Source ID / NASA URL drift '+entry['id'])
    h=(target/'templates/atlas-fragment.html'); original=h.read_text()
    require(original.count(READING)==1,'Ambiguous insertion point')
    enhanced=original.replace(READING,drawer(data)+'\n'+READING,1)
    require(enhanced.count('class="cta"')==1 and enhanced.count(DEST)==1,'Free original-investigation CTA changed')
    h.write_text(enhanced)
    c=target/'assets/atlas-scoped.css'; c.write_text(c.read_text()+CSS_APPEND)
    (target/'source-drawer-records.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    php=target/'fv-ex2-apollo-r217.php';txt=php.read_text()
    require(R217_HTML in txt and R217_CSS in txt,'R217 PHP pins missing')
    txt=txt.replace('r217','r222').replace('R217','R222')
    txt=txt.replace(R217_HTML,sha(h.read_bytes())).replace(R217_CSS,sha(c.read_bytes()))
    txt=txt.replace('function fv_ex2_r222_assets_ok() {','function fv_ex2_r222_assets_ok() {')
    txt=txt.replace("        && hash_file('sha256',$html)", "        && is_readable($root.'source-drawer-records.json') && hash_file('sha256',$root.'source-drawer-records.json')==='"+sha((target/'source-drawer-records.json').read_bytes())+"'\n        && hash_file('sha256',$html)")
    np=target/'fv-ex2-apollo-r222.php';np.write_text(txt);php.unlink()
    sh=target/'wp-render-shim-r217.php'; s=sh.read_text();require('r217' in s,'R217 test shim marker missing')
    (target/'wp-render-shim-r222.php').write_text(s.replace('r217','r222').replace('R217','R222')); sh.unlink()
    files={p.relative_to(target).as_posix():sha(p.read_bytes()) for p in sorted(target.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    manifest={'release':'R222','status':'STAGING_HOLD','parent_manifest_sha256':R217_MANIFEST,
        'not_live':True,'files':files,'known_gates':{'axe_core':'NOT_RUN','WordPress_staging':'NOT_TESTED',
         'sales':'NOT_VERIFIED','R198_ancestry':'NOT_RECONCILED'}}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return sha((target/'manifest.json').read_bytes())

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--target',type=Path,required=True)
    a=ap.parse_args(); print('R222 pinned build manifest SHA-256',build(a.parent,a.target))
