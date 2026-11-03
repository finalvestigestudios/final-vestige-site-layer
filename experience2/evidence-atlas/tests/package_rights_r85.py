#!/usr/bin/env python3
"""Deterministic, static R85 staging-review archive; never a deployable WordPress plugin."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[3]
LIST=(
    "experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json",
    "experience2/evidence-atlas/sources/R79_NASA_PAGE_AUDIT.json",
    "experience2/evidence-atlas/sources/NASA_PAGE_RIGHTS_AUDIT_R55.json",
    "experience2/evidence-atlas/tools/build_rights_board_r85.py",
    "experience2/evidence-atlas/tools/rights_board_r85.css",
    "experience2/evidence-atlas/tests/test_rights_board_r85.py",
    "experience2/evidence-atlas/tests/browser_rights_board_r85.py",
    "experience2/evidence-atlas/tests/package_rights_r85.py",
    "experience2/evidence-atlas/R85_NASA_RIGHTS_REVIEW_BOARD_STAGING_HOLD.md",
    ".github/workflows/ex2-apollo-r85-rights-board.yml",
)
BUILT=("R85_NASA_SOURCE_REVIEW.html","R85_RIGHTS_RECEIPT.json","rights_board_r85.css")

def package(out:Path,built:Path)->str:
    records={}
    for p in LIST:
        b=(ROOT/p).read_bytes()
        records["source/"+p]=b
    for name in BUILT:
        records["built/"+name]=(built/name).read_bytes()
    receipt=json.loads(records["built/R85_RIGHTS_RECEIPT.json"])
    assert receipt["release"]=="STAGING_HOLD" and receipt["rights_cleared"]==0
    assert receipt["images_embedded"]==receipt["geographic_pins"]==0
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in sorted(records.items())}
    records["MANIFEST_SHA256.json"]=(json.dumps({
        "schema":"fv.apollo.r85.review-archive.v1",
        "release":"STAGING_HOLD",
        "files_sha256":hashes,
        "not_a_deployable_plugin":True,
        "nasa_photo_rights_cleared":0,
    },sort_keys=True,indent=2)+"\n").encode("utf8")
    out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(records):
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.create_system=3
            info.external_attr=0o100644<<16
            z.writestr(info,records[name],compress_type=ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(out.read_bytes()).hexdigest()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--built",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print("R85 deterministic STAGING_HOLD ZIP sha256:",package(a.out,a.built))
