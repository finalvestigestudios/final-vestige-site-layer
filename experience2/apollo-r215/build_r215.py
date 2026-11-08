#!/usr/bin/env python3
"""Apollo R215: evidence-link custody and no-script deployment checkpoint (staging only)."""
import hashlib
import json
import os
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
BASE = Path(os.environ.get('FV_APOLLO_R214_DIST', HERE / '../r214/dist')).resolve()
OUT = HERE / 'dist'
PIN = 'f4fb5bcea55c222a25e46b173c4ce273d88c523ed6f0bb82178203f0786465b3'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RIGHTS = 'https://www.nasa.gov/nasa-brand-center/advertising-guidelines/'
ALLOWED = {'www.nasa.gov', 'finalvestige.com'}

def digest(b): return hashlib.sha256(b).hexdigest()
def dump(v): return (json.dumps(v, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()
def check(v, message):
    if not v: raise ValueError(message)

class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.links = []
        self.times = []
        self.ctas = []
        self.failures = []
        self.h1s = 0
    def handle_starttag(self, tag, attrs):
        names = [name.lower() for name,_ in attrs]
        if len(names)!=len(set(names)):
            self.failures.append('Duplicate HTML attribute in '+tag)
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        for key in ('aria-labelledby','aria-describedby'):
            if a.get(key): self.references.extend(a[key].split())
        if tag == 'h1': self.h1s += 1
        if tag == 'script': self.failures.append('Active script in evidence markup')
        if tag == 'img': self.failures.append('Unreviewed image inserted')
        if 'data-lat' in a or 'data-lng' in a: self.failures.append('Unreviewed map coordinates')
        if tag == 'time' and 'datetime' in a: self.times.append(a['datetime'])
        if tag == 'a':
            href=a.get('href','')
            if not href: self.failures.append('Empty link'); return
            if href.startswith('#'):
                self.references.append(href[1:])
            else:
                url=urlsplit(href)
                if url.scheme != 'https' or url.hostname not in ALLOWED or url.username or url.password:
                    self.failures.append('Unapproved link: '+href)
                self.links.append(href)
            if 'cta' in a.get('class','').split(): self.ctas.append(href)

def audit_html(blob):
    text=blob.decode('utf-8',errors='strict')
    a=Audit();a.feed(text);a.close()
    check(not a.failures, '; '.join(a.failures))
    check(len(a.ids)==len(set(a.ids)), 'Duplicate HTML IDs')
    check(all(ref in a.ids for ref in a.references), 'Unresolved anchor/ARIA ID reference')
    check(a.h1s==1 and a.ctas==[FREE], 'Misplaced or duplicated primary investigation action')
    rail = re.search(r'<ol class="rail">(.*?)</ol>', text, re.S)
    check(rail is not None, 'Missing chronology rail')
    rail_times = re.findall(r'<time datetime="([^"]+)">', rail.group(1))
    check(rail_times==['1966-10-18','1967-01-03','1967-01-27','1967-01-28'], 'Unsupported chronology rail dates')
    check(BOARD in a.links and RIGHTS in a.links, 'Missing primary source or NASA rights notice')
    check(all(x.startswith(('https://www.nasa.gov/', 'https://finalvestige.com/')) for x in a.links), 'Unreviewed outbound domain')
    check(text.count(FREE)==1, 'Unexpected duplicate sales/reading link')
    check('April 1967' in text and 'most probable' in text, 'Review Board reporting date/uncertainty lost')
    return {'links_total':len(a.links),'distinct_external':sorted(set(a.links)),
            'ids_total':len(a.ids),'aria_and_fragment_references_total':len(a.references),
            'chronology_dates':rail_times,'single_free_cta':FREE,'active_scripts':0,'images':0,'map_pins':0}

def build():
    raw=(BASE/'manifest.json').read_bytes()
    check(digest(raw)==PIN, 'R214 parent manifest changed')
    parent=json.loads(raw)
    check(parent.get('release')=='r214' and parent.get('campaign_enhancement_enabled') is False, 'Wrong parent/provenance state')
    for flag in ('approved_purchase_offer','media_commercial_rights_cleared','upstream_R198_reconciled','installed_WordPress_accepted','axe_core_accepted'):
        check(parent.get(flag) is False, 'False release claim in parent: '+flag)
    for name, expected in parent['files'].items():
        check(digest((BASE/name).read_bytes())==expected, 'R214 ancestor file changed: '+name)
    html=(BASE/'templates/atlas-fragment.html').read_bytes()
    custody=audit_html(html)
    css=(BASE/'assets/atlas-scoped.css').read_bytes()
    check(b'.fv-apollo-atlas' in css and b'prefers-reduced-motion' in css and b'forced-colors' in css, 'CSS scope/accessibility lost')
    src=(BASE/'fv-ex2-apollo-r214.php').read_text()
    # Remove even dormant optional JavaScript: it must not enter the staged package.
    oldfn=re.search(r'function fv_ex2_r214_optional_js_ok\(\) \{.*?\n\}\n',src,re.S)
    check(oldfn is not None and 'return false;' in oldfn.group(), 'Optional JS quarantine changed')
    src=src.replace(oldfn.group(),'/** No campaign script shipped in R215; creator attribution is unverified. */\n')
    oldenqueue=re.search(r'    if \(fv_ex2_r214_optional_js_ok\(\)\) \{.*?\n    \}\n',src,re.S)
    check(oldenqueue is not None and 'wp_enqueue_script' in oldenqueue.group(), 'Optional JS enqueue changed')
    src=src.replace(oldenqueue.group(),'')
    src=src.replace('r214','r215').replace('R214','R215')
    check(re.search(r'\bwp_enqueue_script\s*\(',src) is None and 'campaign-handoff' not in src and 'optional_js_ok' not in src,'JS still enabled')
    shim=(BASE/'wp-render-shim-r214.php').read_text().replace('r214','r215').replace('R214','R215')
    files={'templates/atlas-fragment.html':html,'assets/atlas-scoped.css':css,
           'fv-ex2-apollo-r215.php':src.encode(),'wp-render-shim-r215.php':shim.encode()}
    for name in ('source-records.json','custody-ledger.json','commercial-offer-gate.json','attribution-release-gate.json'):
        files[name]=(BASE/name).read_bytes()
    source=json.loads((BASE/'source-audit.json').read_text())
    source['R215_link_custody']={'authority':'NASA primary sources', 'link_allowlist':sorted(ALLOWED),
       'direct_nasa_record_links':len([link for link in custody['distinct_external'] if 'nasa.gov' in link]),
       'HTML_duplicate_attribute_guard':True, 'script_shipped':False,'NASA_commercial_endorsement':False,
       'media_commercial_rights_cleared':False}
    files['source-audit.json']=dump(source)
    conv=json.loads((BASE/'conversion-validation.json').read_text())
    conv['R215_no_script_custody']={'offer':'Apollo educator dossier, hypothetical and not sellable',
        'funnel':'Grok documented asset -> NASA evidence Atlas -> single free Apollo investigation CTA',
        'blocker':'Unverified creator assets and no commercial product authorization',
        'change':'Remove dormant UTM script from distributable entirely; validate all evidence links and references',
        'pass_fail':'Local source+PHP+Chromium QA required; no live/paid claim',
        'owner':'Apollo source QA; Grok/Praxxis attribution; Claude commerce; Founder release',
        'paid_orders':None,'qualified_sessions_7d':None,'qualified_sessions_30d':None,'realized_net':None}
    files['conversion-validation.json']=dump(conv)
    files['link-custody-receipt.json']=dump(custody)
    check('assets/campaign-handoff.js' not in files,'Creator script unexpectedly packaged')
    files['manifest.json']=dump({'release':'r215','parent_manifest_sha256':PIN,
      'files':{n:digest(b) for n,b in sorted(files.items())},
      'script_shipped':False,'creator_attribution_verified':False,
      'approved_purchase_offer':False,'media_commercial_rights_cleared':False,
      'upstream_R198_reconciled':False,'installed_WordPress_accepted':False,
      'axe_core_accepted':False,'commercial_release_allowed':False,
      'release_gate':'STAGING HOLD: canonical R198 mismatch, WP, axe, CI, QD, Founder approval'})
    if OUT.exists():shutil.rmtree(OUT)
    for name,body in sorted(files.items()):
        target=OUT/name; target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    return digest(files['manifest.json'])

if __name__=='__main__':
    print('R215 deterministic manifest SHA-256:',build())
