#!/usr/bin/env python3
"""Apollo R208: distinguish event dates from later Board report completion.

Builds exclusively from the SHA-256-pinned R206 staging dist, not from an unreviewed
WordPress snapshot. All figures are source citations, not license grants. No photos,
paid destinations, event scripts, production APIs, or invented map pins.
"""
from __future__ import annotations
import hashlib, json, re, shutil
from pathlib import Path
from html import escape
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'apollo-r206'/'dist'
DIST=HERE/'dist'
REPO='finalvestigestudios/final-vestige-site-layer'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RIGHTS='https://www.nasa.gov/nasa-brand-center/advertising-guidelines/'
RECORDS=(
 {'id':'S66-58038','date':'1966-10-18','type':'photo','label':'Crew training · 18 October 1966','url':'https://www.nasa.gov/image-detail/amf-s66-58038/','supports':'A photograph of the crew preparing for training.','does_not_support':'It does not document ignition, cabin pressure, or the fire.','target':'fv-apollo-photo-1966'},
 {'id':'S67-15717','date':'1967-01-03','type':'photo','label':'Spacecraft processing · 3 January 1967','url':'https://www.nasa.gov/image-detail/amf-s67-15717/','supports':'A dated photograph of spacecraft 012 processing.','does_not_support':'It is not a measurement of the January 27 cabin conditions.','target':'fv-apollo-photo-prep'},
 {'id':'Apollo 204 Review Board','date':'1967-01-27','type':'technical-report','label':'Fire: 27 January 1967; Review Board report: April 1967','url':BOARD,'supports':'The accident account, hazardous test conditions, and the most probable electrical-arc initiator.','does_not_support':'The exact ignition source was not conclusively identified.','target':'fv-apollo-finding-fire','report_completed_month':'1967-04','report_timing_source':'https://www.nasa.gov/apollo-1-resources/'},
 {'id':'S67-21294','date':'1967-01-28','type':'photo','label':'Damage documentation · 28 January 1967','url':'https://www.nasa.gov/image-detail/amf-s67-21294/','supports':'A photograph of command-module damage after the fire.','does_not_support':'It does not show the ignition event or establish the initiating spark.','target':'fv-apollo-photo-aftermath'},
)
CSS='''
/* R208 archival custody capsule with explicit report-date distinction, fail-open source navigation. */
.fv-apollo-atlas .fv-apollo-custody{margin:clamp(1.4rem,3vw,2.8rem) 0;max-width:100%;min-width:0;padding:clamp(1rem,2.4vw,1.6rem);border:1px solid var(--line);background:var(--bg)}
.fv-apollo-atlas .fv-apollo-custody h2{margin:.3rem 0 .65rem}
.fv-apollo-atlas .fv-apollo-custody .intro{max-width:78ch}
.fv-apollo-atlas .fv-apollo-custody-list{list-style:none;padding:0;margin:1.15rem 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}
.fv-apollo-atlas .fv-apollo-custody-list li{min-width:0;padding:clamp(.7rem,1.5vw,1rem);border:1px solid var(--line);overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-custody-list h3{margin:0 0 .55rem;font-size:clamp(1rem,1.7vw,1.2rem);line-height:1.45}
.fv-apollo-atlas .fv-apollo-custody-kind{display:block;color:var(--accent);letter-spacing:.05em;text-transform:uppercase;font-size:.76rem;margin-bottom:.35rem}
.fv-apollo-atlas .fv-apollo-custody-list p{font-size:.93rem;line-height:1.55;margin:.45rem 0}
.fv-apollo-atlas .fv-apollo-custody a{overflow-wrap:anywhere;text-underline-offset:.2em}
.fv-apollo-atlas .fv-apollo-custody a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.fv-apollo-atlas .fv-apollo-custody-rights{font-size:.89rem;max-width:84ch}
@media(max-width:720px){.fv-apollo-atlas .fv-apollo-custody-list{grid-template-columns:minmax(0,1fr)}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-custody,.fv-apollo-atlas .fv-apollo-custody-list li{border-color:CanvasText}.fv-apollo-atlas .fv-apollo-custody-kind{color:CanvasText}}
@media(prefers-reduced-motion:reduce){.fv-apollo-atlas .fv-apollo-custody *{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
@media print{.fv-apollo-atlas .fv-apollo-custody{break-inside:auto;background:white!important;color:black!important}.fv-apollo-atlas .fv-apollo-custody-list{display:block}.fv-apollo-atlas .fv-apollo-custody-list li{break-inside:avoid;margin-bottom:.5rem}.fv-apollo-atlas .fv-apollo-custody a{color:black!important;text-decoration:underline!important}.fv-apollo-atlas .fv-apollo-custody a[href^="https:"]::after{content:' [' attr(href) ']';font-size:.7em;overflow-wrap:anywhere}}

/* R208: the report postdates the accident. */
.fv-apollo-atlas .fv-apollo-report-date-contract{padding:.75rem 1rem;border-left:3px solid var(--accent);line-height:1.55}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-report-date-contract{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-report-date-contract{break-inside:avoid}}
'''
def digest(blob:bytes)->str:return hashlib.sha256(blob).hexdigest()
def html_segment():
 items=[]
 for r in RECORDS:
  date_note=('<p class="fv-apollo-report-date-contract"><strong>Two dates, two roles:</strong> the fire occurred <time datetime="1967-01-27">27 January 1967</time>. NASA describes the Board report as completed in <time datetime="1967-04">April 1967</time>. The findings are retrospective, not an observation recorded at the moment of ignition. <a href="https://www.nasa.gov/apollo-1-resources/">Verify report timing with NASA</a>.</p>' if r['type']=='technical-report' else '')
  items.append('<li data-source-record="'+escape(r['id'])+'" data-evidence-type="'+r['type']+'"><span class="fv-apollo-custody-kind">'+('NASA catalog photograph' if r['type']=='photo' else 'NASA technical report')+'</span><h3>'+escape(r['label'])+'</h3>'+date_note+'<p><strong>What it establishes:</strong> '+escape(r['supports'])+'</p><p id="fv-apollo-custody-limit-'+str(len(items)+1)+'"><strong>What it cannot prove:</strong> '+escape(r['does_not_support'])+'</p><p><a href="#'+r['target']+'">Examine the record in this atlas</a> · <a href="'+r['url']+'" aria-describedby="fv-apollo-custody-limit-'+str(len(items)+1)+'">Inspect original NASA record '+escape(r['id'])+'</a></p></li>')
 return '''<section class="fv-apollo-custody section" id="fv-apollo-custody" aria-labelledby="fv-apollo-custody-title" tabindex="-1">
<span class="eyebrow">Archival custody / source verification</span><h2 id="fv-apollo-custody-title">Four records. Four limits on what we can conclude.</h2>
<p class="intro">These links distinguish photographic records from the technical investigation. Photograph dates and the accident date are not report publication dates. The Review Board report was completed afterward, in April 1967. Each record can be checked in the atlas and directly with NASA.</p>
<ol class="fv-apollo-custody-list">'''+''.join(items)+'''</ol>
<p class="fv-apollo-custody-rights"><strong>Media rights are a separate check.</strong> The NASA records linked here have not been licensed or cleared for use in Final Vestige paid promotions. Cite the source without implying endorsement. <a href="'''+RIGHTS+'''">Read NASA advertising guidance</a>.</p>
</section>'''
def build():
 assert PARENT.is_dir(),'R206 parent dist missing; do not silently rebuild different ancestry'
 old=json.loads((PARENT/'manifest.json').read_text('utf8'))
 assert old['release']=='r206' and old['source_chain_verified'] is False
 for path,h in old['files'].items():assert digest((PARENT/path).read_bytes())==h,'parent hash mismatch '+path
 raw=(PARENT/'templates/atlas-fragment.html').read_bytes();html=raw.decode('utf8')
 marker='<section class="fv-apollo-reading-lab"'
 assert html.count(marker)==1
 assert 'fv-apollo-custody' not in html
 newhtml=html.replace(marker,html_segment()+'\n'+marker,1)
 for r in RECORDS:assert r['target'] in html and r['url'] in newhtml
 assert newhtml.count('datetime="1967-04"')==1
 assert newhtml.count('datetime="1967-01-27"')>=1
 assert newhtml.count('class="cta"')==1 and len(re.findall(r'<details(?: |>)',newhtml))==11
 oldcss=(PARENT/'assets/atlas-scoped.css').read_bytes();newcss=oldcss+CSS.encode('utf8')
 js=(PARENT/'assets/campaign-handoff.js').read_bytes()
 php=(PARENT/'fv-ex2-apollo-r206.php').read_text('utf8')
 assert 'r206' in php
 php=php.replace('r206','r208').replace('R206','R208')
 for prior,new in ((raw,newhtml.encode('utf8')),(oldcss,newcss)):
  assert php.count(digest(prior))==1
  php=php.replace(digest(prior),digest(new),1)
 assert digest(js) in php
 blobs={'templates/atlas-fragment.html':newhtml.encode('utf8'),'assets/atlas-scoped.css':newcss,'assets/campaign-handoff.js':js,'fv-ex2-apollo-r208.php':php.encode('utf8')}
 for file,blob in blobs.items():
  output=DIST/file;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(blob)
 (DIST/'wp-render-shim-r208.php').write_text((PARENT/'wp-render-shim-r206.php').read_text('utf8').replace('r206','r208').replace('R206','R208'))
 for file in ('commercial-offer-gate.json','conversion-validation.json','source-records.json'):(DIST/file).write_bytes((PARENT/file).read_bytes())
 custody={'authority':'NASA','record_types':{'photo':'catalog record, not technical determination','technical-report':'Apollo 204 Board findings'},'records':RECORDS,'commercial_photo_rights_cleared':False,'implied_endorsement_permitted':False,'NASA_advertising_guidelines':RIGHTS,'geo_pins':[],'speculative_edges':[],'purchase_sku_verified':False,'notes':'Dates verified against NASA individual catalog pages. Source availability is independent of media licensing.'}
 custody['chronology_date_contract']={'accident_event_date':'1967-01-27','board_report_completed_month':'1967-04','report_date_precision':'month','date_type':'retrospective technical finding, not accident-day document','timing_source':'https://www.nasa.gov/apollo-1-resources/','rights_not_cleared':True}
 (DIST/'custody-ledger.json').write_text(json.dumps(custody,indent=2,sort_keys=True)+'\n',encoding='utf8')
 manifest={'release':'r208','parent_head':'4187de244b045c8072245769922cd64c424fb1c5','parent_manifest_sha256':digest((PARENT/'manifest.json').read_bytes()),'files':{k:digest(v) for k,v in sorted(blobs.items())},'custody_ledger_sha256':digest((DIST/'custody-ledger.json').read_bytes()),'source_chain_verified':False,'canonical_r198_builder_git_blob':old['canonical_r198_builder_git_blob'],'inherited_r198_local_git_blob':old['inherited_r198_local_git_blob'],'release_gate':'STAGING HOLD: R198 inherited discrepancy, installed WP, genuine axe, NVDA/VoiceOver, CI, independent QA, commercial rights, founder approval'}
 (DIST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8')
 assert custody['chronology_date_contract']['board_report_completed_month']=='1967-04'
 return manifest
if __name__=='__main__':print(json.dumps(build(),sort_keys=True,indent=2))
