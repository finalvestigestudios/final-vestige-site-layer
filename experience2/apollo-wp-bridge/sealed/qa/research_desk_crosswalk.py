#!/usr/bin/env python3
"""Read-only PR158 Research Desk witness reconciled to pinned Apollo PR215.

Same NASA URL is NOT proof of matching catalog identifier, editorial finding,
photo rights, or merge eligibility. R18 does not read or modify PR158's branch.
"""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

WITNESS = Path(__file__).with_name('pr158_research_desk_witness.json')
EXACT_COMMIT = '250d7f05a4de037e73826dcf0cfaef0ec4c29383'
EXACT_BLOB = '403d128c57b9bc82dac7c619651689070edef86c'
EXACT_REPO = 'finalvestigestudios/final-vestige-site-layer'
LEDGER_PATH = 'experience2/research-desk/templates/ledger.html'

class CrosswalkHold(ValueError):
    pass

def verify_witness(records: list[dict], witness: Path = WITNESS) -> list[dict]:
    """Fail closed on source URL drift; preserve rather than paper over ID differences."""
    doc = json.loads(witness.read_text(encoding='utf-8'))
    required = {'repository':EXACT_REPO,'reviewed_commit':EXACT_COMMIT,
                'ledger_path':LEDGER_PATH,'ledger_git_blob_sha1':EXACT_BLOB,
                'pull_request':158,'ledger_not_merged_or_integrated':True,
                'witness_type':'READ_ONLY_PR158_LEDGER_SNAPSHOT_METADATA'}
    if any(doc.get(k) != v for k,v in required.items()):
        raise CrosswalkHold('Research Desk PR158 source identity drifted')
    rows = doc.get('rows')
    if not isinstance(rows,list) or len(rows)!=6 or len(records)!=6:
        raise CrosswalkHold('Expected precisely six independent source records')
    if [r.get('casefile_id') for r in rows] != [f'{i:02}' for i in range(1,7)]:
        raise CrosswalkHold('Research Desk record ordinals changed')
    by_id = {r['id']:r for r in records}
    if len(by_id)!=6 or set(by_id) != {f'{i:02}' for i in range(1,7)}:
        raise CrosswalkHold('Canonical source-record IDs changed')
    reconciled = []
    for row in rows:
        rid = row['casefile_id']
        canonical = by_id[rid]
        u = urlsplit(row['source_url'])
        if (u.scheme!='https' or u.netloc!='www.nasa.gov' or
            not u.path.startswith('/image-detail/') or u.query or u.fragment or
            canonical['image_url'] != row['source_url']):
            raise CrosswalkHold(f'Research Desk NASA source URL differs from canonical record {rid}')
        if row.get('ledger_record_id')!=f'fv-ex2-ledger-apollo1-record-{rid}':
            raise CrosswalkHold(f'Research Desk DOM accession changed at {rid}')
        if (not isinstance(row.get('ledger_title'),str) or not row['ledger_title'].strip()
            or not isinstance(row.get('ledger_catalog_label'),str) or
            not row['ledger_catalog_label'].startswith('NASA ')):
            raise CrosswalkHold(f'Invalid Research Desk label at {rid}')
        if not canonical['rights'].startswith('link_only_'):
            raise CrosswalkHold(f'Unsafe rights promotion at {rid}')
        canonical_id=canonical['source_id'].strip()
        comparable_id=canonical_id.removeprefix('NASA ').strip()
        rd_id=row['ledger_catalog_label'][5:].strip()
        id_match=comparable_id.casefold()==rd_id.casefold()
        reconciled.append({
            'claim_id':rid,'canonical_catalog_label':canonical_id,
            'research_desk_catalog_label':row['ledger_catalog_label'],
            'research_desk_heading':row['ledger_title'],
            'nasa_catalog_url':row['source_url'],
            'research_desk_ledger_record_id':row['ledger_record_id'],
            'research_desk_pr158_source_blob':EXACT_BLOB,
            'same_nasa_catalog_url':True,
            'catalog_identifier_label_match':id_match,
            'catalog_identifier_review': 'LABEL_MATCH_ONLY_NOT_INDEPENDENTLY_VERIFIED' if id_match
                                         else 'HOLD_IDENTIFIERS_DIFFER_REVIEW_ORIGINAL_NASA_RECORD',
            'editorial_findings_equivalence':'NOT_ASSERTED',
            'media_reuse_rights':'NOT_CLEARED',
            'recorded_geolocation':'NONE',
        })
    if sum(not r['catalog_identifier_label_match'] for r in reconciled)!=1 or reconciled[0]['catalog_identifier_label_match']:
        raise CrosswalkHold('Expected exactly one unresolved identifier-label mismatch; editorial review required')
    return reconciled


