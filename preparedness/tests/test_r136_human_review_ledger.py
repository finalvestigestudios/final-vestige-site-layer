"""Synthetic/adversarial tests only; full real archive custody remains necessary."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
from pathlib import Path
import hashlib
import sys
import unittest

TOOL_DIR = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOL_DIR))
spec = importlib.util.spec_from_file_location('r136_human_review_ledger', TOOL_DIR / 'r136_human_review_ledger.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    groups=[{'task_id':f'SOURCE-{i:020x}', 'crosswalk_group_index':i,
             'cited_variant_identities_only':[['food',f'id-{i}','https://example.org/original']],
             'decision':'UNREVIEWED_HUMAN_REQUIRED'} for i in range(1,33)]
    passages=[]
    for i in range(35):
        digest=hashlib.sha256(f'article-{i}'.encode()).hexdigest()
        passages.append({'task_id':'PASSAGE-'+digest[:20], 'witness_sha256':digest,
                         'slug':f'article-{i}', 'risk_families_for_triage_only':
                         ['medicine-medical-dependency'] if i%3==0 else ['water-treatment'],
                         'decision':'UNREVIEWED_HUMAN_REQUIRED'})
    return {'status':'HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION',
            'may_publish':False,'qd_pass':False,'medical_safety_verified':False,
            'merchant_offer_verified':False,
            'provenance':{'candidate_parent':'r132-immutable-sha','article_count':35,
                          'citation_occurrences':2000},
            'summary':{'crosswalk_groups_requiring_human_review':32,
                       'risk_passages_requiring_human_review':35},
            'source_group_tasks':groups,'safety_passage_tasks':passages}


def completed(queue, kind='source'):
    sheet=m.template(queue)
    item=next(r for r in sheet['records'] if r['kind']==kind)
    item.update(outcome='EVIDENCE_LOGGED_NOT_APPROVED',reviewer_reference='review-123',
                reviewed_at_utc='2026-11-04T19:15:00Z',
                evidence_url='https://example.gov/guidance',evidence_passage='relevant exact text',
                source_scope_analysis='author scope differs; requires reviewer adjudication')
    if kind=='passage':item['specialist_review_reference']='qualified-review-request-42'
    return sheet,item


def rejected(fn):
    q=fixture();s=m.template(q);fn(q,s)
    with unittest.TestCase().assertRaises(m.ReviewHold):m.reconcile(q,s)


class Test35Passages(unittest.TestCase):
    pass


def make_passage(i):
    def test(self):
        q=fixture();s=m.template(q); r=m.reconcile(q,s)
        self.assertFalse(r['may_publish']);self.assertFalse(r['qd_pass'])
        self.assertEqual(len([x for x in s['records'] if x['kind']=='passage']),35)
        self.assertTrue(any(x['task_id']==q['safety_passage_tasks'][i]['task_id'] for x in s['records']))
    return test

for i in range(35):setattr(Test35Passages,f'test_passage_{i:02}',make_passage(i))


class TestReviewSecurity(unittest.TestCase):
    def test_template_stable(self):self.assertEqual(m.template(fixture()),m.template(fixture()))
    def test_status_hold(self):self.assertEqual(m.reconcile(fixture(),m.template(fixture()))['status'],m.HOLD)
    def test_zero_approvals(self):self.assertFalse(m.reconcile(fixture(),m.template(fixture()))['human_approval_auto_granted'])
    def test_32_source_records(self):self.assertEqual(len([x for x in m.template(fixture())['records'] if x['kind']=='source']),32)
    def test_all_67_records(self):self.assertEqual(len(m.template(fixture())['records']),67)
    def test_no_review_counts(self):self.assertEqual(m.reconcile(fixture(),m.template(fixture()))['recorded_outcomes']['OPEN'],67)
    def test_can_log_source_evidence_but_hold(self):
        q=fixture();s,_=completed(q)
        self.assertFalse(m.reconcile(q,s)['qd_pass'])
    def test_can_log_passage_with_specialist_ref_but_hold(self):
        q=fixture();s,_=completed(q,'passage')
        self.assertFalse(m.reconcile(q,s)['medical_safety_verified'])
    def test_correction_requires_note(self):
        q=fixture();s,x=completed(q);x['outcome']='NEEDS_CORRECTION'
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
        x['proposed_correction']='Need exact source-context update'
        self.assertEqual(m.reconcile(q,s)['recorded_outcomes']['NEEDS_CORRECTION'],1)
    def test_insufficient_evidence_documented(self):
        q=fixture();s,x=completed(q);x['outcome']='INSUFFICIENT_EVIDENCE'
        self.assertFalse(m.reconcile(q,s)['may_publish'])
    def test_reordered_records_allowed(self):
        q=fixture();s=m.template(q);s['records'].reverse()
        self.assertEqual(m.reconcile(q,s)['total_review_tasks'],67)
    def test_changed_candidate_hash_reject(self):rejected(lambda q,s:q['provenance'].update(candidate_parent='tampered'))
    def test_changed_review_hash_reject(self):rejected(lambda q,s:s.update(queue_sha256='0'*64))
    def test_changed_review_parent_reject(self):rejected(lambda q,s:s.update(candidate_parent='other'))
    def test_forged_purpose_reject(self):rejected(lambda q,s:s.update(purpose='PUBLISH_APPROVED'))
    def test_unknown_extra_root_reject(self):rejected(lambda q,s:s.update(may_publish=True))
    def test_missing_records_reject(self):rejected(lambda q,s:s['records'].pop())
    def test_extra_record_reject(self):rejected(lambda q,s:s['records'].append(deepcopy(s['records'][0])))
    def test_duplicate_record_reject(self):rejected(lambda q,s:s['records'][1].update(task_id=s['records'][0]['task_id']))
    def test_unknown_id_reject(self):rejected(lambda q,s:s['records'][0].update(task_id='SOURCE-'+'f'*20))
    def test_forged_kind_reject(self):rejected(lambda q,s:s['records'][0].update(kind='source'))
    def test_forged_pass_reject(self):rejected(lambda q,s:s['records'][0].update(outcome='PASS'))
    def test_forged_safe_reject(self):rejected(lambda q,s:s['records'][0].update(outcome='MEDICALLY_SAFE'))
    def test_open_with_reviewer_reject(self):rejected(lambda q,s:s['records'][0].update(reviewer_reference='claimed'))
    def test_open_with_timestamp_reject(self):rejected(lambda q,s:s['records'][0].update(reviewed_at_utc='2026-11-04T19:00:00Z'))
    def test_extra_review_field_reject(self):rejected(lambda q,s:s['records'][0].update(approved=True))
    def test_missing_review_field_reject(self):rejected(lambda q,s:s['records'][0].pop('evidence_url'))
    def test_no_evidence_url_reject(self):
        q=fixture();s,x=completed(q);x['evidence_url']=''
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_http_evidence_reject(self):
        q=fixture();s,x=completed(q);x['evidence_url']='http://example.org'
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_file_url_evidence_reject(self):
        q=fixture();s,x=completed(q);x['evidence_url']='file:///etc/passwd'
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_blank_passage_reject(self):
        q=fixture();s,x=completed(q);x['evidence_passage']='   '
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_blank_scope_analysis_reject(self):
        q=fixture();s,x=completed(q);x['source_scope_analysis']='  '
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_blank_reviewer_reject(self):
        q=fixture();s,x=completed(q);x['reviewer_reference']=''
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_invalid_calendar_date_reject(self):
        q=fixture();s,x=completed(q);x['reviewed_at_utc']='2026-02-31T19:15:00Z'
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_offset_time_reject(self):
        q=fixture();s,x=completed(q);x['reviewed_at_utc']='2026-11-04T19:15:00-08:00'
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_high_risk_requires_specialist_ref(self):
        q=fixture();s,x=completed(q,'passage');x['specialist_review_reference']=''
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_water_risk_no_specialist_ref(self):
        q=fixture();s=m.template(q);r=next(x for x in s['records'] if x['task_id']==q['safety_passage_tasks'][1]['task_id'])
        r.update(outcome='INSUFFICIENT_EVIDENCE',reviewer_reference='review-42',
                 reviewed_at_utc='2026-11-04T19:15:00Z',evidence_url='https://example.gov/water',
                 evidence_passage='official passage',source_scope_analysis='scope differs')
        self.assertFalse(m.reconcile(q,s)['qd_pass'])
    def test_wrong_citation_count_reject(self):
        q=fixture();q['provenance']['citation_occurrences']=1999
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_wrong_article_count_reject(self):
        q=fixture();q['provenance']['article_count']=34
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_missing_group_reject(self):
        q=fixture();q['source_group_tasks'].pop()
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_duplicate_group_reject(self):
        q=fixture();q['source_group_tasks'][1]['crosswalk_group_index']=1
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_duplicate_task_id_reject(self):
        q=fixture();q['safety_passage_tasks'][1]['task_id']=q['safety_passage_tasks'][0]['task_id']
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_changed_passage_witness_reject(self):
        q=fixture();q['safety_passage_tasks'][0]['witness_sha256']='f'*64
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_fake_qd_reject(self):
        q=fixture();q['qd_pass']=True
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_fake_medical_reject(self):
        q=fixture();q['medical_safety_verified']=True
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_fake_offer_reject(self):
        q=fixture();q['merchant_offer_verified']=True
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_fake_publish_reject(self):
        q=fixture();q['may_publish']=True
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_origin_variants_required(self):
        q=fixture();q['source_group_tasks'][0]['cited_variant_identities_only']=[]
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_tasks_unreviewed_required(self):
        q=fixture();q['source_group_tasks'][0]['decision']='APPROVED'
        with self.assertRaises(m.ReviewHold):m.template(q)
    def test_long_string_reject(self):
        q=fixture();s,x=completed(q);x['source_scope_analysis']='A'*4001
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)
    def test_non_string_field_reject(self):
        q=fixture();s,x=completed(q);x['reviewer_reference']=12
        with self.assertRaises(m.ReviewHold):m.reconcile(q,s)

if __name__ == '__main__':unittest.main()
