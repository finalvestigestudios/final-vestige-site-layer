"""R9 synthetic/adversarial intake tests; not human source or clinical checks."""
import copy
from datetime import date
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import claim_occurrence_audit as r8
from test_claim_occurrence_audit import fixture
import claim_review_intake as r9

TODAY = date(2026, 10, 30)


def baseline():
    meta, sources, rows = fixture()
    class FixtureLib:
        articles = {'sample': meta}
        def source_for(self, m, sid):
            return sources[sid]
        def url_path(self, slug):
            return '/preparedness/' + slug + '/'
    return r8.make_report(FixtureLib(), rows=rows, fingerprint=lambda lib, meta: 'a'*64,
                          expect={'draft_items': 1, 'article_source_pairs': 2,
                                  'physical_source_rows': 2, 'shared_url_groups': 1})


def bundle(report=None):
    report = report or baseline()
    return {'schema_version': 1, 'parent_evidence_digest_sha256': report['evidence_digest_sha256'],
            'claim_responses': []}


def response(report=None, index=0):
    r = (report or baseline())['claims'][index]
    return {'claim_request_sha256': r['claim_request_sha256'],
            'reviewer': 'Example reviewer, identity not authenticated',
            'reviewed_on': '2026-10-29', 'source_access': 'REACHED_SOURCE',
            'observed_url': r['source_url'], 'source_locator': 'Source section 4 and paragraph 2',
            'claim_assessment': 'SUPPORTED_IN_INSPECTED_SCOPE',
            'proposition_quote': 'A reported claim needs checking',
            'evidence_basis': 'Reviewer reports this source section supports only a limited proposition.',
            'reading_limits': 'Only the designated page was examined, not the full report.',
            'risk_flags': []}


