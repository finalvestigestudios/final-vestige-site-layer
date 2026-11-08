"""Synthetic R219 gate tests; do not certify native build or source safety."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # local standalone replay
import r219_source_to_draft_chain as g


def example():
    originals = {
        7: (b'<p>Clean water requires evidence {{cite:cdc}} and guidance '
            b'to determine suitability {{cite:cdc2}} for specific hazards.</p>'),
        20: b'<p>Household preparation requires source review {{cite:ready}} before use.</p>',
    }
    rendered = {n: {c: (f'<p>{n}/{c} draft proof</p>').encode()
                    for c in ('wp', 'preview')} for n in (7, 20)}
    claims = []
    for n, sid in ((7, 'cdc'), (7, 'cdc2'), (20, 'ready')):
        raw = originals[n]
        marker = ('{{cite:' + sid + '}}').encode()
        start = raw.index(marker)
        visible = 'Synthetic citation review held ' + sid
        claims.append({'article': n, 'source_id': sid,
                       'source_url': 'https://example.org/' + sid,
                       'body_git_blob_sha1': g.blob(raw),
                       'citation_span_bytes': [start, start + len(marker)],
                       'claim_block_span_bytes': [0, len(raw)],
                       'raw_claim_block_sha256': g.digest(raw),
                       'visible_claim_text': visible,
                       'visible_claim_sha256': g.digest(visible.encode()),
                       'receipt_sha256': g.digest((str(n) + ':' + sid).encode()),
                       'human_source_claim_review': 'REQUIRED',
                       'editorial_decision': 'PENDING'})
    dossier = {'schema': 'fv-preparedness-r214-complete-claim-block-v1',
               'state': g.HOLD, 'errors': [], 'claims': claims,
               'human_claim_verified': False, 'medical_safety_verified': False,
               'independent_qd_pass': False, 'publication_authorized': False,
               'issue': 136, 'conversion_issue': 820}
    return dossier, originals, rendered


def fake_stages(originals, rendered, *, stage_tamper=None):
    r215 = {'schema': 'fv-preparedness-r215-wp-draft-transport-v1',
            'state': g.HOLD, 'errors': [],
            'human_source_claim_review': 'REQUIRED',
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'issue': 136, 'conversion_issue': 820,
            'articles': [{'article': n, 'original_blob_sha1': g.blob(originals[n]),
                          'citation_occurrences': 2 if n == 7 else 1,
                          'render_sha256': {c: g.digest(rendered[n][c]) for c in ('wp','preview')},
                          'source_review': 'REQUIRED'} for n in (7,20)]}
    pairs = list(g.TRANSPORTS)
    r216 = {'schema': 'fv-preparedness-r216-draft-exposure-v1',
            'state': g.HOLD, 'errors': [], 'source_claim_review': 'REQUIRED',
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'issue': 136, 'conversion_issue': 820,
            'transports': [{'article': n, 'channel': c, 'sha256': g.digest(rendered[n][c]),
                            'exposure_gate': g.HOLD} for n,c in pairs]}
    r217 = {'schema': 'fv-preparedness-r217-transport-semantics-v1',
            'state': g.HOLD, 'errors': [], 'source_claim_review': 'REQUIRED',
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'issue': 136, 'conversion_issue': 820,
            'transports': [{'article': n, 'channel': c, 'sha256': g.digest(rendered[n][c]),
                            'gate': g.HOLD, 'attributes_and_fragments_checked': True}
                           for n,c in pairs]}
    stage_reports = [r215,r216,r217]
    if stage_tamper:
        stage_tamper(stage_reports)
    return dict(zip(g.PINS, [SimpleNamespace(evaluate=lambda *args, r=r: copy.deepcopy(r))
                             for r in stage_reports]))


def go(dossier=None, originals=None, rendered=None, stage_tamper=None):
    base = example()
    d, o, r = [copy.deepcopy(v) for v in base]
    if dossier: dossier(d)
    if originals: originals(o)
    if rendered: rendered(r)
    return g.evaluate(d, o, r, stages=fake_stages(base[1], base[2], stage_tamper=stage_tamper))


class Baseline(unittest.TestCase):
    def test_all_stages_must_remain_hold(self):
        d,o,r = example()
        x = g.evaluate(d,o,r,stages=fake_stages(o,r))
        self.assertEqual(x['state'],g.HOLD)
        self.assertEqual(len(x['transports']),4)
        self.assertEqual(len(x['articles']),2)
        self.assertEqual(len(x['stages']),3)
        self.assertFalse(x['publication_authorized'])
        self.assertFalse(x['medical_safety_verified'])
        self.assertFalse(x['independent_qd_pass'])

    def test_default_does_not_trust_missing_stages(self):
        d,o,r=example()
        self.assertEqual(g.evaluate(d,o,r)['state'],g.INVALID)

    def test_strict_json_rejects_duplicate(self):
        with self.assertRaises(ValueError):g.strict_json(b'{"a":1,"a":2}')

    def test_strict_json_rejects_nan(self):
        with self.assertRaises(ValueError):g.strict_json(b'{"value":NaN}')

    def test_strict_json_rejects_array(self):
        with self.assertRaises(ValueError):g.strict_json(b'[]')

    def test_bad_source_directory(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):g.load_stages(Path(tmp))

    def test_file_as_stage_directory(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'file';path.write_text('x')
            with self.assertRaises(ValueError):g.load_stages(path)

    def test_symlink_stage_directory(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'alias';path.symlink_to(Path(tmp),target_is_directory=True)
            with self.assertRaises(ValueError):g.load_stages(path)

    def test_unguarded_source_reader_no_release(self):
        self.assertEqual(g.invalid('blocked')['state'],g.INVALID)

    def test_path_symlink(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'file').write_text('data')
            (root/'alias').symlink_to(root/'file')
            with self.assertRaises(ValueError):g._safe_read(root/'alias',root)

    def test_path_escape(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir()
            (Path(tmp)/'external').write_text('data')
            with self.assertRaises(ValueError):g._safe_read(Path(tmp)/'external',root)


class GeneratedMutations(unittest.TestCase):
    pass


def add_case(label, method):
    def run(self):
        result=method()
        self.assertEqual(result['state'],g.INVALID, label+' must be invalid')
        self.assertEqual(result['publication_authorized'],False)
    setattr(GeneratedMutations,'test_'+label,run)


for key in ('human_claim_verified','medical_safety_verified','independent_qd_pass','publication_authorized'):
    for bad in (True, None, 'false'):
        add_case('dossier_flag_'+key+'_'+repr(bad).replace("'",""),
                 lambda key=key,bad=bad:go(dossier=lambda d:d.__setitem__(key,bad)))

for key, bad in [('schema','wrong'),('state','PUBLISHED'),('errors',['false success']),
                 ('issue',0),('conversion_issue',-1),('claims',[]),('claims',[{}])]:
    add_case('dossier_field_'+key,
             lambda key=key,bad=bad:go(dossier=lambda d:d.__setitem__(key,bad)))

for article, idx in [(7,0),(7,1),(20,2)]:
    for key, bad in [('source_id','wrong'),('source_url','http://untrusted.test'),
                     ('body_git_blob_sha1','0'*40),('receipt_sha256','0'),
                     ('raw_claim_block_sha256','0'*64),('visible_claim_sha256','0'*64),
                     ('editorial_decision','APPROVED'),('human_source_claim_review','DONE'),
                     ('citation_span_bytes',[-1,2]),('claim_block_span_bytes',[0,1]),
                     ('visible_claim_text','replaced'),('citation_span_bytes',[0,0])]:
        add_case(f'claim_{article}_{idx}_{key}_{len(str(bad))}',
                 lambda idx=idx,key=key,bad=bad:go(dossier=lambda d:d['claims'][idx].__setitem__(key,bad)))

for article in (7,20):
    add_case(f'original_tamper_{article}',
             lambda article=article:go(originals=lambda o:o.__setitem__(article,o[article]+b'X')))
    add_case(f'original_empty_{article}',
             lambda article=article:go(originals=lambda o:o.__setitem__(article,b'')))
    for mode in ('wp','preview'):
        add_case(f'render_tamper_{article}_{mode}',
                 lambda article=article,mode=mode:go(rendered=lambda r:r[article].__setitem__(mode,r[article][mode]+b'x')))
        add_case(f'render_empty_{article}_{mode}',
                 lambda article=article,mode=mode:go(rendered=lambda r:r[article].__setitem__(mode,b'')))

for stage in range(3):
    for field in ('schema','state','errors','issue','conversion_issue','publication_authorized',
                  'independent_qd_pass','medical_safety_verified'):
        value={'schema':'wrong','state':'PUBLISHED','errors':['oops'],'issue':999,
               'conversion_issue':999,'publication_authorized':True,
               'independent_qd_pass':True,'medical_safety_verified':True}[field]
        add_case(f'stage_{stage}_{field}',
                 lambda stage=stage,field=field,value=value:go(
                     stage_tamper=lambda reports:reports[stage].__setitem__(field,value)))
    add_case(f'stage_{stage}_missing_transport',lambda stage=stage:go(stage_tamper=lambda reports:
        reports[stage]['articles' if stage==0 else 'transports'].pop()))
    add_case(f'stage_{stage}_reverse_order',lambda stage=stage:go(stage_tamper=lambda reports:
        reports[stage]['articles' if stage==0 else 'transports'].reverse()))

for stage in range(3):
    for n, mode in g.TRANSPORTS:
        def alter(rows, stage=stage,n=n,mode=mode):
            collection=rows[stage]['articles' if stage==0 else 'transports']
            if stage==0:
                row=next(x for x in collection if x['article']==n)
                row['render_sha256'][mode]='0'*64
            else:
                row=next(x for x in collection if x['article']==n and x['channel']==mode)
                row['sha256']='0'*64
        add_case(f'stage_{stage}_{n}_{mode}_hash',lambda alter=alter:go(stage_tamper=alter))

for stage,flag in [(0,'source_review'),(1,'exposure_gate'),(2,'gate'),(2,'attributes_and_fragments_checked')]:
    add_case(f'stage_{stage}_release_gate_{flag}',lambda stage=stage,flag=flag:go(
        stage_tamper=lambda rows:rows[stage]['articles' if stage==0 else 'transports'][0].__setitem__(flag,'PASS')))

if __name__=='__main__':unittest.main()
