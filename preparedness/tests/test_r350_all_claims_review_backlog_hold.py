"""R350 synthetic adversarial fixtures only. No canonical manuscript mutation."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r350_all_claims_review_backlog_hold.py'
spec = importlib.util.spec_from_file_location('r350_all_claims_review_backlog_hold', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def row(i=1, sid='fema-plan', doc='articles/household-emergency-plan'):
    return {'document': doc, 'source_id': sid, 'ordinal': i,
            'occurrence_sha256': r.sha('occ'+str(i)),
            'region_sha256': r.sha('region'+str(i)),
            'source_identity_sha256': r.sha('source'+sid),
            'url_sha256': r.sha('https://example.org/'+sid),
            'metadata_source_use_sha256': r.sha('support statement')}


def source(rows=None):
    rows = [row(), row(2)] if rows is None else rows
    return {'schema':'fv-preparedness-r349-41-document-citation-registry-join-v1',
            'status':'DRAFT_CROSSWALK_ONLY_HARD_HOLD',
            'errors':[], 'documents_inspected':41, 'all_citations':rows,
            'occurrences_count':len(rows),'may_publish':False,'qualified_qd_pass':False}


class TestBacklog(unittest.TestCase):
    def setUp(self): self.upstream=source()
    def run_audit(self, proposals=None): return r.compile_backlog(self.upstream, proposals)
    def test_two_occurrences_are_distinct(self):
        v=self.run_audit();self.assertEqual(v['ticket_count'],2)
        self.assertEqual(len({t['ticket_id'] for t in v['tickets']}),2)
    def test_41_corpus_preserved(self): self.assertEqual(self.run_audit()['documents_inspected'],41)
    def test_no_approval_on_clean_input(self):
        for k in r.HARD_HOLD:self.assertIs(self.run_audit()[k],False,k)
    def test_no_claim_text_or_live_urls_exported(self):
        s=json.dumps(self.run_audit());self.assertNotIn('https://',s)
        self.assertNotIn('support statement',s)
    def test_determinism_across_order(self):
        one=self.run_audit()['tickets'];self.upstream['all_citations'].reverse()
        self.assertEqual(one,self.run_audit()['tickets'])
    def test_disputed_source_never_auto_accepted(self):
        self.upstream['all_citations'].append(row(3, 'fsis-power-failure'))
        self.upstream['occurrences_count']+=1
        self.assertEqual(self.run_audit()['unreviewed_count'],3)
    def test_proposal_still_held(self):
        ticket=r.ticket_id(row())
        v=self.run_audit([{'ticket_id':ticket,'disposition':'needs_source_check',
                            'evidence_url':'https://ready.gov/resources',
                            'reviewer_note':'Need expert adjudication'}])
        self.assertEqual(v['proposals_received_count'],1)
        self.assertEqual(v['status'],'PRIVATE_REVIEW_BACKLOG_HARD_HOLD')
        self.assertIs(v['qualified_qd_pass'],False)
    def test_valid_41_synthetic_tickets(self):
        self.upstream=source([row(i+1,doc='articles/guide-'+str(i)) for i in range(35)] +
                             [row(i+36,doc='tools/sheet-'+str(i)) for i in range(6)])
        self.assertEqual(self.run_audit()['ticket_count'],41)
        self.assertEqual(len(self.run_audit()['citation_counts_by_document']),41)
    def test_no_canonical_mutation(self):
        before=copy.deepcopy(self.upstream)
        self.run_audit();self.assertEqual(before,self.upstream)
    def test_no_proposal_mutation(self):
        p=[{'ticket_id':r.ticket_id(row()),'disposition':'needs_claim_revision'}]
        old=copy.deepcopy(p);self.run_audit(p);self.assertEqual(old,p)
    def test_unknown_ticket_rejected(self):
        self.assertIn('STALE_OR_UNKNOWN_REVIEW_TICKET',self.run_audit([{
            'ticket_id':'a'*64,'disposition':'needs_source_check'}])['errors'])
    def test_missing_pinned_predecessor_fails(self):
        with tempfile.TemporaryDirectory() as root:
            v=r.native_audit(Path(root))
            self.assertEqual(v['status'],'INVALID_HARD_HOLD')
    def test_pinned_predecessor_tamper_fails(self):
        with tempfile.TemporaryDirectory() as root:
            target=Path(root)/'preparedness'/'tools'/'r349_full_corpus_citation_registry_hold.py'
            target.parent.mkdir(parents=True);target.write_text('print("bad")')
            v=r.native_audit(Path(root))
            self.assertIn('R349_PINNED_GIT_BLOB_MISMATCH',v['errors'])
    def test_predecessor_symlink_fails(self):
        with tempfile.TemporaryDirectory() as root:
            target=Path(root)/'preparedness'/'tools'/'r349_full_corpus_citation_registry_hold.py'
            target.parent.mkdir(parents=True);target.symlink_to('/etc/passwd')
            self.assertEqual(r.native_audit(Path(root))['status'],'INVALID_HARD_HOLD')


class TestURL(unittest.TestCase):
    def test_valid_public_https(self):
        for url in ('https://ready.gov/','https://www.redcross.org/foo', 'https://nchfp.uga.edu/how'):
            with self.subTest(url=url):self.assertTrue(r.safe_review_url(url))


class TestMutations(unittest.TestCase): pass


def fail_case(name, change, code):
    def test(self):
        v=source()
        change(v)
        got=r.compile_backlog(v)
        self.assertIn(code,got['errors'],name+': '+str(got['errors']))
        self.assertEqual(got['status'],'INVALID_HARD_HOLD')
        for key in r.HARD_HOLD:self.assertIs(got[key],False)
    setattr(TestMutations,'test_'+name,test)


MUTATIONS={
 'missing_schema':(lambda v:v.pop('schema'),'WRONG_R349_SCHEMA'),
 'wrong_schema':(lambda v:v.update(schema='bad'),'WRONG_R349_SCHEMA'),
 'public_state':(lambda v:v.update(status='LIVE'),'R349_NOT_IN_DRAFT_HARD_HOLD_STATE'),
 'approved_state':(lambda v:v.update(status='APPROVED'),'R349_NOT_IN_DRAFT_HARD_HOLD_STATE'),
 'errors_added':(lambda v:v.update(errors=['SOURCE_CONFLICT']),'UPSTREAM_CROSSWALK_BLOCKED'),
 'errors_missing':(lambda v:v.pop('errors'),'INVALID_UPSTREAM_ERRORS_FIELD'),
 'errors_wrong':(lambda v:v.update(errors='err'),'INVALID_UPSTREAM_ERRORS_FIELD'),
 'errors_mixed':(lambda v:v.update(errors=[5]),'INVALID_UPSTREAM_ERRORS_FIELD'),
 'corpus40':(lambda v:v.update(documents_inspected=40),'FULL_41_DOCUMENT_CUSTODY_NOT_ESTABLISHED'),
 'corpus42':(lambda v:v.update(documents_inspected=42),'FULL_41_DOCUMENT_CUSTODY_NOT_ESTABLISHED'),
 'corpus_str':(lambda v:v.update(documents_inspected='41'),'FULL_41_DOCUMENT_CUSTODY_NOT_ESTABLISHED'),
 'release_true':(lambda v:v.update(may_publish=True),'UPSTREAM_RELEASE_FLAG_INCONSISTENCY'),
 'qd_true':(lambda v:v.update(qualified_qd_pass=True),'UPSTREAM_RELEASE_FLAG_INCONSISTENCY'),
 'release_missing':(lambda v:v.pop('may_publish'),'UPSTREAM_RELEASE_FLAG_INCONSISTENCY'),
 'citation_missing':(lambda v:v.pop('all_citations'),'INVALID_UPSTREAM_CITATIONS'),
 'citation_none':(lambda v:v.update(all_citations=None),'INVALID_UPSTREAM_CITATIONS'),
 'count_smaller':(lambda v:v.update(occurrences_count=1),'UPSTREAM_OCCURRENCE_COUNT_MISMATCH'),
 'count_bigger':(lambda v:v.update(occurrences_count=3),'UPSTREAM_OCCURRENCE_COUNT_MISMATCH'),
 'row_bad_type':(lambda v:v['all_citations'].__setitem__(0,False),'MALFORMED_CITATION_IDENTITY'),
 'row_bad_document':(lambda v:v['all_citations'][0].update(document='../secret'),'MALFORMED_CITATION_IDENTITY'),
 'row_invalid_kind':(lambda v:v['all_citations'][0].update(document='videos/foo'),'MALFORMED_CITATION_IDENTITY'),
 'row_bad_source':(lambda v:v['all_citations'][0].update(source_id='Bad Source'),'MALFORMED_CITATION_IDENTITY'),
 'row_bad_ordinal':(lambda v:v['all_citations'][0].update(ordinal=0),'INVALID_CITATION_ORDINAL'),
 'row_negative_ordinal':(lambda v:v['all_citations'][0].update(ordinal=-1),'INVALID_CITATION_ORDINAL'),
 'row_bool_ordinal':(lambda v:v['all_citations'][0].update(ordinal=True),'INVALID_CITATION_ORDINAL'),
 'row_invalid_sha':(lambda v:v['all_citations'][0].update(region_sha256='not a hash'),'MISSING_OR_INVALID_SOURCE_CLAIM_CUSTODY'),
 'row_missing_hash':(lambda v:v['all_citations'][0].pop('source_identity_sha256'),'MISSING_OR_INVALID_SOURCE_CLAIM_CUSTODY'),
 'row_unbound_url':(lambda v:v['all_citations'][0].update(url_sha256=None),'MISSING_OR_INVALID_SOURCE_CLAIM_CUSTODY'),
 'row_unbound_metadata':(lambda v:v['all_citations'][0].update(metadata_source_use_sha256=None),'MISSING_OR_INVALID_SOURCE_CLAIM_CUSTODY'),
 'duplicate_row':(lambda v:v['all_citations'].__setitem__(1,copy.deepcopy(v['all_citations'][0])),'DUPLICATE_SOURCE_CLAIM_TICKET'),
}
for name,(mut,code) in MUTATIONS.items():fail_case(name,mut,code)


class TestProposals(unittest.TestCase):
    def setUp(self):self.id=r.ticket_id(row())
    def check_bad(self, p, expected):
        v=r.compile_backlog(source(),p)
        self.assertIn(expected,v['errors'])
        self.assertIs(v['may_publish'],False)
    def test_three_allowed_unapproved(self):
        for d in sorted(r.ALLOWED_PROPOSALS):
            with self.subTest(d=d):
                self.assertEqual(r.compile_backlog(source(),[{'ticket_id':self.id,'disposition':d}])['proposals_received_count'],1)


PROPOSAL_MUTATIONS={
 'invalid_shape':([42],'INVALID_REVIEW_PROPOSAL'),
 'missing_id':([{'disposition':'needs_source_check'}],'INVALID_REVIEW_PROPOSAL'),
 'duplicate_id':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check'}]*2,'DUPLICATE_REVIEW_TICKET'),
 'fabricated_pass':([{'ticket_id':r.ticket_id(row()),'disposition':'approved'}],'UNSUPPORTED_REVIEW_DECISION_OR_FALSE_APPROVAL'),
 'verified_claim':([{'ticket_id':r.ticket_id(row()),'disposition':'supported'}],'UNSUPPORTED_REVIEW_DECISION_OR_FALSE_APPROVAL'),
 'fake_qd_pass':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','qualified_qd_pass':True}],'UNRECOGNIZED_REVIEW_OR_APPROVAL_FIELD'),
 'illegal_notes':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','reviewer_note':3}],'INVALID_PRIVATE_REVIEW_NOTE'),
 'too_long_notes':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','reviewer_note':'z'*2100}],'INVALID_PRIVATE_REVIEW_NOTE'),
 'http_evidence':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'http://example.org/page'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'localhost':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://localhost/private'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'private_ip':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://192.168.1.20/'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'query_personal':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://example.org/?email=foo'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'password':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://name:password@example.org/'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'javascript_url':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'javascript:alert(1)'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'fragment':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://example.org/page#private'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'local_domain':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://test.internal/page'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'userinfo':([{'ticket_id':r.ticket_id(row()),'disposition':'needs_source_check','evidence_url':'https://user@example.org/foo'}],'UNSAFE_OR_UNTRUSTED_REVIEW_URL'),
 'unknown_ticket':([{'ticket_id':'z'*64,'disposition':'needs_source_check'}],'STALE_OR_UNKNOWN_REVIEW_TICKET'),
}
for name,(p,expected) in PROPOSAL_MUTATIONS.items():
    def make(pp=p,ee=expected):
        def test(self):self.check_bad(pp,ee)
        return test
    setattr(TestProposals,'test_'+name,make())


if __name__ == '__main__': unittest.main()
