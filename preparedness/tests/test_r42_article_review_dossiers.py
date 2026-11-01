"""R42 synthetic source/claim review dossier tests; no real human reviews."""
from __future__ import annotations
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import article_review_dossier_gate as g

H=lambda n:format(n,'064x')
URL='https://example.org/contributor-shared-source'
UNUSED='https://example.org/unused-shared-source'
OTHER='https://example.org/private-tool-source'
SMALL=(2,1,5,3,1,1)

def fixtures(uncited=False):
    src=[('first-guide','modern-a','modern-a','one',URL,2),
         ('old-ways','lost-b','modern-a','two',URL,2),
         ('water-planner','water-tool','water-tool','three',OTHER,1)]
    taxonomy={'slate':[{'n':1,'slug':'first-guide','title':'Practical Water Guide',
                        'track':'modern','section':'water','gate':True,'status':'safety-approved-draft'},
                       {'n':2,'slug':'old-ways','title':'Historical Context',
                        'track':'lost-ways','section':'lost-ways','gate':False,'status':'not-started'}],
              'tools':[{'slug':'water-planner','title':'Emergency Water Math',
                        'gate':True,'status':'drafted-pending-safety-review'},
                       {'slug':'not-developed','title':'Not part of draft','status':'not-started'}]}
    scopes=[];claims=[];falls=[];groups=[]
    for i,(slug,origin,source_origin,sid,url,n) in enumerate(src,1):
        scope=dict.fromkeys(g.r37.SCOPE,'')
        scope.update(source_case_sha256=H(100+i),relationship_sha256=H(200+i),
                     slug=slug,source_id=sid,article_origin=origin,
                     original_source_origin=source_origin,source_url=url,
                     full_original_source_record_json=json.dumps({'id':sid,'url':url,'notes':f'Full individual reading scope {i}'}),
                     full_original_article_source_use=f'Full article-specific reading note {i}',
                     source_record_sha256=H(300+i),source_use_sha256=H(400+i),
                     impacted_claims=str(n),review_state='NOT_STARTED')
        scopes.append(scope)
        if origin!=source_origin:
            fallback=dict.fromkeys(g.r37.FALLBACK,'')
            fallback.update(fallback_case_sha256=H(500+i),relationship_sha256=H(200+i),
                            article_origin=origin,original_source_origin=source_origin,
                            source_url=url,review_state='NOT_STARTED')
            falls.append(fallback)
        for j in range(n):
            claim=dict.fromkeys(g.r37.CLAIM,'')
            claim.update(claim_case_sha256=H(600+10*i+j),relationship_sha256=H(200+i),
                         slug=slug,source_id=sid,source_url=url,
                         original_codepoint_offset=str(j*10),
                         triage_priority_not_verdict=('REVIEW_FIRST' if j==0 else 'STANDARD_REVIEW'),
                         triage_tags_not_safety_findings='["water"]',
                         exact_original_context='original reference [CITATION] with context',
                         review_state='NOT_STARTED')
            claims.append(claim)
    urls=[URL,UNUSED] if uncited else [URL]
    for z,url in enumerate(urls):
        group=dict.fromkeys(g.r37.GROUP,'')
        related=sorted(s['relationship_sha256'] for s in scopes if s['source_url']==url)
        citations=sorted(c['claim_case_sha256'] for c in claims if c['source_url']==url)
        group.update(global_group_case_sha256=H(700+z),source_url=url,
                     original_crosswalk_sha256=H(800+z),
                     full_original_crosswalk_group_json=json.dumps({'url':url,'notes':['original A','original B']}),
                     distinct_original_variants_json='[{"notes":"scope-A"},{"notes":"scope-B"}]',
                     used_in_any_citation=str(bool(related)).lower(),
                     cited_relationship_ids_json=json.dumps(related),
                     cited_claim_case_ids_json=json.dumps(citations),review_state='NOT_STARTED')
        groups.append(group)
    rows=dict(zip(g.r37.TABLES,(claims,scopes,falls,groups)))
    csvs={name:g.r37._render(header,rows[name]) for name,header in g.r37.TABLES.items()}
    expected=(2,1,5,3,1,len(groups))
    meta={'schema_version':1,'issue':136,'release_state':'HOLD',
          'machine_authority':g.r37.AUTHORITY,
          **{f:False for f in g.r37.HOLD_FLAGS},
          'parent_R35_fingerprint_sha256':H(7000),
          'parent_R36_fingerprint_sha256':H(7001),
          'parent_R34_original_reading_sha256':H(7002),
          'counts':dict(zip(('articles','tools','claim_reviews','source_scope_reviews',
                             'fallback_reviews','global_shared_url_reviews'),expected)),
          'csv_tables':{name:{'rows':len(rows[name]),
                              'sha256_utf8':hashlib.sha256(body.encode()).hexdigest(),
                              'bytes_utf8':len(body.encode()),'columns':list(g.r37.TABLES[name])}
                        for name,body in csvs.items()}}
    meta['fingerprint_sha256']=g.r37.sha(meta)
    return {'manifest':meta,'csv_tables':csvs},taxonomy,expected

