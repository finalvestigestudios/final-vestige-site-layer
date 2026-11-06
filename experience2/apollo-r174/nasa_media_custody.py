"""R174: source-pinned, additive media custody annotations for the original Research Desk.

Input is the *R173 actual PR source* (NOT WordPress or a fixture). Offline only.
Never writes to CMS; does not download or redistribute NASA imagery. Source drift fails closed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED_BLOB = 'bc5e9e2618ed5bbde86b9c40c10045fb72fc66c2'
MARK = 'data-fvx-r174-media-custody'
END = 'data-fvx-r173-source-role'
LINK_RE = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>')


def git_blob(value: str) -> str:
    b = value.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def block(entry: dict) -> str:
    status = 'Catalog ID not established on linked NASA page.' if entry['record'] == '01' else 'Catalog ID present on linked NASA page.'
    return (f'<aside class="fv-ex2-media-custody" {MARK}="{escape(entry["record"])}" '
            f'aria-label="NASA photograph provenance for record {escape(entry["record"])}">'
            f'<strong>Photograph provenance · {escape(entry["date"])}</strong>'
            f'<p>{escape(entry["role"])}. {escape(status)} {escape(entry["finding"])}</p>'
            f'<small>Media use in a paid product: not cleared; rights and endorsement review required.</small>'
            f'</aside>')


def annotate(source: str, ledger: dict, *, fixture: bool = False) -> tuple[str, dict]:
    if git_blob(source) != EXPECTED_BLOB and not fixture:
        raise ValueError('STAGING HOLD: exact R173 source Git blob has changed')
    if MARK in source:
        raise ValueError('STAGING HOLD: duplicate R174 custody markup')
    records = ledger['records']
    if len(records) != 6 or [r['record'] for r in records] != [f'{x:02d}' for x in range(1,7)]:
        raise ValueError('STAGING HOLD: six ordered NASA records required')
    if source.count(END) != 6 or len(re.findall(r'<article\b[^>]*\bdata-fvx-record\b', source)) != 6:
        raise ValueError('STAGING HOLD: original six cards or R173 custody missing')
    original_links = LINK_RE.findall(source)
    original_text = source
    inserted = []
    for row in records:
        num, identity, url = row['record'], row['display_id'], row['photo_url']
        selector = f'id="fv-ex2-ledger-apollo1-record-{num}"'
        if source.count(selector) != 1:
            raise ValueError(f'STAGING HOLD: card {num} ambiguous')
        start = source.index(selector)
        end = source.find('</article>', start)
        if end < 0:
            raise ValueError(f'STAGING HOLD: card {num} malformed')
        section = source[start:end]
        if identity not in section:
            raise ValueError(f'STAGING HOLD: NASA catalog number {num} changed')
        if section.count('href="'+url+'"') != 1:
            raise ValueError(f'STAGING HOLD: NASA link destination {num} changed')
        proof = re.search(r'<p class="fv-ex2-source-custody__role"\s+' + END + '="'+num+r'">.*?</p>', section, flags=re.S)
        if proof is None:
            raise ValueError(f'STAGING HOLD: R173 source role {num} missing')
        marker = start + proof.end()
        addition = block(row)
        source = source[:marker] + addition + source[marker:]
        inserted.append(addition)
    if source.count(MARK) != 6 or LINK_RE.findall(source) != original_links:
        raise ValueError('STAGING HOLD: links or annotations drifted')
    recovered = source
    for addition in inserted:
        if recovered.count(addition) != 1:
            raise ValueError('STAGING HOLD: overlay data changed')
        recovered = recovered.replace(addition, '', 1)
    if recovered != original_text:
        raise ValueError('STAGING HOLD: historical source did not round-trip')
    if any(tag in ''.join(inserted).lower() for tag in ('<script','<form','<iframe','href=','onclick=')):
        raise ValueError('STAGING HOLD: executable or commercial HTML insertion')
    return source, {
      'gate':'OFFLINE_PROVENANCE_ONLY_NOT_RELEASED',
      'original_git_blob':git_blob(original_text), 'original_sha256':sha256(original_text),
      'candidate_sha256':sha256(source), 'all_original_links_preserved':True,
      'strict_roundtrip':True, 'date_classifications':6, 'unmatched_catalog_ids':1,
      'unmatched_record':'01', 'post_fire_documentation_record':'05',
      'new_links':0,'new_scripts':0,'staging_installed':False,'paid_media_cleared':False,
      'production_modified':False, 'axe_core':'NOT_RUN', 'net_revenue':'UNKNOWN'
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('r173_source_html',type=Path)
    p.add_argument('output_html',type=Path)
    p.add_argument('--ledger',type=Path, default=Path(__file__).with_name('nasa_media_custody.json'))
    args=p.parse_args()
    source=args.r173_source_html.read_text(encoding='utf-8')
    ledger=json.loads(args.ledger.read_text(encoding='utf-8'))
    rendered,audit=annotate(source,ledger)
    args.output_html.parent.mkdir(parents=True,exist_ok=True)
    args.output_html.write_text(rendered,encoding='utf-8')
    args.output_html.with_suffix('.audit.json').write_text(json.dumps(audit,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,sort_keys=True))

if __name__=='__main__':main()
