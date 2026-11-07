"""Synthetic R196 fragment custody tests. Never a human source or safety approval."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/'tools/r196_fragment_source_custody_gate.py'
spec=importlib.util.spec_from_file_location('r196',P)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def fixture():
    store={};p={};f={};e={}
    def stash(v):
        raw=json.dumps(v,sort_keys=True).encode(); sha=g.oid(raw);store[sha]=raw;return sha
    for cluster,(oldid,newid,oldcount,newcount) in g.PINS.items():
        def src(sid,**patch):
            s={'id':sid,'title':'Test', 'publisher':'Example', 'kind':'archive',
               'url':'https://example.org/source', 'supports':'Historical context only',
               'notes':'Read catalogue only', 'human_link_check':False}
            s.update(patch)
            return s
        old=[src(cluster+'-source-'+str(i)) for i in range(oldcount)]
        new=copy.deepcopy(old)
        ad,rm,ch=g.EXPECTED[cluster]
        for sid in rm:new=[x for x in new if x['id']!=cluster+'-source-'+str(oldcount-1)]
        if rm:old[-1]['id']=next(iter(rm))
        if rm:new=[x for x in new if x['id']!=cluster+'-source-'+str(oldcount-1)]
        for sid in ad:new.append(src(sid))
        for sid,keys in ch.items():
            old[0]['id']=sid;new[0]['id']=sid
            for field in keys:new[0][field]='New source '+field
        so,sn=stash({'sources':old}),stash({'sources':new})
        f[cluster]={'frozen':so,'observed':sn}
        p[cluster]=(so,sn,oldcount,newcount)
        e[cluster]=(set(ad),set(rm),{k:set(v) for k,v in ch.items()})
    docket={'schema':'fv-preparedness-r194-seven-delta-citation-custody-v1',
           'state':g.HOLD,'issue':136,'publication_authorized':False,
           'independent_qd_pass':False,'medical_safety_verified':False,
           'source_claims_human_approved':False,'merchant_offer_verified':False,
           'source_fragments':f}
    raw=json.dumps(docket,sort_keys=True).encode()
    return raw,store,p,e

class FragmentTests(unittest.TestCase):
    def setUp(self):
        self.d,self.store,self.p,self.e=fixture();self.pin=g.oid(self.d)
    def run_gate(self):
        return g.inspect(self.d,self.store.__getitem__,docket_oid=self.pin,
                         pins=self.p,expected=self.e)
    def bad(self):
        x=self.run_gate();self.assertEqual(x['state'],g.INVALID);self.assertTrue(x['errors'])
        self.assertFalse(x['publication_authorized'])
    def change(self,group,ver,fun):
        doc=json.loads(self.d);ident=doc['source_fragments'][group][ver]
        data=json.loads(self.store[ident]);fun(data)
        raw=json.dumps(data,sort_keys=True).encode();new=g.oid(raw);self.store[new]=raw
        doc['source_fragments'][group][ver]=new
        old=list(self.p[group]);old[0 if ver=='frozen' else 1]=new
        self.p[group]=tuple(old)
        self.d=json.dumps(doc,sort_keys=True).encode();self.pin=g.oid(self.d)
    def test_clean_fixture_is_still_hold(self):
        x=self.run_gate();self.assertEqual(x['state'],g.HOLD)
        self.assertEqual((x['fragments_checked'],x['old_sources'],x['observed_sources']),(6,81,85))
        self.assertEqual(x['source_aliases_approved'],0)
        self.assertIsNone(x['verified_paid_orders'])
    def test_deterministic(self):self.assertEqual(self.run_gate(),self.run_gate())
    def test_changed_docket_pin_detected(self):
        self.d+=b' ';self.bad()
    def test_missing_blob(self):
        self.store.pop(self.p['hist-home'][0]);self.bad()
    def test_forbidden_relabel(self):
        self.change('hist-food','observed',lambda d:d['sources'][0].update(id='wrong'))
        self.bad()
    def test_no_automatic_alias(self):
        x=next(w for w in self.run_gate()['workorders'] if w['cluster']=='hist-food')
        self.assertTrue(x['unapproved_source_substitution'])
        self.assertEqual(x['human_review'],'PENDING')
    def test_reject_duplicate_json_key(self):
        with self.assertRaises(g.CustodyError):g.strict_json(b'{"sources":[],"sources":[]}')
    def test_reject_nan(self):
        with self.assertRaises(g.CustodyError):g.strict_json(b'{"x":NaN}')

def make_mutation(group, ver, kind):
    def test(self):
        if kind=='duplicate':
            self.change(group,ver,lambda d:d['sources'].append(copy.deepcopy(d['sources'][0])))
        elif kind=='url':self.change(group,ver,lambda d:d['sources'][0].update(url='http://example.org/'))
        elif kind=='supports':self.change(group,ver,lambda d:d['sources'][0].update(supports=''))
        elif kind=='no-id':self.change(group,ver,lambda d:d['sources'][0].pop('id'))
        elif kind=='false-title':self.change(group,ver,lambda d:d['sources'][0].update(title=''))
        elif kind=='false-link-review':self.change(group,ver,lambda d:d['sources'][0].update(human_link_check='yes'))
        elif kind=='remove':self.change(group,ver,lambda d:d['sources'].pop())
        elif kind=='extra':self.change(group,ver,lambda d:d['sources'].append(dict(d['sources'][0],id='unexpected-new')))
        else:raise AssertionError(kind)
        self.bad()
    return test
for group in g.PINS:
    for ver in ('frozen','observed'):
        for kind in ('duplicate','url','supports','no-id','false-title','false-link-review','remove','extra'):
            setattr(FragmentTests,'test_mutation_'+group.replace('-','_')+'_'+ver+'_'+kind.replace('-','_'),make_mutation(group,ver,kind))

if __name__=='__main__':unittest.main()