def run(bundle,tax,expected, *, pinned=None):
    if pinned is None:pinned=bundle['manifest']['fingerprint_sha256']
    return g.build_article_review_dossiers(bundle,tax,
                trusted_r37_manifest_sha256=pinned,expected=expected)

def mutate_cell(bundle, table, index, key, value):
    rows=list(csv.DictReader(io.StringIO(bundle['csv_tables'][table],newline='')))
    rows[index][key]=value
    bundle['csv_tables'][table]=g.r37._render(g.r37.TABLES[table],rows)
    meta=bundle['manifest']['csv_tables'][table]
    data=bundle['csv_tables'][table].encode()
    meta['sha256_utf8']=hashlib.sha256(data).hexdigest()
    meta['bytes_utf8']=len(data)
    bundle['manifest']['fingerprint_sha256']=g.r37.sha({k:v for k,v in bundle['manifest'].items()
                                                       if k!='fingerprint_sha256'})

class Positive(unittest.TestCase):
    def setUp(self):self.bundle,self.tax,self.expected=fixtures()
    def test_3_article_and_tool_dossiers(self):self.assertEqual(len(run(self.bundle,self.tax,self.expected)['article_dossiers']),3)
    def test_all_claims_preserved(self):self.assertEqual(sum(x['counts']['claims'] for x in run(self.bundle,self.tax,self.expected)['article_dossiers']),5)
    def test_all_scopes_preserved(self):self.assertEqual(sum(x['counts']['scopes'] for x in run(self.bundle,self.tax,self.expected)['article_dossiers']),3)
    def test_fallback_preserved(self):self.assertEqual(sum(x['counts']['fallbacks'] for x in run(self.bundle,self.tax,self.expected)['article_dossiers']),1)
    def test_shared_url_in_two_dossiers(self):self.assertEqual(sum(x['counts']['groups'] for x in run(self.bundle,self.tax,self.expected)['article_dossiers']),2)
    def test_duplicate_url_does_not_merge_scopes(self):
        out=run(self.bundle,self.tax,self.expected)
        a={r['full_original_article_source_use'] for x in out['article_dossiers'] for r in x['original_review_records']['scopes']}
        self.assertEqual(len(a),3)
    def test_tool_marked_distinct(self):
        out=run(self.bundle,self.tax,self.expected)
        self.assertEqual([x['slug'] for x in out['article_dossiers'] if x['is_tool']],['water-planner'])
    def test_taxonomy_approval_label_not_safety_clearance(self):
        d=next(x for x in run(self.bundle,self.tax,self.expected)['article_dossiers'] if x['slug']=='first-guide')
        self.assertEqual(d['taxonomy_status_recorded_not_a_human_verdict'],'safety-approved-draft')
        self.assertIs(d['qualified_safety_clearance'],False)
    def test_group_uncited_preserved(self):
        b,t,e=fixtures(uncited=True);out=run(b,t,e)
        self.assertEqual(len(out['uncited_shared_url_groups_unreviewed']),1)
        self.assertEqual(out['uncited_shared_url_groups_unreviewed'][0]['source_url'],UNUSED)
    def test_all_counters_exact(self):self.assertEqual(run(self.bundle,self.tax,self.expected)['counts'],self.bundle['manifest']['counts'])
    def test_deterministic(self):self.assertEqual(run(self.bundle,self.tax,self.expected),run(self.bundle,self.tax,self.expected))
    def test_source_unchanged(self):
        old=copy.deepcopy((self.bundle,self.tax));run(self.bundle,self.tax,self.expected)
        self.assertEqual((self.bundle,self.tax),old)
    def test_output_fingerprint(self):
        out=run(self.bundle,self.tax,self.expected)
        self.assertEqual(out['fingerprint_sha256'],g.r37.sha({k:v for k,v in out.items() if k!='fingerprint_sha256'}))
    def test_article_fingerprints(self):
        for d in run(self.bundle,self.tax,self.expected)['article_dossiers']:
            self.assertEqual(d['fingerprint_sha256'],g.r37.sha({k:v for k,v in d.items() if k!='fingerprint_sha256'}))
    def test_flags_all_false(self):
        out=run(self.bundle,self.tax,self.expected)
        for x in [out,*out['article_dossiers']]:
            for flag in g.FLAGS:self.assertIs(x[flag],False)
    def test_priority_preserved(self):
        out=run(self.bundle,self.tax,self.expected)
        self.assertEqual(sum(x['high_priority_claim_cases'] for x in out['article_dossiers']),3)
    def test_no_hidden_review_progress(self):
        out=run(self.bundle,self.tax,self.expected)
        for x in out['article_dossiers']:
            for kind in x['original_review_records']:
                for item in x['original_review_records'][kind]:self.assertEqual(item['review_state'],'NOT_STARTED')
    def test_no_url_dedupe(self):self.assertTrue(run(self.bundle,self.tax,self.expected)['all_case_rows_preserved_without_url_deduplication'])
    def test_no_publication(self):self.assertIs(run(self.bundle,self.tax,self.expected)['publication_authorized'],False)
    def test_no_identity(self):self.assertIs(run(self.bundle,self.tax,self.expected)['reviewer_real_identity_verified'],False)
    def test_original_research_text(self):
        out=run(self.bundle,self.tax,self.expected)
        self.assertTrue(any('Full individual reading scope' in s['full_original_source_record_json']
                            for x in out['article_dossiers'] for s in x['original_review_records']['scopes']))