class R9ReportCustody(unittest.TestCase):
    def test_parent_good(self):
        self.assertEqual(len(r9.check_report(baseline(), expected_counts=None)), 2)
    def test_parent_unchanged(self):
        r = baseline(); old = copy.deepcopy(r)
        r9.check_report(r, expected_counts=None); self.assertEqual(old, r)
    def test_parent_verification_required(self):
        with self.assertRaisesRegex(ValueError, 'baseline drift'):
            r9.check_report(baseline())
    def test_parent_identity_unaltered(self):
        r = baseline(); r['claims'][0]['claim_request_sha256'] = 'a'*64
        with self.assertRaisesRegex(ValueError, 'fingerprint'):r9.check_report(r, expected_counts=None)
    def test_parent_evidence_digest_unaltered(self):
        r = baseline();r['evidence_digest_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'evidence digest'):r9.check_report(r, expected_counts=None)
    def test_parent_no_false_approval(self):
        r=baseline();r['may_publish']=True
        with self.assertRaisesRegex(ValueError,'truth'):r9.check_report(r,expected_counts=None)
    def test_parent_no_claim_approval(self):
        r=baseline();r['claims'][0]['claim_review']='VERIFIED'
        with self.assertRaisesRegex(ValueError,'unsafe'):r9.check_report(r,expected_counts=None)
    def test_parent_inherited_safety_not_authority(self):
        r=baseline();r['claims'][0]['inherited_safety_state']='approved'
        self.assertEqual(len(r9.check_report(r,expected_counts=None)),2)
    def test_parent_unknown_safety(self):
        r=baseline();r['claims'][0]['inherited_safety_state']='MEDICALLY_SAFE'
        with self.assertRaisesRegex(ValueError,'safety'):r9.check_report(r,expected_counts=None)
    def test_parent_changed_article_source_use(self):
        r=baseline();r['claims'][0]['article_source_use']='edited after reviewing'
        with self.assertRaisesRegex(ValueError,'fingerprint'):r9.check_report(r,expected_counts=None)
    def test_parent_changed_support_scope(self):
        r=baseline();r['claims'][0]['contributor_claimed_support']='new source scope'
        with self.assertRaisesRegex(ValueError,'fingerprint'):r9.check_report(r,expected_counts=None)
    def test_parent_changed_limits_scope(self):
        r=baseline();r['claims'][0]['contributor_reading_limits']='new limitation'
        with self.assertRaisesRegex(ValueError,'fingerprint'):r9.check_report(r,expected_counts=None)
    def test_parent_missing_source_row(self):
        r=baseline();r['claims'][0]['source_row_key']=''
        with self.assertRaises(ValueError):r9.check_report(r,expected_counts=None)
    def test_parent_wrong_origin(self):
        r=baseline();r['claims'][0]['source_origin']='food'
        with self.assertRaisesRegex(ValueError,'contributor'):r9.check_report(r,expected_counts=None)
    def test_parent_unsupported_http(self):
        r=baseline();r['claims'][0]['source_url']='http://example.org/source'
        with self.assertRaises(ValueError):r9.check_report(r,expected_counts=None)
    def test_parent_ordinal_gap(self):
        r=baseline();r['claims'][1]['ordinal']=3
        with self.assertRaises(ValueError):r9.check_report(r,expected_counts=None)
    def test_parent_occurrence_count_drift(self):
        r=baseline();r['counts']['citation_occurrences']=10
        with self.assertRaisesRegex(ValueError,'count mismatch'):r9.check_report(r,expected_counts=None)
    def test_parent_pair_count_drift(self):
        r=baseline();r['counts']['article_source_pairs']=10
        with self.assertRaisesRegex(ValueError,'pair inventory'):r9.check_report(r,expected_counts=None)
    def test_parent_source_count_drift(self):
        r=baseline();r['counts']['physical_source_rows']=9
        with self.assertRaisesRegex(ValueError,'baseline drift'):r9.check_report(r,expected_counts={'physical_source_rows':2})
    def test_parent_strong_sha_type(self):
        r=baseline();r['claims'][0]['body_sha256']=123
        with self.assertRaises(ValueError):r9.check_report(r,expected_counts=None)
    def test_parent_citation_record_not_object(self):
        r=baseline();r['claims'][0]=[]
        with self.assertRaises(ValueError):r9.check_report(r,expected_counts=None)
    def test_parent_unverified_external_checks(self):
        r=baseline();r['human_link_checks_documented_by_tool']=1
        with self.assertRaisesRegex(ValueError,'truth'):r9.check_report(r,expected_counts=None)

    def test_parent_changed_visible_excerpt(self):
        r=baseline();r['claims'][0]['context_excerpt']='This is a fabricated supporting claim'
        with self.assertRaisesRegex(ValueError,'excerpt/body hash'):
            r9.check_report(r,expected_counts=None)
    def test_parent_context_excerpts_cannot_claim_truncated(self):
        r=baseline();r['claims'][0]['context_is_excerpt']=True
        with self.assertRaisesRegex(ValueError,'truncated'):
            r9.check_report(r,expected_counts=None)
    def test_authoritative_source_rows_catch_tampered_source_url(self):
        r=baseline();r['claims'][0]['source_url']='https://phishing.invalid/replaced'
        sources=[{'row_key':'start:0:one','origin':'start','source_id':'one','url':'https://example.org/source','supports':'Source one section A','reading_limits':'Pages 1–2'},
                 {'row_key':'base:0:two','origin':'base','source_id':'two','url':'https://example.org/source','supports':'Source two section B','reading_limits':'Pages 3–4'}]
        with self.assertRaisesRegex(ValueError,'source record'):
            r9.check_report(r,expected_counts=None,source_rows=sources)
    def test_authoritative_source_rows_match(self):
        r=baseline()
        sources=[{'row_key':'start:0:one','origin':'start','source_id':'one','url':'https://example.org/source','supports':'Source one section A','reading_limits':'Pages 1–2'},
                 {'row_key':'base:0:two','origin':'base','source_id':'two','url':'https://example.org/source','supports':'Source two section B','reading_limits':'Pages 3–4'}]
        self.assertEqual(len(r9.check_report(r,expected_counts=None,source_rows=sources)),2)
    def test_authoritative_source_rows_fewer_than_report(self):
        with self.assertRaisesRegex(ValueError,'source inventory'):
            r9.check_report(baseline(),expected_counts=None,source_rows=[])


class R9ResponseValidation(unittest.TestCase):
    def accept(self, override=None):
        r=baseline();x=response(r)
        if override:x.update(override)
        return r9.validate_response(x,r['claims'][0],TODAY)
    def reject(self, override, regex='response|source|claim|reviewer|URL|content|date|proposition'):
        with self.assertRaisesRegex(ValueError,regex):self.accept(override)
    def test_supported_is_still_unverified(self):
        r=self.accept();self.assertFalse(r['independent_link_check']);self.assertFalse(r['safety_cleared'])
    def test_supported_is_still_hold(self):self.assertFalse(self.accept()['may_publish'])
    def test_lowercase_reviewer_is_not_authenticated(self):self.assertFalse(self.accept({'reviewer':'test reviewer'})['reviewer_authenticated'])
    def test_report_source_reached(self):self.assertEqual(self.accept()['source_access_self_reported'],'REACHED_SOURCE')
    def test_partial_claim_is_follow_up(self):self.assertEqual(self.accept({'claim_assessment':'PARTIALLY_SUPPORTED'})['triage'],'FOLLOW_UP_REQUIRED')
    def test_contradiction_is_follow_up(self):self.assertEqual(self.accept({'claim_assessment':'CONTRADICTED'})['triage'],'FOLLOW_UP_REQUIRED')
    def test_uncertainty_is_follow_up(self):self.assertEqual(self.accept({'claim_assessment':'UNCERTAIN'})['triage'],'FOLLOW_UP_REQUIRED')
    def test_risk_flag_triggers_follow_up(self):self.assertEqual(self.accept({'risk_flags':['WATER']})['triage'],'FOLLOW_UP_REQUIRED')
    def test_infancy_always_follow_up(self):self.assertEqual(self.accept({'risk_flags':['INFANT','MEDICINE']})['triage'],'FOLLOW_UP_REQUIRED')
    def test_redirect_is_follow_up(self):self.assertEqual(self.accept({'source_access':'REDIRECTED_SOURCE','observed_url':'https://example.org/relocated'})['triage'],'FOLLOW_UP_REQUIRED')
    def test_not_reachable_not_checked(self):
        self.assertEqual(self.accept({'source_access':'NOT_REACHABLE','observed_url':None,'source_locator':'','claim_assessment':'NOT_CHECKED','proposition_quote':''})['triage'],'FOLLOW_UP_REQUIRED')
    def test_not_attempted_not_checked(self):
        self.assertEqual(self.accept({'source_access':'NOT_ATTEMPTED','observed_url':None,'source_locator':'','claim_assessment':'NOT_CHECKED','proposition_quote':''})['triage'],'FOLLOW_UP_REQUIRED')
    def test_future_date(self):self.reject({'reviewed_on':'2040-01-01'})
    def test_impossible_date(self):self.reject({'reviewed_on':'2026-02-30'})
    def test_date_not_iso(self):self.reject({'reviewed_on':'10/29/2026'})
    def test_review_date_integer(self):self.reject({'reviewed_on':20261029})
    def test_reviewer_blank(self):self.reject({'reviewer':'  '})
    def test_reviewer_fake_id_control(self):self.reject({'reviewer':'Fake\x00User'})
    def test_observed_http(self):self.reject({'observed_url':'http://example.org/source'})
    def test_observed_auth_user(self):self.reject({'observed_url':'https://user:pass@example.org/source'})
    def test_observed_wrong_port(self):self.reject({'observed_url':'https://example.org:8080/source'})
    def test_observed_space(self):self.reject({'observed_url':'https://example.org/source x'})
    def test_observed_backslash(self):self.reject({'observed_url':'https://example.org\\source'})
    def test_wrong_url_without_redirect(self):self.reject({'observed_url':'https://example.org/new'})
    def test_same_url_fake_redirect(self):self.reject({'source_access':'REDIRECTED_SOURCE'})
    def test_inaccessible_cannot_support(self):self.reject({'source_access':'NOT_REACHABLE','observed_url':None,'source_locator':''})
    def test_inaccessible_cannot_have_observed_url(self):self.reject({'source_access':'NOT_REACHABLE','claim_assessment':'NOT_CHECKED','proposition_quote':'','source_locator':''})
    def test_inaccessible_cannot_have_locator(self):self.reject({'source_access':'NOT_REACHABLE','claim_assessment':'NOT_CHECKED','proposition_quote':'','observed_url':None})
    def test_unsupported_source_state(self):self.reject({'source_access':'CLINICALLY_VERIFIED'})
    def test_unsupported_claim_state(self):self.reject({'claim_assessment':'SAFETY_APPROVED'})
    def test_risk_flags_invalid(self):self.reject({'risk_flags':['CAREFUL']})
    def test_risk_flags_duplicate(self):self.reject({'risk_flags':['WATER','WATER']})
    def test_risk_flags_wrong_type(self):self.reject({'risk_flags':'WATER'})
    def test_no_evidence_basis(self):self.reject({'evidence_basis':'short'})
    def test_no_reading_limits(self):self.reject({'reading_limits':''})
    def test_cannot_quote_unrelated_claim(self):self.reject({'proposition_quote':'completely invented outside paragraph'})
    def test_missing_proposition_quote(self):self.reject({'proposition_quote':''})
    def test_unsafe_quote_control(self):self.reject({'proposition_quote':'A reported\x00 claim needs checking'})
    def test_unreviewed_cannot_quote(self):self.reject({'claim_assessment':'NOT_CHECKED'})
    def test_no_source_locator(self):self.reject({'source_locator':''})
    def test_context_excerpt_follow_up(self):
        r=baseline();r['claims'][0]['context_is_excerpt']=True
        x=r9.validate_response(response(r),r['claims'][0],TODAY)
        self.assertEqual(x['triage'],'FOLLOW_UP_REQUIRED')
    def test_bogus_approval_extra_field(self):
        r=baseline();x=response(r);x['safety_approved']=True
        with self.assertRaisesRegex(ValueError,'strict schema'):r9.validate_response(x,r['claims'][0],TODAY)
    def test_missing_response_field(self):
        r=baseline();x=response(r);x.pop('reading_limits')
        with self.assertRaisesRegex(ValueError,'strict schema'):r9.validate_response(x,r['claims'][0],TODAY)


class R9BundleIntegration(unittest.TestCase):
    def run_audit(self, r=None, b=None):
        r=r or baseline();b=b or bundle(r)
        return r9.audit(r,b,today=TODAY,expected_counts=None)
    def test_empty_bundle_has_pending(self):
        x=self.run_audit();self.assertEqual(x['counts']['unreported_occurrences'],2)
        self.assertTrue(all(r['status']=='PENDING_HUMAN' for r in x['review_queue']))
    def test_summary_preserves_rows(self):
        x=self.run_audit();self.assertEqual(len({q['source_row_key'] for q in x['review_queue']}),2)
    def test_summary_same_url_does_not_merge(self):
        x=self.run_audit();self.assertEqual(len({q['source_url'] for q in x['review_queue']}),1)
    def test_single_valid_response_counts_one(self):
        r=baseline();b=bundle(r);b['claim_responses'].append(response(r))
        x=self.run_audit(r,b);self.assertEqual(x['counts']['distinct_occurrences_with_self_reports'],1)
    def test_single_report_still_cannot_publish(self):
        r=baseline();b=bundle(r);b['claim_responses'].append(response(r))
        self.assertFalse(self.run_audit(r,b)['may_publish'])
    def test_review_agreement_still_not_verified(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r),response(r)]
        b['claim_responses'][1]['reviewer']='Second example reviewer'
        x=self.run_audit(r,b)
        self.assertEqual(x['counts']['self_reported_reviews'],2)
        self.assertEqual(x['counts']['disputed_occurrences'],0)
        self.assertEqual(x['independent_human_source_checks_verified'],0)
    def test_disagreement_escalates(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r),response(r)]
        b['claim_responses'][1]['reviewer']='Second example reviewer'
        b['claim_responses'][1]['claim_assessment']='CONTRADICTED'
        x=self.run_audit(r,b)
        self.assertEqual(x['counts']['disputed_occurrences'],1)
        self.assertIn('DISAGREEMENT',x['review_queue'][0]['status'])
    def test_same_reviewer_cannot_vote_twice(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r),response(r)]
        with self.assertRaisesRegex(ValueError,'duplicate reviewer'):self.run_audit(r,b)
    def test_case_variant_reviewer_not_distinct(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r),response(r)]
        b['claim_responses'][1]['reviewer']=b['claim_responses'][0]['reviewer'].upper()
        with self.assertRaisesRegex(ValueError,'duplicate reviewer'):self.run_audit(r,b)
    def test_stale_parent_digest(self):
        r=baseline();b=bundle(r);b['parent_evidence_digest_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'stale'):self.run_audit(r,b)
    def test_stale_claim_id(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]
        b['claim_responses'][0]['claim_request_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'unknown'):self.run_audit(r,b)
    def test_response_missing_fields(self):
        r=baseline();b=bundle(r);b['claim_responses']=[{'claim_request_sha256':r['claims'][0]['claim_request_sha256']}]
        with self.assertRaises(ValueError):self.run_audit(r,b)
    def test_unexpected_safety_override_at_top(self):
        r=baseline();b=bundle(r);b['may_publish']=True
        with self.assertRaisesRegex(ValueError,'schema'):self.run_audit(r,b)
    def test_unexpected_approved_response(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]
        b['claim_responses'][0]['approved']=True
        with self.assertRaises(ValueError):self.run_audit(r,b)
    def test_reordered_reports_deterministic_queue(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r),response(r)]
        b['claim_responses'][1]['reviewer']='Second example reviewer'
        z=self.run_audit(r,b)
        b['claim_responses'].reverse()
        x=self.run_audit(r,b)
        self.assertEqual(z['review_queue'],x['review_queue'])
    def test_bundle_digest_changes_on_payload(self):
        r=baseline();b=bundle(r);z=self.run_audit(r,b)
        b['claim_responses']=[response(r)];x=self.run_audit(r,b)
        self.assertNotEqual(z['response_digest_sha256'],x['response_digest_sha256'])
    def test_no_response_bundle_mutation(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)];old=copy.deepcopy(b)
        self.run_audit(r,b);self.assertEqual(b,old)
    def test_source_risk_flags_do_not_auto_clear(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]
        b['claim_responses'][0]['risk_flags']=['FOOD','WATER']
        x=self.run_audit(r,b);self.assertEqual(x['review_queue'][0]['status'],'FOLLOW_UP_REQUIRED')
    def test_unknown_source_report_rejected(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]
        b['claim_responses'][0]['claim_request_sha256']=r['claims'][1]['claim_request_sha256']
        # The respondent still uses the paragraph for the first source and cannot anchor it to the second.
        with self.assertRaisesRegex(ValueError,'proposition'):self.run_audit(r,b)
    def test_pending_group_count_retained(self):
        x=self.run_audit();self.assertEqual(x['counts']['shared_url_groups_unresolved_from_parent'],1)
    def test_no_publishing_state_even_when_all_self_reported(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r,0),response(r,1)]
        b['claim_responses'][1]['proposition_quote']='A second reported claim'
        self.assertTrue(all(q['may_publish'] is False for q in self.run_audit(r,b)['review_queue']))
    def test_duplicate_responses_over_limit(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]*17
        with self.assertRaisesRegex(ValueError,'response count'):self.run_audit(r,b)
    def test_unreviewed_claim_not_pseudo_confirmed(self):
        r=baseline();b=bundle(r);b['claim_responses']=[response(r)]
        b['claim_responses'][0].update({'source_access':'NOT_ATTEMPTED','observed_url':None,'source_locator':'','claim_assessment':'NOT_CHECKED','proposition_quote':''})
        self.assertEqual(self.run_audit(r,b)['review_queue'][0]['status'],'FOLLOW_UP_REQUIRED')


class R9FileSecurity(unittest.TestCase):
    def test_missing_json_fails(self):
        with self.assertRaises(ValueError):r9.read_json(Path('/nonexistent-fv-preparedness-private-response.json'))
    def test_small_json_loads(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'review.json';p.write_text('{"hello":"world"}')
            self.assertEqual(r9.read_json(p),{'hello':'world'})
    def test_too_big_json_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'review.json';p.write_text('x'*(r9.MAX_INPUT_BYTES+1))
            with self.assertRaisesRegex(ValueError,'size limit'):r9.read_json(p)
    def test_private_export_only_direct_child(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir()
            p=root/'review-queue.json';r8.safe_export(p,'{"release_state":"HOLD"}',root)
            self.assertIn('HOLD',p.read_text())
    def test_cannot_write_outside_build(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir()
            with self.assertRaises(ValueError):r8.safe_export(Path(d)/'public.json','bad',root)
    def test_no_symlink_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir(); p=root/'review.json';target=Path(d)/'real'
            target.write_text('ORIGINAL');p.symlink_to(target)
            with self.assertRaises(ValueError):r8.safe_export(p,'BAD',root)
            self.assertEqual(target.read_text(),'ORIGINAL')

if __name__=='__main__':unittest.main()
