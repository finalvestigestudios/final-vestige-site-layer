#!/usr/bin/env python3
"""R211: correct year-only NASA photo dating vs a dated Board milestone.

Read-only, deterministic staging builder. No WordPress, network, payments or analytics.
"""
import hashlib, json, os, re, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=Path(os.environ.get('FV_APOLLO_R210_DIST',str(HERE/'../apollo-r210/dist'))).resolve()
OUT=HERE/'dist'
PIN='ff13886f46237b08e71d6b68cb13f8d712941cea6e99b1130c7e8de9736a3e7b'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
PHOTO='https://www.nasa.gov/image-detail/amf-s67-15717/'

def sha(data): return hashlib.sha256(data).hexdigest()
def must(v,msg):
    if not v: raise ValueError(msg)
def swap(body,old,new):
    must(body.count(old)==1, 'Source drift / missing single match: '+old[:85])
    return body.replace(old,new,1)

def build():
    must(sha((BASE/'manifest.json').read_bytes())==PIN,'R210 manifest mismatch')
    parent=json.loads((BASE/'manifest.json').read_text())
    must(parent['release']=='r210' and not parent['approved_purchase_offer'],'Unapproved source/commerce state')
    for path,digest in parent['files'].items():
        must(sha((BASE/path).read_bytes())==digest,'Modified R210 artifact: '+path)
    html=(BASE/'templates/atlas-fragment.html').read_text()
    old='<a href="#fv-apollo-photo-prep">Spacecraft preparation</a>'
    html=swap(html,old,'<a href="#fv-apollo-photo-prep">Module leaves altitude chamber</a>')
    html=swap(html,'NASA photo S67-15717: command/service module processing, not fire evidence.',
      'The Review Board dates the chamber removal to 3 January. NASA catalogs photo S67-15717 to 1967 only; its exact exposure day is not established.')
    html=swap(html,'<a class="fv-apollo-rail-source" href="'+PHOTO+'" aria-describedby="fv-apollo-rail-note-photo-and-history" rel="noopener noreferrer" data-source-id="S67-15717">Open NASA 3 January 1967 spacecraft processing photograph</a>',
      '<a class="fv-apollo-rail-source" href="'+BOARD+'" aria-describedby="fv-apollo-rail-note-photo-and-history" data-source-id="Apollo 204 Review Board">Verify January 3 chamber removal in the NASA Review Board report</a> · <a href="'+PHOTO+'" aria-describedby="fv-apollo-rail-note-photo-and-history" data-source-id="S67-15717">View NASA photograph S67-15717 (catalog year 1967)</a>')
    html=swap(html,'<h3>Spacecraft processing · 3 January 1967</h3><p><strong>What it establishes:</strong> A dated photograph of spacecraft 012 processing.</p>',
      '<h3>Spacecraft processing · catalog year 1967</h3><p><strong>What it establishes:</strong> A photograph of spacecraft 012 processing. NASA catalogs it to 1967, without establishing a January 3 exposure date.</p><p><strong>Separate written record:</strong> The Review Board dates command-module chamber removal to <time datetime="1967-01-03">3 January 1967</time>. <a href="'+BOARD+'">Verify the preparation milestone in the Board report</a>.</p>')
    html=swap(html,'<strong>What it cannot prove:</strong> It is not a measurement of the January 27 cabin conditions.',
      '<strong>What it cannot prove:</strong> It cannot date the photographed moment to 3 January or establish the January 27 cabin conditions.')
    html=swap(html,"<p>The spacecraft processing image is not a photograph of the cabin fire. The specific January 3 processing milestone comes from NASA's written history.</p>",
      '<p>The NASA photograph shows spacecraft processing and is cataloged as 1967; the exact photo day is unverified. The separate January 3 chamber-removal milestone comes from the written Review Board report.</p>')
    html=swap(html,'<ol class="rail">',
      '<p class="fv-apollo-date-precision"><strong>Source-date distinction:</strong> January 3 is a milestone verified in the Review Board text, not the confirmed exposure date of photograph S67-15717. The NASA photo catalog gives only <time datetime="1967">1967</time>.</p><ol class="rail">')
    must('Open NASA 3 January 1967 spacecraft processing photograph' not in html,'Unsupported photographic date survived')
    must(html.count('class="cta"')==1 and html.count('<details')==12,'Evidence actions changed')
    must('data-lat' not in html and 'data-lng' not in html,'Fabricated geo')
    css=(BASE/'assets/atlas-scoped.css').read_text()+'''
/* R211: distinguish event and photo date without implying archival rights. */
.fv-apollo-atlas .fv-apollo-date-precision{max-width:80ch;border-inline-start:3px solid currentColor;padding:.7rem 1rem;line-height:1.55;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-date-precision:focus-within{outline:2px solid currentColor;outline-offset:3px}
@media print{.fv-apollo-atlas .fv-apollo-date-precision{break-inside:avoid;color:black!important}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-date-precision{border-color:CanvasText}}
'''
    assets={'templates/atlas-fragment.html':html.encode(),'assets/atlas-scoped.css':css.encode(),
      'assets/campaign-handoff.js':(BASE/'assets/campaign-handoff.js').read_bytes()}
    php=(BASE/'fv-ex2-apollo-r210.php').read_text().replace('r210','r211').replace('R210','R211')
    for name in ('templates/atlas-fragment.html','assets/atlas-scoped.css'):
        php=swap(php,parent['files'][name],sha(assets[name]))
    php=swap(php,"'"+parent['files']['assets/atlas-scoped.css'][:12]+"'", "'"+sha(assets['assets/atlas-scoped.css'])[:12]+"'")
    assets['fv-ex2-apollo-r211.php']=php.encode()
    generated=dict(assets)
    generated['wp-render-shim-r211.php']=(BASE/'wp-render-shim-r210.php').read_text().replace('r210','r211').replace('R210','R211').encode()
    for name in ['commercial-offer-gate.json','conversion-validation.json']:
        generated[name]=(BASE/name).read_bytes()
    sr=json.loads((BASE/'source-records.json').read_text())
    row=next(r for r in sr if r['source_id']=='S67-15717')
    must(row['date']=='1967-01-03','R210 metadata drift')
    row.update({'date':'1967','date_precision':'year','event_date':'1967-01-03','event_source_url':BOARD,
      'accessible_label':'Open NASA 1967 spacecraft processing photograph',
      'limitation':'NASA photo catalog gives 1967 only; Jan 3 chamber removal is a separate Board-reported event'})
    generated['source-records.json']=(json.dumps(sr,indent=2,sort_keys=True)+'\n').encode()
    ledger=json.loads((BASE/'custody-ledger.json').read_text())
    row=next(r for r in ledger['records'] if r['id']=='S67-15717')
    must(row['date']=='1967-01-03','R210 ledger metadata drift')
    row.update({'date':'1967','date_precision':'year', 'event_date':'1967-01-03', 'event_source_url':BOARD,
      'label':'Spacecraft processing · catalog year 1967',
      'supports':'Photo shows spacecraft processing, catalog year 1967; separate Review Board dates chamber removal to Jan 3.',
      'does_not_support':'Photo does not independently establish January 3 exposure or January 27 cabin conditions.'})
    ledger['notes']='S67-15717 catalog only asserts 1967; the Review Board separately confirms January 3 chamber removal. Never merge event and photo dates.'
    generated['custody-ledger.json']=(json.dumps(ledger,indent=2,sort_keys=True)+'\n').encode()
    audit=json.loads((BASE/'source-audit.json').read_text())
    audit.update({'source':'rendered_R211_html','R211_photo_S67_15717_date_precision':'year-only',
        'R211_board_preparation_event_date':'1967-01-03','R211_photo_exact_day':'NOT_ESTABLISHED',
        'R211_date_claim_source':BOARD,'canonical_ancestry_from_R198':'NOT_RECONCILED'})
    generated['source-audit.json']=(json.dumps(audit,indent=2,sort_keys=True)+'\n').encode()
    manifest={'release':'r211','parent_manifest_sha256':PIN,'files':{k:sha(v) for k,v in sorted(generated.items())},
      'NASA_photo_day_certified':False,'NASA_board_preparation_date_certified':True,
      'approved_purchase_offer':False,'media_commercial_rights_cleared':False,
      'upstream_R198_reconciled':False,'installed_WordPress_accepted':False,
      'axe_core_accepted':False,'release_gate':'STAGING HOLD / WordPress / CI / axe / ancestry / founder'}
    generated['manifest.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    if OUT.exists():shutil.rmtree(OUT)
    for name,data in sorted(generated.items()):
        p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return manifest
if __name__=='__main__':print(json.dumps(build(),indent=2,sort_keys=True))
