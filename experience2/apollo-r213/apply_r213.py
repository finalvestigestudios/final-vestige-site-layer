#!/usr/bin/env python3
"""Staging-only R213 nav/CTA source patch against digest-pinned Apollo R212 output."""
import hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=Path(os.environ.get('FV_APOLLO_R212_DIST',ROOT/'../r212/dist')).resolve()
OUT=ROOT/'dist'
PARENT='d23c2dfe339adfeadf76dc08ac2f4f360c0d71fb64f2721a83488d45619ba9d8'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(c,msg):
 if not c:raise ValueError(msg)
def one(s,a,b):
 need(s.count(a)==1,'parent drift: '+a[:72]);return s.replace(a,b,1)
def j(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def main():
 need(sha((BASE/'manifest.json').read_bytes())==PARENT,'parent manifest changed')
 parent=json.loads((BASE/'manifest.json').read_text())
 need(parent['release']=='r212' and all(parent[k] is False for k in ['approved_purchase_offer','media_commercial_rights_cleared','upstream_R198_reconciled','installed_WordPress_accepted','axe_core_accepted']),'unsafe parent release state')
 for path,digest in parent['files'].items():need(sha((BASE/path).read_bytes())==digest,'parent file tampered: '+path)
 html=(BASE/'templates/atlas-fragment.html').read_text()
 html=one(html,'<nav aria-label="On this page"><a href="#fv-apollo-chronology">Chronology</a><a href="#fv-apollo-evidence">Findings</a><a href="#fv-apollo-gallery">Archive gallery</a><a href="#fv-apollo-source-test">Source test</a></nav>',
 '<nav aria-label="Apollo evidence and next step"><a href="#fv-apollo-evidence">Review findings</a><a href="#fv-apollo-chronology">Chronology</a><a href="#fv-apollo-gallery">Archive gallery</a><a href="#fv-apollo-source-test">Source test</a><a class="fv-apollo-nav-read" href="#fv-apollo-reading-bridge" aria-describedby="fv-apollo-nav-read-note">Read investigation</a></nav>')
 html=one(html,'<aside class="fv-apollo-reading-bridge" id="fv-apollo-reading-bridge"','<aside class="fv-apollo-reading-bridge" id="fv-apollo-reading-bridge" tabindex="-1"')
 html=one(html,'<p id="fv-apollo-reading-bridge-desc">','<p class="fv-apollo-nav-read-note" id="fv-apollo-nav-read-note">The free full investigation is linked after the four source findings.</p><p id="fv-apollo-reading-bridge-desc">')
 need(html.count('class="cta"')==1 and html.count('href="#fv-apollo-reading-bridge"')==2,'single-action/nav invariant')
 need('https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' in html and 'No single ignition source' in html,'NASA source/uncertainty absent')
 need('data-lat=' not in html and 'data-lng=' not in html and '<img' not in html,'unapproved media/geography')
 css=(BASE/'assets/atlas-scoped.css').read_text()+'''
/* R213: one keyboard/touch/no-JS jump to the existing free investigation action. */
.fv-apollo-atlas .mast .fv-apollo-nav-read{padding:.3rem .55rem;border:1px solid currentColor;font-weight:700;overflow-wrap:anywhere}
.fv-apollo-atlas .mast .fv-apollo-nav-read:hover{text-decoration-thickness:3px}
.fv-apollo-atlas .fv-apollo-reading-bridge:target,.fv-apollo-atlas .fv-apollo-reading-bridge:focus-visible{outline:3px solid var(--accent);outline-offset:5px;scroll-margin-top:2rem}
.fv-apollo-atlas .fv-apollo-nav-read-note{font-size:.875rem;margin:.4em 0 1em;color:#eee1d0}
@media(max-width:500px){.fv-apollo-atlas .mast nav{gap:.45rem .8rem}.fv-apollo-atlas .mast .fv-apollo-nav-read{padding:.5rem}}
@media(forced-colors:active){.fv-apollo-atlas .mast .fv-apollo-nav-read{border-color:LinkText}.fv-apollo-atlas .fv-apollo-reading-bridge:target{outline-color:Highlight}}
@media(prefers-reduced-motion:reduce){.fv-apollo-atlas .fv-apollo-reading-bridge{scroll-behavior:auto!important}}
@media print{.fv-apollo-atlas .fv-apollo-nav-read-note{display:none}.fv-apollo-atlas .fv-apollo-reading-bridge:target{outline:0}}
'''
 files={'templates/atlas-fragment.html':html.encode(),'assets/atlas-scoped.css':css.encode(),'assets/campaign-handoff.js':(BASE/'assets/campaign-handoff.js').read_bytes()}
 php=(BASE/'fv-ex2-apollo-r212.php').read_text().replace('r212','r213').replace('R212','R213')
 for path in ('templates/atlas-fragment.html','assets/atlas-scoped.css'):
  php=one(php,parent['files'][path],sha(files[path]))
 files['fv-ex2-apollo-r213.php']=php.encode()
 files['wp-render-shim-r213.php']=(BASE/'wp-render-shim-r212.php').read_text().replace('r212','r213').replace('R212','R213').encode()
 for path in ('source-records.json','custody-ledger.json','commercial-offer-gate.json'):files[path]=(BASE/path).read_bytes()
 audit=json.loads((BASE/'source-audit.json').read_text());audit['R213_nav']={'type':'single in-page jump to free editorial action','commercial_approval':False,'NASA_rights':'uncleared','Grok_asset_id':'unverified'};files['source-audit.json']=j(audit)
 cv=json.loads((BASE/'conversion-validation.json').read_text());cv['R213_path']={'offer':'educator dossier UNAPPROVED','step':'Atlas finding → free investigation','change':'top accessible internal nav link','paid_conversion':'UNVERIFIED','revenue':'NOT COMPUTABLE'};files['conversion-validation.json']=j(cv)
 manifest={'release':'r213','parent_manifest_sha256':PARENT,'files':{k:sha(v) for k,v in sorted(files.items())},'approved_purchase_offer':False,'media_commercial_rights_cleared':False,'upstream_R198_reconciled':False,'installed_WordPress_accepted':False,'axe_core_accepted':False,'release_gate':'STAGING HOLD / WP + axe + provenance + CI + founder'}
 files['manifest.json']=j(manifest)
 if OUT.exists():shutil.rmtree(OUT)
 for path,body in sorted(files.items()):
  dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
 print(json.dumps({'release':'r213','manifest_sha256':sha(files['manifest.json']),'file_count':len(files)}))
if __name__=='__main__':main()
