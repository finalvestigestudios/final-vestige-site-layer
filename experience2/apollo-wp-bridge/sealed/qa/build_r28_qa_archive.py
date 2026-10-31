#!/usr/bin/env python3
"""Reproducible offline Apollo R28 QA archive from verified R27 browser artifacts.

This does not generate or attest a PDF; it rejects any R27 PDF or PNG whose
bytes differ from the supplied original R27 signed-off (SHA-256) QA manifest.
It will not include credentials, WordPress data, or any third-party NASA image.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import zipfile

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
PDF_FILES = tuple(f'apollo-r26-custody-{w}.pdf' for w in WIDTHS)
PNG_FILES = ('apollo-r26-page1-390.png', 'apollo-r26-page1-1440.png')
SOURCE_FILES = ('pdf_binary_security_r28.py', 'test_pdf_binary_security_r28.py',
                'build_r28_qa_archive.py', 'requirements_pdf_binary_r28.txt',
                'R28_PDF_BINARY_RELEASE_HOLD.md')
ZIP_EPOCH = (2020, 1, 1, 0, 0, 0)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError('QA ARCHIVE HOLD: '+reason)


def make_archive(source_dir: Path, pdf_dir: Path, png_dir: Path, r27_manifest: Path,
                 report: Path, mutation_log: Path, out: Path) -> dict:
    provenance = json.loads(r27_manifest.read_text(encoding='utf-8'))
    require(provenance['pr'] == 352 and provenance['parent'] == '12ccf28b6a3cd32931cbe321fddff07b9c5cd4eb', 'Wrong R27 provenance manifest')
    inputs: dict[str, bytes] = {}
    for fname in SOURCE_FILES:
        inputs['source/' + fname] = (source_dir/fname).read_bytes()
    for fname in PDF_FILES + PNG_FILES:
        source = (pdf_dir if fname.endswith('.pdf') else png_dir)/fname
        data = source.read_bytes()
        origin = provenance['files']['qa/pdf/'+fname]
        require(sha256(data).hexdigest() == origin['sha256'] and len(data) == origin['bytes'], 'R27 artifact fingerprint drift: '+fname)
        inputs['evidence/r27/'+fname] = data
    audit = json.loads(report.read_text(encoding='utf-8'))
    require(audit['audited'] == 7 and len(audit['results']) == 7, 'Missing PDF binary audits')
    for w, entry in zip(WIDTHS, audit['results'], strict=True):
        actual = sha256((pdf_dir/f'apollo-r26-custody-{w}.pdf').read_bytes()).hexdigest()
        require(entry['pdf_sha256'] == actual and entry['status'] == 'PASS_OFFLINE_BINARY_SAFETY_ONLY', 'Audit receipt does not match PDF '+str(w))
    inputs['evidence/R28_7_PDF_BINARY_RESULTS.json'] = report.read_bytes()
    inputs['evidence/R28_MUTATION_UNIT_RESULTS.log'] = mutation_log.read_bytes()
    inputs['evidence/R27_SHA256_MANIFEST_ORIGINAL.json'] = r27_manifest.read_bytes()
    manifest = {
        'release_status': 'DRAFT_HOLD_NO_WORDPRESS_INSTALL',
        'r27_parent_pr': 352,
        'r27_head': 'b03881c3414988c736e9c0da78b3462ddb1d7123',
        'material_is': 'exact R27 Playwright-produced PDF/PNG files, independently audited by R28',
        'files': {name:{'sha256':sha256(blob).hexdigest(),'bytes':len(blob)} for name,blob in sorted(inputs.items())},
        'note': 'ZIP determinism means identical input bytes, not deterministic Chrome PDF regeneration or hosted compliance',
    }
    inputs['SHA256_MANIFEST.json'] = (json.dumps(manifest, indent=2,sort_keys=True)+'\n').encode('utf-8')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, payload in sorted(inputs.items()):
            info=zipfile.ZipInfo(name,date_time=ZIP_EPOCH)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            archive.writestr(info,payload,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(out) as archive:
        require(archive.testzip() is None and sorted(archive.namelist())==sorted(inputs), 'Bad QA archive content')
    return {'sha256':sha256(out.read_bytes()).hexdigest(), 'bytes':out.stat().st_size,
            'entries':len(inputs),'source_head':manifest['r27_head'],'release_status':'HOLD'}


def main():
    p=argparse.ArgumentParser()
    for key in ('source-dir','pdf-dir','png-dir','r27-manifest','report','mutation-log','out'):
        p.add_argument('--'+key,required=True,type=Path)
    v=vars(p.parse_args())
    print(json.dumps(make_archive(v['source_dir'],v['pdf_dir'],v['png_dir'],v['r27_manifest'],v['report'],v['mutation_log'],v['out']),indent=2))

if __name__=='__main__':main()
