"""R23 immutable corpus verification: 81 independently named adversarial tests."""
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import source_group_review_gate as gate

MANIFEST=gate.R23_MANIFEST
TAXONOMY='preparedness/taxonomy.json'
SOURCES=set(gate.SOURCE_FILES.values())|{'preparedness/sources/crosswalk.json'}
SLUGS=[f'article-{i:02}' for i in range(35)]
PATHS=sorted(SOURCES|{
    f'preparedness/content/articles/{s}.{ext}' for s in SLUGS
    for ext in ('body.html','meta.json')
}|{f'preparedness/content/tools/water-planner.{ext}'
   for ext in ('body.html','meta.json')})


def make_fixture(root):
    taxonomy={'base_path':'/preparedness/',
              'slate':[{'slug':s,'gate':i<27} for i,s in enumerate(SLUGS)],
              'tools':[{'slug':'water-planner','gate':True}]+[
                  {'slug':s,'status':'not-started'} for s in
                  ('pantry-worksheet','reunification-plan','kit-builder',
                   'checklists','offline-reference')]}
    contents={p:(b'<article>draft only</article>' if p.endswith('.body.html') else
                 gate.canonical({'status':'DRAFT','human_approved':False}))
              for p in PATHS}
    m={'schema_version':1,'issue':136,
       'repository':'finalvestigestudios/final-vestige-site-layer',
       'release_state':'HOLD','may_publish':False,
       'human_source_reviews_completed':False,'independent_QD_approval':False,
       'qualified_emergency_or_medical_safety_review':False,
       'link_and_claim_accuracy_independently_verified':False,
       'native_python_validation_build_or_html_parity_executed':False,
       'exceptions':[{'path':
         'preparedness/content/articles/preparedness-real-households.meta.json',
         'state':'NEEDS_HUMAN_DIFF_REVIEW','is_human_approved':False}],
       'baseline_corpus_source_blob_pairs':[
          {'path':p,'baseline_blob':gate.git_blob(contents[p]),
           'current_blob':gate.git_blob(contents[p])} for p in PATHS]}
    contents[MANIFEST]=gate.canonical(m)
    contents[TAXONOMY]=gate.canonical(taxonomy)
    for name,data in contents.items():
        file=root/name
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data)
    return m,taxonomy,contents


