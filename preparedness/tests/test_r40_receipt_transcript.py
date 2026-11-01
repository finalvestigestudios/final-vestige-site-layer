"""R40: isolated 80+ receipt-custody tests; synthetic keys, no source approvals."""
import copy
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import reviewer_receipt_chain_gate as r39
import reviewer_receipt_transcript_gate as r40
from test_r38_quarantine_synthetic import fixture, mutate_csv

KEY='synthetic-reviewer-001'
SECRET=b'R40-SYNTHETIC-TEST-KEY-NEVER-USE-IN-PRODUCTION'
NOW=datetime(2026,11,1,7,44,tzinfo=timezone.utc)
GENESIS={'sequence':0,'receipt_sha256':r39.ZERO_HEAD}

def keys():
    return {KEY:{'secret':SECRET,'state':'ACTIVE','scope':r39.KEY_SCOPE,
                 'not_before':'2026-10-01T00:00:00Z',
                 'not_after':'2026-12-01T00:00:00Z'}}

def batch(n=2, *, nonces=None, stamps=None):
    b=fixture(); head=copy.deepcopy(GENESIS); entries=[]
    for i in range(n):
        edits=mutate_csv(b,'human_scope_risk_notes','Unreviewed note '+str(i),
                         state='FLAGGED_FOR_FACT_CHECK')
        ch=r39.unsigned_challenge(b,edits)
        env=r39.prepare_unsigned_receipt(
            ch,reviewer_key_id=KEY,
            submission_nonce_hex=(nonces or [f'{j+1:032x}' for j in range(n)])[i],
            issued_at_utc=(stamps or ['2026-11-01T07:43:00Z']*n)[i],
            trusted_chain_head=head)
        receipt=r39.sign_progress_receipt(env,SECRET)
        entries.append({'edited_csv_tables':edits,'receipt':receipt})
        head={'sequence':head['sequence']+1,'receipt_sha256':r39.digest(receipt)}
    return b,entries,head

def check(b,entries,end,**opts):
    return r40.audit_recent_segment(
        b,entries,trusted_registry=opts.get('registry',keys()),
        trusted_start_head=opts.get('start',GENESIS),
        trusted_end_head=end,trusted_prior_nonces=opts.get('seen',frozenset()),
        trusted_now=opts.get('now',NOW))

def rejects(b,entries,end,**opts):
    with unittest.TestCase().assertRaises(r40.TranscriptHold):
        check(b,entries,end,**opts)

class Good(unittest.TestCase):
    def setUp(self):self.b,self.entries,self.end=batch()
    def test_two_signed_receipts(self):
        self.assertEqual(check(self.b,self.entries,self.end)
                         ['verified_key_possession_receipt_count'],2)
    def test_single_signed_receipt(self):
        b,e,h=batch(1)
        self.assertEqual(check(b,e,h)['verified_key_possession_receipt_count'],1)
    def test_original_r37_bound(self):
        self.assertEqual(check(self.b,self.entries,self.end)
                         ['parent_R37_fingerprint_sha256'],
                         self.b['manifest']['fingerprint_sha256'])
    def test_end_anchor_bound(self):
        self.assertEqual(check(self.b,self.entries,self.end)
                         ['externally_pinned_end_head'],self.end)
    def test_crypto_receipts_match(self):
        self.assertEqual(check(self.b,self.entries,self.end)['verified_receipt_sha256'],
                         [r39.digest(s['receipt']) for s in self.entries])
    def test_report_deterministic(self):
        self.assertEqual(check(self.b,self.entries,self.end),
                         check(self.b,self.entries,self.end))
    def test_report_hash_correct(self):
        r=check(self.b,self.entries,self.end)
        self.assertEqual(r['fingerprint_sha256'],r39.digest(
            {k:v for k,v in r.items() if k!='fingerprint_sha256'}))
    def test_original_inputs_unchanged(self):
        old=copy.deepcopy((self.b,self.entries,self.end))
        check(self.b,self.entries,self.end)
        self.assertEqual(old,(self.b,self.entries,self.end))
    def test_nonce_additions_not_automatically_persisted(self):
        s=frozenset();report=check(self.b,self.entries,self.end,seen=s)
        self.assertEqual(len(report['proposed_nonce_additions']),2)
        self.assertFalse(s)
    def test_works_with_unverified_risk_escalation(self):
        self.assertEqual(check(self.b,self.entries,self.end)
                         ['unverified_annotation_records_per_receipt'],[1,1])
    def test_zero_progress_ci_baseline(self):
        ch=r39.unsigned_challenge(self.b,self.b['csv_tables'])
        report=r40.preflight_unsigned_baseline(self.b,ch)
        self.assertEqual(report['verified_human_receipts'],0)
        self.assertFalse(report['key_possession_verified'])
    def test_machine_gates_all_hold(self):
        report=check(self.b,self.entries,self.end)
        for f in ('may_publish','qualified_safety_clearance',
                  'independent_QD_approval','source_claim_accuracy_verified',
                  'human_source_reviews_completed','reviewer_real_identity_verified'):
            self.assertIs(report[f],False)
    def test_unreviewed_remains_hold(self):
        self.assertEqual(check(self.b,self.entries,self.end)['release_state'],'HOLD')