def build_crosswalk(records: list[dict], witness: Path = WITNESS) -> tuple[str,dict]:
    rows=verify_witness(records, witness)
    source_url=f'https://github.com/{EXACT_REPO}/blob/{EXACT_COMMIT}/{LEDGER_PATH}'
    cards=[]
    for row in rows:
        rid=row['claim_id']
        match=row['catalog_identifier_label_match']
        status=('Catalog labels match textually; this is not independent NASA verification.' if match
                else 'CATALOG IDENTIFIER REVIEW NEEDED — Research Desk and Apollo casefile use different labels for the same linked NASA page. Do not silently substitute either identifier.')
        cards.append(f'''<li class="fv-ex2-crosswalk__item" data-crosswalk-id="{rid}" data-crosswalk-review="{'label-match' if match else 'hold'}">
<div class="fv-ex2-crosswalk__accession">{rid} / 06 · Shared NASA source URL</div>
<strong>{escape(row['research_desk_heading'])}</strong>
<p>Research Desk label: <code>{escape(row['research_desk_catalog_label'])}</code><br>
Apollo casefile label: <code>{escape(row['canonical_catalog_label'])}</code></p>
<p class="fv-ex2-crosswalk__status">{escape(status)}</p>
<div class="fv-ex2-crosswalk__links"><a href="{escape(row['nasa_catalog_url'], quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect NASA catalog (new tab)</a>
<a href="#source-{rid}">Apollo source notes {rid}</a></div></li>''')
    html=f'''<details class="fv-ex2-crosswalk" id="fv-ex2-research-desk-crosswalk">
<summary>Research Desk source custody comparison — six matched NASA links, one identifier-label review hold</summary>
<div class="fv-ex2-crosswalk__body">
<p>Independent Research Desk draft PR #158 and this Apollo casefile refer to the same six NASA catalog <em>URLs</em>. Matching a URL does not establish identical photo identifiers, historical claims, archive permissions or deployment readiness. The six URL-and-label references are a pinned read-only comparison; no PR #158 plugin code, photos, or historical assertions were imported.</p>
<p>One identifier mismatch is preserved for archival review. The Research Desk's first image label and the casefile's first catalog label differ; no catalog identifier is silently corrected or promoted as fact.</p>
<ol class="fv-ex2-crosswalk__list">{''.join(cards)}</ol>
<p><a href="{escape(source_url,quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Review the pinned Research Desk staging source on GitHub (new tab)</a>. Source reviewed at commit <code>{EXACT_COMMIT}</code>, blob <code>{EXACT_BLOB}</code>. No Research Desk plugin installation or WordPress changes.</p>
</div></details>'''
    return html, {'status':'CROSS_LANE_URL_MATCH_WITH_IDENTIFIER_HOLD','records':rows,
                  'matched_nasa_urls':6,'catalog_label_review_holds':1,
                  'research_desk_commit':EXACT_COMMIT,'research_desk_ledger_blob':EXACT_BLOB,
                  'source_code_imported_from_pr158':False,'geo_pins':0,'photo_bytes_copied':0}

CSS = '''/* Link-only, no-JS crosswalk; source-label disagreement remains visible. */
.fv-ex2-crosswalk{border:1px solid #aa8e5c;background:#1a1b17;margin:0 0 24px;padding:12px clamp(12px,2vw,22px);color:#f4efe6}
.fv-ex2-crosswalk>summary{cursor:pointer;font-weight:700;min-height:48px;padding:12px 8px;color:#f5db9f;line-height:1.55}
.fv-ex2-crosswalk__body>p{max-width:82ch;color:#e4ddd1;line-height:1.7}
.fv-ex2-crosswalk__list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;list-style:none;margin:18px 0;padding:0}
.fv-ex2-crosswalk__item{background:#10110f;border:1px solid #63533d;padding:18px;min-width:0;overflow-wrap:anywhere}
.fv-ex2-crosswalk__item[data-crosswalk-review="hold"]{border:2px solid #f5c57b;background:#272015}
.fv-ex2-crosswalk__item strong{display:block;font:normal 1.15rem/1.4 Georgia,serif;margin:10px 0}
.fv-ex2-crosswalk__accession{color:#f7d7a1;font:700 .76rem/1.5 ui-monospace,monospace}
.fv-ex2-crosswalk__item p{color:#e7dfd1;font-size:.92rem;line-height:1.6}
.fv-ex2-crosswalk__item code,.fv-ex2-crosswalk__body>p code{overflow-wrap:anywhere;white-space:normal;color:#f7dfad}
.fv-ex2-crosswalk__status{border-left:3px solid #dfb877;padding-left:12px}
.fv-ex2-crosswalk__links{display:flex;gap:12px;flex-wrap:wrap}
.fv-ex2-crosswalk a{color:#f5d69d;display:inline-flex;min-height:44px;align-items:center;text-underline-offset:4px}
@container(max-width:800px){.fv-ex2-crosswalk__list{grid-template-columns:1fr}}
@media(max-width:800px){.fv-ex2-crosswalk__list{grid-template-columns:1fr}}
.fv-ex2-crosswalk :focus-visible{outline:3px solid #ffe4aa;outline-offset:4px}
'''