class ByteCustody(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.manifest,self.taxonomy,self.contents=make_fixture(self.root)
        self.manifest_pin=gate.git_blob(self.contents[MANIFEST])
        self.taxonomy_pin=gate.git_blob(self.contents[TAXONOMY])

    def audit(self):
        with mock.patch.dict(gate.FROZEN_BLOBS,{TAXONOMY:self.taxonomy_pin}):
            return gate.audit_archive_corpus(self.root,manifest_pin=self.manifest_pin)

    def hold(self):
        with self.assertRaises(gate.SourceGateHold):self.audit()

    def edit_manifest(self,edit,repin=True):
        new=copy.deepcopy(self.manifest)
        edit(new)
        data=gate.canonical(new)
        (self.root/MANIFEST).write_bytes(data)
        if repin:self.manifest_pin=gate.git_blob(data)

    def edit_taxonomy(self,edit,repin=True):
        new=copy.deepcopy(self.taxonomy)
        edit(new)
        data=gate.canonical(new)
        (self.root/TAXONOMY).write_bytes(data)
        if repin:self.taxonomy_pin=gate.git_blob(data)

    def test_pass_means_hold(self):
        r=self.audit()
        self.assertEqual(r['release_state'],'HOLD')
        self.assertEqual(r['original_corpus_source_files_pinned'],81)
        self.assertEqual(r['original_articles'],35)
        for key in ('may_publish','medical_safety_approved','independent_qd_pass',
                    'human_source_review_complete'):
            self.assertIs(r[key],False)

    def test_digest_reproducible(self):
        self.assertEqual(self.audit(),self.audit())

    def test_source_manifest_coedit_cannot_bypass_original_pin(self):
        p=PATHS[0]
        (self.root/p).write_bytes(b'rewritten')
        def change(m):
            m['baseline_corpus_source_blob_pairs'][0]['baseline_blob']=gate.git_blob(b'rewritten')
            m['baseline_corpus_source_blob_pairs'][0]['current_blob']=gate.git_blob(b'rewritten')
        self.edit_manifest(change,repin=False)
        self.hold()

    def test_taxonomy_unreviewed_safety_change(self):
        self.edit_taxonomy(lambda t:t['slate'][0].__setitem__('gate',False),repin=False)
        self.hold()

    def test_taxonomy_duplicate_url(self):
        self.edit_taxonomy(lambda t:t['slate'][0].__setitem__('slug',SLUGS[1]))
        self.hold()

    def test_taxonomy_ungated_water_planner(self):
        self.edit_taxonomy(lambda t:t['tools'][0].__setitem__('gate',False))
        self.hold()

    def test_manifest_claims_human_review(self):
        self.edit_manifest(lambda m:m.__setitem__('human_source_reviews_completed',True))
        self.hold()

    def test_manifest_claims_qd(self):
        self.edit_manifest(lambda m:m.__setitem__('independent_QD_approval',True))
        self.hold()

    def test_manifest_claims_medical_safety(self):
        self.edit_manifest(lambda m:m.__setitem__('qualified_emergency_or_medical_safety_review',True))
        self.hold()

    def test_manifest_clears_metadata_exception(self):
        self.edit_manifest(lambda m:m['exceptions'][0].__setitem__('is_human_approved',True))
        self.hold()

    def test_manifest_duplicate_source_path(self):
        self.edit_manifest(lambda m:m['baseline_corpus_source_blob_pairs'].__setitem__(1,
                           m['baseline_corpus_source_blob_pairs'][0]))
        self.hold()

    def test_manifest_shadow_path(self):
        self.edit_manifest(lambda m:m['baseline_corpus_source_blob_pairs'][0].__setitem__(
            'path','preparedness/../../etc/passwd'))
        self.hold()

    def test_manifest_missing_record(self):
        self.edit_manifest(lambda m:m['baseline_corpus_source_blob_pairs'].pop())
        self.hold()

    def test_manifest_baseline_current_mismatch(self):
        self.edit_manifest(lambda m:m['baseline_corpus_source_blob_pairs'][0].__setitem__(
            'current_blob','f'*40))
        self.hold()

    def test_shadow_article_file(self):
        (self.root/'preparedness/content/articles/phantom.body.html').write_text('draft')
        self.hold()

    def test_shadow_source_fragment(self):
        (self.root/'preparedness/sources/fragments/phantom.json').write_text('{}')
        self.hold()

    def test_symlink_source(self):
        x=self.root/PATHS[0]
        x.unlink()
        x.symlink_to(self.root/PATHS[1])
        self.hold()

    def test_missing_source(self):
        (self.root/PATHS[0]).unlink()
        self.hold()


for i,path in enumerate(PATHS):
    def new_test(target):
        def test(self):
            x=self.root/target
            x.write_bytes(x.read_bytes()+b'\n<!-- byte drift -->')
            self.hold()
        return test
    setattr(ByteCustody,f'test_81_file_drift_{i:02}',new_test(path))


class LiveCorpus(unittest.TestCase):
    def test_actual_checkout_81_file_hold(self):
        root=Path(__file__).resolve().parents[2]
        if not (root/'.git').exists() or not (root/MANIFEST).exists():
            self.skipTest('no complete private checkout: actual 81-file scan not executed')
        r=gate.audit_archive_corpus(root)
        self.assertIs(r['may_publish'],False)
        self.assertEqual(r['original_corpus_source_files_pinned'],81)

if __name__=='__main__':unittest.main()
