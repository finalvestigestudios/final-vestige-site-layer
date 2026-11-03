#!/usr/bin/env python3
"""R87 source-custody-first photograph-date rail. Staging reviewer; never publish as-is."""
from __future__ import annotations
import hashlib
import html
import importlib.util
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R86 = HERE / 'build_concordance_r86.py'
CROSSWALK = ROOT / 'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json'
CSS = HERE / 'chronology_r87.css'
BASE_SOURCES = (
    'experience2/evidence-atlas/tools/build_chronology_r87.py',
    'experience2/evidence-atlas/tools/chronology_r87.css',
    'experience2/evidence-atlas/tools/build_concordance_r86.py',
    'experience2/evidence-atlas/tools/build_rights_board_r85.py',
    'experience2/evidence-atlas/build_atlas.py',
    'experience2/evidence-atlas/atlas.css',
    'experience2/evidence-atlas/atlas.js',
    'experience2/research-desk/templates/ledger.html',
    'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
    'experience2/evidence-atlas/sources/R79_NASA_PAGE_AUDIT.json',
    'experience2/evidence-atlas/sources/NASA_PAGE_RIGHTS_AUDIT_R55.json',
    'experience2/evidence-atlas/tests/test_chronology_r87.py',
    'experience2/evidence-atlas/tests/browser_chronology_r87.py',
    'experience2/evidence-atlas/R87_PHOTOGRAPH_DATE_RAIL_STAGING_HOLD.md',
    '.github/workflows/ex2-apollo-r87-photo-date-rail.yml',
)

def hold(code):
    raise ValueError('R87_CUSTODY_HOLD:' + code)

def sha256(blob):
    return hashlib.sha256(blob).hexdigest()

def canon(record, custody):
    """Never turn a month-only record into an invented day or a fire milestone."""
    stamp = custody.get('date')
    precision = record.get('precision')
    if custody.get('media_rights') != 'INDIVIDUAL_REVIEW_REQUIRED':
        hold('RIGHTS_MUST_REMAIN_PENDING')
    if record.get('identity') not in ('PIA_ON_OFFICIAL_PAGE', 'PROVISIONAL_NO_PAGE_PIA'):
        hold('IDENTITY_STATUS')
    if not re.fullmatch(r'https://www\.nasa\.gov/image-detail/[a-z0-9_\-/]+/', record.get('url', '')):
        hold('UNVERIFIED_EXTERNAL_DESTINATION')
    if precision == 'DAY' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', stamp or ''):
        try:
            parsed = date.fromisoformat(stamp)
        except ValueError:
            hold('INVALID_DAY')
        if record['id'] == '01':
            hold('CREW_DAY_INVENTED')
        return parsed.isoformat(), 'DAY'
    if precision == 'MONTH_ONLY' and re.fullmatch(r'\d{4}-\d{2}', stamp or ''):
        if record['id'] != '01' or record['identity'] != 'PROVISIONAL_NO_PAGE_PIA':
            hold('MONTH_UNCERTAINTY_MISMATCH')
        if not re.search(r'unknown|unconfirmed|exact day', record['date'], re.I):
            hold('UNCERTAINTY_DISCLOSURE_MISSING')
        return None, 'MONTH_ONLY'
    hold('DATE_PRECISION_MISMATCH')

def verified_groups(report, crosswalk):
    records = report.get('records', [])
    source_rows = crosswalk.get('records', [])
    if len(records) != 6 or len(source_rows) != 6:
        hold('SIX_RECORDS_REQUIRED')
    source_by_id = {row['id']: row for row in source_rows}
    if len(source_by_id) != 6 or set(source_by_id) != {f'{n:02}' for n in range(1, 7)}:
        hold('SOURCE_SET_INVALID')
    seen = set()
    groups = defaultdict(list)
    uncertain = []
    for record in records:
        rid = record.get('id')
        if rid not in source_by_id or rid in seen:
            hold('DUPLICATE_OR_UNKNOWN_RECORD')
        seen.add(rid)
        custody = source_by_id[rid]
        if record['catalog'] != custody['catalog'] or record['url'] != custody['photo_url']:
            hold('SOURCE_IDENTITY_DRIFT')
        if record['component_date_label'] != custody['date_label']:
            hold('SOURCE_DATE_LABEL_DRIFT')
        date_key, precision = canon(record, custody)
        item = {**record, 'date_key': date_key, 'rail_precision': precision}
        (groups[date_key] if date_key else uncertain).append(item)
    if seen != set(source_by_id) or len(uncertain) != 1:
        hold('UNCERTAINTY_CARDINALITY')
    chronology = [(key, sorted(group, key=lambda r: r['id'])) for key, group in sorted(groups.items())]
    if len(chronology) != 4 or tuple(len(g) for _, g in chronology) != (1, 1, 1, 2):
        hold('PHOTO_MILESTONE_SHAPE_DRIFT')
    if chronology[-1][0] != '2017-01-24' or {r['id'] for r in chronology[-1][1]} != {'04', '06'}:
        hold('TRIBUTE_DATE_COLLISION')
    return chronology, uncertain

