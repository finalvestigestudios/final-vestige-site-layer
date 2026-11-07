#!/usr/bin/env python3
"""R198: evidence-to-NASA-source crosswalk; staging only, no commerce or telemetry."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r197'
DIST=HERE/'dist'
NASA_BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RECORDS=(
 ('oxygen','Oxygen atmosphere','Review Board technical findings','Combustion conditions do not identify the initiating spark.'),
 ('fire','Ignition uncertainty','Review Board determination','A probable electrical arc is not proof of a specific ignition source.'),
 ('hatch','Hatch and egress','Review Board escape findings','Hatch design compounded escape difficulty; it did not start the fire.'),
 ('chronology','Pressure chronology','Review Board instrument and pressure discussion','A reported pressure marker is not a frame-by-frame recording.'),
)
CSS="""
/* R198 evidence-to-source crosswalk: no JavaScript, responsive and printable. */
.fv-apollo-atlas .fv-apollo-trace{margin:1.35rem 0;padding:clamp(.9rem,2vw,1.45rem);border:1px solid var(--line);background:rgba(190,152,88,.045);min-width:0}
.fv-apollo-atlas .fv-apollo-trace h3{font-size:clamp(1.1rem,2vw,1.42rem);margin:.4rem 0 .6rem;line-height:1.3}
.fv-apollo-atlas .fv-apollo-trace p{max-width:70ch;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-trace-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));list-style:none;padding:0;margin:1.1rem 0;gap:clamp(.65rem,2vw,1rem)}
.fv-apollo-atlas .fv-apollo-trace-grid li{min-width:0;padding:.95rem;border:1px solid var(--line);background:var(--bg);overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-trace-grid strong{display:block;color:var(--paper)}
.fv-apollo-atlas .fv-apollo-trace-grid p{margin:.5rem 0;font-size:.91rem;line-height:1.55}
.fv-apollo-atlas .fv-apollo-trace a{text-underline-offset:.2em;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-trace a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.fv-apollo-atlas .fv-apollo-trace-rights{padding:.75rem 0 0;border-top:1px solid var(--line)}
@media(max-width:650px){.fv-apollo-atlas .fv-apollo-trace-grid{grid-template-columns:minmax(0,1fr)}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-trace,.fv-apollo-atlas .fv-apollo-trace-grid li{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-trace{background:#fff!important;color:#111!important}.fv-apollo-atlas .fv-apollo-trace-grid li{background:#fff!important;break-inside:avoid}.fv-apollo-atlas .fv-apollo-trace-grid strong{color:#111!important}.fv-apollo-atlas .fv-apollo-trace a{color:#111!important;text-decoration:underline!important}}
"""
def sha(b): return hashlib.sha256(b).hexdigest()

def build():
 sys.path.insert(0,str(PARENT))
 from build_r197 import build as build_parent
 parent=build_parent(); prior=PARENT/'dist'
 for name,digest in parent['files'].items():
  assert sha((prior/name).read_bytes())==digest,'parent integrity failed: '+name
 original=(prior/'templates/atlas-fragment.html').read_bytes()
 html=original.decode('utf-8')
 marker='</aside>\n<section aria-labelledby="fv-apollo-chronology-title"'
 assert html.count(marker)==1
 rows=[]
 for number,(short,title,record,boundary) in enumerate(RECORDS,1):
  target='fv-apollo-finding-'+short
  assert html.count('id="'+target+'"')==1
  rows.append('<li data-finding="'+target+'" data-record-kind="review-board"><strong>'+str(number).zfill(2)+' · '+title+'</strong><p><b>Record:</b> '+record+'.</p><p><b>Boundary:</b> '+boundary+'</p><p><a href="#'+target+'">Examine '+title.lower()+' finding</a> · <a href="'+NASA_BOARD+'">Read NASA technical source</a></p></li>')
 trace=('''<section class="fv-apollo-trace" aria-labelledby="fv-apollo-trace-title">
<span class="eyebrow">Source custody / claim-to-record crosswalk</span>
<h3 id="fv-apollo-trace-title">Trace each finding to what the source actually supports.</h3>
<p>All four technical findings use the Apollo 204 Review Board, not an archival photograph, as their source of record. A source link is a way to check our wording, not a claim that NASA endorses this site.</p>
<ol class="fv-apollo-trace-grid">'''+''.join(rows)+'''</ol>
<p class="fv-apollo-trace-rights"><strong>Photographic exception:</strong> NASA's <a href="https://www.nasa.gov/image-detail/amf-s67-21294/">S67-21294 aftermath catalog</a> documents January 28 damage, not ignition. NASA's <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/">advertising guidance</a> is a separate rights/endorsement reference; research citation is not commercial-use clearance.</p>
</section>''')
 html=html.replace(marker,trace+'\n'+marker,1)
 assert html.count('data-record-kind="review-board"')==4
 assert html.count('class="cta"')==1 and html.count('<details>')==8
 prior_css=(prior/'assets/atlas-scoped.css').read_bytes()
 css=prior_css+CSS.encode('utf-8')
 php=(prior/'fv-ex2-apollo-r197.php').read_text().replace('r197','r198').replace('R197','R198')
 for before,after in ((original,html.encode('utf-8')),(prior_css,css)):
  assert php.count(sha(before))==1,'missing parent SHA-256 pin'
  php=php.replace(sha(before),sha(after),1)
 js=(prior/'assets/campaign-handoff.js').read_bytes()
 assert sha(js) in php
 files={'templates/atlas-fragment.html':html.encode('utf-8'),
  'assets/atlas-scoped.css':css,
  'assets/campaign-handoff.js':js,
  'fv-ex2-apollo-r198.php':php.encode('utf-8')}
 for name,blob in sorted(files.items()):
  file=DIST/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(blob)
 shim=(prior/'wp-render-shim-r197.php').read_text().replace('r197','r198').replace('R197','R198')
 (DIST/'wp-render-shim-r198.php').write_text(shim)
 manifest={'release':'r198','parent_head':'7bb1742262ca842be8df359fbc317f38cf609f34',
  'purpose':'Visible no-JS NASA claim-source custody and photographic/advertising rights boundary',
  'files':{n:sha(b) for n,b in sorted(files.items())},
  'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
  'release_gate':'DRAFT; installed WP, axe-core, exact-head CI, commercial validation and founder approval outstanding'}
 (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
 return manifest

if __name__=='__main__': print(json.dumps(build(),indent=2))
