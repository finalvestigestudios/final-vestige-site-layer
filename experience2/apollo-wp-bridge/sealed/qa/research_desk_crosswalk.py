#!/usr/bin/env python3
"""Read-only PR158 Research Desk witness reconciled to pinned Apollo PR215.

Same NASA URL is NOT proof of matching catalog identifier, editorial finding,
photo rights, or merge eligibility. R18 does not read or modify PR158's branch.
"""
from __future__ import annotations
from html import escape
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

WITNESS = Path(__file__).with_name('pr158_research_desk_witness.json')
IDENTITY_WITNESS = Path(__file__).with_name('nasa_identity_witness_r23.json')
IDENTITY_WITNESS_SHA256 = '75ef8e509b447bd61dcc3ae63400f49c260b80bf420de57082d34c41f5dac158'
SECONDARY_WITNESS = Path(__file__).with_name('nasa_secondary_witness_r29.json')
SECONDARY_WITNESS_SHA256 = '5deae6099d8e100bccb70ae125bce040d061a529176d286ddf11e873a716f0a1'

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


def verify_nasa_identity(rows: list[dict], source: Path = IDENTITY_WITNESS) -> dict:
    """Pinned curator witness, NOT a live NASA catalog lookup or licensing approval.

    Never promote a loosely related NASA photograph's identifier onto the
    casefile photo. A matching URL on the PR158 draft does not prove image ID.
    """
    raw = source.read_bytes()
    if sha256(raw).hexdigest() != IDENTITY_WITNESS_SHA256:
        raise CrosswalkHold('R23 NASA source-identity witness mutated; editorial HOLD')
    data = json.loads(raw)
    original = rows[0]
    if (len(rows) != 6 or sum(not r['catalog_identifier_label_match'] for r in rows) != 1
            or original['claim_id'] != '01'
            or original['nasa_catalog_url'] != data.get('source_page', {}).get('url')
            or original['canonical_catalog_label'] != 'Apollo 1 crew training portrait'
            or original['research_desk_catalog_label'] != data.get('research_desk_label')
            or original['research_desk_catalog_label'] != 'NASA S67-19766'
            or data.get('verified_manually_on') != '2026-10-31'
            or data.get('subject_claim_id') != '01'
            or data.get('source_page',{}).get('photo_context') != 'January 1967 training'
            or data.get('source_page',{}).get('catalog_identifier_visible_in_page_text') is not None
            or data.get('source_page',{}).get('id_equivalence_verified') is not False
            or data.get('comparison_page',{}).get('url') != 'https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/'
            or data.get('comparison_page',{}).get('nasa_identifier') != 'S66-30236'
            or data.get('comparison_page',{}).get('nasa_image_date') != 'March 31, 1966'
            or data.get('comparison_page',{}).get('is_same_photo_as_casefile_claim_01') is not False
            or data.get('comparison_page',{}).get('not_a_substitute_identifier') is not True
            or data.get('decision') != 'HOLD_UNTIL_FIRST_PARTY_IDENTIFIER_EQUIVALENCE_CONFIRMED'
            or data.get('media_rights') != 'NOT_CLEARED' or data.get('geo_pins') != 0
            or data.get('unresolved_identifiers') != 1
            or data.get('not_an_endorsement_or_live_page_monitor') is not True):
        raise CrosswalkHold('NASA catalog identity decision would be incorrectly promoted or misattributed')
    return data