def e(text):
    return html.escape(str(text), quote=True)

def plate(record):
    rid = e(record['id'])
    original = e(record['url'])
    identity = 'Provisional catalog association; no structured PIA on linked NASA page' if record['id'] == '01' else 'Catalog PIA displayed on linked NASA page'
    return f'''<article class="plate" id="r87-record-{rid}" aria-labelledby="r87-title-{rid}">
<span class="plate-number">PHOTO {rid} / 06 · SOURCE LINK ONLY</span>
<h4 id="r87-title-{rid}">{e(record['title'])}</h4>
<p class="dateline"><strong>Photograph date:</strong> {e(record['date'])} · <strong>Catalog:</strong> {e(record['catalog'])}</p>
<p>{e(record['scope'])}</p>
<p class="limit"><strong>Evidence cannot establish:</strong> {e(record['limitation'])}</p>
<details><summary>Source drawer · identity, custody and reuse</summary><dl>
<dt>NASA source identity</dt><dd>{e(identity)}</dd>
<dt>Evidence context</dt><dd>{e(record['role'])}</dd>
<dt>Photograph credit stated on page</dt><dd>{e(record['credit'])}</dd>
<dt>Component verification</dt><dd>Actual Research Desk and generated Evidence Atlas: matching catalog and NASA URL, verified by R86 cross-component custody.</dd>
<dt>Media permissions</dt><dd><strong>INDIVIDUAL REVIEW REQUIRED</strong>. No downloaded or reproduced image. NASA credit is not image reuse clearance.</dd>
<dt>External primary reference</dt><dd class="full-url">{original}</dd>
</dl></details>
<a class="source" target="_blank" rel="noopener noreferrer" href="{original}">Inspect NASA source for photo {rid} ↗</a></article>'''

def render(chronology, uncertain):
    chapters = []
    jump = []
    for index, (day, records) in enumerate(chronology, 1):
        mark = f'r87-day-{index}'
        label = records[0]['date']
        multiple = len(records) > 1
        shared = '<p class="same-day"><strong>Same date, no verified sequence:</strong> these two 2017 tribute photographs are grouped together. Their order is not chronological evidence.</p>' if multiple else ''
        jump.append(f'<a href="#{mark}">{e(label)} · {len(records)} photo{"s" if multiple else ""}</a>')
        chapters.append(f'''<section class="milestone" id="{mark}" aria-labelledby="r87-date-{index}">
<div class="milestone-heading"><span class="mark">{index:02}</span><div><p class="eyebrow">VERIFIED PHOTOGRAPH DATE · {len(records)} SOURCE{"S" if multiple else ""}</p>
<h3 id="r87-date-{index}"><time datetime="{e(day)}">{e(label)}</time></h3></div></div>
{shared}<div class="plates">{''.join(plate(r) for r in records)}</div></section>''')
    jump.append('<a href="#r87-unplaced">January 1967 · exact day unknown</a>')
    unplaced_cards = ''.join(plate(r) for r in uncertain)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Apollo 1 · Photograph Date Rail · Final Vestige Staging</title>
