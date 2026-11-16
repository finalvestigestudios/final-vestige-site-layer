#!/usr/bin/env python3
"""Deterministic offline fixture-only R400 QA evidence bundle; never staging proof."""
from pathlib import Path
import hashlib, json, zipfile

HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'QA'
FILES=[HERE/'README.md',HERE/'qa/staging_browser_gate.py',HERE/'qa/test_gate.py',
       HERE/'qa/performance_probe.py',HERE/'qa/pack_evidence.py'] + sorted(OUT.glob('*.png')) + [OUT/'report.json',OUT/'lab-performance.json']
ZIP=OUT/'Apollo_R400_Local_Evidence.zip'
MANIFEST=OUT/'MANIFEST.json'

def package():
    for item in FILES:
        if not item.is_file():raise RuntimeError('missing evidence '+str(item))
    listing={item.relative_to(HERE).as_posix():hashlib.sha256(item.read_bytes()).hexdigest() for item in FILES}
    manifest={'scope':'LOCAL_EQUIVALENT_RUNNER_NOT_INSTALLED_STAGING','live_or_merchant_verified':False,
              'github_exact_head_runner_executed':False,
              'github_exact_blob_local_matches':{'qa/performance_probe.py':True,
                  'qa/staging_browser_gate.py':False,'qa/test_gate.py':False,'README.md':False},
              'git_remote_blobs':{'qa/staging_browser_gate.py':'e06d61a2ef2ad627f40eeed05dd79a6621dbb9c2',
                  'qa/test_gate.py':'05ae9fd35a464ba6584b1a2c782d4891a902a5bf',
                  'qa/performance_probe.py':'037c73b047dbbf7db39fb47241a3e2189687e1c3',
                  'README.md':'871bf50d8ae973b421d70ff07e5954e6f3afbf2a'},
              'sha256':listing}
    MANIFEST.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for item in sorted(FILES+[MANIFEST],key=lambda x:x.relative_to(HERE).as_posix()):
            zi=zipfile.ZipInfo('apollo-r400/'+item.relative_to(HERE).as_posix(),date_time=(2020,1,1,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=0o100644<<16
            z.writestr(zi,item.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(ZIP.read_bytes()).hexdigest(),len(FILES)+1
if __name__=='__main__':print('R400_LOCAL_ZIP_SHA256,ENTRIES',*package())
