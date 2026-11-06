"""R175: review-gated correction of Research Desk's unverified NASA image ID.

Adds no links, network calls, scripts or commerce. The source SHA is R174's
unpublished GitHub candidate. Designed for local staging assembly ONLY.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

PINNED_BLOB = 'b23879150024b3b667679ff4dd7faae1e37cfc07'
ORIGINAL = '<div class="fv-ex2-ledger__recordid">NASA S67-19766 · NASA</div>'
REPLACEMENT = (
    '<div class="fv-ex2-ledger__recordid" data-fvx-r175-catalog-review="unverified">'
    'NASA crew-training photograph'
    '<span class="fv-ex2-catalog-warning">Reported catalog ID: S67-19766. '
    'Not verified on the linked NASA archive record.</span></div>'
)
PROVENANCE = 'data-fvx-r174-media-custody="01"'
FIRST_RECORD = 'id="fv-ex2-ledger-apollo1-record-01"'
LINKS = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>', re.I)

def blob(s: str) -> str:
    data = s.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def sha(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def rewrite(source: str, *, expected_blob: str = PINNED_BLOB) -> tuple[str, dict]:
    """Always require exact source match; fixtures may supply their own test digest."""
    if blob(source) != expected_blob:
        raise ValueError('STAGING HOLD: unexpected R174 source Git blob')
    if source.count(FIRST_RECORD) != 1 or source.count(PROVENANCE) != 1:
        raise ValueError('STAGING HOLD: missing/ambiguous record 01 provenance')
    if source.count(ORIGINAL) != 1 or 'data-fvx-r175-catalog-review' in source:
        raise ValueError('STAGING HOLD: unverified ID label missing or already changed')
    start = source.index(FIRST_RECORD)
    end = source.find('</article>', start)
    if end < 0 or not(start < source.index(ORIGINAL) < end):
        raise ValueError('STAGING HOLD: original ID not in card 01')
    section = source[start:end]
    if PROVENANCE not in section or 'Catalog ID not established on linked NASA page' not in section:
        raise ValueError('STAGING HOLD: NASA uncertainty finding absent')
    if 'href="https://www.nasa.gov/image-detail/apollo-1-crew-honored/"' not in section:
        raise ValueError('STAGING HOLD: original NASA image source missing')
    if source.count('data-fvx-r174-media-custody=') != 6 or source.count('data-fvx-record') < 6:
        raise ValueError('STAGING HOLD: six-source ledger incomplete')
    links = LINKS.findall(source)
    result = source.replace(ORIGINAL, REPLACEMENT, 1)
    if LINKS.findall(result) != links or result.replace(REPLACEMENT, ORIGINAL, 1) != source:
        raise ValueError('STAGING HOLD: source links or historical narrative changed')
    if result.count('data-fvx-r175-catalog-review') != 1 or len(result) <= len(source):
        raise ValueError('STAGING HOLD: correction missing')
    return result, {
      'status':'BUILT_NOT_INSTALLED', 'base_blob':blob(source),
      'candidate_sha256':sha(result), 'source_sha256':sha(source),
      'change':'Record 01 visible NASA catalog identifier qualified as unverified',
      'records_preserved':6, 'links_preserved':len(links), 'links_added':0,
      'scripts_added':0, 'source_roundtrip':True, 'media_rights_cleared':False,
      'staging_accepted':False, 'production_modified':False,
      'revenue_verified':False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('r174_html',type=Path)
    p.add_argument('output_html',type=Path)
    a=p.parse_args()
    out, receipt = rewrite(a.r174_html.read_text(encoding='utf-8'))
    a.output_html.parent.mkdir(parents=True,exist_ok=True)
    a.output_html.write_text(out,encoding='utf-8')
    a.output_html.with_suffix('.audit.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
