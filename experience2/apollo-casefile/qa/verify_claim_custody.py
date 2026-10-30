#!/usr/bin/env python3
"""Source-custody contract: Board claims are distinct from image catalog metadata."""
from pathlib import Path
from urllib.parse import urlparse
import json,re
ROOT=Path(__file__).resolve().parents[1]
src=json.loads((ROOT/'records.json').read_text(encoding='utf8'))
audit=json.loads((ROOT/'custody.json').read_text(encoding='utf8'))
assert audit['board_report']==src['primary_report']
assert audit['usage_policy']==src['rights_policy']
assert len(audit['claims'])==len(src['records'])==6
assert [c['stage_id'] for c in audit['claims']]==[r['id'] for r in src['records']]
assert [c['category'] for c in audit['claims']].count('finding')==2
assert [c['category'] for c in audit['claims']].count('timing')==2
assert {c['category'] for c in audit['claims']}=={'finding','timing','uncertain','response'}
for c,r in zip(audit['claims'],src['records']):
    assert all(c[k] and len(c[k])>20 for k in ('claim','board_basis','image_basis','boundary','research_status'))
    assert r['rights'].startswith('link_only_')
    assert r['source_id'] in c['image_basis'] or c['stage_id']=='01'
    assert r['image_url'].startswith('https://www.nasa.gov/image-detail/')
    assert any(x in c['research_status'].lower() for x in ('pending','not cleared','not reproduced','not embedded'))
for row in src['atlas']:
    assert row['geometry'] is None and row['location_review']=='unverified'
    assert urlparse(row['url']).hostname=='finalvestige.com'
html=(ROOT/'index.html').read_text(encoding='utf8')
assert html.count('data-ex2-claim-item data-ex2-claim-category=')==6
assert len(re.findall(r'id="custody-\d{2}"',html))==6
assert 'data-ex2-claim-tools hidden' in html and 'id="claim-ledger"' in html
assert 'NASA does not endorse' in html
assert '<img' not in html.lower() and '<iframe' not in html.lower()
assert not re.search(r'data-(lat|long|geo)',html,re.I)
print('CLAIM_CUSTODY_CONTRACT_PASS 6 claims / 6 image records / no fake coordinates')
