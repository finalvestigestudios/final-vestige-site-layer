#!/usr/bin/env python3
"""Apollo R223 source-to-context EvidencePlate upgrade; local staging only."""
from __future__ import annotations
import argparse,hashlib,json,re,shutil
from pathlib import Path
from html import escape

PARENT={'manifest.json':'a4fc40dc270684686a879183a7e417bfb6e1d05a40e4e819fed603dc45d130a5','templates/atlas-fragment.html':'eefcbd12f58dfc8211162ab1b6fabb6313734b6e99052716c1c3bae38293ec9f','assets/atlas-scoped.css':'d28060ecc20c53d77816ccb079f6e9779a3839bb4fe59c8a1c98fc951be1e634','source-drawer-records.json':'ac40e4595b4e79b82ec1642e7aca698d828191d0fd3bc07eb5f68de34e4a0cbb'}
CONTEXT={'Apollo 204 Review Board':('April 1967','Report issued','#fv-apollo-finding-fire'),'S66-58038':('18 October 1966','Photographed','#fv-apollo-photo-1966'),'S67-15717':('3 January 1967','Photographed','#fv-apollo-photo-prep'),'S67-21294':('28 January 1967','Photographed','#fv-apollo-photo-aftermath')}
START='<details class="fv-apollo-source-drawer" id="fv-apollo-source-drawer">'
CSS='''
/* R223: evidence plates allow source verification or native intra-page context navigation. */
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-facts{margin:.75rem 0;display:grid;gap:.55rem}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-facts>div{border-left:2px solid #8b795b;padding-left:.65rem}
.fv-apollo-atlas .fv-apollo-source-drawer dt{font-size:.82rem;font-weight:700;letter-spacing:.02em;color:#ead09c}
.fv-apollo-atlas .fv-apollo-source-drawer dd{margin:.15rem 0 0;line-height:1.5}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-links{display:flex;flex-wrap:wrap;gap:.6rem 1.2rem;margin-top:.8rem}
.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-links a{display:inline-flex;align-items:center;min-height:44px;padding:.2rem .15rem}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-facts>div{border-left-color:CanvasText}.fv-apollo-atlas .fv-apollo-source-drawer dt{color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-source-drawer dt{color:#000}.fv-apollo-atlas .fv-apollo-source-drawer .fv-apollo-plate-links a{display:inline}}
'''
def digest(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)

def create(parent:Path,target:Path)->str:
    for name,pin in PARENT.items():require(digest((parent/name).read_bytes())==pin,'Parent source drift '+name)
    if target.exists():shutil.rmtree(target)
    shutil.copytree(parent,target)
    data=json.loads((parent/'source-drawer-records.json').read_text())
    records=data['sources'];require(len(records)==len(CONTEXT)==4,'Unexpected NASA source count')
    prior=(parent/'templates/atlas-fragment.html').read_text()
    require(prior.count(START)==1,'Ambiguous SourceDrawer')
    first=prior.index(START);last=prior.index('</details>',first)+len('</details>')
    custody=[];cards=[]
    for r in records:
        sid=r['id'];require(sid in CONTEXT,'Unverified record ID')
        label,date_role,anchor=CONTEXT[sid]
        require('id="'+anchor[1:]+'"' in prior,'Missing context anchor '+anchor)
        rid='fv-apollo-plate-'+re.sub('[^a-z0-9]+','-',sid.lower()).strip('-')
        get=lambda key:escape(r[key])
        cards.append('<li data-fv-plate-source="'+escape(sid,quote=True)+'">'
         '<h3>'+get('id')+'</h3><dl class="fv-apollo-plate-facts">'
         '<div><dt>Source kind</dt><dd>'+get('type')+'</dd></div>'
         '<div><dt>'+date_role+'</dt><dd><time datetime="'+get('date')+'">'+escape(label)+'</time></dd></div>'
         '<div><dt>Can establish</dt><dd>'+get('supports')+'</dd></div>'
         '<div><dt>Cannot establish</dt><dd id="'+rid+'-limit">'+get('limit')+'</dd></div>'
         '</dl><nav class="fv-apollo-plate-links" aria-label="Source options for '+escape(sid,quote=True)+'">'
         '<a href="'+escape(r['url'],quote=True)+'" rel="noopener noreferrer" aria-describedby="'+rid+'-limit">Verify at NASA ↗</a>'
         '<a href="'+anchor+'">Find this source in the investigation ↓</a></nav></li>')
        custody.append({'source_id':sid,'url':r['url'],'date':r['date'],'date_label':label,'date_role':date_role,'context_anchor':anchor,'supports':r['supports'],'limitation':r['limit']})
    drawer=START+'<summary>Compare four NASA records and their limits</summary><div class="fv-apollo-drawer-body">'
    drawer+='<h2>Follow a record from its source to its place in the story</h2><p>Source date, source purpose and event date are not interchangeable. The Review Board is the technical source; photographs show preparation or aftermath, never the initiating spark.</p>'
    drawer+='<ol class="fv-apollo-drawer-list">'+''.join(cards)+'</ol><p><strong>Rights boundary:</strong> NASA links document historical evidence, not commercial approval. <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/">NASA advertising guidance</a> applies separately. The original investigation remains free to read.</p></div></details>'
    enhanced=prior[:first]+drawer+prior[last:]
    require(enhanced.count('class="cta"')==1 and 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in enhanced,'Reading CTA drift')
    h=target/'templates/atlas-fragment.html';h.write_text(enhanced)
    c=target/'assets/atlas-scoped.css';c.write_text(c.read_text()+CSS)
    ledger=target/'source-context-plates.json';ledger.write_text(json.dumps({'schema':'fv-apollo-plate-custody-v1','source_records':custody,'published_asset_id':None,'paid_offer_approved':False,'rights_clearance':'NOT_CERTIFIED'},sort_keys=True,indent=2)+'\n')
    old=target/'fv-ex2-apollo-r222.php';text=old.read_text()
    require(PARENT['templates/atlas-fragment.html'] in text and PARENT['assets/atlas-scoped.css'] in text,'PHP parent pins missing')
    text=text.replace('r222','r223').replace('R222','R223')
    text=text.replace(PARENT['templates/atlas-fragment.html'],digest(h.read_bytes())).replace(PARENT['assets/atlas-scoped.css'],digest(c.read_bytes()))
    anchor="        && hash_file('sha256',$html)"
    require(text.count(anchor)==1,'Missing PHP custody gate')
    gate="        && is_readable($root.'source-context-plates.json') && hash_file('sha256',$root.'source-context-plates.json')==='"+digest(ledger.read_bytes())+"'\n"
    text=text.replace(anchor,gate+anchor)
    (target/'fv-ex2-apollo-r223.php').write_text(text);old.unlink()
    sh=target/'wp-render-shim-r222.php';(target/'wp-render-shim-r223.php').write_text(sh.read_text().replace('r222','r223').replace('R222','R223'));sh.unlink()
    files={p.relative_to(target).as_posix():digest(p.read_bytes()) for p in sorted(target.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    manifest={'release':'R223','status':'STAGING_HOLD','parent_manifest_sha256':PARENT['manifest.json'],'files':files,'not_live':True,'release_gates':{'axe_core':'NOT_EXECUTED','wordpress':'NOT_TESTED','founder':'NOT_APPROVED','R198':'UNRESOLVED','commercial_offer':'NOT_VERIFIED'}}
    (target/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return digest((target/'manifest.json').read_bytes())
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--parent',type=Path,required=True);a.add_argument('--target',type=Path,required=True);o=a.parse_args();print(create(o.parent,o.target))
