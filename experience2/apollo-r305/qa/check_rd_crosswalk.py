#!/usr/bin/env python3
"""R305 deterministic custody validator. Research Desk media are not historical claim proof."""
import copy, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=Path(__file__).resolve().parents[1]/'RESEARCH_DESK_HANDOFF.json'
ATLAS=(ROOT/'apollo-r281/apollo-source-experience.php').read_text()
EXPECTED=['S67-19766','S67-15717','S66-58038','KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090']

def valid(doc):
    rows=doc.get('archive_records',[])
    if len(rows)!=6 or [r.get('id') for r in rows]!=EXPECTED: return False
    for row in rows:
        if set(row)!=set(['id','url','role','claim_support','image_rights']): return False
        if row['role']!='contextual-photo-record' or row['claim_support']!='not-primary-claim-proof' or row['image_rights']!='not-cleared': return False
        if not re.fullmatch(r'https://www\.nasa\.gov/image-detail/[a-z0-9_\-]+/',row['url']): return False
    return True

doc=json.loads(MANIFEST.read_text())
assert valid(doc)
assert doc['source_blob_sha1']=='403d128c57b9bc82dac7c619651689070edef86c'
assert 'data-fv-evidence-role="documented-textual-claim"' in ATLAS
assert all(r['url'] not in ATLAS and r['id'] not in ATLAS for r in doc['archive_records'])
mutations=0
for i in range(6):
    for key,value in [('role','causal-evidence'),('claim_support','verified-ignition-source'),('image_rights','approved'),('url','https://tracker.example.org/a/')]:
        tampered=copy.deepcopy(doc)
        tampered['archive_records'][i][key]=value
        assert not valid(tampered)
        mutations+=1
print(json.dumps({'manifest_records':6,'misattributed_photo_controls_rejected':mutations,'atlas_photo_links':0,'media_licensing':'NOT CLEARED','research_desk_pr':'UNCHANGED'}))
