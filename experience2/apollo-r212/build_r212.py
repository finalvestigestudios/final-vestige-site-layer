#!/usr/bin/env python3
"""R212: source-first, single-action reading bridge; staging only, fail-closed build."""
import hashlib, json, os, re, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path(os.environ.get('FV_APOLLO_R211_DIST', str(HERE / '../apollo-r211/dist'))).resolve()
OUT = HERE / 'dist'
PIN = 'ee5a10237cca0a57718b435425dfc0969562da957cc1cd6c50e32558423268b4'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'

def sha(data): return hashlib.sha256(data).hexdigest()
def require(test, message):
    if not test: raise ValueError(message)
def once(body, old, new):
    require(body.count(old) == 1, 'Drift in pinned parent: ' + old[:75])
    return body.replace(old, new, 1)

def build():
    require(sha((BASE / 'manifest.json').read_bytes()) == PIN, 'R211 manifest not pinned')
    parent = json.loads((BASE / 'manifest.json').read_text())
    require(parent['release'] == 'r211' and parent['approved_purchase_offer'] is False, 'Commerce/parent drift')
    require(parent['upstream_R198_reconciled'] is False and parent['media_commercial_rights_cleared'] is False, 'Unsafe release claim')
    for path, digest in parent['files'].items():
        require(sha((BASE / path).read_bytes()) == digest, 'R211 file drift: ' + path)
    html = (BASE / 'templates/atlas-fragment.html').read_text()
    cta = '<a class="cta" href="' + FREE + '">Read original investigation →</a>'
    require(html.count(cta) == 1, 'Missing single free editorial action')
    html = once(html, cta, '')
    html = once(html, '<h2>Continue into the full investigation.</h2>', '<h2>Where the records leave questions open.</h2>')
    html = once(html, '</footer>', '<p class="small"><a href="#fv-apollo-reading-bridge">Return to the free investigation link ↑</a></p></footer>')
    bridge = (
      '<aside class="fv-apollo-reading-bridge" id="fv-apollo-reading-bridge" aria-labelledby="fv-apollo-reading-bridge-title">'
      '<span class="eyebrow">Next step / original reporting</span>'
      '<h2 id="fv-apollo-reading-bridge-title">Continue from the record to the investigation.</h2>'
      '<p id="fv-apollo-reading-bridge-desc">You have the source boundaries and the Review Board report above. '
      'The original Apollo 1 investigation expands the story with its historical context. Free to read, no account needed.</p>'
      '<a class="cta" href="' + FREE + '" aria-describedby="fv-apollo-reading-bridge-desc">Read original investigation →</a>'
      '</aside>\n')
    html = once(html, '</section>\n<section aria-labelledby="fv-apollo-chronology-title"', '</section>\n' + bridge + '<section aria-labelledby="fv-apollo-chronology-title"')
    require(html.count('class="cta"') == 1 and html.count(FREE) == 1, 'Exactly one editorial action required')
    require(html.index('fv-apollo-trace-title') < html.index('id="fv-apollo-reading-bridge"') < html.index('id="fv-apollo-chronology"'), 'Bridge not after source proof')
    require(html.count('<details') == 12 and 'data-lat' not in html and 'data-lng' not in html, 'Evidence/geo drift')
    css = (BASE / 'assets/atlas-scoped.css').read_text() + '''
/* R212 proof-to-reading bridge: one action, after source proof, no JS or sticky overlay. */
.fv-apollo-atlas .fv-apollo-reading-bridge{margin:clamp(24px,4vw,54px) 0;padding:clamp(20px,3vw,42px);border:1px solid #b9a27f;background:#1b1a18;color:#f5f0e8;overflow-wrap:anywhere}
.fv-apollo-atlas .fv-apollo-reading-bridge h2{font-size:clamp(1.45rem,3vw,2.4rem);line-height:1.18;max-width:28ch;margin:.65em 0}
.fv-apollo-atlas .fv-apollo-reading-bridge p{max-width:68ch;line-height:1.65}
.fv-apollo-atlas .fv-apollo-reading-bridge .cta{display:inline-block;max-width:100%;white-space:normal;min-height:44px}
.fv-apollo-atlas .fv-apollo-reading-bridge :focus-visible{outline:3px solid #f6cf86;outline-offset:4px}
@media print{.fv-apollo-atlas .fv-apollo-reading-bridge{color:black!important;background:white!important;border-color:black!important;break-inside:avoid}}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-reading-bridge{border:2px solid CanvasText;background:Canvas;color:CanvasText}}
'''
    files = {'templates/atlas-fragment.html': html.encode(), 'assets/atlas-scoped.css':css.encode(),
             'assets/campaign-handoff.js': (BASE / 'assets/campaign-handoff.js').read_bytes()}
    php = (BASE / 'fv-ex2-apollo-r211.php').read_text().replace('r211', 'r212').replace('R211', 'R212')
    for name in ('templates/atlas-fragment.html','assets/atlas-scoped.css'):
        php = once(php, parent['files'][name], sha(files[name]))
    php = once(php, "'" + parent['files']['assets/atlas-scoped.css'][:12] + "'", "'" + sha(files['assets/atlas-scoped.css'])[:12] + "'")
    files['fv-ex2-apollo-r212.php'] = php.encode()
    files['wp-render-shim-r212.php'] = (BASE / 'wp-render-shim-r211.php').read_text().replace('r211','r212').replace('R211','R212').encode()
    for name in ('source-records.json','custody-ledger.json','commercial-offer-gate.json'):
        files[name] = (BASE / name).read_bytes()
    audit = json.loads((BASE / 'source-audit.json').read_text())
    audit.update({'source':'rendered_R212_html', 'R212_single_action_location':'after_NASA_technical_source_crosswalk',
      'R212_CTA_count':1, 'R212_paid_offer_approved':False,
      'R212_experiment':'Test qualified Apollo documentary-to-investigation click-through, only after asset ID and consent-safe existing measurement confirmed; never equate click with sale.',
      'R212_target_URL_live_status':'NOT_VERIFIED_BY_BROWSER', 'canonical_ancestry_from_R198':'NOT_RECONCILED'})
    files['source-audit.json'] = (json.dumps(audit,sort_keys=True,indent=2)+'\n').encode()
    validation = json.loads((BASE / 'conversion-validation.json').read_text())
    validation['R212_reading_bridge'] = {'pathway':'verified Grok Apollo asset → source crosswalk → ONE free investigation link → unapproved educator dossier hypothesis',
      'cta_click':'diagnostic_only_not_sale','qualified_sessions':'UNVERIFIED','confirmed_orders':'UNVERIFIED','net_revenue':'NOT_COMPUTABLE',
      'commercial_product_gate':'HOLD','attribution_owner':'Claude (site analytics); Grok/Praxxis (published asset IDs)'}
    files['conversion-validation.json'] = (json.dumps(validation,sort_keys=True,indent=2)+'\n').encode()
    manifest = {'release':'r212','parent_manifest_sha256':PIN,'files':{k:sha(v) for k,v in sorted(files.items())},
        'approved_purchase_offer':False,'media_commercial_rights_cleared':False,'upstream_R198_reconciled':False,
        'installed_WordPress_accepted':False,'axe_core_accepted':False,
        'release_gate':'STAGING HOLD / WP acceptance / genuine axe / canonical ancestry / CI / founder'}
    files['manifest.json'] = (json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    if OUT.exists(): shutil.rmtree(OUT)
    for name, data in sorted(files.items()):
        path = OUT / name; path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return manifest

if __name__ == '__main__':print(json.dumps(build(),sort_keys=True,indent=2))
