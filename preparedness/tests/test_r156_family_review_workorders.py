"""Synthetic adversarial tests. No external fetches, user data, or QD authorization."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).parents[1] / 'tools' / 'r156_family_review_workorders.py'
spec = importlib.util.spec_from_file_location('r156_review', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    rows = []
    observed = []
    task_rows = []
    for n, (sid, (access, scope)) in enumerate(gate.EXPECTED.items()):
        url = 'https://example.gov/source/' + sid
        citation_count = 2 if n < 5 else 1
        rows.append({'source_id': sid, 'citation_occurrences': citation_count, 'url': url,
                     'observed_access': access, 'observed_scope': scope,
                     'independent_review': False, 'human_link_verified': False,
                     'publication_allowed': False})
        observed.append({'source_id': sid, 'source_url': url, 'access': access, 'scope': scope,
                         'observation': 'Synthetic observation, not actual safety evidence.',
                         'review_state': 'PENDING', 'human_link_checked': False,
                         'qualified_safety_review': False})
        task_rows.append({'task_fingerprint': hashlib.sha256(sid.encode()).hexdigest(),
                          'original_identity': gate.FAMILY + '/' + sid,
                          'review_lane': 'FAMILY_REUNIFICATION_SOURCE_AND_PRIVACY',
                          'priority': 1, 'note_status': 'NO_NOTE', 'reviewer_note': None,
                          'evidence_urls_unverified': [], 'source_url': url,
                          'qualified_source_review': False,
                          'medical_or_food_safety_approved': False, 'publication_allowed': False})
    for i in range(64):
        task_rows.append({'task_fingerprint': hashlib.sha256(('other'+str(i)).encode()).hexdigest(),
                          'original_identity': 'other-' + str(i),
                          'review_lane': 'HISTORICAL_FOOD_SOURCE_AND_FOOD_SAFETY' if i < 8
                                 else 'SOURCE_INTERPRETATION_CHANGE' if i < 12 else 'TOOL_SOURCE_SCOPE',
                          'qualified_source_review': False,
                          'medical_or_food_safety_approved': False,
                          'publication_allowed': False})
    fam = {'schema':'fv-preparedness-r155-family-source-observation-v1','status':'DRAFT_HARD_HOLD',
           'source_relationships': 11, 'citation_occurrences':16,
           'text_accessible_limited_claim_match':3, 'source_scope_flags':2,
           'retrieval_blocked_not_link_dead':6,'unreviewed_source_relationships':11,
           'qualified_source_review':False,'medical_safety_approval':False,
           'independent_qd_pass':False,'publish_allowed':False,'paid_offer_verified':False,
           'items':rows}
    tri = {'schema':'fv-preparedness-r154-triage-v1','decision':'DRAFT_HARD_HOLD',
           'review_tasks_total':75,'priority_hist_food':8,'priority_reunification':11,
           'priority_interpretation':4,'remaining_tool_source':52,
           'qualified_source_review':False,'safety_approved':False,
           'independent_qd_pass':False,'publication_authorized':False,'merchant_offer_verified':False,
           'original_packet_fingerprint':hashlib.sha256(b'R153 frozen reference').hexdigest(),
           'tasks':task_rows}
    obs = {'schema':'fv-preparedness-r155-family-source-observation-v1',
           'observed_date':'2026-11-05','tool':gate.FAMILY,
           'source_approval':False,'independent_review':False,
           'publication_authorized':False,'commercial_offer_verified':False,
           'observations':observed}
    return fam,tri,obs


class Guard(unittest.TestCase):
    def test_baseline_exact_11_sources_16_citations(self):
        p = gate.reconcile(*fixture())
        self.assertEqual((p['family_source_relationships'],p['family_citation_occurrences']),(11,16))
        self.assertEqual((p['critical_source_scope'],p['blocked_retrieval_not_link_death'],
                          p['narrow_text_matches_not_approved']),(2,6,3))
        self.assertEqual(p['other_review_tasks_still_pending'],64)
        self.assertEqual(p['status'],'DRAFT_HARD_HOLD')
        self.assertIsNone(p['net_revenue_per_1000_sessions'])
        self.assertTrue(all(x['publish_allowed'] is False for x in p['workorders']))
        self.assertTrue(all(x['safety_approved'] is False for x in p['workorders']))
    def test_priorities_are_disputes_then_blocked_then_limited_match(self):
        orders=gate.reconcile(*fixture())['workorders']
        self.assertEqual([x['queue_priority'] for x in orders],[0]*2+[1]*6+[2]*3)
    def test_source_specific_questions_preserved(self):
        data={r['source_id']:r for r in gate.reconcile(*fixture())['workorders']}
        self.assertIn('CyberTipline',data['shelter-ncmec-hotline']['reviewer_question'])
        self.assertIn('photo ID',data['shelter-co-oss-reunification']['reviewer_question'])
        self.assertIn('privacy',data['shelter-ready-plan-form']['reviewer_question'])
    def test_gate_invalid_checkout_exits_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gate.main(['--repo',d]),2)
    def test_no_external_report_on_invalid_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d).parent/'r156-invalid-report.json'
            self.assertEqual(gate.main(['--repo',d,'--report',str(f)]),2)
            self.assertFalse(f.exists())
    def test_git_blob_known(self):
        self.assertEqual(gate.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_pinned_evidence_rejects_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'file').write_text('bad')
            with self.assertRaisesRegex(ValueError,'changed Git source identity'):
                gate.pinned(r,'file',gate.git_blob(b'good'))
    def test_pinned_evidence_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'original').write_text('hi');(r/'link').symlink_to('original')
            with self.assertRaisesRegex(ValueError,'missing/symlink'):
                gate.pinned(r,'link',gate.git_blob(b'hi'))
    def test_pinned_evidence_exact_sha_works(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'original').write_bytes(b'hi')
            self.assertEqual(gate.pinned(r,'original',gate.git_blob(b'hi')),r/'original')
    def test_forged_paid_offer_fails(self):
        f,t,o=fixture();f['paid_offer_verified']=True
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_forged_qd_fails(self):
        f,t,o=fixture();t['independent_qd_pass']=True
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_forged_safety_fails(self):
        f,t,o=fixture();t['safety_approved']=True
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_source_date_drift_fails(self):
        f,t,o=fixture();o['observed_date']='2026-11-06'
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_count_drift_fails(self):
        f,t,o=fixture();t['review_tasks_total']=74
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_missing_nonfamily_task_fails(self):
        f,t,o=fixture();t['tasks'].pop()
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_duplicate_nonfamily_fingerprint_fails(self):
        f,t,o=fixture();t['tasks'][-1]['task_fingerprint']=t['tasks'][-2]['task_fingerprint']
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_missing_r154_packet_fingerprint_fails(self):
        f,t,o=fixture();t['original_packet_fingerprint']='x'
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_corrupted_family_citations_fails(self):
        f,t,o=fixture();f['items'][0]['citation_occurrences']+=1
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_family_unreviewed_state_fails(self):
        f,t,o=fixture();f['unreviewed_source_relationships']=10
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_source_observation_extra_fails(self):
        f,t,o=fixture();o['observations'].append(copy.deepcopy(o['observations'][0]))
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_approval_on_other_task_fails(self):
        f,t,o=fixture();t['tasks'][-1]['publication_allowed']=True
        with self.assertRaises(ValueError):gate.reconcile(f,t,o)
    def test_social_asset_not_inferred(self):
        p=gate.reconcile(*fixture())
        for k in ['source_safety_qd_approved','public_release_allowed','merchant_sku_verified',
                  'social_asset_id_verified','paid_conversions_verified']:
            self.assertIs(p[k],False)


def register_mutations():
    for i,sid in enumerate(gate.EXPECTED):
        for kind in ('url','scope','access','removed','source_approval','review_approval','triage_url'):
            def check(self,i=i,kind=kind):
                f,t,o=fixture()
                if kind=='url':o['observations'][i]['source_url']='https://example.org/forged'
                elif kind=='scope':o['observations'][i]['scope']='APPROVED'
                elif kind=='access':f['items'][i]['observed_access']='HTTP_200'
                elif kind=='removed':o['observations'].pop(i)
                elif kind=='source_approval':f['items'][i]['human_link_verified']=True
                elif kind=='review_approval':t['tasks'][i]['qualified_source_review']=True
                else:t['tasks'][i]['source_url']='https://example.org/forged'
                with self.assertRaises(ValueError):gate.reconcile(f,t,o)
            setattr(Guard,'test_'+kind+'_'+sid.replace('-','_'),check)

register_mutations()

if __name__=='__main__':unittest.main(verbosity=2)