class Mutation(unittest.TestCase):
    def setUp(self):self.b,self.t,self.e=fixtures()
    def fails(self,b=None,t=None,e=None,pinned=None):
        with self.assertRaises((g.DossierHold,ValueError,TypeError)):
            run(b if b is not None else self.b,t if t is not None else self.t,
                e if e is not None else self.e,pinned=pinned)
    def test_untrusted_anchor(self):self.fails(pinned='a'*64)
    def test_missing_anchor(self):self.fails(pinned='')
    def test_missing_worksheet(self):
        b=copy.deepcopy(self.b);del b['csv_tables']['claim_review.csv'];self.fails(b=b)
    def test_extra_worksheet(self):
        b=copy.deepcopy(self.b);b['csv_tables']['extra.csv']='';self.fails(b=b)
    def test_manifest_approval(self):
        b=copy.deepcopy(self.b);b['manifest']['may_publish']=True;self.fails(b=b)
    def test_changed_manifest_without_resign(self):
        b=copy.deepcopy(self.b);b['manifest']['counts']['articles']=42;self.fails(b=b)
    def test_missing_slate(self):
        t=copy.deepcopy(self.t);del t['slate'];self.fails(t=t)
    def test_bad_ordinal(self):
        t=copy.deepcopy(self.t);t['slate'][0]['n']=999;self.fails(t=t)
    def test_duplicate_article_slug(self):
        t=copy.deepcopy(self.t);t['slate'][1]['slug']='first-guide';self.fails(t=t)
    def test_slug_traversal(self):
        t=copy.deepcopy(self.t);t['slate'][1]['slug']='../../etc';self.fails(t=t)
    def test_missing_tool(self):
        t=copy.deepcopy(self.t);t['tools']=[];self.fails(t=t)
    def test_taxonomy_loses_article(self):
        t=copy.deepcopy(self.t);t['slate'].pop();self.fails(t=t)
    def test_wrong_expected_counts(self):self.fails(e=(2,1,5,3,1,3))
    def test_wrong_expected_type(self):self.fails(e=[2,1,5,3,1,1])
    def test_unsupported_tool_slug(self):
        with self.assertRaises(g.DossierHold):g.build_article_review_dossiers(
            self.b,self.t,trusted_r37_manifest_sha256=self.b['manifest']['fingerprint_sha256'],
            expected=self.e,tool_slugs=('fake',))

