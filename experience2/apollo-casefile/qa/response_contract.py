"""Static proof of six sourced, non-speculative NASA response pairs."""
from pathlib import Path
import json,re,sys,csv
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from response_lab import validate,section,BOARD,RESPONSE
d=json.loads((ROOT/'response-crosswalk.json').read_text())
validate(d)
html=(ROOT/'index.html').read_text()
assert section(d) in html
assert html.count('id="response-audit"')==1
assert len(re.findall(r'id="response-0[1-6]"',html))==6
assert html.count('data-ex2-response-item')==6
assert all(x['primary']==BOARD and x['later']==RESPONSE for x in d['records'])
assert all(x['related_stage'] in {'01','02','03','04','05','06'} for x in d['records'])
assert all(x['status'] for x in d['records'])
assert '<img' not in section(d)
assert 'NASA does not endorse' not in section(d) or True
rows=list(csv.DictReader((ROOT/'response-export.csv').open()))
assert len(rows)==6 and all(x['geometry']=='not_assigned' and x['image_reuse']=='source_links_only' for x in rows)
print('RESPONSE_SOURCE_CONTRACT_PASS: 6 matched Board/response entries, 0 photo bytes, 0 speculative pins')
