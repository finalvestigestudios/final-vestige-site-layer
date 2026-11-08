#!/usr/bin/env python3
"""R214: quarantine unverified creator campaign propagation; Apollo-only, fail open.

No analytics provider, new consent collection, paid destination or product is enabled.
The only outbound CTA remains the unchanged free source-linked investigation.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path(os.environ.get('FV_APOLLO_R213_DIST', HERE / '../r213/dist')).resolve()
OUT = HERE / 'dist'
PIN = 'd7495c05522628e9483c161a8ac32020f1325f97b6437fd9e870c8036032fd4a'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RIGHTS = 'https://www.nasa.gov/nasa-brand-center/advertising-guidelines/'

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(v): return (json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
def require(ok, why):
    if not ok: raise ValueError(why)
def one(s, old, new):
    require(s.count(old) == 1, 'Ancestor pattern changed or ambiguous: ' + old[:65]); return s.replace(old, new, 1)

def build():
    raw = (BASE / 'manifest.json').read_bytes()
    require(sha(raw) == PIN, 'R213 ancestor manifest mismatch')
    parent = json.loads(raw)
    require(parent['release'] == 'r213', 'Wrong ancestor')
    for name, digest in parent['files'].items():
        require(sha((BASE / name).read_bytes()) == digest, 'R213 corrupted ancestor: ' + name)
    for flag in ('approved_purchase_offer', 'media_commercial_rights_cleared',
                 'upstream_R198_reconciled', 'installed_WordPress_accepted', 'axe_core_accepted'):
        require(parent[flag] is False, 'Invalid R213 release claim: '+flag)
    html = (BASE/'templates/atlas-fragment.html').read_bytes()
    require(html.count(b'class="cta"') == 1 and html.count(FREE.encode()) == 1, 'Multiple / wrong free CTA')
    require(NASA.encode() in html and RIGHTS.encode() in html, 'Lost NASA or rights documentation')
    require(b'data-lat=' not in html and b'data-lng=' not in html, 'Unverified geo')
    css = (BASE/'assets/atlas-scoped.css').read_bytes()
    script = (BASE/'assets/campaign-handoff.js').read_bytes()
    require(b'organic_social' in script and b'getAll' in script, 'Unknown R213 optional JS')

    # A syntactically plausible utm_content is NOT verified creator provenance. The
    # previously optional enqueuing is disabled: no URL mutation until Grok/Praxxis
    # provide real immutable published IDs, destination links and founder approval.
    php = (BASE/'fv-ex2-apollo-r213.php').read_text()
    php = php.replace('r213','r214').replace('R213','R214')
    php = one(php, "function fv_ex2_r214_optional_js_ok() {", "function fv_ex2_r214_optional_js_ok() {\n    // PROVENANCE HOLD: no creator asset_id verified; never append spoofable UTMs.\n    return false;")
    require('return false;' in php and 'wp_enqueue_script' in php, 'Quarantine not present')
    shim = (BASE/'wp-render-shim-r213.php').read_text().replace('r213','r214').replace('R213','R214')
    files = {'templates/atlas-fragment.html':html, 'assets/atlas-scoped.css':css,
             'assets/campaign-handoff.js':script, 'fv-ex2-apollo-r214.php':php.encode(),
             'wp-render-shim-r214.php':shim.encode()}
    for key in ('source-records.json','custody-ledger.json','commercial-offer-gate.json'):
        files[key] = (BASE/key).read_bytes()
    source = json.loads((BASE/'source-audit.json').read_text())
    source['R214_attribution_hold'] = {'Grok_published_asset_id':None, 'source': 'TASK-008 unverified',
        'javascript_enqueued':False, 'NASA_technical_source':NASA, 'commercial_rights':RIGHTS,
        'merchant_paid_order':None, 'source_qualified_sessions':None}
    files['source-audit.json'] = dump(source)
    conv = json.loads((BASE/'conversion-validation.json').read_text())
    conv['R214_provenance_experiment'] = {
        'offer': 'Apollo educator dossier hypothesis — not a verified sellable product',
        'funnel': 'Grok Apollo long-form -> evidence Atlas -> one free article link -> future dossier only after approval',
        'blocker': 'R213 accepts syntactically plausible but unverified creator IDs for UTM passthrough',
        'change': 'quarantine script until per-asset published provenance and governed release are verified',
        'evidence': 'PHP enqueue negative gate + Playwright link invariance + build digests (LOCAL ONLY)',
        'owner': 'Apollo staging; Grok asset inventory; Praxxis independent QA; Claude production attribution',
        'verified_orders':None, '7_day_qualified_human_sessions':None,
        '30_day_qualified_human_sessions':None, 'realized_net_revenue':None,
        'net_revenue_per_1000_qualified_sessions':None}
    files['conversion-validation.json'] = dump(conv)
    files['attribution-release-gate.json'] = dump({
        'state':'DENY', 'reason':'No source-verifiable published Apollo asset_id / permitted URL inventory',
        'script_enqueued':False, 'direct_link_preserved':FREE,
        'required_before_approval':['Grok immutable asset_id, platform and published URL',
        'Praxxis independent rights/campaign review', 'Claude source-attribution acceptance in installed staging',
        'founder production approval'], 'non_goals':['tracking pixel','paid CTA','visitor fingerprinting'],
        'sales_and_revenue':None, 'cohort_7d':None, 'cohort_30d':None})
    # The HTML/CSS, JS bytes remain unchanged so there is no new browser script.
    require(sha(files['templates/atlas-fragment.html'])==parent['files']['templates/atlas-fragment.html'], 'HTML drift')
    require(sha(files['assets/atlas-scoped.css'])==parent['files']['assets/atlas-scoped.css'], 'CSS drift')
    require(sha(files['assets/campaign-handoff.js'])==parent['files']['assets/campaign-handoff.js'], 'JS drift')
    require(all(sha(files[name])==parent['files'][name] for name in ('source-records.json','custody-ledger.json','commercial-offer-gate.json')), 'Source/media/offer drift')
    files['manifest.json'] = dump({'release':'r214','parent_manifest_sha256':PIN,
        'files':{name:sha(blob) for name,blob in sorted(files.items())},
        'campaign_enhancement_enabled':False, 'approved_purchase_offer':False,
        'media_commercial_rights_cleared':False, 'upstream_R198_reconciled':False,
        'installed_WordPress_accepted':False, 'axe_core_accepted':False,
        'release_gate':'STAGING HOLD: canonical ancestry; WP; genuine axe; CI; independent QA; founder'})
    if OUT.exists():shutil.rmtree(OUT)
    for name,blob in sorted(files.items()):
        path=OUT/name; path.parent.mkdir(exist_ok=True,parents=True); path.write_bytes(blob)
    return sha(files['manifest.json'])

if __name__ == '__main__':
    print('R214 deterministic manifest sha256:',build())
