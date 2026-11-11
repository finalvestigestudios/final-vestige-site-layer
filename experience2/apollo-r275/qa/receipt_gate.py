#!/usr/bin/env python3
"""Deterministic negative-control regression for integrity-only receipts."""
import copy
import hashlib
import importlib.util
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

script = Path(__file__).resolve().parents[1] / 'receipt_custody.py'
spec = importlib.util.spec_from_file_location('fv_receipt_custody', script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def expect(condition, label):
    assert condition, label
    print('PASS', label)

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    for name in ('board.txt', 'chronology.txt'):
        (root / name).write_text('Fixture-only source review metadata for ' + name + '\n')
    records = []
    for rid, name in [('board', 'board.txt'), ('chronology', 'chronology.txt')]:
        records.append({'record_id':rid,'source_url':module.SOURCE,'reviewer':'Fixture editor (NOT AUTHENTICATED)',
            'review_date':'2026-11-10','evidence_file':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest()})
    base={'version':1,'records':records}
    asof=date(2026,11,10)
    def checked(m): return module.inspect(m, root, asof)
    good=checked(base)
    expect(good['result']=='INTEGRITY_ONLY_PASS', '2 distinct receipt file digests pass integrity only')
    expect(all(good[k] is False for k in ('editorial_verified','release_authorized','media_rights_cleared')), 'receipt integrity never grants editorial/rights/release approval')
    expect(good['source_independence']=='SHARED_NASA_REPORT','shared NASA primary source is disclosed')
    def fail(mod,label):
        m=copy.deepcopy(base);mod(m)
        expect(checked(m)['result']=='FAIL',label)
    fail(lambda m:m['records'][0].update(sha256='0'*64),'digest forgery blocked')
    fail(lambda m:m['records'][0].update(source_url='https://example.com'),'unrecognized source blocked')
    fail(lambda m:m['records'][0].update(review_date='2026-11-11'),'future dated receipt blocked')
    fail(lambda m:m['records'][0].update(review_date='2026-02-30'),'impossible dated receipt blocked')
    fail(lambda m:m['records'][0].update(evidence_file='../escape'),'path traversal blocked')
    fail(lambda m:m['records'][0].update(evidence_file='chronology.txt'),'duplicate evidence-file reuse blocked')
    fail(lambda m:m['records'][0].update(record_id='chronology'),'duplicate record id blocked')
    fail(lambda m:m.update(approved=True),'unapproved schema/approval flag blocked')
    fail(lambda m:m['records'][0].update(approved=True),'unapproved per-record flag blocked')
    fail(lambda m:m['records'].pop(),'missing review record blocked')
    (root/'evil.txt').symlink_to(root/'board.txt')
    fail(lambda m:m['records'][0].update(evidence_file='evil.txt'),'symlinked evidence rejected')
    fail(lambda m:m['records'][0].update(reviewer=''), 'blank reviewer metadata rejected')
    print('R275 receipt integrity tests: 15/15 PASS')
