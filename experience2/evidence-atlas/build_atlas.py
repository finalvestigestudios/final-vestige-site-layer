#!/usr/bin/env python3
"""Generate a deterministic, map-free Apollo 1 Evidence Atlas from R37 custody.

Only approved metadata fields are rendered. Unreviewed images and inferred
geospatial claims are never emitted. Generate for private review, not publishing.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CROSSWALK = HERE.parent / 'research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json'
EXPECTED_BLOB = 'ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea'
IDS = ('01', '02', '03', '04', '05', '06')
ALLOWED_YEARS = {'1966', '1967', '2017'}
EXPECTED_URLS = {
    '01': 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    '02': 'https://www.nasa.gov/image-detail/amf-s67-15717/',
    '03': 'https://www.nasa.gov/image-detail/amf-s66-58038/',
    '04': 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    '05': 'https://www.nasa.gov/image-detail/amf-s67-21294/',
    '06': 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
}
RECORD_KEYS = {'id', 'catalog', 'date', 'date_label', 'photo_url', 'photo_role', 'identity_note', 'media_rights'}
# R51: NASA's linked crew-photo page does not itself print this catalog number.
# Preserve the pinned R37 crosswalk but do not promote its filename-based match
# into an independently authenticated catalog-to-photograph identity.
PROVISIONAL_CATALOG_NOTICE = ('The S67-19766 association is based on a NASA-hosted filename; '
    'the linked NASA page does not state that catalog number. '
    'Catalog-to-photograph identity remains unconfirmed pending archival review.')

# R56: The page-level NASA metadata audit is an independently tracked preflight,
# not image-use clearance. Pin the exact reviewed ledger so a quiet JSON edit
# cannot silently change public-facing SourceDrawer metadata.
RIGHTS_AUDIT = HERE / 'sources/NASA_PAGE_RIGHTS_AUDIT_R55.json'
EXPECTED_AUDIT_SHA256 = 'a3c87196da3c48490a84e6a5b1ad7f3e6a21f4d908ebccded7ab8517597f25c9'

def validate_rights_audit(custody: dict, path: Path = RIGHTS_AUDIT) -> dict:
    raw = path.read_bytes()
    if sha256(raw) != EXPECTED_AUDIT_SHA256:
        raise ValueError('NASA source page audit changed without review: refuse build')
    audit = json.loads(raw)
    rows = audit.get('records')
    if (audit.get('schema') != 'fv.ex2.apollo.nasa-page-rights.r55.v1'
        or audit.get('status') != 'STAGING_HOLD'
        or audit.get('policy', {}).get('independent_rights_clearance') != 'NOT_COMPLETE'
        or audit.get('crosswalk_blob_git_sha1') != EXPECTED_BLOB
        or not isinstance(rows, list) or len(rows) != 6):
        raise ValueError('NASA page audit schema or release gate changed')
    for source, rights in zip(custody['records'], rows):
        if (rights.get('id') != source['id']
            or rights.get('crosswalk_catalog') != source['catalog']
            or rights.get('nasa_page') != source['photo_url']
            or rights.get('rights_status') != 'INDIVIDUAL_REVIEW_PENDING'
            or rights.get('human_link_check') is not False
            or rights.get('downloaded_or_embedded') is not False
            or rights.get('recognizable_person_review') != 'required_or_undetermined'
            or not rights.get('page_last_updated')):
            raise ValueError('NASA source page identity or image-release status changed')
    if (rows[0]['catalog_display'] != 'not_displayed_on_linked_nasa_page'
        or any(r['catalog_display'] != 'displayed_as_PIA_number' for r in rows[1:])):
        raise ValueError('Unreviewed NASA catalog verification change')
    return audit

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def validate_custody(path: Path = CROSSWALK) -> dict:
    data = path.read_bytes()
    if git_blob(data) != EXPECTED_BLOB:
        raise ValueError('R37 custody blob changed without independent review: refuse build')
    crosswalk = json.loads(data)
    if crosswalk.get('schema') != 'fv.ex2.apollo.photo_custody.r37.v1' or crosswalk.get('release') != 'STAGING_HOLD':
        raise ValueError('Unapproved custody schema/release')
    if crosswalk.get('rights_guidance') != 'https://www.nasa.gov/nasa-brand-center/':
        raise ValueError('NASA rights-guidance link changed')
    rows = crosswalk.get('records')
    if not isinstance(rows, list) or [r.get('id') for r in rows] != list(IDS):
        raise ValueError('Expected exactly six reviewed source IDs in custody order')
    for r in rows:
        if set(r) != RECORD_KEYS or r['photo_url'] != EXPECTED_URLS[r['id']]:
            raise ValueError('Unexpected source fields or NASA destination')
        if r['media_rights'] != 'INDIVIDUAL_REVIEW_REQUIRED':
            raise ValueError('Image reuse not reviewed for this candidate')
        if r['date'][:4] not in ALLOWED_YEARS or not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?', r['date']):
            raise ValueError('Invalid historical photographic date')
        if not all(isinstance(r[k], str) and r[k].strip() for k in RECORD_KEYS):
            raise ValueError('Empty source datum')
    return crosswalk

def make_html(custody: dict, css: str, js: str) -> str:
    audit = validate_rights_audit(custody)
    rights_by_id = {entry['id']: entry for entry in audit['records']}
    q = lambda s: html.escape(str(s), quote=True)
    cards = []
    for r in custody['records']:
        year = r['date'][:4]
        is_2017 = year == '2017'
        label = ('Retrospective exhibit, not contemporaneous evidence' if is_2017
                 else 'Contextual source photograph, not proof of causation')
        provisional = ('<p class="fva-card__catalog-caution" data-fva-catalog-unconfirmed>'
            + q(PROVISIONAL_CATALOG_NOTICE) + '</p>') if r['id'] == '01' else ''
        audit_entry = rights_by_id[r['id']]
        catalog_display = ('Not printed on the linked NASA page; attribution provisional.'
            if r['id'] == '01' else 'Identifier displayed in the linked NASA page PIA field.')
        credit = audit_entry['image_credit_as_displayed'] or 'No individual image credit displayed in reviewed metadata.'
        producer = audit_entry['producer_as_displayed'] or 'No producing center displayed in reviewed metadata.'
        catalog_state = "provisional" if r["id"] == "01" else "page-displayed"
        cards.append(f'''<article class="fva-card" data-fva-record data-fva-id="{q(r['id'])}" data-fva-year="{year}" data-fva-catalog-state="{catalog_state}" id="fva-record-{q(r['id'])}" tabindex="-1">
          <div class="fva-card__top"><span>DOCUMENT {q(r['id'])} / 06</span><span>{year} · NASA RECORD</span></div>
          <div class="fva-card__plate" aria-hidden="true"><span>{q(r['catalog'])}</span><b>ARCHIVAL RECORD</b></div>
          {provisional}
          <h2>{q(r['photo_role'].capitalize())}</h2>
          <p class="fva-card__date"><strong>Photograph date</strong> <span>{q(r['date_label'])}</span></p>
          <p class="fva-card__limit">{q(label)}</p>
          <details data-fva-drawer>
             <summary>Source custody and reuse status</summary>
             <dl><dt>Catalog reference</dt><dd>{q(r['catalog'])}</dd>
             <dt>Record identity note</dt><dd>{q(r['identity_note'])}</dd>
             <dt>Catalog verification on NASA page</dt><dd data-fva-catalog-status>{q(catalog_display)}</dd>
             <dt>Credit displayed by NASA</dt><dd>{q(credit)}</dd>
             <dt>Producing center displayed by NASA</dt><dd>{q(producer)}</dd>
             <dt>NASA page last updated</dt><dd>{q(audit_entry['page_last_updated'])}</dd>
             <dt>Editorial source check</dt><dd>NASA metadata reviewed {q(audit['page_text_reviewed_on'])}; no human link check or photograph inspection completed.</dd>
             <dt>Reuse status</dt><dd>Individual review required. No photograph is reproduced here.</dd>
             <dt>Documentary boundary</dt><dd>{q(r['photo_role'])}. The photograph alone does not prove the cause or sequence of the Apollo 1 fire.</dd></dl>
          </details>
          <a class="fva-card__external" href="{q(r['photo_url'])}" target="_blank" rel="noopener noreferrer">Open original NASA record (opens in new tab) <span aria-hidden="true">↗</span></a>
          <a class="fva-card__cite-link" data-fva-to-citation href="#fva-citation-{q(r['id'])}">Cite this NASA record</a>
          <a class="fva-card__desk-link" data-fva-to-desk href="#fv-ex2-ledger-apollo1-record-{q(r['id'])}" hidden>Read the Research Desk finding for this NASA record</a>
          <button type="button" class="fva-card__compare" data-fva-select="{q(r['id'])}" aria-pressed="false" hidden>Inspect source {q(r['id'])} alongside another</button>
        </article>''')
    all_cards = '\n'.join(cards)
    # Fixed, source-custody-backed navigation; still navigable when JS is absent.
    index_items = '\n'.join(
        f'<li><a data-fva-jump href="#fva-record-{q(r["id"])}"><span class="fva-index__num">{q(r["id"])}</span>'
        f'<span class="fva-index__name">{q(r["catalog"])} <small>{q(r["date_label"])}</small></span></a></li>'
        for r in custody['records'])
    # ChronologyRail is a chronology of source photographs, never of the fire itself.
    # Year buckets deliberately preserve custody order. S67-19766 has a known month
    # but no confirmed exact day; sorting it among known January days would imply
    # evidence that does not exist.
    eras = (
        ('1966', 'Preparations before the fire',
         'Contextual rehearsal record from 1966. Not a depiction of the fire.'),
        ('1967', 'Contemporary source context',
         'January records are not arranged as an accident sequence. One photographic day is unresolved.'),
        ('2017', 'Retrospective memorial exhibits',
         'These photographs document later displays, not the 1967 spacecraft.'),
    )
    chronology_items = []
    for year, era_title, note in eras:
        records = [r for r in custody['records'] if r['date'].startswith(year)]
        links = '\n'.join(
            f'<li><a data-fva-timejump data-fva-time-id="{q(r["id"])}" href="#fva-record-{q(r["id"])}">'
            f'<time datetime="{q(r["date"])}">{q(r["date_label"])}</time>'
            f'<strong>{q(r["catalog"])}</strong><span>{q(r["photo_role"])}</span>'
            f'</a></li>' for r in records
        )
        chronology_items.append(
            f'<li data-fva-era="{year}"><div class="fva-chronology__year">'
            f'<span class="fva-chronology__date">{year}</span><h3>{q(era_title)}</h3>'
            f'<p>{q(note)}</p></div><ol>{links}</ol></li>'
        )
    chronology = '\n'.join(chronology_items)
    # R44: scholar-ready, TEXT-ONLY source citations. Every line is generated
    # from the pinned NASA custody crosswalk; no photo licenses are inferred.
    citation_items = []
    for r in custody['records']:
        citation = (f'NASA · catalog {r["catalog"]} · photograph date {r["date_label"]} · '
                    f'source: {r["photo_url"]} · image reuse: individual review required.')
        if r["id"] == "01":
            citation += " " + PROVISIONAL_CATALOG_NOTICE
        citation_items.append(
            f'<li data-fva-cite-id="{q(r["id"])}" id="fva-citation-{q(r["id"])}">'
            f'<p class="fva-citation__text" data-fva-citation-text>{q(citation)}</p>'
            f'<a data-fva-back-record href="#fva-record-{q(r["id"])}">Return to NASA record {q(r["id"])}</a>'
            f'<button type="button" data-fva-copy hidden '
            f'aria-label="Copy NASA source {q(r["id"])} citation">Copy citation {q(r["id"])}</button></li>'
        )
    citations = '\n'.join(citation_items)
    filters = '\n'.join(f'<button type="button" data-fva-filter="{v}" aria-pressed="{str(v=="all").lower()}">{label}</button>'
                        for v, label in [('all', 'All 6 sources'), ('1966', '1966 · 1 source'),
                                         ('1967', '1967 · 3 sources'), ('2017', '2017 · 2 exhibits')])
    # Catalog certainty is a *page-metadata* label only, never image clearance.
    # The filter is optional and must never conceal the complete citation index.
    catalog_filters = '\n'.join(
        f'<button type="button" data-fva-proof-filter="{value}" aria-pressed="{str(value=="all").lower()}">{label}</button>'
        for value, label in [('all', 'All catalog records (6)'),
                             ('page-displayed', 'Identifier displayed on NASA page (5)'),
                             ('provisional', 'Provisional association (1)')])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Apollo 1 Evidence Atlas · Final Vestige Studios · STAGING ONLY</title><style>{css}</style></head>
<body><main class="fva" data-fva-atlas aria-labelledby="fva-title">
  <header class="fva-header"><div class="fva-mark">FINAL VESTIGE STUDIOS <span> / EXPERIENCE 2.0</span></div>
    <p class="fva-kicker">RESEARCH DESK / APOLLO 1</p>
    <h1 id="fva-title">The Evidence <em>Atlas.</em></h1>
    <p class="fva-deck">Six NASA photographic-source records, presented without imagery until reuse review is complete. Navigate what a record documents—and what it does not.</p>
    <p class="fva-provenance-note">Catalog verification notice: record 01 has a provisional catalog-to-image association. See the record and source register for the limitation.</p>
    <div class="fva-caution"><strong>Why no map?</strong> The reviewed source ledger does not establish precise locations for six independently verified map pins or evidentiary connections. No coordinates or inferred relationships are shown.</div>
  </header>
  <section class="fva-custody-status" aria-labelledby="fva-custody-status-title" data-fva-custody-status>
    <h2 id="fva-custody-status-title">What is verified—and what is not.</h2>
    <p>The source-page metadata was checked on {q(audit['page_text_reviewed_on'])}. This was an editorial research pass, <strong>not a human link check, photograph inspection, or rights clearance</strong>.</p>
    <ul><li><strong>5 of 6</strong> catalog identifiers are displayed on their linked NASA pages.</li>
      <li><strong>1 of 6</strong> identifier-to-photograph associations remains provisional: S67-19766.</li>
      <li><strong>0 of 6</strong> photographs is approved for reuse or reproduced here.</li></ul>
    <p>Open each record's <em>Source custody and reuse status</em> drawer for the NASA credit, producing-center field, page revision date, and remaining limitations. NASA metadata alone is not a license.</p>
  </section>
  <section class="fva-guide" aria-labelledby="fva-how"><h2 id="fva-how">Read before exploring</h2>
    <p>The 1966 rehearsal image precedes the 1967 fire. The 2017 exhibit photographs are retrospective. Photograph dates are not a minute-by-minute fire chronology; NASA's Apollo 204 Review Board report is the source for technical findings.</p>
    <p><a href="{q(custody['historical_primary'])}" target="_blank" rel="noopener noreferrer">Read the Apollo 204 Review Board report <span aria-hidden="true">↗</span></a></p>
  </section>
  <nav class="fva-index" aria-labelledby="fva-index-title">
    <div><h2 id="fva-index-title">Source index</h2><p>Navigate by NASA reference label. The index lists records, not geographic sites or links between events.</p></div>
    <ol>{index_items}</ol>
  </nav>
  <section class="fva-chronology" aria-labelledby="fva-chronology-title" data-fva-chronology>
    <div class="fva-chronology__intro"><p class="fva-chronology__eyebrow">CHRONOLOGY RAIL / SOURCE DATES</p>
      <h2 id="fva-chronology-title">Three eras. Six selected NASA references.</h2>
      <p>Follow when the <em>photographic sources</em> were made, not a reconstruction of the Apollo 1 fire. Entries within each era retain ledger order; January 1967 is not presented as a minute-by-minute sequence.</p>
    </div>
    <ol class="fva-chronology__eras">{chronology}</ol>
  </section>
  <div class="fva-controls" data-fva-controls hidden>
    <div class="fva-filter" role="group" aria-label="Filter photographic-source records by year">{filters}</div>
    <div class="fva-proof-filter" role="group" aria-label="Filter catalog verification against NASA page metadata">
      <p>Catalog identifier on linked NASA page (not image-use permission)</p>{catalog_filters}</div>
    <div class="fva-search"><label for="fva-search">Search source descriptions</label><input type="search" id="fva-search" data-fva-search aria-controls="fva-records" autocomplete="off" placeholder="Hatch, rehearsal, Shiflett…" />
      <button type="button" data-fva-reset>Reset filters</button></div>
    <p class="fva-count" data-fva-status role="status" aria-live="polite" aria-atomic="true"></p>
  </div>
  <section class="fva-grid" id="fva-records" aria-label="NASA photographic-source gallery">{all_cards}</section>
  <p class="fva-desk-status" data-fva-desk-status role="status" aria-live="polite" hidden></p>
  <p class="fva-empty" data-fva-empty hidden>No source records match. Reset filters to restore all six.</p>
  <section class="fva-compare" data-fva-compare hidden aria-labelledby="fva-compare-title">
    <p class="fva-compare__eyebrow">SOURCE PAIR INSPECTOR / OPTIONAL ENHANCEMENT</p>
    <h2 id="fva-compare-title">Two records. Their documented limits.</h2>
    <p>Choose up to two source cards to inspect their labels, photographic dates and documentary scope side by side. This comparison <strong>does not establish causation, proximity, or a historical connection</strong>. All six originals remain below and in the citation register.</p>
    <button type="button" data-fva-compare-clear hidden>Clear comparison</button>
    <p data-fva-compare-status role="status" aria-live="polite" aria-atomic="true">No records selected.</p>
    <div class="fva-compare__pair"><div data-fva-compare-slot></div><div data-fva-compare-slot></div></div>
  </section>
  <section class="fva-citations" aria-labelledby="fva-citations-title" data-fva-citations>
    <p class="fva-citations__eyebrow">RESEARCH ACCESS / CITATION REGISTER</p>
    <h2 id="fva-citations-title">Trace every reference.</h2>
    <p>These are source references, not licenses to reproduce photographs. Exact dates are not inferred where NASA's record gives only a month. The register remains complete when filters are applied or JavaScript is unavailable.</p>
    <div class="fva-export"><p>All six citations remain below. With JavaScript enabled, save a plain-text research sheet containing each record’s NASA source-custody details and pending photo-rights status. No images or inferred historical relationships are included.</p>
      <button type="button" data-fva-export hidden>Save six citations and source-custody notes (.txt)</button>
      <p class="fva-export__status" role="status" aria-live="polite" aria-atomic="true" data-fva-export-status></p>
    </div>
    <ol>{citations}</ol>
    <p class="fva-citations__status" role="status" aria-live="polite" aria-atomic="true" data-fva-copy-status></p>
  </section>
  <footer class="fva-footer"><p><strong>Six source references · Six individual image-rights reviews outstanding.</strong> This is a source-reference gallery, not a reproduction of NASA photographs or a geo-map.</p>
   <p>NASA record credits retained. <a href="{q(custody['rights_guidance'])}" target="_blank" rel="noopener noreferrer">NASA media and branding guidelines <span aria-hidden="true">↗</span></a> · Private staging candidate; not for publication. No endorsement implied.</p></footer>
</main><script>{js}</script></body></html>\n'''

def build(output: Path) -> dict:
    custody = validate_custody()
    css_path, js_path = HERE / 'atlas.css', HERE / 'atlas.js'
    css, js = css_path.read_text(encoding='utf-8'), js_path.read_text(encoding='utf-8')
    document = make_html(custody, css, js)
    # The output is self-contained; a browser cannot fetch NASA images because none are present.
    output.mkdir(parents=True, exist_ok=True)
    page_path = output / 'apollo-evidence-atlas.html'
    page_path.write_text(document, encoding='utf-8', newline='\n')
    receipt = {
       'schema': 'fv.ex2.apollo.atlas.r48.v1', 'release': 'STAGING_HOLD',
       'crosswalk_git_blob': EXPECTED_BLOB, 'records': list(IDS),
       'source_year_counts': {'1966': 1, '1967': 3, '2017': 2},
       'image_rights': '6 INDIVIDUAL_REVIEW_REQUIRED', 'image_binaries': 0,
       'geographic_pins': 0, 'relationship_edges': 0,
       'output_sha256': sha256(page_path.read_bytes()),
       'css_sha256': sha256(css_path.read_bytes()),
       'js_sha256': sha256(js_path.read_bytes()),
       'crosswalk_sha256': sha256(CROSSWALK.read_bytes()),
       'wordPress_staging': 'NOT_TESTED', 'hosted_CWV': 'NOT_MEASURED',
    }
    (output / 'atlas-build-manifest.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    return receipt


# R71: OPTIONAL read-only editorial rights matrix, never installed by default.
# The six source rows derive from exact, independently pinned R37/R55 records.
# This is a staging review utility, NOT an image-use admission or change to
# the existing shortcode template hash/Research Desk/production WordPress.
def build_rights_matrix_r71(output: Path) -> dict:
    custody=validate_custody()
    audit=validate_rights_audit(custody)
    q=lambda value: html.escape(str(value), quote=True)
    rows=[]
    for source, rights in zip(custody['records'], audit['records']):
        if (source['id'] != rights['id'] or source['catalog'] != rights['crosswalk_catalog']
            or source['photo_url'] != rights['nasa_page']
            or source['media_rights'] != 'INDIVIDUAL_REVIEW_REQUIRED'
            or rights['rights_status'] != 'INDIVIDUAL_REVIEW_PENDING'
            or rights['human_link_check'] is not False
            or rights['downloaded_or_embedded'] is not False):
            raise ValueError('Photo identity or rights drift: review board withheld')
        provisional=source['id']=='01'
        catalog=rights['catalog_display']
        if catalog != ('not_displayed_on_linked_nasa_page' if provisional else 'displayed_as_PIA_number'):
            raise ValueError('Unreviewed catalog certainty change')
        certainty=('PROVISIONAL: NASA page does not print this catalog ID'
                   if provisional else 'Identifier displayed in NASA page PIA metadata')
        rows.append(f'''<li data-r71-rights-row data-r71-id="{q(source['id'])}">
          <details><summary>NASA source {q(source['id'])} / {q(source['catalog'])} — reuse pending</summary>
          <p><strong>Photograph date:</strong> {q(source['date_label'])}</p>
          <p><strong>Catalog verification:</strong> {q(certainty)}</p>
          <p><strong>Credit:</strong> {q(rights['image_credit_as_displayed'] or 'Not individually listed')}</p>
          <p><strong>Producing center:</strong> {q(rights['producer_as_displayed'] or 'Not listed')}</p>
          <p><strong>Page updated:</strong> {q(rights['page_last_updated'])}</p>
          <p><strong>Documentary boundary:</strong> {q(source['photo_role'])}</p>
          <p><strong>Reuse:</strong> Individual photo review outstanding; no human
          link verification, image inspection, or license granted.</p>
          <a href="{q(source['photo_url'])}" rel="noopener noreferrer"
             target="_blank">Original NASA source for record {q(source['id'])} ↗</a>
          </details>
          <div class="fva-r73-print-proof" data-r73-print-proof>
            <h3>NASA source {q(source['id'])} / {q(source['catalog'])} — reuse pending</h3>
            <p><strong>Photograph date:</strong> {q(source['date_label'])}</p>
            <p><strong>Catalog verification:</strong> {q(certainty)}</p>
            <p><strong>Credit:</strong> {q(rights['image_credit_as_displayed'] or 'Not individually listed')}</p>
            <p><strong>Producing center:</strong> {q(rights['producer_as_displayed'] or 'Not listed')}</p>
            <p><strong>Page updated:</strong> {q(rights['page_last_updated'])}</p>
            <p><strong>Documentary boundary:</strong> {q(source['photo_role'])}</p>
            <p><strong>Reuse:</strong> Individual photo review outstanding; no human
            link verification, image inspection, or license granted.</p>
            <p><strong>Original NASA source:</strong>
              <span data-r73-print-url>{q(source['photo_url'])}</span>
            </p>
          </div></li>''')
    if len(rows)!=6:
        raise ValueError('Expected six individual source reviews')
    matrix=('''<section class="fva-r71-rights" data-r71-rights aria-labelledby="r71-rights-title">
      <h2 id="r71-rights-title">Six source reviews. Zero reuse clearances.</h2>
      <p>This private editorial matrix is not a license. NASA's general media
      guidance is not image-specific permission. No photographs, map pins or
      unsupported historical relationships are reproduced. S67-19766 remains
      a provisional catalog-to-photograph association.</p><ol>'''
      + ''.join(rows) + '</ol></section>')
    style='''<style id="r71-private-rights-css">
      .fva-r71-rights{margin:24px 0 36px;padding:clamp(18px,3vw,32px);
        border:1px solid #998052;background:#1b1e18;color:#eee8dc}
      .fva-r71-rights h2{font:400 clamp(25px,3vw,39px)/1.2 Georgia,serif;
        margin:0 0 12px;color:#f4efe2}
      .fva-r71-rights>p{max-width:75ch;line-height:1.7}
      .fva-r71-rights ol{list-style:none;padding:0;
        display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
      .fva-r71-rights li{min-width:0;background:#121510;border:1px solid #89734e}
      .fva-r71-rights .fva-r73-print-proof{display:none}
      .fva-r71-rights summary{cursor:pointer;min-height:44px;padding:13px;
        font-weight:600;color:#ffe1a2;overflow-wrap:anywhere}
      .fva-r71-rights details p{padding:0 14px;line-height:1.55}
      .fva-r71-rights details a{display:inline-flex;align-items:center;
        min-height:44px;margin:4px 14px 18px;color:#ffe1a2}
      .fva-r71-rights summary:focus-visible,.fva-r71-rights a:focus-visible{
        outline:3px solid #fff;outline-offset:2px}
      @media(max-width:760px){.fva-r71-rights ol{grid-template-columns:1fr}}
      @media(forced-colors:active){.fva-r71-rights,.fva-r71-rights li{
        border-color:CanvasText}.fva-r71-rights summary,.fva-r71-rights a{color:LinkText}}
      @media print{
        .fva-r71-rights details{display:none!important}
        .fva-r71-rights ol{display:block!important}
        .fva-r71-rights .fva-r73-print-proof{display:block!important}
        .fva-r71-rights .fva-r73-print-proof h3{font:700 15px/1.3 Georgia,serif;color:#111}
        .fva-r71-rights .fva-r73-print-proof p{padding:0 12px;line-height:1.35;color:#111}
        .fva-r71-rights .fva-r73-print-proof [data-r73-print-url]{color:#111;text-decoration:underline;overflow-wrap:anywhere}
        .fva-r71-rights li{margin:0 0 14px;page-break-inside:avoid}
        .fva-r71-rights,.fva-r71-rights li{background:none!important;
        color:#111;border-color:#444}.fva-r71-rights h2,.fva-r71-rights summary,
        .fva-r71-rights a{color:#111}.fva-r71-rights li{break-inside:avoid}
        .fva-r71-rights details>*{display:block!important}}
      </style>'''
    base=make_html(custody,(HERE/'atlas.css').read_text(encoding='utf-8'),
                   (HERE/'atlas.js').read_text(encoding='utf-8'))
    marker='<section class="fva-guide"'
    if base.count(marker)!=1 or base.count('</head>')!=1:
        raise ValueError('Atlas template changed: refuse review board injection')
    document=base.replace('</head>',style+'</head>',1).replace(marker,matrix+'\n  '+marker,1)
    output.mkdir(parents=True,exist_ok=True)
    path=output/'apollo-r71-media-rights-STAGING-ONLY.html'
    path.write_text(document,encoding='utf-8',newline='\n')
    receipt={'schema':'fv.apollo.r71.media-review.v1','release':'STAGING_HOLD',
      'crosswalk_git_blob':EXPECTED_BLOB,'source_audit_sha256':EXPECTED_AUDIT_SHA256,
      'source_rows':len(rows),'photo_reuse_clearances':0,'photograph_binaries':0,
      'actual_wordpress_tested':False,'html_sha256':sha256(path.read_bytes())}
    (output/'R71_MEDIA_RIGHTS_BUILD_RECEIPT.json').write_text(
      json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output), indent=2, sort_keys=True))