class Bad(unittest.TestCase):
    def setUp(self):self.b,self.entries,self.end=batch()
    def test_empty(self):rejects(self.b,[],self.end)
    def test_tuple_not_list(self):rejects(self.b,tuple(self.entries),self.end)
    def test_missing_end(self):rejects(self.b,self.entries,{})
    def test_missing_start(self):rejects(self.b,self.entries,self.end,start={})
    def test_wrong_end_sequence(self):
        rejects(self.b,self.entries,{**self.end,'sequence':3})
    def test_wrong_end_hash(self):
        rejects(self.b,self.entries,{**self.end,'receipt_sha256':'f'*64})
    def test_drop_one(self):rejects(self.b,self.entries[:1],self.end)
    def test_duplicate_entry(self):rejects(self.b,[self.entries[0]]*2,self.end)
    def test_reordered(self):rejects(self.b,list(reversed(self.entries)),self.end)
    def test_wrong_entry_shape(self):
        bad=copy.deepcopy(self.entries);bad[0]['untrusted_pass']=True
        rejects(self.b,bad,self.end)
    def test_no_receipt(self):
        bad=copy.deepcopy(self.entries);bad[0].pop('receipt')
        rejects(self.b,bad,self.end)
    def test_original_source_tamper(self):
        b=copy.deepcopy(self.b);b['manifest']['fingerprint_sha256']='a'*64
        rejects(b,self.entries,self.end)
    def test_edited_observation_tamper(self):
        bad=copy.deepcopy(self.entries)
        bad[0]['edited_csv_tables']=mutate_csv(self.b,'human_scope_risk_notes',
                                               'changed since signing',state='IN_PROGRESS')
        rejects(self.b,bad,self.end)
    def test_missing_registry(self):rejects(self.b,self.entries,self.end,registry={})
    def test_revoked_registry(self):
        k=keys();k[KEY]['state']='REVOKED'
        rejects(self.b,self.entries,self.end,registry=k)
    def test_wrong_registry_scope(self):
        k=keys();k[KEY]['scope']='PUBLICATION'
        rejects(self.b,self.entries,self.end,registry=k)
    def test_short_registry_key(self):
        k=keys();k[KEY]['secret']=b'weak'
        rejects(self.b,self.entries,self.end,registry=k)
    def test_duplicate_nonce_across_segment(self):
        b,e,h=batch(nonces=['b'*32,'b'*32]);rejects(b,e,h)
    def test_nonce_exists_externally(self):
        rejects(self.b,self.entries,self.end,
                seen=frozenset({(KEY,self.entries[0]['receipt']['submission_nonce_hex'])}))
    def test_stale(self):rejects(self.b,self.entries,self.end,now=NOW+timedelta(days=2))
    def test_naive_clock(self):
        rejects(self.b,self.entries,self.end,now=NOW.replace(tzinfo=None))
    def test_out_of_order_issue_times(self):
        b,e,h=batch(stamps=['2026-11-01T07:43:00Z','2026-11-01T07:42:00Z'])
        rejects(b,e,h)
    def test_unreviewed_ci_challenge_tampered(self):
        ch=r39.unsigned_challenge(self.b,self.b['csv_tables'])
        ch['may_publish']=True
        with self.assertRaises(r40.TranscriptHold):
            r40.preflight_unsigned_baseline(self.b,ch)
    def test_zero_progress_cannot_be_signed_as_review(self):
        ch=r39.unsigned_challenge(self.b,self.b['csv_tables'])
        env=r39.prepare_unsigned_receipt(ch,reviewer_key_id=KEY,
                  submission_nonce_hex='d'*32,issued_at_utc='2026-11-01T07:43:00Z',
                  trusted_chain_head=GENESIS)
        receipt=r39.sign_progress_receipt(env,SECRET)
        end={'sequence':1,'receipt_sha256':r39.digest(receipt)}
        rejects(self.b,[{'edited_csv_tables':self.b['csv_tables'],
                         'receipt':receipt}],end)

MUTATIONS={
 'schema_version':2,'issue':999,'release_state':'PUBLISHED',
 'machine_authority':'SURELY_APPROVED',
 'parent_R37_fingerprint_sha256':'a'*64,
 'parent_R38_fingerprint_sha256':'b'*64,
 'original_R34_R35_R36_lineage_sha256':'c'*64,
 'edited_worksheet_manifest_sha256':'d'*64,
 'quarantined_observations_sha256':'e'*64,
 'unverified_progress_records':44,
 'source_claim_accuracy_verified':True,
 'human_source_reviews_completed':True,
 'qualified_safety_clearance':True,
 'independent_QD_approval':True,
 'may_publish':True,'challenge_sha256':'a'*64,
 'reviewer_key_id':'intruder-key','submission_nonce_hex':'x'*32,
 'issued_at_utc':'2026-02-30T07:43:00Z','sequence':99,
 'previous_receipt_sha256':'9'*64,'signature_algorithm':'MD5',
 'signature_hex':'f'*64,
}
for _field,_value in MUTATIONS.items():
    def changed(self,field=_field,value=_value):
        e=copy.deepcopy(self.entries);e[0]['receipt'][field]=value
        rejects(self.b,e,self.end)
    setattr(Bad,'test_mutated_'+_field,changed)
    def missing(self,field=_field):
        e=copy.deepcopy(self.entries);e[0]['receipt'].pop(field)
        rejects(self.b,e,self.end)
    setattr(Bad,'test_missing_'+_field,missing)
for _label,_value in {
    'list':[], 'set':set(), 'none':None,
    'bad_key':frozenset({('!!bad','a'*32)}),
    'bad_nonce':frozenset({(KEY,'Z'*32)}),
    'wrong_type':frozenset({'text'}),
    'short_tuple':frozenset({(KEY,)}),
    'long_tuple':frozenset({(KEY,'a'*32,'extra')}),
    'int_nonce':frozenset({(KEY,100)})
}.items():
    def untrusted(self,value=_value):
        rejects(self.b,self.entries,self.end,seen=value)
    setattr(Bad,'test_untrusted_prior_nonces_'+_label,untrusted)
if __name__=='__main__':unittest.main()
