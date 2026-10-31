#!/usr/bin/env python3
"""Source-pinned, link-only Apollo photograph/claim concordance.

Build-time derived editorial surface: no speculative coordinates, no image bytes,
no network, no rights clearance. Produces an accessible no-JS document index
from the six existing NASA records. The original PR215 source stays unchanged.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

CASEFILE = Path(__file__).resolve().parents[3] / 'apollo-casefile'
GENERATED = Path(__file__).resolve().parents[2] / 'generated'

# The distinction is based on the reviewed NASA catalog witness, never the claim
# chronology or the gallery's visual appearance. A 2017 exhibit is NOT 1967 footage.
ERA = {
    '01': ('1967', 'Contemporary crew photograph'),
    '02': ('1967', 'Contemporary spacecraft-preparation photograph'),
    '03': ('1966', 'Earlier crew rehearsal photograph'),
    '04': ('2017', 'Retrospective tribute exhibit'),
    '05': ('1967', 'Post-fire damage photograph'),
    '06': ('2017', 'Retrospective hatch exhibit'),
}

# Only source dates established by NASA catalog witnesses. These are **source
# contexts**, not a reconstruction of an event or a geospatial relationship.
ERA_FILTERS = (('all', 'All six source records', 6),
               ('1966', '1966 rehearsal — 1', 1),
               ('1967', '1967 photographs — 3', 3),
               ('2017', '2017 commemorations — 2', 2))
CONTEXT_EXPORT = '{{FV_EX2_CONTEXT_EXPORT}}'

CSS = """/* Source-concordance is embedded only in authenticated Apollo staging review. */
.fv-ex2-concordance{background:#10110f;color:#f4efe6;border-block:1px solid #514738;padding:clamp(30px,5vw,72px) clamp(16px,5vw,72px);font-family:Inter,system-ui,sans-serif;line-height:1.6;}
.fv-ex2-concordance *{box-sizing:border-box;}
.fv-ex2-concordance__inner{max-width:1350px;margin-inline:auto}
.fv-ex2-concordance__eyebrow{color:#d5b980;font:700 .75rem/1.5 ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase}
.fv-ex2-concordance h2{font:normal clamp(1.75rem,3vw,3rem)/1.17 Georgia,serif;max-width:28ch;color:#f4efe6;margin:1rem 0;letter-spacing:-.02em}
.fv-ex2-concordance__intro{max-width:75ch;color:#d2cabc;font-size:1rem;margin-bottom:2rem}
.fv-ex2-concordance__cards{margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:14px;list-style:none}
.fv-ex2-concordance__card{padding:clamp(18px,2.5vw,28px);border:1px solid #78684d;background:#1e1d19;min-width:0;overflow-wrap:anywhere;}
.fv-ex2-concordance__type{font:700 .76rem/1.5 ui-monospace,monospace;color:#e4c791;letter-spacing:.03em}
.fv-ex2-concordance__card h3{font:normal clamp(1.2rem,2vw,1.6rem)/1.24 Georgia,serif;margin:.8rem 0;color:#fff9ef}
.fv-ex2-concordance__metadata{font-size:.94rem;color:#e5ddd0}
.fv-ex2-concordance__links{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:18px}
.fv-ex2-concordance a{color:#f2d69b;text-underline-offset:4px;min-height:44px;display:inline-flex;align-items:center}
.fv-ex2-concordance a:hover{text-decoration-thickness:2px}
.fv-ex2-concordance summary{cursor:pointer;color:#f2d69b;min-height:44px;display:list-item;padding:10px 5px;font-weight:650}
.fv-ex2-concordance details{margin-top:12px;border-top:1px solid #665944;}
.fv-ex2-concordance details p{margin:0 0 12px;color:#e7dfd2}

/* The temporal lens works without JS. Older browsers that lack :has() see
   ALL records and NO misleading filter controls (progressive fail-open). */
.fv-ex2-concordance__filters{display:none;min-width:0;border:1px solid #77654c;padding:14px;margin:0 0 20px;gap:10px 16px;flex-wrap:wrap}
.fv-ex2-concordance__filters legend{font-weight:700;color:#f4efe6;padding:0 6px}
.fv-ex2-concordance__filters label{display:inline-flex;gap:9px;align-items:center;min-height:44px;cursor:pointer;color:#f4efe6;border:1px solid #665944;padding:8px 12px;max-width:100%;overflow-wrap:anywhere}
.fv-ex2-concordance__filters input{margin:0;width:20px;height:20px;accent-color:#dbbb7e;flex:none}
.fv-ex2-concordance__filters label:has(input:checked){background:#4c3a23;outline:1px solid #d9bd85}
.fv-ex2-concordance__filters label:focus-within{outline:3px solid #ffe4aa;outline-offset:3px}
.fv-ex2-concordance__availability{font-size:.88rem;color:#d8d0c5;max-width:75ch;margin:0 0 18px}
.fv-ex2-concordance__export{display:inline-flex;margin:8px 0 24px}
@supports selector(:has(*)) {
  .fv-ex2-concordance__filters{display:flex}
  #source-concordance:has(#fv-ex2-lens-1966:checked) [data-concordance-era]:not([data-concordance-era="1966"]),
  #source-concordance:has(#fv-ex2-lens-1967:checked) [data-concordance-era]:not([data-concordance-era="1967"]),
  #source-concordance:has(#fv-ex2-lens-2017:checked) [data-concordance-era]:not([data-concordance-era="2017"]){display:none}
}
.fv-ex2-concordance :focus-visible{outline:3px solid #ffe4aa;outline-offset:4px}
@media(prefers-reduced-motion:reduce){.fv-ex2-concordance *, .fv-ex2-concordance *::before,.fv-ex2-concordance *::after{scroll-behavior:auto!important;transition:none!important}}
"""

class ConcordanceHold(ValueError):
    pass

def checked(condition: bool, message: str) -> None:
    if not condition:
        raise ConcordanceHold(message)


def build_context_index(casefile: Path = CASEFILE, generated: Path = GENERATED) -> str:
    """Return a deterministic, non-geolocated JSON research/custody index.

    This export is a *derived editorial index* of pinned NASA catalog records;
    it is not a newly sourced claim, rights clearance, or incident geolocation.
    """
    data = json.loads((casefile/'records.json').read_text(encoding='utf-8'))
    rows = data['records']
    fragment = (generated/'fragment.html').read_text(encoding='utf-8')
    checked(len(rows) == 6 and [r['id'] for r in rows] == list(ERA),
            'Context index requires the six original records')
    result = []
    for row in rows:
        rid = row['id']
        era, role = ERA[rid]
        url = urlsplit(row['image_url'])
        checked(era in row['source_date'], f'Context index date drift {rid}')
        checked(url.scheme=='https' and url.netloc=='www.nasa.gov' and
                url.path.startswith('/image-detail/') and not url.query and not url.fragment,
                f'Context index lost NASA catalog host {rid}')
        checked(row['rights'].startswith('link_only_'),f'Context export rights escalation {rid}')
        checked(f'id="stage-{rid}"' in fragment and f'id="source-{rid}"' in fragment,
                f'Context export broken claim/source custody {rid}')
        for key in ('title','source_id','source_date','image_credit','limit','image_url'):
            checked(isinstance(row.get(key),str) and row[key].strip(),
                    f'Context export missing {key} {rid}')
        result.append({
            'claim_id':rid, 'catalog_id':row['source_id'],
            'catalog_date':row['source_date'], 'source_era':era,
            'source_role':role, 'source_url':row['image_url'],
            'source_credit':row['image_credit'], 'title':row['title'],
            'cannot_establish':row['limit'], 'media_status':row['rights'],
            'chronology_anchor':f'#stage-{rid}', 'source_drawer_anchor':f'#source-{rid}',
            'geometry':'not_assigned',
        })
    checked({era:sum(r['source_era']==era for r in result) for era in ('1966','1967','2017')}
            == {'1966':1,'1967':3,'2017':2}, 'NASA temporal group counts drifted')
    obj={'schema':'fv-ex2-apollo-source-context-v1',
         'canonical_source_commit':'74375657f2cdaac0710f94c6de6c24534ee06858',
         'media_rights':'HOLD_PER_ITEM_REVIEW', 'not_a_rights_clearance':True,
         'not_an_incident_reconstruction':True, 'geographic_coordinates_assigned':0,
         'record_count':len(result), 'records':result}
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n'


def build_concordance(casefile: Path = CASEFILE, generated: Path = GENERATED) -> tuple[str,str,dict]:
    source_bytes = (casefile/'records.json').read_bytes()
    data = json.loads(source_bytes)
    source = data['records']
    fragment = (generated/'fragment.html').read_text(encoding='utf-8')
    checked(len(source)==6 and [r['id'] for r in source]==list(ERA), 'Expected precisely six canonical NASA records')
    cards=[]
    for row in source:
        rid=row['id']; date=row['source_date']; url=row['image_url']
        era, kind=ERA[rid]
        checked(era in date, f'Image date differs from catalog witness for {rid}')
        u=urlsplit(url)
        checked(u.scheme=='https' and u.netloc=='www.nasa.gov' and u.path.startswith('/image-detail/')
                and not u.query and not u.fragment, f'Non-NASA or ambiguous catalog URL at {rid}')
        checked(f'id="stage-{rid}"' in fragment and f'id="source-{rid}"' in fragment,
                f'Unresolved claim/source route {rid}')
        checked(fragment.count(url)>=4, f'NASA catalog citation missing from existing content {rid}')
        checked(row['rights'].startswith('link_only_'), f'Embedded media/rights escalation {rid}')
        for field in ('title','source_id','image_credit','limit','finding'):
            checked(isinstance(row.get(field),str) and row[field].strip(), f'Missing {field} at {rid}')
        e=lambda key:escape(row[key],quote=True)
        cards.append(f'''<li class="fv-ex2-concordance__card" data-concordance-record="{rid}" data-concordance-era="{era}">
<p class="fv-ex2-concordance__type">{rid} / {escape(kind)} / {escape(date)}</p>
<h3>{e('title')}</h3>
<p class="fv-ex2-concordance__metadata">NASA catalog: {e('source_id')}. Credit: {e('image_credit')}.</p>
<div class="fv-ex2-concordance__links"><a href="#stage-{rid}">Read the associated claim</a>
<a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect NASA catalog <span class="ex2-sr-only">(opens in a new tab)</span></a></div>
<details><summary>What this photograph cannot establish</summary><p>{e('limit')}</p></details>
</li>''')
    filters=''.join(
        '<label for="fv-ex2-lens-'+era+'"><input type="radio" id="fv-ex2-lens-'+era+'" '
        'name="fv-ex2-source-era" value="'+era+'"'+(' checked' if era=='all' else '')+'>'
        +escape(label)+'</label>'
        for era,label,count in ERA_FILTERS
    )
    html=f'''<section id="source-concordance" class="fv-ex2-concordance" aria-labelledby="fv-ex2-concordance-title">
<div class="fv-ex2-concordance__inner"><p class="fv-ex2-concordance__eyebrow">THE EVIDENCE / DOCUMENTARY SOURCE CONCORDANCE</p>
<h2 id="fv-ex2-concordance-title">The photograph has a date. The claim has a different burden of proof.</h2>
<p class="fv-ex2-concordance__intro">These six NASA catalog records help orient the investigation; they do not independently prove every accompanying historical claim. A 1966 rehearsal is not the 1967 fire, and two 2017 tribute exhibits are not accident footage. Open each record to see its limits. All images remain links to NASA, not reproduced here.</p>
<fieldset class="fv-ex2-concordance__filters"><legend>View records by source year</legend>{filters}</fieldset>
<p class="fv-ex2-concordance__availability">Choose a year to narrow the catalog records without changing the historical conclusions. Select “All six source records” to restore the complete index.</p>
<ol class="fv-ex2-concordance__cards">{''.join(cards)}</ol>
<a class="fv-ex2-concordance__export" href="{CONTEXT_EXPORT}" download="apollo-source-context.json">Download the six-record source context index (JSON)</a>
<p class="fv-ex2-concordance__intro">Media reproduction and promotional rights remain under item-level review; NASA does not endorse this independent investigation.</p>
</div></section>'''
    checked('<img' not in html and '<script' not in html and '<iframe' not in html,
            'Concordance must remain static and link-only')
    checked('latitude' not in html.lower() and 'longitude' not in html.lower(), 'No geospatial claims permitted')
    digest=lambda s: sha256(s.encode('utf-8')).hexdigest()
    context_json=build_context_index(casefile,generated)
    receipt={'status':'PASS_SOURCE_PINN_LINK_ONLY', 'record_count':len(source),
             'source_records_sha256':sha256(source_bytes).hexdigest(),
             'concordance_html_sha256':digest(html),'concordance_css_sha256':digest(CSS),
             'context_index_sha256':digest(context_json),'context_index_records':6,
             'filter_counts':{'all':6,'1966':1,'1967':3,'2017':2}, 'css_only_era_filter':True,
             'links_to_original_nasa':len(source),'links_to_existing_chronology':len(source),
             'photos_embedded':0,'geographic_pins':0,'no_js_native_details':True,
             'rights':'HOLD_PER_ITEM_REVIEW'}
    return html,CSS,receipt
