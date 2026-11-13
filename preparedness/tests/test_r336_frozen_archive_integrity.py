"""R336 synthetic ONLY mutation testing. Tests do not approve authentic content."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r336_frozen_archive_integrity as gate

HEADS={k:f'{i+1:040x}' for i,k in enumerate(('start','food','health','hist-field','hist-food','hist-home','shelter','shelter-continuation','shelter-followup'))}


def tree(root):
    sections=['start-here','water','food','shelter-power','health-sanitation','family-communication','lost-ways','field-tools']
    sl=[{'n':n,'slug':f'article-{n:02d}','section':sections[(n-1)%7]} for n in range(1,36)]
    (root/'taxonomy.json').write_text(json.dumps({'base_path':'/preparedness/','sections':[{'slug':s} for s in sections],'slate':sl}),encoding='utf-8')
    for kind, count in [('articles',35),('tools',6)]:
        folder=root/'content'/kind; folder.mkdir(parents=True)
        for i in range(1,count+1):
            slug=f'article-{i:02d}' if kind=='articles' else f'tool-{i:02d}'
            meta={'slug':slug,'n':i if kind=='articles' else 100+i,
                  'section':sections[(i-1)%7] if kind=='articles' else 'field-tools',
                  'status':{'publish':'draft'},'safety_review':{'state':'pending'},
                  'source_use':{'source-one':'Official research scope unadjudicated'}}
            (folder/f'{slug}.meta.json').write_text(json.dumps(meta),encoding='utf-8')
            (folder/f'{slug}.body.html').write_text(f'<h2 id="section-{i}">Section {i}</h2>\n<p>'+('Relevant background evidence with context. '*25)+'{{cite:source-one}}</p>',encoding='utf-8')
    (root/'audits').mkdir()
    (root/'audits'/'r334_frozen_nine_head_source_object_crosswalk.json').write_text(json.dumps({
       'source_heads':HEADS,'distinct_source_divergence_count':14,
       'unresolved_legacy_adjudication_conflict_count_from_issue136':15,
       **{k:False for k in ('word_depth_verified','canonical_url_uniqueness_verified','citation_claim_support_verified',
                    'source_conflict_human_signoff','qualified_qd_pass','may_merge','may_publish')}}),encoding='utf-8')
    return gate.snapshot_from_tree(root,evidence_sha='a'*40,source_heads=HEADS)


class SourceCustodyR336(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td=tempfile.TemporaryDirectory(prefix='r336-synthetic-only-')
        cls.root=Path(cls.td.name)
        cls.witness=tree(cls.root)
        cls.items=[(r['kind'],r['slug']) for r in cls.witness['entries']]
    @classmethod
    def tearDownClass(cls):cls.td.cleanup()
    def audit(self,w=None):return gate.audit(self.root,copy.deepcopy(self.witness if w is None else w))
    def test_baseline_is_review_only(self):
        r=self.audit();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual((r['articles_checked'],r['tools_checked']),(35,6))
        self.assertFalse(r['may_merge']);self.assertFalse(r['may_publish'])
    def test_frozen_holds_are_explicit(self):self.assertEqual(len(gate.FROZEN_HOLDS),5)
    def test_41_entries_present(self):self.assertEqual(len(self.witness['entries']),41)
    def test_all_citations_have_source_use(self):self.assertTrue(all('source-one' in x['source_use_ids'] for x in self.witness['entries']))
    def test_no_original_writes(self):
        b=(self.root/'content'/'articles'/'article-01.body.html').read_bytes()
        self.audit();self.assertEqual((self.root/'content'/'articles'/'article-01.body.html').read_bytes(),b)
    def test_missing_native_files_reject(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.audit(Path(t),self.witness)['state'],'INVALID_HARD_HOLD')
    def test_invalid_manifest_schema(self):
        w=copy.deepcopy(self.witness);w['schema']='MADE_UP';self.assertIn('INVALID_MANIFEST_SCHEMA',self.audit(w)['errors'])
    def test_manifest_missing_record(self):
        w=copy.deepcopy(self.witness);w['entries'].pop();self.assertIn('MANIFEST_MUST_HAVE_41_ENTRIES',self.audit(w)['errors'])
    def test_tampered_source_ref(self):
        w=copy.deepcopy(self.witness);w['source_ref']='fake';self.assertIn('MISSING_AUTHENTIC_SOURCE_COMMIT',self.audit(w)['errors'])
    def test_forged_qd(self):
        w=copy.deepcopy(self.witness);w['qualified_qd_pass']=True;self.assertIn('FORGED_RELEASE_OR_REVENUE_EVIDENCE',self.audit(w)['errors'])
    def test_forged_merchant(self):
        w=copy.deepcopy(self.witness);w['commercial_sku_verified']=True;self.assertIn('FORGED_RELEASE_OR_REVENUE_EVIDENCE',self.audit(w)['errors'])
    def test_forged_publish(self):
        w=copy.deepcopy(self.witness);w['published_or_live']=True;self.assertIn('FORGED_RELEASE_OR_REVENUE_EVIDENCE',self.audit(w)['errors'])
    def test_forged_holds(self):
        w=copy.deepcopy(self.witness);w['unresolved_holds']=[];self.assertIn('FORGED_RELEASE_OR_REVENUE_EVIDENCE',self.audit(w)['errors'])
    def test_missing_cluster(self):
        w=copy.deepcopy(self.witness);w['source_heads'].pop('shelter');self.assertIn('NINE_HEAD_PINS_MISSING',self.audit(w)['errors'])
    def test_duplicate_manifest_slug(self):
        w=copy.deepcopy(self.witness);w['entries'][1]['slug']=w['entries'][0]['slug'];self.assertIn('DUPLICATE_MANIFEST_SLUG',self.audit(w)['errors'])
    def test_unsafe_slug(self):
        w=copy.deepcopy(self.witness);w['entries'][0]['slug']='../bad';self.assertIn('INVALID_KIND_OR_SLUG',self.audit(w)['errors'])
    def test_route_alias_change(self):
        w=copy.deepcopy(self.witness);w['entries'][0]['route']='/preparedness/water/article-01/';self.assertTrue(any('CANONICAL_ROUTE_DRIFT:' in e for e in self.audit(w)['errors']))
    def test_taxonomy_duplicate_slug(self):
        p=self.root/'taxonomy.json';old=p.read_bytes();d=json.loads(old);d['slate'][1]['slug']=d['slate'][0]['slug']
        try:
            p.write_text(json.dumps(d));self.assertIn('DUPLICATE_TAXONOMY_SLUG',self.audit()['errors'])
        finally:p.write_bytes(old)
    def test_taxonomy_status_not_approval(self):
        p=self.root/'taxonomy.json';old=p.read_bytes();d=json.loads(old);d['slate'][0]['status']='safety-approved-draft'
        try:
            p.write_text(json.dumps(d));self.assertEqual(self.audit()['state'],'DRAFT_HARD_HOLD')
        finally:p.write_bytes(old)
    def test_crosswalk_false_qd(self):
        p=self.root/'audits'/'r334_frozen_nine_head_source_object_crosswalk.json';old=p.read_bytes();d=json.loads(old);d['qualified_qd_pass']=True
        try:
            p.write_text(json.dumps(d));self.assertIn('CROSSWALK_FORGED_APPROVAL',self.audit()['errors'])
        finally:p.write_bytes(old)
    def test_crosswalk_conflicts(self):
        p=self.root/'audits'/'r334_frozen_nine_head_source_object_crosswalk.json';old=p.read_bytes();d=json.loads(old);d['unresolved_legacy_adjudication_conflict_count_from_issue136']=0
        try:
            p.write_text(json.dumps(d));self.assertIn('NINE_HEAD_CROSSWALK_OR_15_CONFLICT_LEDGER_DRIFT',self.audit()['errors'])
        finally:p.write_bytes(old)
    def test_citation_not_in_source_use(self):
        p=self.root/'content'/'articles'/'article-01.body.html';old=p.read_bytes()
        try:
            p.write_bytes(old.replace(b'source-one',b'fake-source'));self.assertIn('CITED_SOURCE_NOT_IN_SOURCE_USE:article-01',self.audit()['errors'])
        finally:p.write_bytes(old)
    def test_duplicate_h2_id(self):
        p=self.root/'content'/'articles'/'article-01.body.html';old=p.read_bytes()
        try:
            p.write_bytes(old+b'<h2 id="section-1">Duplicate</h2>');self.assertIn('DUPLICATE_HEADING_ID:article-01',self.audit()['errors'])
        finally:p.write_bytes(old)


def attach_mutation_tests():
    for kind,slug in SourceCustodyR336.items if hasattr(SourceCustodyR336,'items') else [('articles',f'article-{i:02d}') for i in range(1,36)]+[('tools',f'tool-{i:02d}') for i in range(1,7)]:
        safe=slug.replace('-','_')
        def body_mutation(self,kind=kind,slug=slug):
            p=self.root/'content'/kind/f'{slug}.body.html';before=p.read_bytes()
            try:
                p.write_bytes(before.replace(b'Relevant background evidence with context. ',b''));r=self.audit()
                self.assertIn('READING_DEPTH_LOSS:'+slug,r['errors']);self.assertIn('BODY_SOURCE_DRIFT_REQUIRES_REVIEW:'+slug,r['errors'])
            finally:p.write_bytes(before)
        def evidence_mutation(self,kind=kind,slug=slug):
            p=self.root/'content'/kind/f'{slug}.body.html';before=p.read_bytes()
            try:
                p.write_bytes(before.replace(b'{{cite:source-one}}',b''));r=self.audit()
                self.assertIn('CITATION_WITNESS_DRIFT:'+slug,r['errors'])
            finally:p.write_bytes(before)
        def metadata_mutation(self,kind=kind,slug=slug):
            p=self.root/'content'/kind/f'{slug}.meta.json';before=p.read_bytes()
            try:
                d=json.loads(before);d['status']['publish']='published';p.write_text(json.dumps(d));r=self.audit()
                self.assertIn('PUBLISH_STATE_NOT_DRAFT:'+slug,r['errors']);self.assertIn('METADATA_SOURCE_DRIFT_REQUIRES_REVIEW:'+slug,r['errors'])
            finally:p.write_bytes(before)
        setattr(SourceCustodyR336,'test_body_depth_'+safe,body_mutation)
        setattr(SourceCustodyR336,'test_citation_loss_'+safe,evidence_mutation)
        setattr(SourceCustodyR336,'test_published_block_'+safe,metadata_mutation)
attach_mutation_tests()
if __name__=='__main__': unittest.main()
