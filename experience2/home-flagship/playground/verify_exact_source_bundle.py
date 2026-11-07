#!/usr/bin/env python3
"""EX2 release review: reject stale evidence files, then retain mandatory staging HOLD.

Run: python3 experience2/home-flagship/playground/verify_exact_source_bundle.py
Optional: --source-dir DIR --out receipt.json --selftest
No HTTP, CMS, affiliate, subscriber, filesystem writes outside --out.
Exit 1 = missing/stale source; 2 = source-custody PASS but release HOLD.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

# Source files observed at immutable parent PR #1351 commit
# 6bad43a36d7473f1061adb25bb9f63e15710f4a7 on 2026-11-07 UTC.
EXPECTED = {
  'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json':'137c74a476005684a28f5ff9a36e75c6b03268f7',
  'LIVE_PAGE6_PUBLIC_MANIFEST_20261107.json':'8fea74a220dd3a8186fe7c1a210b7ad1eeb977ef',
  'make_private_playground_launcher.py':'cd6abf7044c6e66f78b7a26e76cff2d76479f643',
  'verify_private_playground_bridge.py':'bde15fb9b8f851cc033ef00717253f66e6e61f9d',
  'test_verify_private_playground_bridge.py':'c002c0c7a15f2704c6fc1e155fc570836e12f467',
  'verify_anchor_clearance_browser.py':'925e5f56e92ad9bd4d3b8f3a47aa8f21cade4cd1',
  'verify_php_shortcode_execution.py':'7739caca6fa11515f94cfefcfc0620188c6f26f8',
  'verify_integrated_playground.py':'e61acd0cbbbe36f8ec8cdebe2bb1b77c7aa5aeb6',
  'test_verify_archival_provenance.py':'6450a77e0197b861e3cb937c36de25a787e063bd',
  'verify_archival_provenance.py':'f55049ce88254bd855e98a95e1c43eeed98b33de',
  'verify_flagship_fullpage_review.py':'e9b509e21cbe0d5a3a420a3d50090c06f9ee9a68',
  'verify_live_candidate_divergence.py':'90cac71df8cdd2c1a4a0efea5edc3f7c3315d90d',
  'test_verify_live_candidate_divergence.py':'00a1c140b6334e512566983c68efe802b847aded',
}

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def scan(root, expected=EXPECTED):
    files=[]
    for name,pin in expected.items():
        path=root/name
        if path.is_file():
            raw=path.read_bytes();got=git_blob(raw)
            files.append({'file':name,'expected_blob':pin,'actual_blob':got,
                          'bytes':len(raw),'status':'MATCH' if got==pin else 'MISMATCH'})
        else:
            files.append({'file':name,'expected_blob':pin,'actual_blob':None,
                          'status':'MISSING'})
    verified=all(f['status']=='MATCH' for f in files)
    return {'parent_pr':1351,'parent_commit':'6bad43a36d7473f1061adb25bb9f63e15710f4a7',
            'file_count':len(files),'match_count':sum(f['status']=='MATCH' for f in files),
            'files':files,'source_custody':'PASS' if verified else 'FAIL',
            'wordpress_assembler':'NOT_TESTED','real_image_bytes':'NOT_TESTED',
            'axe_wcag_2_2_aa':'NOT_TESTED','lighthouse_cwv':'NOT_TESTED',
            'jetpack_confirmed_signup':'NOT_TESTED','ci_qd':'NOT_VERIFIED',
            'founder_release_approval':'NOT_GRANTED','release_decision':'HOLD'}

def selftest():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        root=Path(d);p=root/'sample';p.write_bytes(b'approved')
        pin=git_blob(b'approved')
        assert scan(root,{'sample':pin})['source_custody']=='PASS'
        p.write_bytes(b'altared')
        assert scan(root,{'sample':pin})['source_custody']=='FAIL'
        p.unlink()
        assert scan(root,{'sample':pin})['source_custody']=='FAIL'
        assert len(EXPECTED)==len(set(EXPECTED))==13
    print('PASS: 4 source-custody controls')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--selftest',action='store_true')
    args=ap.parse_args()
    if args.selftest:
        selftest();return 0
    report=scan(args.source_dir)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'custody':report['source_custody'],'exact_files':report['match_count'],
                      'required':report['file_count'],'release_decision':'HOLD',
                      'differences':[f['file'] for f in report['files'] if f['status']!='MATCH']},indent=2))
    return 2 if report['source_custody']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
