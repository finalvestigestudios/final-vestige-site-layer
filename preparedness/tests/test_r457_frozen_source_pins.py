"""R457 proof: frozen original 8-source-file SHA/count/origin pins fail closed."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r457_native_authority_export as gate

class PinFixture(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'preparedness'
        (self.root/'sources/fragments').mkdir(parents=True)
        self.tax={'slate':[{'slug':f'guide-{i:02d}'} for i in range(35)]}
        self.sources={'base':[{'id':'baseline','url':'https://www.ready.gov/plan','title':'FEMA plan',
                                'supports':'Read only planning notes','publisher':'FEMA','verified_on':'2026-10-30'}],
                      'start':[{'id':'start-plan','url':'https://www.ready.gov/plan','title':'Start review',
                                'supports':'Different independent read depth','publisher':'FEMA'}]}
        self.pathbase=self.root/'sources/register.json'
        self.pathfragment=self.root/'sources/fragments/start.json'
        self.write(self.root/'taxonomy.json',self.tax)
        self.write(self.pathbase,{'sources':self.sources['base']})
        self.write(self.pathfragment,{'sources':self.sources['start']})
        self.repin()
    def write(self,p,doc):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(doc),encoding='utf-8')
    def git_sha(self,p):
        b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    def repin(self):
        pins=[{'path':'preparedness/sources/register.json','origin':'base','count':len(self.sources['base']),
               'git_blob_sha':self.git_sha(self.pathbase)},
              {'path':'preparedness/sources/fragments/start.json','origin':'start','count':len(self.sources['start']),
               'git_blob_sha':self.git_sha(self.pathfragment)}]
        self.cross={'article_origins':{},'source_files':pins,'groups':[]}
        self.write(self.root/'sources/crosswalk.json',self.cross)
        self.lib=self.freshlib()
    def freshlib(self):
        expected={}
        for origin,p in [('base',self.pathbase),('start',self.pathfragment)]:
            for row in json.loads(p.read_text())['sources']:
                expected.setdefault(row['id'],[]).append({**row,'_origin':origin})
        reg={sid:next((r for r in versions if r.get('verified_on')),versions[0]) for sid,versions in expected.items()}
        return SimpleNamespace(taxonomy=copy.deepcopy(self.tax),crosswalk=copy.deepcopy(self.cross),
                               article_origins=copy.deepcopy(self.cross['article_origins']),
                               source_variants=expected,register=reg)
    def check(self):return gate.check_original_source_graph(self.root,self.lib)
    def hold(self):
        with self.assertRaises((gate.CustodyHold,ValueError,OSError)):
            self.check()
    def test_positive_two_source_file_origins(self):
        r=self.check();self.assertEqual(r['source_variant_ids'],2);self.assertEqual(len(r['source_file_sha256']),2)
    def test_stable_frozen_replay(self):self.assertEqual(self.check(),self.check())
    def test_same_url_different_ids_preserved(self):
        self.assertEqual(len(self.lib.source_variants),2);self.check()
    def test_disk_and_memory_tamper_still_blocked_by_frozen_sha(self):
        self.sources['start'][0]['supports']='NEW unreviewed scope';self.write(self.pathfragment,{'sources':self.sources['start']})
        self.lib=self.freshlib();self.hold()
    def test_disk_and_memory_url_retarg_still_blocked_by_frozen_sha(self):
        self.sources['base'][0]['url']='https://other.example/';self.write(self.pathbase,{'sources':self.sources['base']})
        self.lib=self.freshlib();self.hold()
    def test_disk_pin_count_corrupt(self):
        self.cross['source_files'][0]['count']=999;self.write(self.root/'sources/crosswalk.json',self.cross)
        self.lib=self.freshlib();self.hold()
    def test_disk_pin_blob_corrupt(self):
        self.cross['source_files'][0]['git_blob_sha']='0'*40;self.write(self.root/'sources/crosswalk.json',self.cross)
        self.lib=self.freshlib();self.hold()
    def test_disk_pin_path_corrupt(self):
        self.cross['source_files'][0]['path']='preparedness/sources/bad.json';self.write(self.root/'sources/crosswalk.json',self.cross)
        self.lib=self.freshlib();self.hold()
    def test_disk_pin_origin_corrupt(self):
        self.cross['source_files'][0]['origin']='health';self.write(self.root/'sources/crosswalk.json',self.cross)
        self.lib=self.freshlib();self.hold()
    def test_disk_pin_duplicate(self):
        self.cross['source_files'][1]['path']=self.cross['source_files'][0]['path']
        self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib();self.hold()

# 56 independent mutation cases for hashes, paths, counts, membership and origins.
def mutation(i):
    def test(self):
        p=self.pathbase if i%2==0 else self.pathfragment
        if i%7==0:
            doc=json.loads(p.read_text());doc['sources'][0]['supports']+=' unreviewed-'+str(i)
            self.write(p,doc);self.lib=self.freshlib()
        elif i%7==1:
            doc=json.loads(p.read_text());doc['sources'][0]['publisher']='Vendor-'+str(i)
            self.write(p,doc);self.lib=self.freshlib()
        elif i%7==2:
            self.cross['source_files'][i%2]['git_blob_sha']='0'*40
            self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib()
        elif i%7==3:
            self.cross['source_files'][i%2]['count']+=1
            self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib()
        elif i%7==4:
            self.cross['source_files'][i%2]['origin']='forged'
            self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib()
        elif i%7==5:
            self.cross['source_files'][i%2]['path']='preparedness/other-source.json'
            self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib()
        else:
            self.cross['source_files'].append(copy.deepcopy(self.cross['source_files'][i%2]))
            self.write(self.root/'sources/crosswalk.json',self.cross);self.lib=self.freshlib()
        self.hold()
    return test
for i in range(56):setattr(PinFixture,f'test_frozen_pin_mutation_{i:02d}',mutation(i))

if __name__=='__main__': unittest.main()