<link rel="stylesheet" href="chronology_r87.css"></head><body>
<a class="skip" href="#r87-content">Skip to photograph dates</a>
<div class="page"><header class="hero"><p class="brand">FINAL VESTIGE STUDIOS · APOLLO EVIDENCE STUDIO · PRIVATE STAGING</p>
<p class="eyebrow">CHRONOLOGY RAIL / VERIFIED NASA SOURCE METADATA</p>
<h1>What the dates <em>actually tell us.</em></h1>
<p class="intro">Six NASA photographic references, one transparent distinction: <strong>the date a photograph was taken is not the chronology of the Apollo 1 fire.</strong> Browse only date-verified source milestones. A month-only crew portrait stays outside the dated sequence.</p>
<p class="hold" role="note"><strong>STAGING HOLD · 0/6 media reuse cleared.</strong> No NASA photos reproduced. The crew portrait's S67-19766 association is provisional. These links and dates do not establish ignition, pressure, egress, or causal conclusions.</p>
<div class="summary"><span>4 dated milestones</span><span>5 day-specific photographs</span><span>1 unplaced month-only portrait</span><span>0 inferred map relationships</span></div></header>
<main id="r87-content"><nav class="rail-nav" aria-label="Photograph-date chapters"><h2>Jump to a verified photograph date</h2><p>Photograph dates only — not an accident-event timeline.</p><div class="rail-jumps">{''.join(jump)}</div></nav>
<div class="rail" aria-label="Verified photograph dates">{''.join(chapters)}</div>
<section class="uncertain" id="r87-unplaced" aria-labelledby="r87-unknown"><div class="milestone-heading"><span class="mark">?</span><div><p class="eyebrow">UNPLACED / NOT AN ORDERED DAY</p><h3 id="r87-unknown">January 1967 · exact day unconfirmed</h3></div></div>
<p>The crew portrait is dated only to a month. It cannot be positioned between January 3 and January 28, or assigned to the January 27 fire.</p><div class="plates">{unplaced_cards}</div></section>
</main><footer><p><strong>Source custody is not media permission.</strong> R37, R79 and R55 registers crosschecked against rendered Research Desk and Evidence Atlas. All photograph-specific image-use assessments remain pending.</p>
<p>Official policy reference: <a href="https://www.nasa.gov/nasa-brand-center/">NASA Brand Center</a>. No photo binaries, third-party scripts, geographic pins or unsupported relationships are included.</p><p class="signoff">NOT A PUBLICATION CANDIDATE · INDEPENDENT REVIEW + FOUNDER APPROVAL REQUIRED</p></footer></div></body></html>'''

def build(out):
    spec = importlib.util.spec_from_file_location('r86_actual_components_r87', R86)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    report = module.verify()  # actual Desk + Atlas + immutable NASA registers, fail closed
    crosswalk = json.loads(CROSSWALK.read_text('utf-8'))
    chronology, uncertain = verified_groups(report, crosswalk)
    page = render(chronology, uncertain).encode('utf-8')
    stylesheet = CSS.read_bytes()
    out.mkdir(parents=True, exist_ok=True)
    (out/'R87_PHOTOGRAPH_DATE_RAIL.html').write_bytes(page)
    (out/'chronology_r87.css').write_bytes(stylesheet)
    receipt = {'schema':'fv.apollo.r87.photograph-date-rail.v1','release':'STAGING_HOLD',
        'approved_for_publication':False,'hosted_wordpress_tested':False,'media_reuse_cleared':0,
        'photographs_embedded':0,'inferred_geo_edges':0,
        'verified_photograph_days':[{'day':key,'catalogs':[r['catalog'] for r in records]} for key,records in chronology],
        'unplaced_month_only':[r['catalog'] for r in uncertain],
        'source_hashes':{**report['sha256'],'r37':sha256(CROSSWALK.read_bytes())},
        'html_sha256':sha256(page),'css_sha256':sha256(stylesheet)}
    (out/'R87_RAIL_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return receipt

def package(out, zip_path):
    contents = {}
    for relative in BASE_SOURCES:
        contents['source/'+relative] = (ROOT/relative).read_bytes()
    for name in ('R87_PHOTOGRAPH_DATE_RAIL.html','chronology_r87.css','R87_RAIL_RECEIPT.json'):
        contents['built/'+name] = (out/name).read_bytes()
    contents['SHA256_MANIFEST.json']=(json.dumps({'schema':'fv.apollo.r87.deterministic-review.v1',
        'release':'STAGING_HOLD','not_deployable':True,
        'files':{key:sha256(blob) for key,blob in sorted(contents.items())}},sort_keys=True,indent=2)+'\n').encode()
    zip_path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(zip_path,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for key,blob in sorted(contents.items()):
            info=ZipInfo(key,date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            info.create_system=3
            archive.writestr(info,blob)
    return sha256(zip_path.read_bytes())

if __name__=='__main__':
    try:
        dest = Path(sys.argv[1]) if len(sys.argv)>1 else Path('dist/r87')
        build(dest)
        if len(sys.argv)>2: print('R87 deterministic artifact sha256',package(dest,Path(sys.argv[2])))
        print('R87: verified photograph dates grouped, month-only separated. STAGING_HOLD')
    except Exception:
        print('R87_CUSTODY_HOLD: failed independent source review',file=sys.stderr)
        sys.exit(1)