def verify_secondary_catalog(source: Path = SECONDARY_WITNESS) -> dict:
    """Pinned secondary discovery; NEVER elevate an aggregator to NASA authority."""
    raw = source.read_bytes()
    if sha256(raw).hexdigest() != SECONDARY_WITNESS_SHA256:
        raise CrosswalkHold('R29 secondary source witness mutated; review HOLD')
    doc = json.loads(raw)
    item = doc.get('secondary_listing', {})
    expected = {
        'schema':'fv-ex2-r29-secondary-photo-catalog-witness-v1',
        'reviewed_on':'2026-10-31',
        'identity_status':'UNRESOLVED_NOT_FIRST_PARTY_CONFIRMED',
        'research_desk_claim':'NASA S67-19766',
        'primary_casefile_photo_url':'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
        'distinct_nasa_photo_url':'https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/',
        'distinct_nasa_photo_identifier':'S66-30236',
        'research_action':'FIND_FIRST_PARTY_CATALOG_RECORD_AND_COMPARE_IMAGE_BYTES_BEFORE_CORRECTING_LABEL',
        'photo_reuse_status':'LINK_ONLY_UNCLEARED',
        'atlas_geographic_pins':0,
        'source_witness_type':'DATED_EDITORIAL_WEB_REVIEW_NOT_MACHINE_VERIFIED_ARCHIVE_METADATA',
    }
    required_listing = {
        'url':'https://timelessmoon.getarchive.net/amp/media/astro-grissom-chaffee-white-in-va-in-mission-simulator-and-on-complex-34-a5cc67',
        'displayed_nasa_identifier':'S67-19766',
        'headline':'ASTRO GRISSOM, CHAFFEE, WHITE IN VA, IN MISSION SIMULATOR AND ON COMPLEX 34',
        'claimed_source':'Defense Visual Information Distribution Service',
        'date_range_as_displayed':'1968 - 1972',
        'first_party_nasa_catalog_record':False,
        'establishes_same_image_as_casefile_link':False,
        'date_correlates_with_casefile_january_1967':False,
        'promotes_geolocation_or_rights':False,
    }
    if (set(doc) != set(expected) | {'secondary_listing'} or
        any(doc.get(k) != v for k,v in expected.items()) or
        not isinstance(item,dict) or item != required_listing):
        raise CrosswalkHold('Secondary identifier evidence is not independently established')
    return doc


def build_crosswalk(records: list[dict], witness: Path = WITNESS) -> tuple[str,dict]:
    rows=verify_witness(records, witness)
    identity=verify_nasa_identity(rows)
    secondary=verify_secondary_catalog()
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
    identity_card = f'''<aside class="fv-ex2-crosswalk__identity" id="fv-ex2-catalog-identity" aria-labelledby="fv-ex2-catalog-identity-title" data-catalog-review="hold">
<p class="fv-ex2-crosswalk__identity-kicker">SOURCE 01 / EDITORIAL IDENTITY HOLD</p>
<h3 id="fv-ex2-catalog-identity-title">Same source link. Unproven photograph identifier.</h3>
<p>The pinned Research Desk calls this <code>NASA S67-19766</code>. The linked Apollo casefile instead uses <code>Apollo 1 crew training portrait</code>. NASA’s source page describes the crew near Launch Complex 34 in January 1967, but the page text does not supply the Research Desk accession number. <strong>The equivalence has not been verified.</strong></p>
<details><summary>Compare NASA references and review what remains unresolved</summary>
<ol class="fv-ex2-crosswalk__identity-sources">
<li><strong>Original linked NASA record.</strong> Crew training outside near Launch Complex 34, January 1967. The page is evidence for subject/context, not a verified S67-19766 accession. <a href="{escape(identity['source_page']['url'],quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect the exact NASA page (opens in a new tab)</a>.</li>
<li><strong>Different NASA studio portrait.</strong> A separate 1966 NASA image article identifies <code>S66-30236</code>, dated March 31, 1966. It is not the original linked image and its identifier must <em>never</em> be substituted for this casefile photo. <a href="{escape(identity['comparison_page']['url'],quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect the separate NASA portrait (opens in a new tab)</a>.</li>
<li data-secondary-catalog-review="hold"><strong>Secondary archive listing; NOT NASA confirmation.</strong> A third-party catalog page displays <code>{escape(secondary['secondary_listing']['displayed_nasa_identifier'])}</code> under a broad simulator / Launch Complex 34 title and attributes the source to DVIDS. Its date range reads <code>1968–1972</code>, which does not corroborate the January 1967 casefile date. <strong>Neither the image identity nor NASA accession equivalence is established.</strong> <a href="{escape(secondary['secondary_listing']['url'],quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect the third-party catalog clue (new tab)</a>.</li>
</ol>
<p class="fv-ex2-crosswalk__secondary-caution" data-secondary-source-status="not-first-party">The catalog number appears in a secondary listing; it is not linked by a first-party NASA identifier to this particular photograph. Preserve both labels and the release hold. No image bytes, rights decision, coordinate or relationship has been imported.</p>
<p><strong>Clearance condition:</strong> obtain a first-party NASA media/caption or archive record that expressly ties the specific linked photo to a catalog identifier; compare photo identity and archival metadata. Until then, retain descriptive label, preserve PR #158 disagreement and do not assert an assigned accession number, reuse permission or a geographic pin.</p>
<p><a href="#source-01">Inspect SourceDrawer 01</a> · <a href="#stage-01">Read ChronologyRail 01</a></p>
<p class="fv-ex2-crosswalk__identity-note">Curator witness checked 2026-10-31. This offline snapshot is not a live NASA change monitor, image-rights authorization, or NASA endorsement.</p>
</details></aside>'''
    html=f'''<details class="fv-ex2-crosswalk" id="fv-ex2-research-desk-crosswalk">
<summary>Research Desk source custody comparison — six matched NASA links, one identifier-label review hold</summary>
<div class="fv-ex2-crosswalk__body">
<p>Independent Research Desk draft PR #158 and this Apollo casefile refer to the same six NASA catalog <em>URLs</em>. Matching a URL does not establish identical photo identifiers, historical claims, archive permissions or deployment readiness. The six URL-and-label references are a pinned read-only comparison; no PR #158 plugin code, photos, or historical assertions were imported.</p>
<p>One identifier mismatch is preserved for archival review. The Research Desk's first image label and the casefile's first catalog label differ; no catalog identifier is silently corrected or promoted as fact.</p>
{identity_card}
<ol class="fv-ex2-crosswalk__list">{''.join(cards)}</ol>
<p><a href="{escape(source_url,quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Review the pinned Research Desk staging source on GitHub (new tab)</a>. Source reviewed at commit <code>{EXACT_COMMIT}</code>, blob <code>{EXACT_BLOB}</code>. No Research Desk plugin installation or WordPress changes.</p>
</div></details>'''
    return html, {'status':'CROSS_LANE_URL_MATCH_WITH_IDENTIFIER_HOLD','records':rows,
                  'matched_nasa_urls':6,'catalog_label_review_holds':1,
                  'research_desk_commit':EXACT_COMMIT,'research_desk_ledger_blob':EXACT_BLOB,
                  'source_code_imported_from_pr158':False,'geo_pins':0,'photo_bytes_copied':0,
                  'nasa_identity_witness_sha256':IDENTITY_WITNESS_SHA256,
                  'identity_adjudication':'HOLD_UNRESOLVED_PR158_S67_19766',
                  'comparison_portrait_not_a_substitute':True,
                  'source_identifier_verified':False,
                  'secondary_nasa_accession_listing':'S67-19766',
                  'secondary_witness_sha256':SECONDARY_WITNESS_SHA256,
                  'secondary_first_party_corroboration':False,
                  'secondary_image_equivalence':False,
                  'secondary_catalog_date_warning':True}

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

