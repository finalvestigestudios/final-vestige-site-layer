#!/usr/bin/env python3
"""Deterministic QA receipt archive; fixed order, compression and timestamps."""
import hashlib, json, pathlib, zipfile
HERE = pathlib.Path(__file__).resolve().parents[1]
FILES = [
 'qa/bootstrap_exact_sources.py', 'qa/test_bootstrap.py', 'qa/package_evidence.py',
 'QA/bootstrap_receipt.json', 'QA/unit_test_output.txt',
 'QA/remote_source_receipt.json', 'QA/qa_boundary.md'
]

def make_archive(output: pathlib.Path) -> str:
    sources = {}
    for path in FILES:
        data=(HERE/path).read_bytes()
        sources[path]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    manifest=json.dumps({'files':sources,'mode':'read-only source bootstrap QA','release':'HARD_HOLD'},sort_keys=True,indent=2).encode()+b'\n'
    with zipfile.ZipFile(output,'w') as z:
        for path,data in sorted([(path,(HERE/path).read_bytes()) for path in FILES]+[('MANIFEST.json',manifest)]):
            info=zipfile.ZipInfo(path,(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest()

if __name__=='__main__':
    out=HERE/'QA/Apollo_R425_Local_Evidence.zip'
    print(make_archive(out))
