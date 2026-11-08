#!/usr/bin/env python3
"""R224: source-custodied retrospective Review Board stop in Apollo ChronologyRail.
Staging-only additive builder. Never writes WordPress, deploys, or follows a network link.
"""
from __future__ import annotations
import argparse,hashlib,json,re,shutil
from pathlib import Path
PINS={
 'manifest.json':'60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e',
 'templates/atlas-fragment.html':'704178e8e56c1608b65492467f56ed538e4cc18652f7f847114be40c7a7c08b0',
 'assets/atlas-scoped.css':'9df7ae4c1c19de7a85ea57c5d245355d9a68fc638e9ce90fd838373de54e1a23',
 'source-url-crosswalk.json':'998191dd07f2fde2d0e14c9fd91b58b6670fd662afe692d3ded6e0454f0948cc',
}
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
STOP=('\n<li data-evidence-kind="retrospective-report"><time datetime="1967-04">April 1967</time>'
 '<span class="fv-apollo-rail-kind">Review Board report · retrospective findings</span>'
 '<a href="#fv-apollo-source-drawer">See the Board source limits</a>'
 '<small id="fv-apollo-rail-note-retrospective-report">This report records findings reached after the 27 January accident. '
 'It is not a photograph of the fire or a continuous sensor timeline; no single ignition source was conclusively identified.</small>'
 '<a class="fv-apollo-rail-report-link" data-source-id="Apollo 204 Review Board" '
 'aria-describedby="fv-apollo-rail-note-retrospective-report" href="'+NASA+'" '
 'rel="noopener noreferrer">Read the NASA Apollo 204 Review Board report</a></li>\n')
CSS='''\n/* R224: tactile report source target, scoped to this one retrospective chronology record. */
.fv-apollo-atlas .rail .fv-apollo-rail-report-link{display:inline-flex;align-items:center;min-height:44px}
@media (forced-colors:active){.fv-apollo-atlas .rail .fv-apollo-rail-report-link:focus-visible{outline:3px solid Highlight;outline-offset:3px}}
'''
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,reason):
 if not ok:raise ValueError(reason)
def create(parent:Path,target:Path)->str:
 for name,h in PINS.items():require(sha(parent/name)==h,'Unreviewed R223 parent drift: '+name)
 if target.exists():shutil.rmtree(target)
 shutil.copytree(parent,target)
 hfile=target/'templates/atlas-fragment.html';h=hfile.read_text()
 old_heading='Four dates. Distinct kinds of evidence.'
 require(h.count(old_heading)==1,'Chronology heading drift')
 require(h.count('<ol class="rail">')==1,'Ambiguous chronology rail')
 require(h.count(FREE)>=1 and h.count('class="cta"')==1,'Free CTA drift')
 h=h.replace(old_heading,'Five dates. Distinct kinds of evidence.')
 start=h.index('<ol class="rail">');end=h.index('</ol>',start)
 require('datetime="1967-01-28"' in h[start:end] and 'datetime="1967-04"' not in h[start:end],'Sequence drift')
 h=h[:end]+STOP+h[end:]
 hfile.write_text(h)
 css_file=target/'assets/atlas-scoped.css';css_file.write_text(css_file.read_text()+CSS)
 cross=target/'source-url-crosswalk.json';old_cross=json.loads(cross.read_text())
 require(old_cross['chronology_dates']==['1966-10-18','1967-01-03','1967-01-27','1967-01-28'],'Chronology ledger drift')
 old_cross['chronology_dates'].append('1967-04')
 cross.write_text(json.dumps(old_cross,sort_keys=True,indent=2)+'\n')
 ledger=target/'chronology-report-custody.json';ledger.write_text(json.dumps({
  'schema':'fv-apollo-retrospective-report-v1','record_id':'Apollo 204 Review Board',
  'source_url':NASA,'source_date':'1967-04','source_date_role':'report issued',
  'accident_date':'1967-01-27','accident_date_role':'event described retrospectively',
  'conclusion':'electrical arc most probable; no conclusive single ignition source',
  'limitations':'Report findings must not be presented as a direct photograph or continuous sensor record.',
  'context_anchor':'#fv-apollo-source-drawer','approved_paid_product':False,
  'verified_creator_asset_id':None,'further_media_rights':'NOT_CERTIFIED'
 },sort_keys=True,indent=2)+'\n')
 old_php=target/'fv-ex2-apollo-r223.php';php=old_php.read_text()
 for name in ['templates/atlas-fragment.html','assets/atlas-scoped.css','source-url-crosswalk.json']:
  require(php.count(PINS[name])>=1,'PHP custody pin drift: '+name)
  php=php.replace(PINS[name],sha(target/name))
 marker="        && hash_file('sha256',$html)"
 require(php.count(marker)==1,'PHP gate anchor drift')
 pin=("        && is_readable($root.'chronology-report-custody.json') && hash_file('sha256',$root.'chronology-report-custody.json')==='"+sha(ledger)+"'\n")
 php=php.replace(marker,pin+marker)
 php=php.replace('r223','r224').replace('R223','R224')
 (target/'fv-ex2-apollo-r224.php').write_text(php);old_php.unlink()
 old_shim=target/'wp-render-shim-r223.php';(target/'wp-render-shim-r224.php').write_text(old_shim.read_text().replace('r223','r224').replace('R223','R224'));old_shim.unlink()
 files={f.relative_to(target).as_posix():sha(f) for f in sorted(target.rglob('*')) if f.is_file() and f.name!='manifest.json'}
 manifest={'release':'R224','status':'STAGING_HOLD','parent_manifest_sha256':PINS['manifest.json'],'files':files,
 'not_live':True,'release_gates':{'axe_core':'NOT_EXECUTED','wordpress':'NOT_TESTED','founder':'NOT_APPROVED',
 'R198':'UNRESOLVED','commercial_offer':'NOT_VERIFIED','Grok_asset_id':'UNVERIFIED'}}
 (target/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
 return sha(target/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--parent',required=True,type=Path);p.add_argument('--target',required=True,type=Path)
 a=p.parse_args();print(create(a.parent,a.target))
