"""R41 synthetic retrospective custody tests. NO verified human or source advice."""
import copy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import reviewer_receipt_history_gate as h

PARENT='a'*64
KEY='synthetic-reviewer-001'

def seed():
    return h.genesis(PARENT)

def mock_record(previous, nonce=1, n=2):
    """ONLY synthetic test anatomy; has no signed/verifiable R39 key evidence."""
    start=copy.deepcopy(previous['receipt_chain_head'])
    submissions=[]; hashes=[]; pairs=[]
    for i in range(n):
        receipt={'reviewer_key_id':KEY,
                 'submission_nonce_hex':f'{nonce+i:032x}',
                 'sequence':start['sequence']+i+1,
                 'previous_receipt_sha256':start['receipt_sha256'] if i==0 else hashes[-1],
                 'synthetic_unverified_note':f'no-source-approval-{i}'}
        submissions.append({'edited_csv_tables':{'synthetic':f'UNVERIFIED-{i}'},
                            'receipt':receipt})
        hashes.append(h.digest(receipt))
        pairs.append([KEY,receipt['submission_nonce_hex']])
    report={'schema_version':1,'issue':136,'release_state':'HOLD',
            'machine_authority':h.R40_AUTHORITY,
            'parent_R37_fingerprint_sha256':PARENT,
            'verified_key_possession_receipt_count':n,
            'unverified_annotation_records_per_receipt':[1]*n,
            'original_trusted_start_head':start,
            'externally_pinned_end_head':{'sequence':start['sequence']+n,
                                         'receipt_sha256':hashes[-1]},
            'verified_receipt_sha256':hashes,
            'proposed_nonce_additions':pairs,
            **{f:False for f in h.FLAGS}}
    report['fingerprint_sha256']=h.digest(report)
    record={'schema_version':1,'issue':136,'release_state':'HOLD',
            'machine_authority':h.AUTHORITY,
            'previous_archive_head':copy.deepcopy(previous),
            'r40_audit_report':report,
            'complete_private_submissions':submissions,
            'submissions_sha256':h.digest(submissions),
            **{f:False for f in h.FLAGS}}
    record['record_sha256']=h.digest(record)
    nexthead={'event_index':previous['event_index']+1,
              'archive_tip_sha256':record['record_sha256'],
              'receipt_chain_head':report['externally_pinned_end_head'],
              'parent_R37_fingerprint_sha256':PARENT}
    return record,nexthead

def chain(n=2):
    original=seed(); head=original; rows=[]
    for i in range(n):
        r,head=mock_record(head,nonce=1+i*10,n=2)
        rows.append(r)
    return original,rows,head

def inspect(start, rows, end, *, nonces=frozenset()):
    return h.audit_archive_segment(rows, trusted_start_head=start,
                                   trusted_end_head=end,
                                   trusted_prior_nonces=nonces)

def reject(start,rows,end,*,nonces=frozenset()):
    with unittest.TestCase().assertRaises(h.HistoryHold):
        inspect(start,rows,end,nonces=nonces)

def reseal(rec):
    rec['submissions_sha256']=h.digest(rec['complete_private_submissions'])
    rec['r40_audit_report']['fingerprint_sha256']=h.digest(
        {k:v for k,v in rec['r40_audit_report'].items() if k!='fingerprint_sha256'})
    rec['record_sha256']=h.digest({k:v for k,v in rec.items() if k!='record_sha256'})

def fix_end(rows,original):
    # Used only to test stronger invariants even after synthetics are rehashed.
    prev=original
    for r in rows:
        r['previous_archive_head']=copy.deepcopy(prev)
        reseal(r)
        prev={'event_index':prev['event_index']+1,
              'archive_tip_sha256':r['record_sha256'],
              'receipt_chain_head':copy.deepcopy(r['r40_audit_report']['externally_pinned_end_head']),
              'parent_R37_fingerprint_sha256':PARENT}
    return prev

