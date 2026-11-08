#!/usr/bin/env python3
"""R224 staging-only ChronologyRail. No production or WordPress writes."""
import argparse, hashlib, json, shutil
from pathlib import Path

PARENT = {
    'manifest.json': '60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e',
    'templates/atlas-fragment.html': '704178e8e56c1608b65492467f56ed538e4cc18652f7f847114be40c7a7c08b0',
    'assets/atlas-scoped.css': '9df7ae4c1c19de7a85ea57c5d245355d9a68fc638e9ce90fd838373de54e1a23'
}
NASA = 'https://www.nasa.gov/apollo-1-resources/'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
APRIL = ('<li data-evidence-kind="retrospective-report">'
    '<time datetime="1967-04">April 1967</time>'
    '<span class="fv-apollo-rail-kind">Review Board report · completed after the accident</span>'
    '<a href="#fv-apollo-source-drawer">Examine the Board findings and their limits</a>'
    '<small id="fv-apollo-rail-note-report">NASA dates completion of the investigation report to '
    'April 1967, not to the January accident. It does not establish an exact completion day.</small>'
    '<a href="' + NASA + '" data-source-id="Apollo 204 Review Board" '
    'aria-describedby="fv-apollo-rail-note-report" rel="noopener noreferrer">'
    'Verify the report completion month at NASA</a></li>')
LEGEND = ('<aside class="fv-apollo-period-key" aria-labelledby="fv-apollo-period-title">'
    '<h3 id="fv-apollo-period-title">Read the date and the record type</h3>'
    '<p>A photograph date is not a fire timestamp; the completed report came later.</p>'
    '<dl><div><dt>Capture date</dt><dd>When NASA dated a photograph.</dd></div>'
    '<div><dt>Event date</dt><dd>January 27, 1967; the accident the Board investigated.</dd></div>'
    '<div><dt>Report date</dt><dd>April 1967; when NASA says the review was completed.</dd></div>'
    '</dl></aside>')
CSS = """
.fv-apollo-atlas .fv-apollo-period-key{border:1px solid #a78d61;padding:clamp(12px,2vw,22px);margin:1.2rem 0;background:#1b1b18}
.fv-apollo-atlas .fv-apollo-period-key dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:.75rem}
.fv-apollo-atlas .fv-apollo-period-key dt{color:#ebcf9c;font-weight:700}
.fv-apollo-atlas .fv-apollo-period-key dd{margin:0}
.fv-apollo-atlas .rail li[data-evidence-kind="retrospective-report"]{border-left:3px solid #c5a974;padding-left:1rem}
.fv-apollo-atlas .rail li[data-evidence-kind="retrospective-report"] a{display:inline-block;min-height:44px}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-period-key{background:Canvas;border-color:CanvasText}.fv-apollo-atlas .fv-apollo-period-key dt{color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-period-key{background:transparent;border-color:#000}.fv-apollo-atlas .fv-apollo-period-key dt{color:#000}}
"""

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check(condition, reason):
    if not condition: raise ValueError(reason)

def build(parent, output):
    for name, expected in PARENT.items():
        check(sha(parent/name)==expected, 'Parent drift: '+name)
    if output.exists(): shutil.rmtree(output)
    shutil.copytree(parent, output)
    html_path=output/'templates/atlas-fragment.html'
    html=html_path.read_text()
    a='<ol class="rail">'
    start=html.index(a)
    end=html.index('</ol>', start)
    check(html[start:end].count('<li data-evidence-kind=')==4, 'Unexpected parent rail')
    check(html.count('class="cta"')==1 and FREE in html, 'Canonical reading CTA altered')
    check(NASA not in html[start:end], 'Duplicate report source already in rail')
    html=html[:end]+APRIL+html[end:]
    check(html.count('Four dates. Distinct kinds of evidence.')==1,'Title drift')
    html=html.replace('Four dates. Distinct kinds of evidence.','Five milestones. Distinct record types.')
    html=html.replace(a, LEGEND+a,1)
    html_path.write_text(html)
    css=output/'assets/atlas-scoped.css'
    css.write_text(css.read_text()+CSS)
    ledger=output/'chronology-period-custody.json'
    ledger.write_text(json.dumps({
        'schema':'fv-apollo-r224-period-precision-v1',
        'report_completion_month':'1967-04',
        'report_source':NASA,
        'event_date':'1967-01-27',
        'distinction':'capture_date != accident_event_date != review_completion_month',
        'rights_clearance':'NOT_CERTIFIED',
        'approved_paid_offer':False,
        'published_creator_asset_id':None,
        'geographic_coordinates':None
    },sort_keys=True,indent=2)+'\n')
    php=output/'fv-ex2-apollo-r223.php'
    code=php.read_text().replace('r223','r224').replace('R223','R224')
    for name in ('templates/atlas-fragment.html','assets/atlas-scoped.css'):
        check(PARENT[name] in code,'Expected parent PHP pin absent')
        code=code.replace(PARENT[name],sha(output/name))
    key="        && hash_file('sha256',$html)"
    check(code.count(key)==1,'PHP custody gate location changed')
    code=code.replace(key, "        && is_readable($root.'chronology-period-custody.json')"
        " && hash_file('sha256',$root.'chronology-period-custody.json')==='"
        +sha(ledger)+"'\n"+key)
    (output/'fv-ex2-apollo-r224.php').write_text(code)
    php.unlink()
    shim=output/'wp-render-shim-r223.php'
    (output/'wp-render-shim-r224.php').write_text(shim.read_text().replace('r223','r224').replace('R223','R224'))
    shim.unlink()
    files={p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    manifest={'release':'R224','status':'STAGING_HOLD','parent_manifest_sha256':PARENT['manifest.json'],
       'files':files,'not_live':True,'axe_core':'NOT_EXECUTED','wordpress':'NOT_TESTED','founder':'NOT_APPROVED'}
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return sha(output/'manifest.json')
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--parent',required=True,type=Path)
    a.add_argument('--target',required=True,type=Path)
    args=a.parse_args()
    print(build(args.parent,args.target))
