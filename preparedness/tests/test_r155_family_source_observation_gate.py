"""Purely synthetic and adversarial tests; no live network/CMS/merchant or QD approval."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MOD = Path(__file__).with_name('r155_family_source_observation_gate.py')
spec = importlib.util.spec_from_file_location('r155_gate', MOD)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
REFERENCE = json.loads(Path(__file__).parents[1].joinpath('docs/r155/family-source-observations.json').read_text())


def fixture():
    rows = []
    for n, item in enumerate(REFERENCE['observations']):
        rows.append({'tool':gate.FAMILY,'source_id':item['source_id'],
                     'literal_url':item['source_url'],'citation_occurrences':2 if n<5 else 1,
                     'review_decision':'PENDING','reviewer':None,
                     'human_link_check_recorded':False,
                     'human_source_scope_adjudicated':False,'medical_safety_approved':False,
                     'author_specific_use':'Specific interpretation requiring review',
                     'source_supports':'Original publisher supporting evidence summary'})
    for n in range(56):
        rows.append({'tool':'other-tool','source_id':f'other-{n}',
                     'citation_occurrences':102 if n==0 else 1})
    doc={'schema':'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1','publication_allowed':False,
         'independent_qd':'NOT_APPROVED','source_scope_human_review':'PENDING',
         'human_link_checked_rows':0,'payment_offer_verified':False,
         'source_use_row_count':67,'currently_unresolved_source_ids':58,
         'source_use_rows':rows}
    # 5*2 + 6*1 = 16; 102+55 = 157; total=173.
    assert sum(r['citation_occurrences'] for r in rows)==173
    return doc,copy.deepcopy(REFERENCE)


class Adversarial(unittest.TestCase):
    def test_valid_observations_are_still_hard_hold(self):
        report=gate.inspect(*fixture())
        self.assertEqual(report['status'],'DRAFT_HARD_HOLD')
        self.assertEqual((report['source_relationships'],report['citation_occurrences']),(11,16))
        self.assertEqual((report['text_accessible_limited_claim_match'],report['source_scope_flags'],report['retrieval_blocked_not_link_dead']),(3,2,6))
        for key in ('qualified_source_review','medical_safety_approval','independent_qd_pass','publish_allowed','paid_offer_verified'):
            self.assertIs(report[key],False)
    def test_gate_exits_hard_hold_with_invalid_repo(self):
        with tempfile.TemporaryDirectory() as path:
            self.assertEqual(gate.main(['--repo',path]),2)
    def test_git_blob_roundtrip(self):
        self.assertEqual(gate.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); f=root/'source';f.write_text('ok');(root/'link').symlink_to(f)
            with self.assertRaises(ValueError):gate.frozen_bytes(root,'link',gate.git_blob(b'ok'))
    def test_sha_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'source').write_text('bad')
            with self.assertRaises(ValueError):gate.frozen_bytes(root,'source',gate.git_blob(b'ok'))
    def test_undisclosed_new_field_rejected(self):
        a,b=fixture();b['publisher_approved']=True
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_changed_snapshot_date_rejected(self):
        a,b=fixture();b['observed_date']='2026-11-06'
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_false_approval_rejected(self):
        a,b=fixture();b['source_approval']=True
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_false_merchant_verification_rejected(self):
        a,b=fixture();b['commercial_offer_verified']=True
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_missing_family_row_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['tool']='other-tool'
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_missing_all_source_relationships_rejected(self):
        a,b=fixture();a['source_use_rows']=[]
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_citation_occurrence_loss_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['citation_occurrences']=1
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_original_source_claim_missing_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['source_supports']=''
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_original_author_claim_missing_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['author_specific_use']=''
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_html_injected_note_rejected(self):
        a,b=fixture();b['observations'][0]['observation']='<script>example code injection</script>'
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_duplicate_observation_rejected(self):
        a,b=fixture();b['observations'][0]=copy.deepcopy(b['observations'][1])
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_missing_observation_rejected(self):
        a,b=fixture();b['observations'].pop()
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_observation_extra_field_rejected(self):
        a,b=fixture();b['observations'][0]['human_safety_pass']=True
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_source_review_state_change_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['review_decision']='APPROVED'
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_human_link_claim_rejected(self):
        a,b=fixture();a['source_use_rows'][0]['human_link_check_recorded']=True
        with self.assertRaises(ValueError):gate.inspect(a,b)
    def test_report_path_untouched_on_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); out=root/'report.json'
            self.assertEqual(gate.main(['--repo',d,'--report',str(out)]),2)
            self.assertFalse(out.exists())


def add_source_mutation_tests():
    # Each named test independently targets one of the eleven original source identities.
    # 44 methods cover origin substitutions, access claims, scope claims, and forged approval.
    for idx,row in enumerate(REFERENCE['observations']):
        sid=row['source_id'].replace('-','_')
        for kind in ('url','access','scope','approval'):
            def check(self,idx=idx,kind=kind):
                docket,obs=fixture()
                r=obs['observations'][idx]
                if kind=='url':r['source_url']='https://example.org/unrelated-source'
                elif kind=='access':r['access']=('RETRIEVAL_BLOCKED' if r['access']=='RETRIEVED_TEXT' else 'RETRIEVED_TEXT')
                elif kind=='scope':r['scope']='CLAIM_MATCH_OBSERVED' if r['scope']!='CLAIM_MATCH_OBSERVED' else 'NOT_OBSERVABLE'
                else:r['human_link_checked']=True
                with self.assertRaises(ValueError): gate.inspect(docket,obs)
            setattr(Adversarial,f'test_{kind}_mutation_{sid}',check)

add_source_mutation_tests()

if __name__ == '__main__':
    unittest.main(verbosity=2)
