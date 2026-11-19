"""R477 synthetic-only fail-closed custody tests: no original content edited."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r477_origin_scope_custody as g


def emit(root, path, obj):
    p=root/path
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode()
    p.write_bytes(raw)
    return g.blob(raw)

class TestR477(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        base=[{'id':'base-plan','url':'https://example.org/plan','verified_on':'2026-11-01',
               'title':'Plan source','supports':'Plan-specific guidance'},
              {'id':'shared-base','url':'https://example.org/shared','verified_on':'2026-11-01',
               'title':'Original shared source','supports':'Base reading only'}]
        shelter=[{'id':'shelter-shared','url':'https://example.org/shared',
                  'title':'Other team same URL','supports':'Different narrower reading',
                  'verified_on':'2026-11-02'}]
        base_sha=emit(self.root,Path('sources/register.json'),{'sources':base})
        shelter_sha=emit(self.root,Path('sources/fragments/shelter.json'),{'sources':shelter})
        srcfiles=[{'origin':'base','path':'preparedness/sources/register.json','git_blob_sha':base_sha,'count':2},
                  {'origin':'shelter','path':'preparedness/sources/fragments/shelter.json','git_blob_sha':shelter_sha,'count':1}]
        self.crosswalk={'raw_source_rows':3,'unique_source_urls':2,'duplicate_url_groups':1,
                        'source_files':srcfiles,'article_origins':{}}
        self.cb=emit(self.root,Path('sources/crosswalk.json'),self.crosswalk)
        recs=[]
        for spec,seq in [(srcfiles[0],base),(srcfiles[1],shelter)]:
            for source in seq:
                recs.append({'origin':spec['origin'],'source_file':spec['path'],
                             'source_file_git_blob':spec['git_blob_sha'],'source':source})
        self.index={'schema':'fv-r477-authentic-244-source-row-index-v1','repo':g.REPO,
                    'candidate_ref':g.PARENT,'crosswalk_blob':self.cb,
                    'release':'DRAFT_HARD_HOLD','qualified_qd_pass':False,
                    'publication_authorized':False,'review_required':True,
                    'raw_source_rows':3,'unique_literal_urls':2,'shared_literal_url_groups':1,
                    'source_file_blobs':[{'origin':s['origin'],'path':s['path'],
                                          'blob':s['git_blob_sha'],'count':s['count']} for s in srcfiles],
                    'records':recs,
                    'shared_urls':[{'url':'https://example.org/shared','source_origin_id_memberships':[
                        {'origin':'base','id':'shared-base'}, {'origin':'shelter','id':'shelter-shared'}],
                        'human_reading_scope_review':'PENDING'}]}
        self.ib=emit(self.root,Path('reviews/r477_authenticated_source_register_index.json'),self.index)
        articles=[]
        self.batches=[]
        for i in range(35):
            slug=f'article-{i+1:02}'
            origin='base' if i%2==0 else 'shelter'
            self.crosswalk['article_origins'][slug]=origin
            ids=['base-plan','shared-base' if origin=='base' else 'shelter-shared']
            body=('<section><p>Original context and '+f'{{{{cite:{ids[0]}}}}}' +
                  '</p><p>Another safe reading context '+f'{{{{cite:{ids[1]}}}}}'+'</p></section>')
            bpath=Path(f'content/articles/{slug}.body.html')
            (self.root/bpath).parent.mkdir(parents=True,exist_ok=True)
            (self.root/bpath).write_text(body)
            meta={'n':i+1,'slug':slug,'status':{'publish':'draft'},
                  'safety_review':{'state':'pending','reviewer':None},
                  'source_use':{ids[0]:'Specific original plan context',ids[1]:'Other original limited reading'}}
            mpath=Path(f'content/articles/{slug}.meta.json')
            mb=emit(self.root,mpath,meta)
            bb=g.blob(body.encode())
            articles.append({'slug':slug,'body':{'path':str(bpath),'git_blob':bb,'bytes':len(body)},
                             'meta':{'path':str(mpath),'git_blob':mb,'bytes':(self.root/mpath).stat().st_size}})
            a={'slug':slug,'n':i+1,'origin':origin,'body_git_blob':bb,'metadata_git_blob':mb,
               'authored_publish':'draft','authored_safety_state':'pending',
               'qualified_safety_approval_verified':False,'citation_occurrences':2,
               'distinct_citation_ids':2,'citation_sequence':ids,
               'source_claims':[{'sid':sid,'source_use_exact':meta['source_use'][sid],
                     'occurrences':1,'first_context':body[max(0,body.index('{{cite:'+sid+'}}')-100):
                         body.index('{{cite:'+sid+'}}')+160]} for sid in ids]}
            if i%7==0:
                self.batches.append({'schema':'fv-r477-authentic-35-article-scope-custody-batch-v1',
                  'repo':g.REPO,'candidate_ref':g.PARENT,'candidate_manifest_blob':None,
                  'crosswalk_blob':None,'authenticated_source_index_blob':None,
                  'batch':len(self.batches)+1,'total_batches':5,'release':'DRAFT_HARD_HOLD',
                  'review_state':'ALL_CLAIM_SCOPES_UNADJUDICATED',
                  'qualified_qd_pass':False,'publication_authorized':False,'articles':[]})
            self.batches[-1]['articles'].append(a)
        self.cb=emit(self.root,Path('sources/crosswalk.json'),self.crosswalk)
        self.index['crosswalk_blob']=self.cb
        self.ib=emit(self.root,Path('reviews/r477_authenticated_source_register_index.json'),self.index)
        self.manifest={'schema':'fv-preparedness-r476-35-candidate-pair-snapshot-v1',
                       'candidate_parent_sha':'1f8261505202ccd3def3c10a0dc070' if False else
                       '1f8261505202ccd3def3c10b34853da21868acf2',
                       'release':'DRAFT_HARD_HOLD','articles':articles}
        self.mb=emit(self.root,Path('reviews/r476_35_article_candidate_custody.json'),self.manifest)
        for b in self.batches:
            b['crosswalk_blob']=self.cb
            b['authenticated_source_index_blob']=self.ib
            b['candidate_manifest_blob']=self.mb

    def check(self, manifest=None,crosswalk=None,index=None,batches=None):
        return g.audit(self.root,manifest if manifest is not None else self.manifest,
             crosswalk if crosswalk is not None else self.crosswalk,
             index if index is not None else self.index,
             batches if batches is not None else self.batches,
             expected=(35,3,2,1,70,70),expected_manifest_blob=self.mb,
             expected_crosswalk_blob=self.cb,expected_index_blob=self.ib)

    def test_structural_receipt_never_releases(self):
        result=self.check()
        self.assertEqual(result['literal_citations'],70)
        for key in ['qualified_qd_pass','native_build_pass','wordpress_export_parity_pass',
                    'publication_authorized','verified_commercial_conversion']:
            self.assertIs(result[key],False)

    def test_every_original_article_guarded(self):
        for i in range(35):
            with self.subTest(article=i):
                rows=copy.deepcopy(self.batches)
                rows[i//7]['articles'][i%7]['source_claims'][0]['source_use_exact']='genericized claim'
                with self.assertRaises(g.Hold):self.check(batches=rows)

    def test_every_original_citation_sequence_guarded(self):
        for i in range(35):
            with self.subTest(article=i):
                rows=copy.deepcopy(self.batches)
                rows[i//7]['articles'][i%7]['citation_sequence'].reverse()
                with self.assertRaises(g.Hold):self.check(batches=rows)

    def test_source_origins_cannot_be_reassigned(self):
        for i in range(35):
            with self.subTest(article=i):
                rows=copy.deepcopy(self.batches)
                rows[i//7]['articles'][i%7]['origin']='unrelated-team'
                with self.assertRaises(g.Hold):self.check(batches=rows)

    def test_source_and_human_review_mutations(self):
        for i in range(40):
            with self.subTest(i=i):
                ix=copy.deepcopy(self.index)
                if i%8==0:ix['records'][i%3]['source']['supports']='false universal claim'
                elif i%8==1:ix['records'][i%3]['source']['url']='https://example.org/substitute'
                elif i%8==2:ix['records'][i%3]['origin']='other author'
                elif i%8==3:ix['shared_urls'][0]['human_reading_scope_review']='APPROVED'
                elif i%8==4:ix['shared_urls'][0]['source_origin_id_memberships'].reverse()
                elif i%8==5:ix['qualified_qd_pass']=True
                elif i%8==6:ix['source_file_blobs'][0]['blob']='0'*40
                else:ix['records'].pop()
                with self.assertRaises(g.Hold):self.check(index=ix)

    def test_article_mutations(self):
        for i in range(50):
            with self.subTest(i=i):
                b=copy.deepcopy(self.batches)
                row=b[i%5]['articles'][i%7]
                k=i%10
                if k==0:row['body_git_blob']='0'*40
                elif k==1:row['metadata_git_blob']='f'*40
                elif k==2:row['authored_publish']='published'
                elif k==3:row['authored_safety_state']='approved'
                elif k==4:row['qualified_safety_approval_verified']=True
                elif k==5:row['source_claims'][0]['occurrences']+=1
                elif k==6:row['citation_occurrences']+=1
                elif k==7:row['distinct_citation_ids']+=1
                elif k==8:row['source_claims'][1]['first_context']='citation context obscured'
                else:row['source_claims'].pop()
                with self.assertRaises(g.Hold):self.check(batches=b)

    def test_batch_review_status(self):
        for i in range(5):
            b=copy.deepcopy(self.batches)
            b[i]['review_state']='QD_PASS'
            with self.assertRaises(g.Hold):self.check(batches=b)

    def test_body_edit_detected_even_if_same_citation_count(self):
        path=self.root/'content/articles/article-01.body.html'
        original=path.read_bytes()
        try:
            path.write_bytes(original.replace(b'Original context',b'Changed context!'))
            with self.assertRaises(g.Hold):self.check()
        finally:path.write_bytes(original)

    def test_metadata_safety_state_change_detected(self):
        path=self.root/'content/articles/article-02.meta.json'
        original=path.read_bytes()
        try:
            path.write_bytes(original.replace(b'"pending"',b'"approved"'))
            with self.assertRaises(g.Hold):self.check()
        finally:path.write_bytes(original)

    def test_native_source_registry_changed_detected(self):
        path=self.root/'sources/register.json'
        original=path.read_bytes()
        try:
            path.write_bytes(original.replace(b'Plan source',b'Other claim'))
            with self.assertRaises(g.Hold):self.check()
        finally:path.write_bytes(original)

    def test_invalid_json_duplicate_keys(self):
        with self.assertRaises(g.Hold):g.strict_json(b'{"a":1,"a":2}')

    def test_symlink_escape_not_accepted(self):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile() as f:
            target=self.root/'rogue.json'
            target.symlink_to(f.name)
            with self.assertRaises(g.Hold):g.native_file(self.root,'rogue.json','0'*40)

    def test_missing_source_file_is_hold(self):
        path=self.root/'sources/fragments/shelter.json'
        original=path.read_bytes()
        try:
            path.unlink()
            with self.assertRaises(g.Hold):self.check()
        finally:path.write_bytes(original)

    def test_no_article_batch_can_go_missing(self):
        for i in range(5):
            b=copy.deepcopy(self.batches)
            b[i]['articles'].pop()
            with self.assertRaises(g.Hold):self.check(batches=b)



def _case_scope(i):
    def run(self):
        batch=copy.deepcopy(self.batches)
        batch[i//7]['articles'][i%7]['source_claims'][0]['source_use_exact']='false claimed reading scope'
        with self.assertRaises(g.Hold):
            self.check(batches=batch)
    return run

def _case_citation(i):
    def run(self):
        batch=copy.deepcopy(self.batches)
        batch[i//7]['articles'][i%7]['citation_sequence'].reverse()
        with self.assertRaises(g.Hold):
            self.check(batches=batch)
    return run

for _i in range(35):
    setattr(TestR477,f'test_each_article_scope_{_i:02}',_case_scope(_i))
    setattr(TestR477,f'test_each_article_citation_{_i:02}',_case_citation(_i))

if __name__=='__main__':unittest.main()
