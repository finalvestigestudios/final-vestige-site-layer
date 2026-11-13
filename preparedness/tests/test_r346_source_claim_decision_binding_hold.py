"""R346 pure synthetic tests. No actual source files, CMS, release or network touched."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import r345_conflicted_source_claim_quarantine as prior
import r346_source_claim_decision_binding_hold as gate


def sample():
    records, tickets = {'register.json': []}, []
    for i, (sid, pair) in enumerate(sorted(prior.CONFLICT_FILES.items())):
        records['register.json'].append({'id': sid, 'url': 'https://www.example.gov/' + sid,
                                         'title': 'reference', 'verified_on': None})
        for j, filename in enumerate(pair):
            records.setdefault(filename, []).append({'id': sid,
                'url': 'https://www.example.gov/' + sid,
                'title': 'version ' + str(j), 'publisher': 'Agency', 'kind': 'reference',
                'supports': 'different scope ' + str(j), 'verified_on': '2026-10-29',
                'human_link_check': False})
        tickets.append({'ticket_id': '%024x' % (i + 1), 'source_id': sid,
            'kind': 'articles', 'slug': 'test-article-' + str(i),
            'claim_text_sha256': chr(97 + i) * 64,
            'human_claim_source_adjudication': 'UNREVIEWED_REQUIRED',
            'heading': 'private heading'})
    return prior.make_packets(records, tickets)['packets']


def proposals(packets):
    out = []
    for p in packets:
        binding = gate.source_packet_binding(p)
        out.append({'source_id': binding['source_id'], 'packet_sha256': binding['packet_sha256'],
          'proposed_variant_sha256': binding['variant_sha256s'][0],
          'ticket_bindings': binding['ticket_bindings'],
          'proposal_note': 'For independent human inspection only; the underlying scope and each claim remain unreviewed.',
          'disposition': gate.DISPOSITION})
    return out


class Core(unittest.TestCase):
    def test_01_baseline(self):
        d = gate.review_preflight(sample())
        self.assertEqual(d['errors'], [])
        self.assertEqual(len(d['docket']), 4)
        self.assertEqual(d['state'], 'PENDING_PROPOSALS_HARD_HOLD')
    def test_02_complete_proposals_still_hard_hold(self):
        p = sample(); d = gate.review_preflight(p, proposals(p))
        self.assertEqual(d['errors'], [])
        self.assertEqual(d['state'], 'PROPOSALS_STILL_UNREVIEWED_HARD_HOLD')
        self.assertFalse(d['may_publish'])
        self.assertFalse(d['qualified_qd_pass'])
        self.assertFalse(d['claim_source_support_verified'])
        self.assertFalse(d['human_decisions_authenticated'])
    def test_03_stable_order(self):
        p = sample(); q = copy.deepcopy(p); q.reverse()
        for x in q: x['citations'].reverse(); x['verified_variants'].reverse()
        self.assertEqual(gate.canonical(gate.review_preflight(p)), gate.canonical(gate.review_preflight(q)))
    def test_04_stable_proposal_order(self):
        p = sample(); x = proposals(p)
        self.assertEqual(gate.canonical(gate.review_preflight(p,x)), gate.canonical(gate.review_preflight(p,list(reversed(x)))))
    def test_05_candidate_no_full_private_text(self):
        p = sample(); d = gate.review_preflight(p, proposals(p)); raw = json.dumps(d)
        self.assertNotIn('https://www.example.gov',raw)
        self.assertNotIn('different scope',raw)
    def test_06_missing_native_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            x=gate.native_audit(Path(td))
            self.assertEqual(x['state'],'INVALID_HARD_HOLD')
            self.assertTrue(x['errors'])
            self.assertFalse(x['may_merge'])
    def test_07_git_blob(self):
        self.assertEqual(gate.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_08_no_unsigned_approval(self):
        p=sample(); d=gate.review_preflight(p,proposals(p))
        for k,v in gate.HOLD.items(): self.assertIs(d[k],False)
    def test_09_consistent_source_count(self):
        self.assertEqual(len(gate.EXPECTED_IDS),4)
    def test_10_incomplete_pending(self):
        p=sample(); d=gate.review_preflight(p,proposals(p)[:2])
        self.assertEqual(d['state'],'PENDING_PROPOSALS_HARD_HOLD')
        self.assertEqual(d['proposals_received'],2)
        self.assertEqual(len(d['proposals_missing']),2)
    def test_11_all_claim_fingerprints_required(self):
        p=sample(); p[0]['citations'].append({**p[0]['citations'][0], 'ticket_id':'f'*24})
        p[0]['claim_tickets_impacted']+=1
        x=gate.source_packet_binding(p[0]); self.assertEqual(x['claim_count'],2)
    def test_12_nonlist_packets(self):
        self.assertEqual(gate.review_preflight(None)['state'],'INVALID_HARD_HOLD')
    def test_13_nonlist_proposals(self):
        self.assertIn('PROPOSALS_LIST_REQUIRED',gate.review_preflight(sample(),{})['errors'])
    def test_14_duplicate_packet(self):
        p=sample(); p.append(copy.deepcopy(p[0]))
        self.assertTrue(any('DUPLICATE_SOURCE_PACKET' in x for x in gate.review_preflight(p)['errors']))
    def test_15_duplicate_proposal(self):
        p=sample(); x=proposals(p); x.append(copy.deepcopy(x[0]))
        self.assertTrue(any('DUPLICATE_PROPOSAL' in e for e in gate.review_preflight(p,x)['errors']))
    def test_16_missing_packet(self):
        self.assertIn('EXACT_FOUR_QUARANTINED_SOURCES_REQUIRED',gate.review_preflight(sample()[1:])['errors'])
    def test_17_missing_proposal(self):
        self.assertEqual(gate.review_preflight(sample(),[])['proposals_received'],0)
    def test_18_unauthenticated_reviewer(self):
        d=gate.review_preflight(sample(),proposals(sample()))
        self.assertFalse(d['reviewer_identity_authenticated'])
    def test_19_unchanged_claim_guards(self):
        d=gate.review_preflight(sample()); self.assertEqual(d['outstanding_editorial_conflicts'],15)
        self.assertEqual(d['outstanding_article15_tool104_reviews'],17)
    def test_21_cross_source_ticket_identity_collision(self):
        p=sample(); p[1]['citations'][0]['ticket_id']=p[0]['citations'][0]['ticket_id']
        self.assertIn('CROSS_SOURCE_DUPLICATE_CITATION_TICKET',gate.review_preflight(p)['errors'])
    def test_20_docket_digests(self):
        d=gate.review_preflight(sample()); self.assertTrue(all(len(x['packet_sha256'])==64 for x in d['docket']))


def make_packet_case(label,fn,needle):
    def check(self):
        p=copy.deepcopy(sample())
        fn(p)
        d=gate.review_preflight(p)
        self.assertTrue(any(needle in e for e in d['errors']), (label,d['errors']))
        self.assertEqual(d['state'],'INVALID_HARD_HOLD')
    setattr(Core,'test_packet_'+label,check)


def make_proposal_case(label,fn,needle):
    def check(self):
        p=sample(); proposals_ = proposals(p)
        fn(proposals_)
        d=gate.review_preflight(p,proposals_)
        self.assertTrue(any(needle in e for e in d['errors']),(label,d['errors']))
        self.assertEqual(d['state'],'INVALID_HARD_HOLD')
    setattr(Core,'test_proposal_'+label,check)


packet_cases = {
    'fake_approval':(lambda p:p[0].update(candidate_selected='first'),'FORGED_PACKET_APPROVAL'),
    'fake_qd':(lambda p:p[0].update(human_claim_source_adjudication='QD_PASS'),'FORGED_PACKET_APPROVAL'),
    'fake_review_disposition':(lambda p:p[0].update(review_disposition='APPROVED'),'FORGED_PACKET_APPROVAL'),
    'missing_variants':(lambda p:p[0].pop('verified_variants'),'EXACTLY_TWO_SOURCE_VARIANTS_REQUIRED'),
    'one_variant':(lambda p:p[0]['verified_variants'].pop(),'EXACTLY_TWO_SOURCE_VARIANTS_REQUIRED'),
    'extra_variant':(lambda p:p[0]['verified_variants'].append(copy.deepcopy(p[0]['verified_variants'][0])),'EXACTLY_TWO_SOURCE_VARIANTS_REQUIRED'),
    'fake_link':(lambda p:p[0]['verified_variants'][0].update(human_link_check_established=True),'FORGED_LINK_REVIEW'),
    'missing_link':(lambda p:p[0]['verified_variants'][0].pop('human_link_check_established'),'FORGED_LINK_REVIEW'),
    'invalid_variant_hash':(lambda p:p[0]['verified_variants'][0].update(source_record_sha256='wrong'),'INVALID_VARIANT_DIGEST'),
    'nontext_source_path':(lambda p:p[0]['verified_variants'][0].update(source_file=None),'INVALID_VARIANT'),
    'duplicate_variant_path':(lambda p:p[0]['verified_variants'][1].update(source_file=p[0]['verified_variants'][0]['source_file']),'DUPLICATE_VARIANT_PATH'),
    'zero_claims':(lambda p:p[0].update(citations=[]),'UNREVIEWED_CLAIMS_REQUIRED'),
    'missing_claims':(lambda p:p[0].pop('citations'),'UNREVIEWED_CLAIMS_REQUIRED'),
    'fake_claim_clearance':(lambda p:p[0]['citations'][0].update(unreviewed_only=False),'FORGED_CLAIM_CLEARANCE'),
    'missing_claim_unreviewed':(lambda p:p[0]['citations'][0].pop('unreviewed_only'),'FORGED_CLAIM_CLEARANCE'),
    'path_traversal':(lambda p:p[0]['citations'][0].update(document='tools/../../wallet'),'INVALID_DOCUMENT_ID'),
    'bad_ticket':(lambda p:p[0]['citations'][0].update(ticket_id='bad'),'INVALID_OR_DUPLICATE_TICKET'),
    'duplicate_ticket':(lambda p:p[0]['citations'].append(copy.deepcopy(p[0]['citations'][0])),'INVALID_OR_DUPLICATE_TICKET'),
    'bad_claim_hash':(lambda p:p[0]['citations'][0].update(claim_text_sha256='wrong'),'INVALID_CLAIM_FINGERPRINT'),
    'missing_impact_count':(lambda p:p[0].update(claim_tickets_impacted=0),'IMPACT_COUNT_OR_DOCUMENT_DRIFT'),
    'missing_doc_inventory':(lambda p:p[0].update(impacted_document_ids=[]),'IMPACT_COUNT_OR_DOCUMENT_DRIFT'),
    'unknown_source':(lambda p:p[0].update(source_id='unrecognized'),'UNKNOWN_REVIEW_SOURCE'),
    'unapproved_variant_file':(lambda p:p[0]['verified_variants'][0].update(source_file='fragments/evil.json'),'SOURCE_VARIANT_FILE_PROVENANCE_DRIFT'),
    'duplicate_variant_digest':(lambda p:p[0]['verified_variants'][0].update(source_record_sha256=p[0]['verified_variants'][1]['source_record_sha256']),'DUPLICATE_VARIANTS'),
    'null_packet':(lambda p:p.__setitem__(0,None),'INVALID_REVIEW_PACKET'),
}
for label,(mut,needle) in packet_cases.items(): make_packet_case(label,mut,needle)

proposal_cases = {
    'fake_pass':(lambda x:x[0].update(disposition='QD_PASS'),'FORGED_APPROVAL_DISPOSITION'),
    'other_disposition':(lambda x:x[0].update(disposition='ACCEPTED'),'FORGED_APPROVAL_DISPOSITION'),
    'stale_packet':(lambda x:x[0].update(packet_sha256='0'*64),'STALE_OR_FORGED_PACKET_BINDING'),
    'missing_packet_hash':(lambda x:x[0].pop('packet_sha256'),'UNAUTHORIZED_OR_MISSING_PROPOSAL_FIELDS'),
    'fake_variant':(lambda x:x[0].update(proposed_variant_sha256='0'*64),'UNKNOWN_VARIANT_SELECTION'),
    'null_variant':(lambda x:x[0].update(proposed_variant_sha256=None),'UNKNOWN_VARIANT_SELECTION'),
    'missing_ticket':(lambda x:x[0].update(ticket_bindings={}),'MISSING_OR_STALE_CLAIM_BINDINGS'),
    'wrong_ticket_hash':(lambda x:x[0].update(ticket_bindings={k:'0'*64 for k in x[0]['ticket_bindings']}),'MISSING_OR_STALE_CLAIM_BINDINGS'),
    'new_ticket':(lambda x:x[0]['ticket_bindings'].update({'f'*24:'0'*64}),'MISSING_OR_STALE_CLAIM_BINDINGS'),
    'empty_note':(lambda x:x[0].update(proposal_note=''),'MISSING_OR_UNSAFE_REVIEW_RATIONALE'),
    'short_note':(lambda x:x[0].update(proposal_note='too short'),'MISSING_OR_UNSAFE_REVIEW_RATIONALE'),
    'long_note':(lambda x:x[0].update(proposal_note='x'*801),'MISSING_OR_UNSAFE_REVIEW_RATIONALE'),
    'control_note':(lambda x:x[0].update(proposal_note='x'*40+'\x00'),'MISSING_OR_UNSAFE_REVIEW_RATIONALE'),
    'extra_field':(lambda x:x[0].update(qualified_qd_pass=True),'UNAUTHORIZED_OR_MISSING_PROPOSAL_FIELDS'),
    'extra_reviewer':(lambda x:x[0].update(reviewer_authenticated=True),'UNAUTHORIZED_OR_MISSING_PROPOSAL_FIELDS'),
    'omit_disposition':(lambda x:x[0].pop('disposition'),'UNAUTHORIZED_OR_MISSING_PROPOSAL_FIELDS'),
    'unknown_source':(lambda x:x[0].update(source_id='not-a-source'),'UNKNOWN_PROPOSAL_SOURCE'),
    'nonmapping':(lambda x:x.__setitem__(0,None),'INVALID_PROPOSAL'),
}
for label,(mut,needle) in proposal_cases.items(): make_proposal_case(label,mut,needle)

# Four independent sources x three separately exercised proposal tampering cases.
for idx,sid in enumerate(gate.EXPECTED_IDS):
    def ticket_loss(x,idx=idx): x[idx].update(ticket_bindings={})
    make_proposal_case('ticket_loss_'+sid.replace('-','_'),ticket_loss,'MISSING_OR_STALE_CLAIM_BINDINGS')
    def stale_packet(x,idx=idx): x[idx].update(packet_sha256='a'*64)
    make_proposal_case('stale_packet_'+sid.replace('-','_'),stale_packet,'STALE_OR_FORGED_PACKET_BINDING')
    def fake_approval(x,idx=idx): x[idx].update(disposition='RELEASED')
    make_proposal_case('false_approval_'+sid.replace('-','_'),fake_approval,'FORGED_APPROVAL_DISPOSITION')


if __name__=='__main__': unittest.main()