class GoodHistory(unittest.TestCase):
    def setUp(self):self.s,self.r,self.e=chain()
    def test_two_archived_segments(self):
        self.assertEqual(inspect(self.s,self.r,self.e)['verified_history_record_count'],2)
    def test_signed_receipts_retained(self):
        self.assertEqual(inspect(self.s,self.r,self.e)['retained_signed_receipt_count'],4)
    def test_private_submissions_retained(self):
        self.assertTrue(inspect(self.s,self.r,self.e)['retained_complete_private_submissions'])
    def test_archival_tip_matched(self):
        self.assertEqual(inspect(self.s,self.r,self.e)['externally_pinned_end_head'],self.e)
    def test_report_is_deterministic(self):
        self.assertEqual(inspect(self.s,self.r,self.e),inspect(self.s,self.r,self.e))
    def test_original_inputs_not_mutated(self):
        original=copy.deepcopy((self.s,self.r,self.e))
        inspect(self.s,self.r,self.e)
        self.assertEqual((self.s,self.r,self.e),original)
    def test_exact_hash_history(self):
        self.assertEqual(inspect(self.s,self.r,self.e)['record_sha256'],
                         [x['record_sha256'] for x in self.r])
    def test_all_flags_remain_false(self):
        z=inspect(self.s,self.r,self.e)
        for flag in h.FLAGS:self.assertIs(z[flag],False)
    def test_pinned_single(self):
        one=self.r[0]
        end={'event_index':1,'archive_tip_sha256':one['record_sha256'],
             'receipt_chain_head':one['r40_audit_report']['externally_pinned_end_head'],
             'parent_R37_fingerprint_sha256':PARENT}
        self.assertEqual(inspect(self.s,[one],end)['retained_signed_receipt_count'],2)
    def test_non_genesis_segment_with_trusted_prior(self):
        mid=self.r[1]['previous_archive_head']
        prior=frozenset(tuple(x) for x in self.r[0]['r40_audit_report']['proposed_nonce_additions'])
        self.assertEqual(inspect(mid,[self.r[1]],self.e,nonces=prior)['verified_history_record_count'],1)
    def test_separate_key_same_nonce_can_coexist(self):
        r,e=mock_record(self.e,nonce=99,n=1)
        r['complete_private_submissions'][0]['receipt']['reviewer_key_id']='other-synthetic-key'
        r['r40_audit_report']['proposed_nonce_additions'][0][0]='other-synthetic-key'
        r['r40_audit_report']['verified_receipt_sha256'][0]=h.digest(r['complete_private_submissions'][0]['receipt'])
        r['r40_audit_report']['externally_pinned_end_head']['receipt_sha256']=r['r40_audit_report']['verified_receipt_sha256'][0]
        reseal(r)
        e={'event_index':3,'archive_tip_sha256':r['record_sha256'],
           'receipt_chain_head':r['r40_audit_report']['externally_pinned_end_head'],
           'parent_R37_fingerprint_sha256':PARENT}
        prior=frozenset({('synthetic-reviewer-001',f'{99:032x}')})
        self.assertEqual(inspect(self.e,[r],e,nonces=prior)['retained_signed_receipt_count'],1)
    def test_report_digest_self_consistent(self):
        z=inspect(self.s,self.r,self.e)
        self.assertEqual(z['fingerprint_sha256'], h.digest({k:v for k,v in z.items() if k!='fingerprint_sha256'}))
    def test_anchored_source_parent(self):
        self.assertEqual(inspect(self.s,self.r,self.e)['original_trusted_start_head']['parent_R37_fingerprint_sha256'],PARENT)

