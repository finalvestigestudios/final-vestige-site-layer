"""R393 adversarial fixture-only tests; these do not establish native source safety."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r393_cross_gate_witness.py'
spec = importlib.util.spec_from_file_location('r393_cross_gate_witness', P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
HEX, DIG = 'a'*40, 'b'*64


def fixture():
    slugs=[f'guide-{i:02d}' for i in range(35)]
    allslugs=slugs+[f'page-{i:02d}' for i in range(15)]
    candidates=lambda: [{'branch':'claude/prep-original','body_sha':HEX}]
    packet={'status':'REVIEW_PACKET_HARD_HOLD','release':'DRAFT_HARD_HOLD',
            'publication_approved':False,'qualified_safety_approved':False,'errors':[],
            'articles':[{'slug':s,'variants':candidates()} for s in slugs],
            'unselected_conflicts':[{'path':f'fork-{i}'} for i in range(9)]}
    render={'status':'RENDER_PARITY_REVIEW_HARD_HOLD','publication_approved':False,
            'qualified_safety_approved':False,'errors':[],
            'articles':[{'slug':s,'matching_variant_candidates':candidates()} for s in slugs]}
    anchor={'status':'CLAIM_POSITION_REVIEW_HARD_HOLD','publication_approved':False,
            'qualified_safety_approved':False,'errors':[],
            'articles':[{'slug':s,'matching_original_candidates':candidates()} for s in slugs]}
    full={'status':'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD','publication_approved':False,
          'qualified_safety_approved':False,'errors':[],
          'exports':[{'slug':s,'wp_sha256':DIG,'preview_sha256':DIG,'wp_bytes':99,
                      'preview_bytes':100,'errors':[],'release_allowed':False,
                      'qualified_review_required':True} for s in allslugs]}
    frozen={'status':'FROZEN_EXPORT_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
            'publication_approved':False,'qualified_safety_approved':False,'errors':[],
            'snapshot_sha256':DIG,'matched_snapshot_pairs':50,
            'reports':{'render':render,'anchor':anchor,'full':full}}
    integrated={'status':'INTEGRATED_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
                'publication_approved':False,'qualified_safety_approved':False,'errors':[],
                'counts':{'original_articles':35,'unselected_manuscript_forks':9,
                          'unselected_source_collisions':5,'wp_exports':50,
                          'private_previews':50,'candidate_intersection_articles':35},
                'candidate_intersections':[{'slug':s,'matching_review_candidates':candidates(),
                                            'auto_selected':False,'qualified_review_required':True} for s in slugs]}
    return packet,integrated,frozen


def mutations():
    return [
        lambda p,i,f:p.update(status='PASS'),
        lambda p,i,f:p.update(publication_approved=True),
        lambda p,i,f:p.update(qualified_safety_approved=True),
        lambda p,i,f:p.update(release='LIVE'),
        lambda p,i,f:p['articles'].pop(),
        lambda p,i,f:p['articles'].append(copy.deepcopy(p['articles'][0])),
        lambda p,i,f:p['articles'][0].update(slug='../escape'),
        lambda p,i,f:p['articles'][0].update(variants=[]),
        lambda p,i,f:p['articles'][0]['variants'][0].update(body_sha='z'*40),
        lambda p,i,f:p['articles'][0]['variants'].append(copy.deepcopy(p['articles'][0]['variants'][0])),
        lambda p,i,f:p['unselected_conflicts'].pop(),
        lambda p,i,f:p['unselected_conflicts'][0].update(selected_sha=HEX),
        lambda p,i,f:i.update(status='PASS'),
        lambda p,i,f:i.update(publication_approved=True),
        lambda p,i,f:i.update(qualified_safety_approved=True),
        lambda p,i,f:i.update(release_state='LIVE'),
        lambda p,i,f:i['counts'].update(original_articles=34),
        lambda p,i,f:i['counts'].update(unselected_manuscript_forks=8),
        lambda p,i,f:i['counts'].update(unselected_source_collisions=4),
        lambda p,i,f:i['counts'].update(wp_exports=49),
        lambda p,i,f:i['counts'].update(private_previews=49),
        lambda p,i,f:i['counts'].update(candidate_intersection_articles=34),
        lambda p,i,f:i['candidate_intersections'].pop(),
        lambda p,i,f:i['candidate_intersections'].append(copy.deepcopy(i['candidate_intersections'][0])),
        lambda p,i,f:i['candidate_intersections'][0].update(auto_selected=True),
        lambda p,i,f:i['candidate_intersections'][0].update(qualified_review_required=False),
        lambda p,i,f:i['candidate_intersections'][0].update(matching_review_candidates=[]),
        lambda p,i,f:i['candidate_intersections'][0]['matching_review_candidates'][0].update(body_sha='z'*40),
        lambda p,i,f:f.update(status='PASS'),
        lambda p,i,f:f.update(snapshot_sha256='x'*64),
        lambda p,i,f:f.update(release_state='LIVE'),
        lambda p,i,f:f.update(matched_snapshot_pairs=49),
        lambda p,i,f:f.update(reports={}),
        lambda p,i,f:f['reports']['render'].update(status='PASS'),
        lambda p,i,f:f['reports']['anchor'].update(errors=['missing citation']),
        lambda p,i,f:f['reports']['full'].update(publication_approved=True),
        lambda p,i,f:f['reports']['render']['articles'].pop(),
        lambda p,i,f:f['reports']['anchor']['articles'].pop(),
        lambda p,i,f:f['reports']['render']['articles'][0].update(matching_variant_candidates=[]),
        lambda p,i,f:f['reports']['anchor']['articles'][0].update(matching_original_candidates=[]),
        lambda p,i,f:f['reports']['render']['articles'][0]['matching_variant_candidates'][0].update(body_sha='z'*40),
        lambda p,i,f:f['reports']['full']['exports'].pop(),
        lambda p,i,f:f['reports']['full']['exports'].append(copy.deepcopy(f['reports']['full']['exports'][0])),
        lambda p,i,f:f['reports']['full']['exports'][0].update(slug='bad/slug'),
        lambda p,i,f:f['reports']['full']['exports'][0].update(wp_sha256='invalid'),
        lambda p,i,f:f['reports']['full']['exports'][0].update(preview_sha256='invalid'),
        lambda p,i,f:f['reports']['full']['exports'][0].update(wp_bytes=True),
        lambda p,i,f:f['reports']['full']['exports'][0].update(preview_bytes=0),
        lambda p,i,f:f['reports']['full']['exports'][0].update(release_allowed=True),
        lambda p,i,f:f['reports']['full']['exports'][0].update(qualified_review_required=False),
    ]

class TestR393(unittest.TestCase):
    def test_good_fixture_remains_hard_hold(self):
        result=mod.check(*fixture())
        self.assertEqual(result['status'],'CROSS_GATE_WITNESS_REVIEW_HARD_HOLD')
        self.assertFalse(result['publication_approved'])
        self.assertEqual(result['article_count'],35)
    def test_stable_evidence_digest(self):
        self.assertEqual(mod.check(*fixture())['witness_sha256'], mod.check(*fixture())['witness_sha256'])
    def test_missing_files_never_exit_zero(self):
        self.assertEqual(mod.main(['--original','/missing','--integrated','/missing','--frozen','/missing']),2)
    def test_malformed_parents(self):
        for n in range(3):
            with self.subTest(n=n):
                x=list(fixture()); x[n]=None
                self.assertEqual(mod.check(*x)['status'],'INVALID_HARD_HOLD')


def _make_case(idx):
    def _case(self):
        packet,integrated,frozen=fixture()
        mutations()[idx](packet,integrated,frozen)
        result=mod.check(packet,integrated,frozen)
        self.assertEqual(result['status'],'INVALID_HARD_HOLD',str(idx))
        self.assertFalse(result['publication_approved'])
    return _case

for _index in range(len(mutations())):
    setattr(TestR393,f'test_mutation_{_index:02d}',_make_case(_index))

if __name__=='__main__':unittest.main()
