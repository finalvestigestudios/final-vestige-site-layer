"""Synthetic mutation regressions for R194 dual-version Git evidence admission.

Never rely on these tests as an authentic 35-article build or safety QD pass.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest
import importlib.util

path=Path(__file__).resolve().parents[1] / 'tools/r194_dual_version_citation_gate.py'
spec=importlib.util.spec_from_file_location('r194_custody',path)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
ROWS=[('hist-field','navigation-before-gps',47,47),
      ('hist-field','pioneer-supply-chains-failed',57,63),
      ('hist-food','pemmican-and-dried-meats',46,46),
      ('hist-food','pioneer-travel-rations',39,39),
      ('hist-home','pickling-fermentation-old-recipes',42,49),
      ('hist-home','root-cellars-cool-storage',37,42),
      ('hist-home','sanitation-before-germ-theory',47,48)]

def fixture():
    objects={}
    def keep(raw):
        oid=gate.blob_oid(raw)
        objects[oid]=raw
        return oid
    docket={'schema':gate.SCHEMA,'state':gate.HOLD,'issue':136,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'source_claims_human_approved':False,
            'merchant_offer_verified':False,'articles':[]}
    for i,(group,slug,old_n,new_n) in enumerate(ROWS):
        row={'cluster':group,'slug':slug,'human_source_review':'PENDING',
             'qualified_safety_review':'PENDING'}
        for ver,n in (('frozen',old_n),('observed',new_n)):
            sid=f'synthetic-{i}'
            body=('Original unabridged text. {{cite:'+sid+'}}\n')*n
            meta={'slug':slug,'source_use':{sid:'Synthetic source scope.'},
                  'status':{'publish':'draft'},'safety_review':{'status':'pending'}}
            row[ver]={'body_blob':keep(body.encode()),
                      'meta_blob':keep(json.dumps(meta,sort_keys=True).encode()),
                      'citations':n}
        docket['articles'].append(row)
    return docket,objects

class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.docket,self.objects=fixture()
    def run_gate(self):
        return gate.inspect(self.docket, self.objects.__getitem__)
    def rejected(self):
        receipt=self.run_gate()
        self.assertEqual(receipt['state'],gate.INVALID)
        self.assertFalse(receipt['publication_authorized'])
        self.assertTrue(receipt['errors'])

    def test_complete_docket_cannot_authorize_publication(self):
        receipt=self.run_gate()
        self.assertEqual(receipt['state'],gate.HOLD)
        self.assertEqual(receipt['articles_checked'],7)
        self.assertEqual(receipt['old_citations'],315)
        self.assertEqual(receipt['new_citations'],334)
        self.assertFalse(receipt['independent_qd_pass'])
        self.assertIsNone(receipt['verified_paid_orders'])
        self.assertIsNone(receipt['realized_net_revenue'])
        self.assertEqual(len(receipt['old_and_new_readings_preserved']),7)

    def test_unauthorized_receipt_status(self):
        self.docket['state']='PUBLISHED'
        self.rejected()

    def test_missing_article(self):
        self.docket['articles'].pop()
        self.rejected()

    def test_duplicate_article(self):
        self.docket['articles'][0]=deepcopy(self.docket['articles'][1])
        self.rejected()

    def test_bad_schema(self):
        self.docket['schema']='r999-fake'
        self.rejected()

    def test_bad_issue(self):
        self.docket['issue']=820
        self.rejected()

    def test_bad_total_even_if_valid_objects(self):
        self.docket['articles'][0]['observed']['citations']=48
        self.rejected()

    def test_missing_object(self):
        self.objects.pop(self.docket['articles'][0]['frozen']['body_blob'])
        self.rejected()

    def test_blob_substitution(self):
        oid=self.docket['articles'][0]['frozen']['body_blob']
        self.objects[oid]=b'{{cite:fake}}'
        self.rejected()

    def test_meta_publication_state(self):
        row=self.docket['articles'][0]['observed']
        meta=json.loads(self.objects[row['meta_blob']])
        meta['status']['publish']='published'
        raw=json.dumps(meta,sort_keys=True).encode()
        row['meta_blob']=gate.blob_oid(raw);self.objects[row['meta_blob']]=raw
        self.rejected()

    def test_independent_safety_review_rewrite(self):
        row=self.docket['articles'][0]['observed']
        meta=json.loads(self.objects[row['meta_blob']]);meta['safety_review']={'status':'approved'}
        raw=json.dumps(meta,sort_keys=True).encode()
        row['meta_blob']=gate.blob_oid(raw);self.objects[row['meta_blob']]=raw
        self.rejected()

    def test_modified_meta_omits_source_explanation(self):
        row=self.docket['articles'][0]['observed']
        meta=json.loads(self.objects[row['meta_blob']]);meta['source_use']={}
        raw=json.dumps(meta,sort_keys=True).encode()
        row['meta_blob']=gate.blob_oid(raw);self.objects[row['meta_blob']]=raw
        self.rejected()

    def test_duplicate_json_key_in_metadata(self):
        row=self.docket['articles'][0]['observed']
        raw=b'{"slug":"navigation-before-gps","slug":"override","status":{"publish":"draft"},"source_use":{}}'
        row['meta_blob']=gate.blob_oid(raw);self.objects[row['meta_blob']]=raw
        self.rejected()

def make_case(idx,field,version):
    def test(self):
        row=self.docket['articles'][idx]
        if field=='slug':
            row['slug']='incorrect-route'
        elif field=='count':
            row[version]['citations']+=1
        elif field=='blob':
            row[version]['body_blob']='1'*40
        elif field=='meta':
            row[version]['meta_blob']='2'*40
        elif field=='review':
            row['qualified_safety_review']='CLEARED'
        elif field=='missing':
            row[version].pop('body_blob')
        self.rejected()
    return test

for i in range(7):
    for fld in ('slug','review'):
        setattr(IntegrityTests,f'test_{fld}_{i}',make_case(i,fld,'frozen'))
    for ver in ('frozen','observed'):
        for fld in ('count','blob','meta','missing'):
            setattr(IntegrityTests,f'test_{fld}_{ver}_{i}',make_case(i,fld,ver))

if __name__=='__main__':
    unittest.main()