class BadHistory(unittest.TestCase):
    def setUp(self):self.s,self.r,self.e=chain()
    def test_empty_history(self):reject(self.s,[],self.e)
    def test_tuple_history(self):reject(self.s,tuple(self.r),self.e)
    def test_too_many_records(self):reject(self.s,self.r*65,self.e)
    def test_missing_start(self):reject({},self.r,self.e)
    def test_missing_end(self):reject(self.s,self.r,{})
    def test_false_end_tip(self):reject(self.s,self.r,{**self.e,'archive_tip_sha256':'b'*64})
    def test_false_end_sequence(self):reject(self.s,self.r,{**self.e,'event_index':3})
    def test_truncate(self):reject(self.s,self.r[:1],self.e)
    def test_reorder(self):reject(self.s,list(reversed(self.r)),self.e)
    def test_duplicate_record(self):reject(self.s,[self.r[0]]*2,self.e)
    def test_untrusted_prior_nonce_type(self):reject(self.s,self.r,self.e,nonces=set())
    def test_malformed_prior_nonce(self):reject(self.s,self.r,self.e,nonces=frozenset({'bad'}))
    def test_known_replay(self):
        reject(self.s,self.r,self.e,nonces=frozenset({(KEY,f'{1:032x}')}))
    def test_source_parent_substitution(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['parent_R37_fingerprint_sha256']='b'*64
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_change_notes(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][0]['edited_csv_tables']['synthetic']='tampered'
        reject(self.s,r,self.e)
    def test_change_signed_receipt(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][0]['receipt']['reviewer_key_id']='other-key'
        reject(self.s,r,self.e)
    def test_delete_full_evidence(self):
        r=copy.deepcopy(self.r);del r[0]['complete_private_submissions']
        reject(self.s,r,self.e)
    def test_drop_signed_receipt(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'].pop()
        reject(self.s,r,self.e)
    def test_remove_parent_chain(self):
        r=copy.deepcopy(self.r);del r[0]['previous_archive_head']
        reject(self.s,r,self.e)
    def test_add_pass_field(self):
        r=copy.deepcopy(self.r);r[0]['QD_PASS']='fake'
        reject(self.s,r,self.e)
    def test_r40_false_claim(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['may_publish']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_archive_false_claim(self):
        r=copy.deepcopy(self.r);r[0]['qualified_safety_clearance']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_invented_reviewer_identity(self):
        r=copy.deepcopy(self.r);r[0]['reviewer_real_identity_verified']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_valid_archive_fp_but_missing_r40_fp(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['fingerprint_sha256']='b'*64
        r[0]['record_sha256']=h.digest({k:v for k,v in r[0].items() if k!='record_sha256'})
        reject(self.s,r,self.e)
    def test_report_authority_tamper(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['machine_authority']='FAKE_PASS'
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_mismatched_original_start_anchor(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['original_trusted_start_head']['receipt_sha256']='b'*64
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_duplicate_nonce_after_reseal(self):
        r=copy.deepcopy(self.r)
        # Keep the R39 hash chain internally consistent while intentionally reusing a key/nonce.
        r[0]['complete_private_submissions'][1]['receipt']['submission_nonce_hex']=f'{1:032x}'
        r[0]['r40_audit_report']['proposed_nonce_additions'][1]=[KEY,f'{1:032x}']
        rec=r[0]['complete_private_submissions'][1]['receipt']
        r[0]['r40_audit_report']['verified_receipt_sha256'][1]=h.digest(rec)
        r[0]['r40_audit_report']['externally_pinned_end_head']['receipt_sha256']=h.digest(rec)
        e=fix_end(r[:1],self.s);reject(self.s,r[:1],e)
    def test_invalid_receipt_previous(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][1]['receipt']['previous_receipt_sha256']='b'*64
        r[0]['r40_audit_report']['verified_receipt_sha256'][1]=h.digest(r[0]['complete_private_submissions'][1]['receipt'])
        r[0]['r40_audit_report']['externally_pinned_end_head']['receipt_sha256']=r[0]['r40_audit_report']['verified_receipt_sha256'][1]
        e=fix_end(r[:1],self.s);reject(self.s,r[:1],e)
    def test_history_identity_wrong(self):
        r=copy.deepcopy(self.r);r[0]['issue']=999
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_r40_wrong_issue(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['issue']=999
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_r40_wrong_count(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['verified_key_possession_receipt_count']=3
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_r40_notes_fabricated_zero(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['unverified_annotation_records_per_receipt'][0]=0
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_receipt_nonce_mismatch(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['proposed_nonce_additions'][0][1]='a'*32
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_extra_field_in_original_submission(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][0]['approved']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_missing_csv(self):
        r=copy.deepcopy(self.r);del r[0]['complete_private_submissions'][0]['edited_csv_tables']
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_noncanonical_digest_rejected(self):
        with self.assertRaises(h.HistoryHold):h.digest({'bad':float('nan')})
    def test_false_archive_head_bool_index(self):
        s=copy.deepcopy(self.s);s['event_index']=False
        reject(s,self.r,self.e)
    def test_untrustworthy_head_zero(self):
        s=copy.deepcopy(self.s);s['parent_R37_fingerprint_sha256']=h.ZERO
        reject(s,self.r,self.e)
    def test_genesis_wrong_receipt(self):
        s=copy.deepcopy(self.s);s['receipt_chain_head']['sequence']=1
        reject(s,self.r,self.e)
    def test_genesis_wrong_tip(self):
        s=copy.deepcopy(self.s);s['archive_tip_sha256']='b'*64
        reject(s,self.r,self.e)
    def test_production_source_identity_must_not_be_approved(self):
        r=copy.deepcopy(self.r);r[0]['source_claim_accuracy_verified']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_signed_history_cannot_be_unsigned(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][0]['receipt']={}
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_remove_nonce_list(self):
        r=copy.deepcopy(self.r);del r[0]['r40_audit_report']['proposed_nonce_additions']
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_wrong_trusted_end_digest_even_after_reseal(self):
        r=copy.deepcopy(self.r);r[-1]['complete_private_submissions'][-1]['receipt']['synthetic_unverified_note']='new'
        e=fix_end(r,self.s);reject(self.s,r,self.e)
    def test_history_source_record_chain_break(self):
        r=copy.deepcopy(self.r);r[1]['previous_archive_head']['archive_tip_sha256']='b'*64
        reseal(r[1]);reject(self.s,r,self.e)
    def test_missing_first_report(self):
        r=copy.deepcopy(self.r);del r[0]['r40_audit_report']
        reject(self.s,r,self.e)
    def test_source_parent_drift(self):
        r=copy.deepcopy(self.r);r[0]['previous_archive_head']['parent_R37_fingerprint_sha256']='c'*64
        reseal(r[0]);reject(self.s,r,self.e)
    def test_nonce_register_cannot_be_mutable(self):
        reject(self.s,self.r,self.e,nonces=[(KEY,f'{1:032x}')])
    def test_unknown_extra_report_flag(self):
        r=copy.deepcopy(self.r);r[0]['r40_audit_report']['independent_QD_approval']=True
        e=fix_end(r,self.s);reject(self.s,r,e)
    def test_sequence_is_not_bool(self):
        r=copy.deepcopy(self.r);r[0]['complete_private_submissions'][0]['receipt']['sequence']=True
        e=fix_end(r,self.s);reject(self.s,r,e)

class Preflight(unittest.TestCase):
    def baseline(self):
        return {'issue':136,'release_state':'HOLD',
                'machine_authority':'R40_UNSIGNED_ZERO_PROGRESS_CUSTODY_ONLY',
                'verified_human_receipts':0,'key_possession_verified':False,
                'reviewer_real_identity_verified':False,
                'parent_R37_fingerprint_sha256':PARENT,
                'challenge_sha256':'b'*64,
                **{flag:False for flag in h.FLAGS}}
    def test_zero_progress(self):
        z=h.preflight_unsigned_history(self.baseline())
        self.assertEqual(z['archived_signed_receipt_records'],0)
        self.assertFalse(z['trusted_external_ledger_present'])
    def test_digest_fingerprinted(self):
        z=h.preflight_unsigned_history(self.baseline())
        self.assertEqual(z['fingerprint_sha256'],h.digest({k:v for k,v in z.items() if k!='fingerprint_sha256'}))
    def test_no_review(self):
        z=h.preflight_unsigned_history(self.baseline())
        for flag in h.FLAGS:self.assertIs(z[flag],False)
    def test_reject_fake_receipt(self):
        b=self.baseline();b['verified_human_receipts']=1
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_reject_fake_QD(self):
        b=self.baseline();b['independent_QD_approval']=True
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_reject_fake_safety(self):
        b=self.baseline();b['qualified_safety_clearance']=True
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_reject_fake_source_review(self):
        b=self.baseline();b['source_claim_accuracy_verified']=True
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_reject_fake_reviewer(self):
        b=self.baseline();b['reviewer_real_identity_verified']=True
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_reject_missing_parent(self):
        b=self.baseline();del b['parent_R37_fingerprint_sha256']
        with self.assertRaises(h.HistoryHold):h.preflight_unsigned_history(b)
    def test_genesis_reject_none(self):
        with self.assertRaises(h.HistoryHold):h.genesis(None)
    def test_genesis_does_not_impersonate_receipts(self):
        z=h.genesis(PARENT)
        self.assertEqual(z['receipt_chain_head']['sequence'],0)
        self.assertEqual(z['archive_tip_sha256'],h.ZERO)

# Native hosted suite executes full R37/R38/R39/R40 integration. The local
# engineering snapshot contains only R40, so it cannot falsely claim a native
# 81-file checkout. Optional integration is exercised when available.
try:
    from test_r40_receipt_transcript import batch, keys, NOW, GENESIS
except ImportError:
    batch=keys=NOW=GENESIS=None

@unittest.skipIf(batch is None, 'complete real R37-R40 fixture chain unavailable')
class IntegratedRecent(unittest.TestCase):
    def test_actual_r40_approval_free_append(self):
        b,receipts,end=batch(2)
        proposal=h.append_recent_candidate(
            b,receipts,trusted_registry=keys(),
            trusted_archive_head=h.genesis(b['manifest']['fingerprint_sha256']),
            trusted_end_receipt_head=end,trusted_prior_nonces=frozenset(),trusted_now=NOW)
        self.assertFalse(proposal['independently_atomic_commit_performed'])
        original=h.genesis(b['manifest']['fingerprint_sha256'])
        check=h.audit_archive_segment([proposal['record_uncommitted']],
              trusted_start_head=original,
              trusted_end_head=proposal['proposed_next_archive_head'],
              trusted_prior_nonces=frozenset())
        self.assertEqual(check['retained_signed_receipt_count'],2)
        self.assertFalse(check['may_publish'])
    def test_real_r40_rejects_wrong_nonce(self):
        b,receipts,end=batch(1)
        with self.assertRaises(h.HistoryHold):
            h.append_recent_candidate(b,receipts,trusted_registry=keys(),
                trusted_archive_head=h.genesis(b['manifest']['fingerprint_sha256']),
                trusted_end_receipt_head=end,
                trusted_prior_nonces=frozenset({(KEY,'00000000000000000000000000000001')}),
                trusted_now=NOW)

if __name__=='__main__':unittest.main()
