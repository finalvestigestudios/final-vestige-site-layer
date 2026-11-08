import copy
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from audience_delta import validate_snapshot, compare_snapshots, admitted_confirmed_signups, revenue_per_1000

OLD = {"as_of":"2026-11-04T18:33:00+00:00","subscribers":{"total":2,"confirmed":2,"unconfirmed":2,"suppressed":0,"paid":0}}
NEW = {"as_of":"2026-11-04T19:33:44+00:00","subscribers":{"total":3,"confirmed":3,"unconfirmed":2,"suppressed":0,"paid":0,"imported_last_24h":1}}
GOOD = {"opaque_subscriber_id":"a"*64,"native_event_id":"wp_nativeref_123", "source":"native_wordpress", "confirmed_status":"confirmed", "consent_evidence":True,"occurred_at":"2026-11-04T18:56:00+00:00","source_verified":True,"email_eligible":None,"opted_out":False}

class SnapshotTests(unittest.TestCase):
    def test_current_real_delta(self):
        d=compare_snapshots(OLD,NEW)
        self.assertEqual(d['delta'], {'total':1,'confirmed':1,'unconfirmed':0})
        self.assertEqual(d['current_imported_last_24h'],1)
        self.assertFalse(d['import_is_signup_proof'])
        self.assertIsNone(d['confirmed_signup_events_verified'])
        self.assertEqual(d['release_gate'],'HOLD_ALL_UNSENT')
    def test_nonadditive(self):
        self.assertEqual(validate_snapshot(NEW)['total'],3)
    def test_float_not_int(self):
        bad=copy.deepcopy(NEW);bad['subscribers']['total']=3.0
        with self.assertRaises(ValueError):validate_snapshot(bad)
    def test_boolean_not_int(self):
        bad=copy.deepcopy(NEW);bad['subscribers']['total']=True
        with self.assertRaises(ValueError):validate_snapshot(bad)
    def test_negative(self):
        bad=copy.deepcopy(NEW);bad['subscribers']['confirmed']=-1
        with self.assertRaises(ValueError):validate_snapshot(bad)
    def test_missing_total(self):
        bad=copy.deepcopy(NEW);del bad['subscribers']['total']
        with self.assertRaises(ValueError):validate_snapshot(bad)
    def test_bad_clock(self):
        bad=copy.deepcopy(NEW);bad['as_of']='2026-11-04'
        with self.assertRaises(ValueError):compare_snapshots(OLD,bad)
    def test_reversed_clock(self):
        with self.assertRaises(ValueError):compare_snapshots(NEW,OLD)
    def test_stable(self):
        b=copy.deepcopy(OLD);b['as_of']='2026-11-04T18:34:00+00:00'
        self.assertFalse('GREW' in compare_snapshots(OLD,b)['interpretation'])

class ConsentTests(unittest.TestCase):
    def test_valid_confirmed_without_email_eligible(self):
        self.assertEqual(admitted_confirmed_signups([GOOD])['verified_unique_signups'],1)
    def test_duplicate_is_one(self):
        self.assertEqual(admitted_confirmed_signups([GOOD,GOOD])['verified_unique_signups'],1)
    def test_different_is_two(self):
        b=dict(GOOD,opaque_subscriber_id='b'*64)
        self.assertEqual(admitted_confirmed_signups([GOOD,b])['verified_unique_signups'],2)
    def test_unverified_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,source_verified=False)])['verified_unique_signups'],0)
    def test_pending_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,confirmed_status='pending')])['verified_unique_signups'],0)
    def test_consent_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,consent_evidence=False)])['verified_unique_signups'],0)
    def test_opted_out_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,opted_out=True)])['verified_unique_signups'],0)
    def test_pii_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,email='private@example.invalid')])['verified_unique_signups'],0)
    def test_wrong_source_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,source='social_click')])['verified_unique_signups'],0)
    def test_invalid_hmac_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,opaque_subscriber_id='plain_address')])['verified_unique_signups'],0)
    def test_invalid_date_reject(self):
        self.assertEqual(admitted_confirmed_signups([dict(GOOD,occurred_at='2026-11-04')])['verified_unique_signups'],0)

class RevenueTests(unittest.TestCase):
    def test_no_denominator(self):self.assertEqual(revenue_per_1000(None,[])['status'],'NOT_COMPUTABLE')
    def test_no_orders(self):self.assertEqual(revenue_per_1000(100,[])['status'],'NOT_COMPUTABLE')
    def test_unsettled(self):
        self.assertEqual(revenue_per_1000(100,[dict(merchant_verified=True,status='pending')])['status'],'NOT_COMPUTABLE')
    def test_no_click_as_sale(self):
        self.assertEqual(revenue_per_1000(100,[{'clicks':99}])['status'],'NOT_COMPUTABLE')
    def test_verified_synthetic(self):
        x={'merchant_verified':True,'status':'settled','merchant_order_id':'opaque_12345','gross':'20','fees':'2','refunds':'3'}
        self.assertEqual(revenue_per_1000(100,[x])['net_revenue_per_1000_sessions'],'150.00')
    def test_order_dedup(self):
        x={'merchant_verified':True,'status':'settled','merchant_order_id':'opaque_12345','gross':'20','fees':'2','refunds':'3'}
        self.assertEqual(revenue_per_1000(100,[x,x])['settled_order_count'],1)
    def test_nan_reject(self):
        x={'merchant_verified':True,'status':'settled','merchant_order_id':'opaque_12345','gross':'NaN','fees':'2','refunds':'3'}
        self.assertEqual(revenue_per_1000(100,[x])['status'],'NOT_COMPUTABLE')

if __name__=='__main__':unittest.main()
