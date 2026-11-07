"""R197 synthetic-only origin-collision and citation source-use tests; no safety/QD PASS."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r197_source_origin_collision_gate.py'
spec=importlib.util.spec_from_file_location('r197_source_origin_collision_gate',PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)


def fixture():
    store={};pins={};rows=[];bygroup={}
    def save(obj):
        raw=json.dumps(obj,sort_keys=True).encode()
        sha=g.oid(raw);store[sha]=raw;return sha
    def src(ident):
        return {'id':ident,'title':'Title','publisher':'Issuer','url':'https://example.org/a',
                'supports':'Only a synthetic test','human_link_check':False}
    for origin in ('base','hist-field','hist-food','hist-home'):
        arr={'sources':[src('global-source' if origin=='base' else origin+'-source')]}
        sha=save(arr);pins[origin]=(sha,sha,1,1);bygroup[origin]=arr
    for group,slug,_,_ in g.ARTICLES:
        use={'global-source':'Synthetic use',group+'-source':'Synthetic scoped use'}
        meta={'slug':slug,'status':{'publish':'draft'},'source_use':use}
        old,new=save(meta),save(meta)
        rows.append({'cluster':group,'slug':slug,'human_source_review':'PENDING',
          'qualified_safety_review':'PENDING', 'frozen':{'meta_blob':old},
          'observed':{'meta_blob':new}})
    docket={'schema':'fv-preparedness-r194-seven-delta-citation-custody-v1',
      'state':g.HOLD,'issue':136,'publication_authorized':False,
      'independent_qd_pass':False,'medical_safety_verified':False,
      'source_claims_human_approved':False,'merchant_offer_verified':False,
      'source_fragments':{k:{'frozen':v[0],'observed':v[1]}
                          for k,v in pins.items() if k!='base'},'articles':rows}
    doid=save(docket)
    articles=tuple((r['cluster'],r['slug'],r['frozen']['meta_blob'],r['observed']['meta_blob']) for r in rows)
    return store,pins,articles,docket,doid

class CollisionTests(unittest.TestCase):
    def setUp(self):
        self.store,self.pins,self.articles,self.docket,self.doid=fixture()
        self.expected={'frozen':set(),'observed':set()}

    def evaluate(self):
        return g.audit(self.store.__getitem__,docket_oid=self.doid,pins=self.pins,
            articles=self.articles,expected=self.expected,check_real_census=False)

    def assert_invalid(self):
        r=self.evaluate();self.assertEqual(r['state'],g.INVALID)
        self.assertTrue(r['errors']);self.assertFalse(r['publication_authorized'])

    def save(self,obj):
        raw=json.dumps(obj,sort_keys=True).encode();sha=g.oid(raw);self.store[sha]=raw
        return sha

    def rewrite_register(self,group,ver,mutation):
        orig=list(self.pins[group]);ix=0 if ver=='frozen' else 1
        data=json.loads(self.store[orig[ix]])
        mutation(data)
        sha=self.save(data);orig[ix]=sha
        self.pins[group]=tuple(orig)
        if group!='base':self.docket['source_fragments'][group][ver]=sha
        self.doid=self.save(self.docket)

    def rewrite_meta(self,idx,ver,mutation):
        rows=self.docket['articles'];row=rows[idx];old=row[ver]['meta_blob']
        doc=json.loads(self.store[old]);mutation(doc)
        new=self.save(doc);row[ver]['meta_blob']=new
        arr=[list(x) for x in self.articles];arr[idx][2 if ver=='frozen' else 3]=new
        self.articles=tuple(tuple(x) for x in arr)
        self.doid=self.save(self.docket)

    def test_fixture_is_a_hard_hold(self):
        r=self.evaluate();self.assertEqual(r['state'],g.HOLD)
        self.assertEqual(r['versioned_source_rows'],{'frozen':4,'observed':4})
        self.assertEqual(len(r['article_origin_workorders']),14)
        self.assertEqual(r['same_id_conflicts'],[])
        self.assertEqual(r['objects_checked'],23)
        self.assertIsNone(r['verified_paid_orders'])

    def test_determinism(self): self.assertEqual(self.evaluate(),self.evaluate())
    def test_docket_mutation_without_authentication(self):
        self.docket['state']='APPROVED';self.assertEqual(self.evaluate()['state'],g.HOLD)
        # In-memory mutation has no authority until supplied as the authenticated object.
    def test_docket_changed_approval_even_if_rehashed(self):
        self.docket['publication_authorized']=True;self.doid=self.save(self.docket);self.assert_invalid()
    def test_docket_changed_state(self):
        self.docket['state']='APPROVED';self.doid=self.save(self.docket);self.assert_invalid()
    def test_docket_missing_article(self):
        self.docket['articles'].pop();self.doid=self.save(self.docket);self.assert_invalid()
    def test_article_metadata_relabel(self):
        self.rewrite_meta(0,'observed',lambda x:x['status'].update(publish='published'))
        self.assert_invalid()
    def test_article_metadata_wrong_slug(self):
        self.rewrite_meta(0,'frozen',lambda x:x.update(slug='other'))
        self.assert_invalid()
    def test_article_metadata_missing_source(self):
        self.rewrite_meta(0,'observed',lambda x:x['source_use'].update(unknown='no trace'))
        self.assert_invalid()
    def test_article_metadata_nonexplanatory_source_use(self):
        self.rewrite_meta(0,'observed',lambda x:x['source_use'].update(**{'global-source':'  '}))
        self.assert_invalid()
    def test_tampered_raw_object(self):
        self.store[self.pins['base'][0]]=b'{}';self.assert_invalid()
    def test_missing_blob(self):
        self.store.pop(self.pins['base'][0]);self.assert_invalid()
    def test_nonstandard_json(self):
        with self.assertRaises(g.AdmissionError):g.strict_json(b'{"x":NaN}')
    def test_duplicate_json_fields(self):
        with self.assertRaises(g.AdmissionError):g.strict_json(b'{"x":1,"x":2}')
    def test_input_overlong(self):
        with self.assertRaises(g.AdmissionError):g.strict_json(b' '*200001)
    def test_source_id_collision_is_pending_and_unmerged(self):
        # One versioned shared ID between base and hist-food is *not* merged.
        for ver in ('frozen','observed'):
            self.rewrite_register('hist-food',ver,lambda x:x['sources'][0].update(id='global-source',title='Different title'))
        self.expected={'frozen':{'global-source'},'observed':{'global-source'}}
        # The food article's own source-use must now refer to shared ID only.
        for i,x in enumerate(self.articles):
            if x[0]=='hist-food':
                for ver in ('frozen','observed'):
                    self.rewrite_meta(i,ver,lambda m:m['source_use'].pop('hist-food-source'))
        r=self.evaluate();self.assertEqual(r['state'],g.HOLD)
        self.assertEqual(len(r['same_id_conflicts']),2)
        self.assertFalse(r['same_id_conflicts'][0]['automatic_collapse_allowed'])
        self.assertTrue(any(x['ambiguous'] for z in r['article_origin_workorders'] if z['cluster']=='hist-food' for x in z['origins']))


def mutation_case(group,ver,kind):
    def test(self):
        def f(doc):
            s=doc['sources'][0]
            if kind=='missing_id':s.pop('id')
            elif kind=='bad_id':s['id']='Invalid id'
            elif kind=='missing_title':s.pop('title')
            elif kind=='blank_publisher':s['publisher']='  '
            elif kind=='blank_supports':s['supports']=''
            elif kind=='http':s['url']='http://example.org/'
            elif kind=='false_human_link_check':s['human_link_check']=True
            elif kind=='nonbool_human_link_check':s['human_link_check']='false'
            elif kind=='duplicate':doc['sources'].append(copy.deepcopy(s))
            elif kind=='wrong_count':doc['sources'].clear()
            else:raise AssertionError(kind)
        self.rewrite_register(group,ver,f)
        self.assert_invalid()
    return test

for group in ('base','hist-field','hist-food','hist-home'):
    for ver in ('frozen','observed'):
        for kind in ('missing_id','bad_id','missing_title','blank_publisher','blank_supports',
                     'http','false_human_link_check','nonbool_human_link_check','duplicate','wrong_count'):
            setattr(CollisionTests,'test_mutation_'+group.replace('-','_')+'_'+ver+'_'+kind,mutation_case(group,ver,kind))

if __name__=='__main__':unittest.main()
