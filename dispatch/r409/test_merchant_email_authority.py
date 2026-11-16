import copy
import unittest
from datetime import date, timedelta
from merchant_email_authority import audit, AUTHORITY, REQUIRED, PARTNER_KINDS

TODAY = date(2026,11,16)

def record(kind, product="ZEN12"):
    return {"kind":kind,"product":product,"authority":AUTHORITY[kind],"proof_ref":"case-qa-opaque-00012", "reviewed_on":"2026-11-15", "expires_on":"2026-12-15", "email_scoped":True}

def fixture(product="ZEN12"):
    return {"schema":"fv-dispatch-merchant-v1","as_of":TODAY.isoformat(),"issue":"03" if product=="ZEN12" else "05", "product":product, "records":[record(k,product) for k in sorted(REQUIRED)]}

class AuthorityTests(unittest.TestCase):
    def test_empty_index_holds(self):
        x=fixture();x['records']=[]
        r=audit(x); self.assertEqual(len(r['blockers']),len(REQUIRED));self.assertFalse(r['mail_allowed'])
    def test_synthetic_complete_never_sends(self):
        x=audit(fixture());self.assertTrue(x['structural_review_candidate']);self.assertFalse(x['partner_authorization_authenticated']);self.assertFalse(x['mail_allowed'])
    def test_other_product_complete_never_sends(self):
        x=audit(fixture('TOTAL_FOCUS'));self.assertTrue(x['structural_review_candidate']);self.assertFalse(x['mail_allowed']);self.assertEqual(x['issue'],'05')
    def test_missing_each_kind(self):
        for kind in REQUIRED:
            with self.subTest(kind=kind):
                x=fixture();x['records']=[r for r in x['records'] if r['kind']!=kind];self.assertIn('MISSING_'+kind.upper(),audit(x)['blockers'])
    def test_wrong_authority_for_every_partner_proof(self):
        for kind in PARTNER_KINDS:
            with self.subTest(kind=kind):
                x=fixture();next(r for r in x['records'] if r['kind']==kind)['authority']='merchant_public';self.assertIn('WRONG_AUTHORITY_'+kind.upper(),audit(x)['blockers'])
    def test_specific_email_scope_for_every_partner_proof(self):
        for kind in PARTNER_KINDS:
            with self.subTest(kind=kind):
                x=fixture();next(r for r in x['records'] if r['kind']==kind)['email_scoped']=False;self.assertIn('NOT_EMAIL_SPECIFIC_'+kind.upper(),audit(x)['blockers'])
    def test_cross_product_witness_rejected(self):
        x=fixture();x['records'][0]['product']='TOTAL_FOCUS';self.assertTrue(any(b.startswith('CROSS_PRODUCT') for b in audit(x)['blockers']))
    def test_expired(self):
        x=fixture();x['records'][0]['expires_on']='2026-11-10';self.assertTrue(any(b.startswith('EXPIRED') for b in audit(x)['blockers']))
    def test_stale(self):
        x=fixture();x['records'][0]['reviewed_on']='2026-01-01';self.assertTrue(any(b.startswith('STALE') for b in audit(x)['blockers']))
    def test_future_review(self):
        x=fixture();x['records'][0]['reviewed_on']='2026-11-17';self.assertTrue(any(b.startswith('FUTURE') for b in audit(x)['blockers']))
    def test_duplicate_evidence(self):
        x=fixture();x['records'].append(copy.deepcopy(x['records'][0]));self.assertTrue(any(b.startswith('DUPLICATED') for b in audit(x)['blockers']))
    def test_raw_email_in_ref_rejected(self):
        x=fixture();x['records'][0]['proof_ref']='person@example.com';self.assertRaises(ValueError,audit,x)
    def test_url_in_ref_rejected(self):
        x=fixture();x['records'][0]['proof_ref']='https://site.com/account?id=123';self.assertRaises(ValueError,audit,x)
    def test_secret_like_ref_rejected(self):
        x=fixture();x['records'][0]['proof_ref']='sk-proj-secret123';self.assertRaises(ValueError,audit,x)
    def test_extra_pii_record_rejected(self):
        x=fixture();x['records'][0]['subscriber_email']='x@x.com';self.assertRaises(ValueError,audit,x)
    def test_extra_top_field_rejected(self):
        x=fixture();x['list_emails']=[];self.assertRaises(ValueError,audit,x)
    def test_boolean_string_rejected(self):
        x=fixture();x['records'][0]['email_scoped']='true';self.assertRaises(ValueError,audit,x)
    def test_unknown_product_rejected(self):
        x=fixture();x['product']='OTHER';self.assertRaises(ValueError,audit,x)
    def test_wrong_issue_rejected(self):
        x=fixture();x['issue']='05';self.assertRaises(ValueError,audit,x)
    def test_too_many_records_rejected(self):
        x=fixture();x['records']=x['records']*8;self.assertRaises(ValueError,audit,x)
    def test_bad_calendar_date(self):
        x=fixture();x['as_of']='2026-11-99';self.assertRaises(ValueError,audit,x)
    def test_wrong_schema(self):
        x=fixture();x['schema']='v2';self.assertRaises(ValueError,audit,x)
    def test_public_swipe_not_email_permission(self):
        x=fixture();next(r for r in x['records'] if r['kind']=='email_channel_permission')['authority']='merchant_public';self.assertFalse(audit(x)['structural_review_candidate'])
    def test_witness_does_not_prove_partner(self):
        x=audit(fixture());self.assertEqual(x['release'],'HOLD_UNSENT');self.assertFalse(x['founder_release_approved'])

if __name__=='__main__':unittest.main()
