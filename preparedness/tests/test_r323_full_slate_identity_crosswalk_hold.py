"""R323 complete synthetic 35+6 slate, adversarial source/identity/safety fixtures.
No test writes into real Preparedness source or fires any CMS/merchant request.
"""
import copy
import json
import unittest
from preparedness.tests.test_r320_conflict_adjudication_docket_hold import dossier_fixture
from preparedness.tools import r323_full_slate_identity_crosswalk_hold as gate
from preparedness.tools import r320_conflict_adjudication_docket_hold as review
from preparedness.tools import r319_three_way_custody_hold as custody

class Slate(unittest.TestCase):
    def setUp(self):
        self.manifest,_ = dossier_fixture()
        for rec in self.manifest['records']:
            rec['path']=rec['path'].replace('/tools/extra-tool-00.', '/tools/family-reunification-card.')
        self.raw={}
        self.taxonomy={'base_path':'/preparedness/','sections':[{'slug':'start-here'},{'slug':'field-tools'}], 'slate':[], 'tools':[]}
        self.paths={r['path']:r for r in self.manifest['records']}
        for family in ('articles','tools'):
            meta_paths=sorted(p for p in self.paths if f'/{family}/' in p and p.endswith('.meta.json'))
            for i,mp in enumerate(meta_paths):
                slug=mp.split('/')[-1].removesuffix('.meta.json')
                n=(i+1 if family=='articles' else i+101)
                if slug=='reunification-plan':n=102
                if slug=='family-reunification-card':n=104
                # Ensure identity 102/104 reserved and unique even for arbitrary fake names.
                if family=='tools' and slug not in ('reunification-plan','family-reunification-card') and n in (102,104):n+=10
                meta={'n':n,'slug':slug,'section':'start-here' if family=='articles' else 'field-tools',
                      'track':'modern','kind':'tool' if family=='tools' else 'article',
                      'status':{'editorial':'drafted','publish':'draft'},
                      'safety_review':{'state':'pending'},'source_use':{'src-001':'Synthetic context only'},
                      'related':[]}
                if family=='articles':
                    self.taxonomy['slate'].append({'n':n,'slug':slug,'section':'start-here','track':'modern'})
                else:self.taxonomy['tools'].append({'slug':slug})
                self.raw[mp]=json.dumps(meta,sort_keys=True).encode()
                self.raw[mp.replace('.meta.json','.body.html')]=b'<h2>Guide {{cite:src-001}}</h2><p>Read the full synthetic guide before doing anything.</p>'
        for path, rec in self.paths.items():
            self._pin(path, self.raw[path])
        self.docket=review.build_docket(self.manifest)
    def _pin(self,path,data):
        self.raw[path]=data
        rec=self.paths[path]
        rec['integrated']={'sha':custody.blob(data),'size':len(data)}
        if rec['disposition']=='IDENTICAL':
            rec['continuation']=rec['integrated'].copy();rec['followup']=rec['integrated'].copy()
    def replace(self,path,data):
        self._pin(path,data)
        self.docket=review.build_docket(self.manifest)
    def edit_meta(self,slug,mutate, family='articles'):
        path=f'preparedness/content/{family}/{slug}.meta.json'
        v=json.loads(self.raw[path]);mutate(v)
        self.replace(path,json.dumps(v,sort_keys=True).encode())
    def check(self):return gate.audit(self.manifest,self.docket,self.taxonomy,self.raw.__getitem__)
    def has(self,part):
        r=self.check();self.assertEqual(r['state'],'INVALID_HARD_HOLD',r)
        self.assertTrue(any(part in e for e in r['errors']),r['errors'])
    def test_valid_synthetic_integrity_still_hard_holds(self):
        r=self.check();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors']);self.assertEqual(r['guides_audited'],41)
        self.assertEqual(r['source_conflicts_held'],15)
        self.assertFalse(r['release']['independent_qd_pass']);self.assertFalse(r['release']['paid_conversion_verified'])
    def test_deterministic(self):self.assertEqual(self.check(),self.check())
    def test_no_lead_or_sales_claim(self):self.assertFalse(any(self.check()['release'].values()))
    def test_missing_taxonomy(self):self.taxonomy={};self.has('TAXONOMY_BASE_PATH_DRIFT')
    def test_unreviewed_extra_source(self):self.manifest['records'].append(copy.deepcopy(self.manifest['records'][0]));self.has('R319_INTEGRATED_INVENTORY_INVALID')
    def test_review_false_approval(self):self.docket['records'][0]['independent_reviewer_approved']=True;self.has('R320_CONFLICT_REVIEW_DOCKET_INVALID')
    def test_wrong_base_url(self):self.taxonomy['base_path']='/products/';self.has('TAXONOMY_BASE_PATH_DRIFT')
    def test_missing_article_slate(self):self.taxonomy['slate'].pop();self.has('TAXONOMY_ARTICLE_OR_TOOL_MAP_INVALID')
    def test_duplicate_taxonomy_slug(self):self.taxonomy['slate'][0]['slug']=self.taxonomy['slate'][1]['slug'];self.has('TAXONOMY_DUPLICATE_OR_MISSING_ARTICLES')
    def test_no_safety_claim_from_approved_label(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v['safety_review'].update(state='approved'))
        r=self.check();self.assertEqual(r['state'],'DRAFT_HARD_HOLD');self.assertTrue(r['independent_review_flags']);self.assertFalse(r['release']['qualified_safety_approved'])
    def test_published_metadata_rejected(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v['status'].update(publish='published'));self.has('NON_DRAFT_AUTHORED_SOURCE')
    def test_duplicate_article_number(self):
        a,b=self.taxonomy['slate'][:2];self.edit_meta(b['slug'],lambda v:v.update(n=a['n']));self.has('MISSING_OR_DUPLICATE_NUMBER')
    def test_duplicate_tool_number(self):
        paths=[p for p in self.raw if '/tools/' in p and p.endswith('.meta.json')]
        val=json.loads(self.raw[paths[0]])['n'];v=json.loads(self.raw[paths[1]]);v['n']=val
        self.replace(paths[1],json.dumps(v).encode());self.has('MISSING_OR_DUPLICATE_NUMBER')
    def test_wrong_tool_102_id(self):
        self.edit_meta('reunification-plan',lambda v:v.update(n=999),family='tools');self.has('REUNIFICATION_TOOL_IDENTITY_COLLISION')
    def test_wrong_tool_104_id(self):
        self.edit_meta('family-reunification-card',lambda v:v.update(n=999),family='tools');self.has('REUNIFICATION_TOOL_IDENTITY_COLLISION')
    def test_unrecognized_section(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v.update(section='secret'));self.has('INVALID_SOURCE_SECTION')
    def test_wrong_article_taxonomy_number(self):
        self.taxonomy['slate'][0]['n']=99;self.has('ARTICLE_TAXONOMY_IDENTITY_DRIFT')
    def test_wrong_tool_section(self):self.edit_meta('reunification-plan',lambda v:v.update(section='start-here'),family='tools');self.has('TOOL_SECTION_DRIFT')
    def test_meta_slug_disagreement(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v.update(slug='impostor'));self.has('METADATA_SLUG_DRIFT')
    def test_source_use_removed(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v.update(source_use={}));self.has('CITATION_DECLARATION_MISMATCH')
    def test_source_use_fabricated(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v['source_use'].update(fake='citation'));self.has('CITATION_DECLARATION_MISMATCH')
    def test_unresolved_related_link(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v.update(related=['retired-water-freebie']));self.has('BROKEN_INTERNAL_RELATED_ROUTE')
    def test_bad_source_use_type(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v.update(source_use=['src-001']));self.has('MISSING_SOURCE_USE_EVIDENCE')
    def test_malformed_citation(self):
        slug=self.taxonomy['slate'][0]['slug'];path=f'preparedness/content/articles/{slug}.body.html'
        self.replace(path,b'<p>{{cite:INVALID!}} words</p>');self.has('MALFORMED_CITATION_TOKEN')
    def test_missing_reading_depth(self):
        slug=self.taxonomy['slate'][0]['slug'];path=f'preparedness/content/articles/{slug}.body.html';self.replace(path,b'');self.has('MISSING_READING_DEPTH')
    def test_duplicate_json_keys(self):
        slug=self.taxonomy['slate'][0]['slug'];path=f'preparedness/content/articles/{slug}.meta.json'
        self.replace(path,self.raw[path].replace(b'"slug":',b'"slug": "wrong", "slug":',1));self.has('MISSING_OR_CHANGED_PINNED_PAIR')
    def test_bad_encoded_body(self):
        slug=self.taxonomy['slate'][0]['slug'];path=f'preparedness/content/articles/{slug}.body.html';self.replace(path,b'\xff');self.has('MISSING_OR_CHANGED_PINNED_PAIR')
    def test_safety_state_unknown(self):
        slug=self.taxonomy['slate'][0]['slug'];self.edit_meta(slug,lambda v:v['safety_review'].update(state='QD PASS'));self.has('UNKNOWN_SAFETY_REVIEW_STATE')
    def test_missing_reunification_plan_tool(self):
        self.manifest['records']=[r for r in self.manifest['records'] if 'tools/reunification-plan' not in r['path']];self.has('R319_INTEGRATED_INVENTORY_INVALID')


def mutation_test(path):
    def test(self):
        self.raw[path]=self.raw[path]+b'\nmutated without source ref approval'
        self.has('MISSING_OR_CHANGED_PINNED_PAIR')
    return test
for family in ('articles','tools'):
    for slug in ((['family-communication-plan','home-fire-escape-plan','homemade-water-filters','making-water-safer','outage-heat-cold-generators','salt-beef-salt-pork-age-of-sail','shelter-or-evacuate'] + [f'extra-article-{i:02}' for i in range(28)]) if family=='articles' else ['power-outage-planner','reunification-plan','family-reunification-card']+[f'extra-tool-{i:02}' for i in range(1,4)]):
        for ext in ('body.html','meta.json'):
            p=f'preparedness/content/{family}/{slug}.{ext}'
            setattr(Slate, 'test_mutate_'+family+'_'+slug.replace('-','_')+'_'+ext.replace('.','_'),mutation_test(p))

if __name__=='__main__':unittest.main()