CSS += '''/* R23 source-identity decision is not an assertion of NASA photo ID. */
.fv-ex2-crosswalk__identity{background:#221c14;border:2px solid #f3c37c;padding:clamp(14px,2vw,22px);margin:18px 0;overflow-wrap:anywhere}
.fv-ex2-crosswalk__identity h3{font:400 clamp(1.25rem,3cqw,1.65rem)/1.32 Georgia,serif;color:#fff4d8;margin:8px 0 12px}
.fv-ex2-crosswalk__identity p,.fv-ex2-crosswalk__identity li{color:#f2e6d1;line-height:1.7;max-width:90ch}
.fv-ex2-crosswalk__identity code{white-space:normal;overflow-wrap:anywhere;color:#ffe0a1}
.fv-ex2-crosswalk__identity-kicker{font:700 .73rem/1.5 ui-monospace,monospace;letter-spacing:.09em;color:#ffdc97}
.fv-ex2-crosswalk__identity-sources{margin:14px 0;padding-left:clamp(22px,3vw,34px);display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.fv-ex2-crosswalk__identity-sources li{background:#121711;border:1px solid #836d4e;padding:14px 16px;min-width:0}
.fv-ex2-crosswalk__identity summary{border:1px solid #ac8d61;padding:11px 14px;min-height:48px}
.fv-ex2-crosswalk__identity-note{font-size:.84rem;border-left:3px solid #efce91;padding-left:12px}
.fv-ex2-crosswalk__secondary-caution{border:2px solid #f1c779;padding:12px 16px;background:#151715;font-weight:600;color:#fff5dc!important}
.fv-ex2-crosswalk__identity-sources [data-secondary-catalog-review=hold]{border:2px solid #f1c779}
.fv-ex2-crosswalk__identity-sources a:focus-visible{outline:3px solid #ffe4aa;outline-offset:3px}
@container(max-width:700px){.fv-ex2-crosswalk__identity-sources{grid-template-columns:1fr}}
@media(max-width:750px){.fv-ex2-crosswalk__identity-sources{grid-template-columns:1fr}}
'''
