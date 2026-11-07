"""R195 deterministic synthetic threat model; never certifies source accuracy."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

MOD=Path(__file__).resolve().parents[1]/'tools/r195_claim_impact_preflight.py'
spec=importlib.util.spec_from_file_location('r195_pinned',MOD)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
COUNTS=[(47,47),(57,63),(46,46),(39,39),(42,49),(37,42),(47,48)]

def fixture():
    objects={}; rows=[]; pins=[]
    def store(raw):
        oid=gate.git_oid(raw)
        objects[oid]=raw
        return oid
    for i,orig in enumerate(gate.PINS):
        cluster,slug=orig[:2]
        row={'cluster':cluster,'slug':slug,'human_source_review':'PENDING',
             'qualified_safety_review':'PENDING'}
        vals=[]
        for ver,count in (('frozen',COUNTS[i][0]),('observed',COUNTS[i][1])):
            sid=('nchfp-jerky' if (i in (2,3) and ver=='observed')
                 else 'hist-food-nchfp-jerky' if i in (2,3) else 'synthetic-source')
            text=('<p>Long, substantive, synthetic reading scope sample. '
                  + '{{cite:'+sid+'}}</p>\n')*count
            meta={'slug':slug,'source_use':{sid:'Synthetic research scope for review.'},
                  'status':{'publish':'draft'},'safety_review':{'state':'pending'}}
            bod,md=store(text.encode()),store(json.dumps(meta,sort_keys=True).encode())
            vals.extend([bod,md,count])
            row[ver]={'body_blob':bod,'meta_blob':md,'citations':count}
        pins.append((cluster,slug,*vals));rows.append(row)
    docket={'schema':gate.R194_SCHEMA,'issue':136,'state':gate.HOLD,
      'publication_authorized':False,'independent_qd_pass':False,
      'medical_safety_verified':False,'merchant_offer_verified':False,
      'source_claims_human_approved':False,'articles':rows}
    raw=json.dumps(docket,sort_keys=True).encode()
    return raw,objects,tuple(pins)

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.raw,self.objects,self.pins=fixture()
        self.pin=gate.git_oid(self.raw)
    def run_gate(self):
        return gate.evaluate(self.raw,self.objects.__getitem__,
               trusted_docket_oid=self.pin,trusted_pins=self.pins)
    def reject(self):
        r=self.run_gate()
        self.assertEqual(r['state'],gate.INVALID)
        self.assertTrue(r['errors'])
        self.assertFalse(r['publication_authorized'])
    def mutate_docket(self, change, resign=False):
        d=json.loads(self.raw)
        change(d)
        self.raw=json.dumps(d,sort_keys=True).encode()
        if resign: self.pin=gate.git_oid(self.raw)
    def rewrite_object(self,i,ver,which,transform):
        d=json.loads(self.raw)
        item=d['articles'][i][ver]
        field=which+'_blob'; oid=item[field]
        data=transform(self.objects[oid])
        new_oid=gate.git_oid(data)
        self.objects[new_oid]=data
        item[field]=new_oid
        self.raw=json.dumps(d,sort_keys=True).encode()
        self.pin=gate.git_oid(self.raw)
        old=list(self.pins[i]);old[(2 if ver=='frozen' else 5)+(0 if which=='body' else 1)]=new_oid
        pins=list(self.pins);pins[i]=tuple(old);self.pins=tuple(pins)
    def test_structurally_complete_is_still_hold(self):
        r=self.run_gate()
        self.assertEqual(r['state'],gate.HOLD)
        self.assertEqual((r['frozen_citations'],r['observed_citations']),(315,334))
        self.assertEqual(r['articles_checked'],7)
        self.assertEqual(r['source_aliases_approved'],0)
        self.assertIsNone(r['verified_paid_orders'])
        self.assertFalse(r['independent_qd_pass'])
    def test_synthetic_eight_jerky_aliases_not_approved(self):
        r=self.run_gate()
        rows=[x for x in r['workorders'] if x['cluster']=='hist-food']
        self.assertEqual(len(rows),2)
        self.assertTrue(all('nchfp-jerky' in x['unapproved_source_aliases'] for x in rows))
        self.assertEqual(r['source_aliases_approved'],0)
    def test_output_is_deterministic(self):
        a=self.run_gate();b=self.run_gate()
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))
    def test_mutated_docket_cannot_silently_rebaseline(self):
        self.mutate_docket(lambda d:d.update(description='unauthorized'))
        self.reject()
    def test_docket_rebaseline_requires_exact_production_pin(self):
        self.mutate_docket(lambda d:d.update(description='changed'),resign=True)
        self.assertEqual(self.run_gate()['state'],gate.HOLD)
        self.assertNotEqual(gate.git_oid(self.raw),gate.PINNED_DOCKET_BLOB)
    def test_wrong_schema(self):
        self.mutate_docket(lambda d:d.update(schema='fake'),True);self.reject()
    def test_wrong_issue(self):
        self.mutate_docket(lambda d:d.update(issue=820),True);self.reject()
    def test_false_qd(self):
        self.mutate_docket(lambda d:d.update(independent_qd_pass=True),True);self.reject()
    def test_roster_missing(self):
        self.mutate_docket(lambda d:d['articles'].pop(),True);self.reject()
    def test_duplicate_json_key(self):
        self.raw=b'{"x":1,"x":2}'
        self.pin=gate.git_oid(self.raw);self.reject()
    def test_status_approval_prohibited(self):
        self.mutate_docket(lambda d:d.update(publication_authorized=True),True);self.reject()
    def test_source_scope_change_emits_manual_workorder(self):
        def f(raw):
            d=json.loads(raw);d['source_use']['synthetic-source']='A changed reading context.'
            return json.dumps(d,sort_keys=True).encode()
        self.rewrite_object(0,'observed','meta',f)
        r=self.run_gate()
        self.assertEqual(r['state'],gate.HOLD)
        x=next(x for x in r['workorders'] if x['slug']=='navigation-before-gps')
        self.assertTrue(x['source_use_scope_changes'])
        self.assertEqual(x['source_use_scope_changes'][0]['human_review'],'PENDING')
    def test_changed_citation_sequence_yields_context_workorder(self):
        r=self.run_gate()
        x=next(x for x in r['workorders'] if x['slug']=='pemmican-and-dried-meats')
        self.assertTrue(x['citation_sequence_edits'])
        edit=x['citation_sequence_edits'][0]
        self.assertTrue(edit['frozen'][0]['excerpt_sha256'])
        self.assertEqual(edit['human_review'],'PENDING')
    def test_nonexplanatory_source_use_rejected(self):
        def f(raw):
            d=json.loads(raw);d['source_use']['synthetic-source']='   '
            return json.dumps(d,sort_keys=True).encode()
        self.rewrite_object(0,'observed','meta',f);self.reject()
    def test_historical_safety_state_switch_rejected(self):
        def f(raw):
            d=json.loads(raw);d['safety_review']={'state':'approved'}
            return json.dumps(d,sort_keys=True).encode()
        self.rewrite_object(0,'observed','meta',f);self.reject()
    def test_truncated_reading_rejected(self):
        self.rewrite_object(0,'observed','body',lambda raw:raw[:120]);self.reject()
    def test_invalid_meta_json_rejected(self):
        self.rewrite_object(0,'observed','meta',lambda raw:b'{bad-json');self.reject()
    def test_no_unauthorized_merchant_offer(self):
        self.mutate_docket(lambda d:d.update(merchant_offer_verified=True),True);self.reject()
    def test_unicode_text_counts(self):
        self.assertEqual(gate.text_words('<p>Text &amp; more. Café</p>'.encode()),3)

def mutation_case(i,ver,variant):
    def test(self):
        if variant=='route':
            self.mutate_docket(lambda d:d['articles'][i].update(slug='false-route'),True)
        elif variant=='count':
            self.mutate_docket(lambda d:d['articles'][i][ver].update(citations=999),True)
        elif variant=='wrong_blob':
            self.mutate_docket(lambda d:d['articles'][i][ver].update(body_blob='0'*40),True)
        elif variant=='missing_blob':
            self.objects.pop(self.pins[i][2 if ver=='frozen' else 5])
        elif variant=='approval':
            self.mutate_docket(lambda d:d['articles'][i].update(human_source_review='APPROVED'),True)
        self.reject()
    return test

for i in range(7):
    for v in ('frozen','observed'):
        for kind in ('route','count','wrong_blob','missing_blob','approval'):
            setattr(CustodyTests,f'test_negative_{kind}_{v}_{i}',mutation_case(i,v,kind))

if __name__=='__main__':unittest.main()
