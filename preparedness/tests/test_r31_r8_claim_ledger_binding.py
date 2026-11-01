"""R31: full R8 source claim ledger must be cryptographically bound to R10 HOLD receipt.

Fixtures are in-memory; no source rewrite, outbound link access, CMS write or PASS.
"""
from __future__ import annotations
from hashlib import sha256
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import high_consequence_claim_triage as triage

def original():
    return {'schema_version':1,'release_state':'HOLD','may_publish':False,
            'claims':[{'article':'draft-a','citation':'a','position':12},
                      {'article':'draft-b','citation':'b','position':37}],
            'counts':{'citation_occurrences':2},
            'human_source_review_completed':False}

def digest(report):
    return sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,
                            separators=(',',':')).encode('utf-8')).hexdigest()

def receipt(report):
    return {'release_state':'HOLD','may_publish':False,
            'source_content_digest_sha256':digest(report)}

def run(report, proof):
    def factory(lib, *, rows, fingerprint, expect):
        if lib != 'PRIVATE_LIB' or rows != ['RAW_ROWS'] or fingerprint != 'FROZEN':
            raise AssertionError('source input changed')
        if expect != {'expected':'baseline'}:
            raise AssertionError('baseline missing')
        return report
    return triage.bind_full_R8_claim_evidence(
        'PRIVATE_LIB',['RAW_ROWS'],'FROZEN',proof,
        make_report=factory,baseline={'expected':'baseline'},
        expected_occurrences=2)

class Accepted(unittest.TestCase):
    def test_unapproved_digest_bound_report(self):
        r=original();self.assertEqual(run(r,receipt(r)),r)
    def test_does_not_mutate_evidence(self):
        r=original();p=receipt(r)
        before=copy.deepcopy((r,p));run(r,p)
        self.assertEqual((r,p),before)
    def test_deterministic_canonical_digest(self):
        r=original();other={k:r[k] for k in reversed(list(r))}
        self.assertEqual(digest(r),digest(other))
        self.assertEqual(run(other,receipt(r)),other)
    def test_no_false_approval_claims(self):
        r=original();v=run(r,receipt(r))
        self.assertIs(v['human_source_review_completed'],False)
        self.assertIs(v['may_publish'],False)
    def test_full_per_occurrence_evidence_preserved(self):
        r=original()
        self.assertEqual([x['position'] for x in run(r,receipt(r))['claims']],[12,37])
    def test_original_receipt_is_not_confused_with_full_ledger(self):
        r=original();p=receipt(r)
        self.assertNotIn('claims',p)
        with self.assertRaises(triage.TriageFailure):
            run(p,p)

MUTATIONS={
 'receipt_not_object':lambda p,r:'bad',
 'receipt_publish_true':lambda p,r:{**p,'may_publish':True},
 'receipt_status_pass':lambda p,r:{**p,'release_state':'APPROVED'},
 'receipt_hash_forged':lambda p,r:{**p,'source_content_digest_sha256':'0'*64},
 'receipt_hash_missing':lambda p,r:{k:v for k,v in p.items() if k!='source_content_digest_sha256'},
 'report_not_object':lambda p,r:'bad',
 'report_publish_true':lambda p,r:{**r,'may_publish':True},
 'report_status_pass':lambda p,r:{**r,'release_state':'APPROVED'},
 'claims_missing':lambda p,r:{k:v for k,v in r.items() if k!='claims'},
 'claims_not_array':lambda p,r:{**r,'claims':'not-a-claim-list'},
 'claims_shortened':lambda p,r:{**r,'claims':r['claims'][:1]},
 'claims_overfilled':lambda p,r:{**r,'claims':r['claims']+[r['claims'][0]]},
 'citation_position_changed':lambda p,r:{**r,'claims':[{**r['claims'][0],'position':88},r['claims'][1]]},
 'article_identity_changed':lambda p,r:{**r,'claims':[{**r['claims'][0],'article':'modified'},r['claims'][1]]},
 'source_identity_changed':lambda p,r:{**r,'claims':[{**r['claims'][0],'citation':'other'},r['claims'][1]]},
 'extra_unreviewed_fake_state':lambda p,r:{**r,'safety_claim_verified':True},
 'altered_counts':lambda p,r:{**r,'counts':{'citation_occurrences':300}},
 'removed_human_review_flag':lambda p,r:{k:v for k,v in r.items() if k!='human_source_review_completed'},
 'changed_schema':lambda p,r:{**r,'schema_version':12},
 'changed_claim_order':lambda p,r:{**r,'claims':list(reversed(r['claims']))},
}
class Adversarial(unittest.TestCase):pass
def make_case(name,func):
    def test(self):
        r=original();p=receipt(r)
        if name.startswith('receipt_'):
            p=func(p,r)
        else:
            r=func(p,r)
        with self.assertRaises(triage.TriageFailure,msg=name):
            run(r,p)
    return test
for name,func in MUTATIONS.items():
    setattr(Adversarial,'test_reject_'+name,make_case(name,func))

if __name__=='__main__':unittest.main()