MUTATIONS={
 ('source_scope_review.csv',0,'relationship_sha256'):'f'*64,
 ('source_scope_review.csv',0,'source_case_sha256'):'0'*64,
 ('source_scope_review.csv',0,'slug'):'other-article',
 ('source_scope_review.csv',0,'source_id'):'',
 ('source_scope_review.csv',0,'source_url'):'http://unsafe.example',
 ('source_scope_review.csv',0,'full_original_source_record_json'):'',
 ('source_scope_review.csv',0,'full_original_article_source_use'):'',
 ('source_scope_review.csv',0,'source_record_sha256'):'bogus',
 ('source_scope_review.csv',0,'source_use_sha256'):'bogus',
 ('source_scope_review.csv',0,'impacted_claims'):'99',
 ('source_scope_review.csv',0,'review_state'):'APPROVED',
 ('source_scope_review.csv',0,'human_reading_scope_check'):'APPROVED',
 ('claim_review.csv',0,'relationship_sha256'):'f'*64,
 ('claim_review.csv',0,'slug'):'different-article',
 ('claim_review.csv',0,'source_id'):'different-source',
 ('claim_review.csv',0,'source_url'):'https://evil.example',
 ('claim_review.csv',0,'triage_priority_not_verdict'):'SAFE_TO_PUBLISH',
 ('claim_review.csv',0,'exact_original_context'):'citation missing marker',
 ('claim_review.csv',0,'original_codepoint_offset'):'-1',
 ('claim_review.csv',0,'review_state'):'FINISHED',
 ('claim_review.csv',0,'human_claim_support_assessment'):'VERIFIED',
 ('fallback_scope_review.csv',0,'relationship_sha256'):'f'*64,
 ('fallback_scope_review.csv',0,'article_origin'):'wrong-cluster',
 ('fallback_scope_review.csv',0,'original_source_origin'):'lost-b',
 ('fallback_scope_review.csv',0,'source_url'):'https://evil.example',
 ('fallback_scope_review.csv',0,'review_state'):'DONE',
 ('fallback_scope_review.csv',0,'human_reading_scope_match'):'YES',
 ('global_shared_url_review.csv',0,'source_url'):'https://evil.example',
 ('global_shared_url_review.csv',0,'used_in_any_citation'):'false',
 ('global_shared_url_review.csv',0,'cited_relationship_ids_json'):'[]',
 ('global_shared_url_review.csv',0,'cited_claim_case_ids_json'):'[]',
 ('global_shared_url_review.csv',0,'original_crosswalk_sha256'):'',
 ('global_shared_url_review.csv',0,'full_original_crosswalk_group_json'):'',
 ('global_shared_url_review.csv',0,'distinct_original_variants_json'):'',
 ('global_shared_url_review.csv',0,'review_state'):'APPROVED',
 ('global_shared_url_review.csv',0,'human_source_conflict_notes'):'approved',
}
class CellMutations(unittest.TestCase):pass
for name,value in MUTATIONS.items():
    table,index,field=name
    def make(table,index,field,value):
        def test(self):
            b,t,e=fixtures();mutate_cell(b,table,index,field,value)
            with self.assertRaises((g.DossierHold,ValueError,TypeError)):
                run(b,t,e)
        return test
    setattr(CellMutations,'test_reject_'+field+'_'+str(len(CellMutations.__dict__)),
            make(table,index,field,value))

if __name__=='__main__':unittest.main()
