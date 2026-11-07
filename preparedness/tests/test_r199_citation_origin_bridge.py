"""R199 synthetic bridge tests only; no original repository safety or release claim."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1] / 'tools/r199_citation_origin_bridge.py'
spec=importlib.util.spec_from_file_location('r199_bridge',PATH)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def scenario():
    blobs={}; entries=[]
    for v in ('frozen','observed'):
        body=('<p>Action {{cite:base-source}} followed by '\
              '{{cite:field-source}}. Verify before use.</p>\n').encode()
        meta=json.dumps({'slug':'test-page','status':{'publish':'draft'},
             'source_use':{'base-source':'background evidence',
                            'field-source':'historical evidence'}},sort_keys=True).encode()
        bo,mo=gate.git_oid(body),gate.git_oid(meta)
        blobs[bo]=body; blobs[mo]=meta; entries.append((bo,mo,2))
    pin=('hist-field','test-page',*entries[0],*entries[1])
    scope={'schema':'fv-preparedness-r198-source-scope-custody-v1',
       'state':gate.HOLD,'errors':[], 'publication_authorized':False,
       'independent_qd_pass':False,'medical_safety_verified':False,
       'merchant_offer_verified':False,'verified_paid_orders':None,
       'realized_net_revenue':None,'summary':{'frozen':{'source_uses':2},'observed':{'source_uses':2}},
       'origin_scope_workorders':[]}
    for version in ('frozen','observed'):
        for sid, origin in (('base-source','base'),('field-source','hist-field')):
            scope['origin_scope_workorders'].append({'cluster':'hist-field','slug':'test-page',
                'version':version,'source_id':sid,'human_review':'PENDING',
                'all_original_origins':[origin],'eligible_origins':[origin],
                'foreign_alternatives':[],'automatic_origin_selection':False})
    impact={'schema':'fv-preparedness-r195-claim-impact-review-v1',
       'state':gate.HOLD,'errors':[], 'publication_authorized':False,
       'independent_qd_pass':False,'medical_safety_verified':False,
       'merchant_offer_verified':False,'verified_paid_orders':None,
       'realized_net_revenue':None,
       'workorders':[{'cluster':'hist-field','slug':'test-page',
         'manual_source_claim_review':'PENDING',
         'frozen_blob_sha1':entries[0][0],'observed_blob_sha1':entries[1][0]}]}
    return scope,impact,blobs,[pin]

class BridgeTests(unittest.TestCase):
    def setUp(self): self.scope,self.impact,self.blobs,self.pins=scenario()
    def result(self):
        return gate.bridge(self.scope,self.impact,self.blobs.__getitem__,pins=self.pins,strict=False)
    def deny(self):
        r=self.result()
        self.assertEqual(r['state'],gate.INVALID,r)
        self.assertEqual(r['source_origin_workorders'],[])
        self.assertTrue(r['errors'])
        self.assertFalse(r['publication_authorized'])
    def test_hard_hold_still_unverified(self):
        r=self.result();self.assertEqual(r['state'],gate.HOLD)
        self.assertEqual(r['citation_occurrences'],{'frozen':2,'observed':2})
        self.assertEqual(len(r['source_origin_workorders']),4)
        self.assertEqual(len(r['article_versions']),2)
        self.assertTrue(all(x['human_claim_check']=='PENDING' for x in r['source_origin_workorders']))
        self.assertFalse(r['independent_qd_pass'])
    def test_repeat_is_deterministic(self):
        self.assertEqual(json.dumps(self.result(),sort_keys=True),json.dumps(self.result(),sort_keys=True))
    def test_true_census_refuses_synthetic(self):
        r=gate.bridge(self.scope,self.impact,self.blobs.__getitem__,pins=self.pins)
        self.assertEqual(r['state'],gate.INVALID)
    def test_ambiguous_origins_not_approved(self):
        r=self.scope['origin_scope_workorders'][0]
        r['all_original_origins']=['base','hist-food']
        r['foreign_alternatives']=['hist-food']
        report=self.result();self.assertEqual(report['state'],gate.HOLD)
        self.assertTrue(report['source_origin_workorders'][0]['requires_origin_adjudication'])
        self.assertEqual(report['source_origin_workorders'][0]['eligible_origins'],['base'])
    def test_pinned_code_mutation_refused(self):
        with tempfile.TemporaryDirectory() as p:
            path=Path(p)/'test.py';path.write_text('pass\n')
            with self.assertRaises(gate.BridgeError):
                gate.pinned_module(p,'test.py','0'*40,'bad')
    def test_blob_algorithm(self):
        self.assertEqual(gate.git_oid(b'test content\n'),'d670460b4b4aece5915caf5c68d12f560a9fe3e4')

# Exhaustively mutate both versioned citation-origin edges; no fake success allowed.
def bad_edge(index,change):
    def test(self):
        row=self.scope['origin_scope_workorders'][index]
        if change=='wrong_slug':row['slug']='another-page'
        elif change=='wrong_cluster':row['cluster']='hist-food'
        elif change=='wrong_version':row['version']='latest'
        elif change=='unknown_source':row['source_id']='unknown-id'
        elif change=='missing_source':row['source_id']=''
        elif change=='duplicate_source':row['source_id']=self.scope['origin_scope_workorders'][index^1]['source_id']
        elif change=='approved':row['human_review']='APPROVED'
        elif change=='fake_auto_choice':row['automatic_origin_selection']=True
        elif change=='foreign_only':row['eligible_origins']=['hist-food']
        elif change=='missing_eligible':row['eligible_origins']=[]
        elif change=='faked_origin':row['all_original_origins']=['hist-food']
        elif change=='duplicate_origin':row['all_original_origins']=['base','base']
        elif change=='unsorted_origin':row['all_original_origins']=['hist-food','base'];row['eligible_origins']=['base']
        else:raise AssertionError(change)
        self.deny()
    return test

for i in range(4):
    for change in ('wrong_slug','wrong_cluster','wrong_version','unknown_source','missing_source',
                   'duplicate_source','approved','fake_auto_choice','foreign_only','missing_eligible',
                   'faked_origin','duplicate_origin','unsorted_origin'):
        setattr(BridgeTests,f'test_edge_{i}_{change}',bad_edge(i,change))

def bad_state(change):
    def test(self):
        target=self.scope if change.startswith('scope_') else self.impact
        attr=change.split('_',1)[1]
        if attr=='schema':target['schema']='another-producer'
        elif attr=='state':target['state']='PASS'
        elif attr=='error':target['errors']=['failure']
        elif attr=='pub':target['publication_authorized']=True
        elif attr=='qd':target['independent_qd_pass']=True
        elif attr=='medical':target['medical_safety_verified']=True
        elif attr=='merchant':target['merchant_offer_verified']=True
        elif attr=='sale':target['verified_paid_orders']=1
        elif attr=='revenue':target['realized_net_revenue']=25
        else:raise AssertionError(attr)
        self.deny()
    return test
for stage in ('scope','impact'):
    for state in ('schema','state','error','pub','qd','medical','merchant','sale','revenue'):
        setattr(BridgeTests,f'test_{stage}_{state}',bad_state(stage+'_'+state))

if __name__=='__main__':unittest.main()
