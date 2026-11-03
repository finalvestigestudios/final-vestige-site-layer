#!/usr/bin/env python3
"""Deterministic, SHA256-manifested R87 offline review ZIP; NEVER deployable."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
ROOT=Path(__file__).resolve().parents[3]
SOURCE=[
 'experience2/evidence-atlas/tools/build_claim_boundary_r87.py',
 'experience2/evidence-atlas/tools/claim_boundary_r87.css',
 'experience2/evidence-atlas/tests/test_claim_boundary_r87.py',
 'experience2/evidence-atlas/tests/browser_claim_boundary_r87.py',
 'experience2/evidence-atlas/tests/package_claim_boundary_r87.py',
 'experience2/evidence-atlas/R87_CLAIM_PHOTO_BOUNDARY_STAGING_HOLD.md',
 '.github/workflows/ex2-apollo-r87-claim-boundary.yml',
 'experience2/evidence-atlas/tools/build_concordance_r86.py',
 'experience2/evidence-atlas/tools/build_rights_board_r85.py',
 'experience2/research-desk/templates/ledger.html',
 'experience2/evidence-atlas/build_atlas.py',
 'experience2/evidence-atlas/atlas.css',
 'experience2/evidence-atlas/atlas.js',
 'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
 'experience2/evidence-atlas/sources/R79_NASA_PAGE_AUDIT.json',
 'experience2/evidence-atlas/sources/NASA_PAGE_RIGHTS_AUDIT_R55.json',
]
BUILT=['R87_CLAIM_PHOTO_BOUNDARY.html','claim_boundary_r87.css','R87_RECEIPT.json']
def package(built,out):
    content={'source/'+p:(ROOT/p).read_bytes() for p in SOURCE}
    content.update({'built/'+name:(built/name).read_bytes() for name in BUILT})
    receipt=json.loads(content['built/R87_RECEIPT.json'])
    assert receipt['release']=='STAGING_HOLD' and receipt['image_reuse_cleared']==0
    assert receipt['published'] is False and receipt['record_count']==6
    content['SHA256_MANIFEST.json']=(json.dumps({'schema':'fv.apollo.r87.deterministic-source.v1',
       'release':'STAGING_HOLD','not_deployable':True,
       'files_sha256':{p:hashlib.sha256(b).hexdigest() for p,b in sorted(content.items())}},
       sort_keys=True,indent=2)+'\n').encode()
    out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for path,raw in sorted(content.items()):
            item=ZipInfo(path,date_time=(1980,1,1,0,0,0));item.create_system=3
            item.external_attr=0o100644<<16;item.compress_type=ZIP_DEFLATED
            z.writestr(item,raw,compress_type=ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(out.read_bytes()).hexdigest()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--built',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print('R87 SHA256',package(a.built,a.out))
